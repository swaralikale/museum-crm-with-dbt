with members as (
    select * from {{ ref('stg_memberships') }}
),

contacts as (
    select * from {{ ref('stg_contacts') }}
),

donations as (
    select
        contact_id,
        count(*) as donation_count,
        sum(amount) as total_donations
    from {{ ref('stg_donations') }}
    group by contact_id
),

tickets as (
    select
        contact_id,
        count(*) as ticket_count,
        sum(total_amount) as total_ticket_spend
    from {{ ref('stg_tickets') }}
    group by contact_id
),

member_stats as (
    select
        contact_id,
        count(*) as membership_count,
        sum(amount_paid) as total_membership_spend,
        max(renewal_count) as max_renewal_count,
        min(start_date) as first_membership_date,
        max(end_date) as latest_end_date,
        max(case when status = 'active' then 1 else 0 end) as has_active_membership
    from members
    group by contact_id
)

select
    c.contact_id,
    c.first_name,
    c.last_name,
    c.email,
    c.acquisition_source,
    ms.membership_count,
    ms.max_renewal_count,
    ms.first_membership_date,
    ms.latest_end_date,
    ms.has_active_membership = 1 as is_active_member,
    case
        when ms.has_active_membership = 1 then 'active'
        when ms.latest_end_date >= current_date - interval '90 days' then 'at_risk'
        else 'lapsed'
    end as renewal_status,
    current_date - ms.first_membership_date as tenure_days,
    coalesce(ms.total_membership_spend, 0) as total_membership_spend,
    coalesce(d.total_donations, 0) as total_donations,
    coalesce(d.donation_count, 0) as donation_count,
    coalesce(t.total_ticket_spend, 0) as total_ticket_spend,
    coalesce(t.ticket_count, 0) as ticket_count,
    coalesce(ms.total_membership_spend, 0)
        + coalesce(d.total_donations, 0)
        + coalesce(t.total_ticket_spend, 0) as total_lifetime_value,
    rank() over (
        order by coalesce(ms.total_membership_spend, 0)
            + coalesce(d.total_donations, 0)
            + coalesce(t.total_ticket_spend, 0) desc
    ) as ltv_rank,
    ntile(4) over (
        order by coalesce(ms.total_membership_spend, 0)
            + coalesce(d.total_donations, 0)
            + coalesce(t.total_ticket_spend, 0) desc
    ) as ltv_quartile
from member_stats ms
inner join contacts c on ms.contact_id = c.contact_id
left join donations d on ms.contact_id = d.contact_id
left join tickets t on ms.contact_id = t.contact_id