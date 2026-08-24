with visits as (
    select * from {{ ref('stg_visits') }}
),

members as (
    select * from {{ ref('stg_memberships') }}
),

contacts as (
    select * from {{ ref('stg_contacts') }}
),

visit_sequence as (
    select
        contact_id,
        visit_date,
        row_number() over (partition by contact_id order by visit_date) as visit_number,
        lag(visit_date) over (partition by contact_id order by visit_date) as previous_visit_date
    from visits
),

visit_cadence as (
    select
        contact_id,
        min(visit_date) as first_visit_date,
        count(*) as total_visits,
        avg(visit_date - previous_visit_date) as avg_days_between_visits
    from visit_sequence
    group by contact_id
),

first_membership as (
    select
        contact_id,
        min(start_date) as first_membership_date
    from members
    group by contact_id
)

select
    c.contact_id,
    c.first_name,
    c.last_name,
    c.acquisition_source,
    vc.first_visit_date,
    vc.total_visits,
    vc.avg_days_between_visits,
    ntile(4) over (order by vc.total_visits desc) as visit_frequency_quartile,
    fm.first_membership_date,
    fm.first_membership_date is not null as converted_to_member,
    case
        when fm.first_membership_date is not null and vc.first_visit_date is not null
        then fm.first_membership_date - vc.first_visit_date
        else null
    end as days_to_convert
from visit_cadence vc
inner join contacts c on vc.contact_id = c.contact_id
left join first_membership fm on vc.contact_id = fm.contact_id