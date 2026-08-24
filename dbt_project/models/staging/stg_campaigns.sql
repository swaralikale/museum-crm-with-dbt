with source as (
    select * from {{ source('museum_raw', 'raw_campaigns') }}
),

cleaned as (
    select
        campaign_id,
        campaign_name,
        campaign_type,
        start_date,
        end_date,
        budget,
        target_audience,
        status,
        end_date - start_date as duration_days,
        created_at
    from source
    where campaign_id is not null
)

select * from cleaned