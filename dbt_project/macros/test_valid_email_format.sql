{% test valid_email_format(model, column_name) %}

with validation as (
    select
        {{ column_name }} as email_value
    from {{ model }}
    where {{ column_name }} is not null
)

select email_value
from validation
where email_value not like '%_@_%.__%'

{% endtest %}