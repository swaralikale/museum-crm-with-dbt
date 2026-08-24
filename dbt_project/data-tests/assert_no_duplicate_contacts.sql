-- Singular data test: Detect potential duplicate contacts
with potential_duplicates as (
    select
        first_name,
        last_name,
        phone,
        count(distinct contact_id) as contact_count
    from {{ ref('stg_contacts') }}
    where phone is not null
        and first_name is not null
        and last_name is not null
    group by first_name, last_name, phone
    having count(distinct contact_id) > 1
)

select * from potential_duplicates