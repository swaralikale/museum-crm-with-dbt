with source as (
    select * from {{ source('museum_raw', 'raw_tickets') }}
),

cleaned as (
    select
        ticket_id,
        contact_id,
        ticket_type,
        quantity,
        unit_price,
        total_amount,
        coupon_code,
        discount_amount,
        purchase_date,
        visit_date,
        coupon_code is not null as used_coupon,
        created_at
    from source
    where ticket_id is not null
        and purchase_date <= current_date
)

select * from cleaned