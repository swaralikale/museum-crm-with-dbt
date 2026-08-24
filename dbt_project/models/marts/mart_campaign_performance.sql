with campaigns as (
    select * from {{ ref('stg_campaigns') }}
),

donations as (
    select * from {{ ref('stg_donations') }}
),

memberships as (
    select * from {{ ref('stg_memberships') }}
),

campaign_donations as (
    select
        campaign_id,
        count(*) as donation_count,
        sum(amount) as total_donation_revenue,
        count(distinct contact_id) as unique_donors
    from donations
    where campaign_id is not null
    group by campaign_id
),

campaign_memberships as (
    select
        d.campaign_id,
        count(distinct m.contact_id) as memberships_driven
    from donations d
    inner join memberships m on d.contact_id = m.contact_id
        and m.start_date between d.donation_date - interval '30 days'
            and d.donation_date + interval '30 days'
    where d.campaign_id is not null
    group by d.campaign_id
)

select
    c.campaign_id,
    c.campaign_name,
    c.campaign_type,
    c.start_date,
    c.end_date,
    c.duration_days,
    c.budget,
    c.target_audience,
    c.status,
    coalesce(cd.donation_count, 0) as donation_count,
    coalesce(cd.total_donation_revenue, 0) as total_donation_revenue,
    coalesce(cd.unique_donors, 0) as unique_donors,
    coalesce(cm.memberships_driven, 0) as memberships_driven,
    case
        when c.budget > 0
        then round(coalesce(cd.total_donation_revenue, 0) / c.budget, 2)
        else 0
    end as roi_ratio,
    case
        when c.budget > 0
        then round(c.budget / nullif(coalesce(cd.unique_donors, 0), 0), 2)
        else null
    end as cost_per_donor
from campaigns c
left join campaign_donations cd on c.campaign_id = cd.campaign_id
left join campaign_memberships cm on c.campaign_id = cm.campaign_id