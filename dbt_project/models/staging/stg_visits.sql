with source as (
    select * from {{ source('museum_raw', 'raw_visits') }}
),

cleaned as (
    select
        visit_id,
        contact_id,
        visit_date,
        exhibit_visited,
        duration_minutes,
        is_member_visit,
        party_size,
        created_at
    from source
    where visit_id is not null
        and visit_date <= current_date
)

select * from cleaned