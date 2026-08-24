with donations as (
    select * from {{ ref('stg_donations') }}
),

contacts as (
    select * from {{ ref('stg_contacts') }}
),

donor_stats as (
    select
        contact_id,
        count(*) as donation_count,
        sum(amount) as total_donated,
        avg(amount) as avg_donation,
        max(donation_date) as last_donation_date,
        min(donation_date) as first_donation_date,
        sum(case when is_recurring then 1 else 0 end) as recurring_donation_count
    from donations
    group by contact_id
)

select
    c.contact_id,
    c.first_name,
    c.last_name,
    c.email,
    c.is_email_contactable,
    ds.donation_count,
    ds.total_donated,
    ds.avg_donation,
    ds.first_donation_date,
    ds.last_donation_date,
    ds.recurring_donation_count,
    current_date - ds.last_donation_date as days_since_last_donation,
    case
        when ds.total_donated >= 5000 then 'major'
        when ds.total_donated >= 1000 then 'mid_level'
        when ds.total_donated >= 100 then 'small'
        else 'micro'
    end as donor_tier,
    case
        when current_date - ds.last_donation_date <= 90 then 'active'
        when current_date - ds.last_donation_date <= 365 then 'lapsing'
        else 'lapsed'
    end as recency_segment,
    ds.recurring_donation_count > 0 as is_recurring_donor
from donor_stats ds
inner join contacts c on ds.contact_id = c.contact_id