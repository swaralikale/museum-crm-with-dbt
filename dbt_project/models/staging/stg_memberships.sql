with source as (
    select * from {{ source('museum_raw', 'raw_memberships') }}
),

deduplicated as (
    select
        *,
        row_number() over (
            partition by membership_id
            order by created_at desc
        ) as row_num
    from source
),

cleaned as (
    select
        membership_id,
        contact_id,
        membership_type,
        case
            when status in ('active', 'expired', 'cancelled', 'pending') then status
            else 'unknown'
        end as status,
        start_date,
        end_date,
        renewal_count,
        amount_paid,
        payment_method,
        created_at
    from deduplicated
    where row_num = 1
)

select * from cleaned