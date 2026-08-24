with source as (
    select * from {{ source('museum_raw', 'raw_donations') }}
),

cleaned as (
    select
        donation_id,
        contact_id,
        campaign_id,
        amount,
        donation_date,
        donation_type,
        is_recurring,
        tax_receipt_sent,
        created_at
    from source
    where donation_id is not null
        and amount > 0
)

select * from cleaned