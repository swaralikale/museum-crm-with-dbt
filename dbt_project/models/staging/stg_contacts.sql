with source as (
    select * from {{ source('museum_raw', 'raw_contacts') }}
),

cleaned as (
    select
        contact_id,
        initcap(trim(first_name)) as first_name,
        initcap(trim(last_name)) as last_name,
        lower(trim(email)) as email,
        phone,
        address_city,
        address_state,
        source as acquisition_source,
        coalesce(email_consent, false) as email_consent,
        coalesce(communication_preference, 'none') as communication_preference,
        coalesce(privacy_opt_out, false) as privacy_opt_out,
        case
            when email is not null
                and email_consent = true
                and privacy_opt_out = false
            then true
            else false
        end as is_email_contactable,
        email is not null as has_valid_email,
        created_at,
        updated_at
    from source
    where contact_id is not null
)

select * from cleaned