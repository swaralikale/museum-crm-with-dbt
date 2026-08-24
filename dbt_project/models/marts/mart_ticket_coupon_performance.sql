with tickets as (
    select * from {{ ref('stg_tickets') }}
),

summary_by_type as (
    select
        ticket_type,
        count(*) as total_purchases,
        sum(quantity) as total_tickets_sold,
        sum(total_amount) as total_revenue,
        avg(unit_price) as avg_unit_price,
        sum(case when used_coupon then 1 else 0 end) as coupon_purchases,
        sum(discount_amount) as total_discounts_given
    from tickets
    group by ticket_type
),

coupon_stats as (
    select
        coupon_code,
        count(*) as times_used,
        sum(discount_amount) as total_discount_value,
        sum(total_amount) as revenue_with_coupon,
        avg(quantity) as avg_quantity_per_purchase
    from tickets
    where used_coupon
    group by coupon_code
)

select
    st.ticket_type,
    st.total_purchases,
    st.total_tickets_sold,
    st.total_revenue,
    st.avg_unit_price,
    st.coupon_purchases,
    st.total_discounts_given,
    case
        when st.total_purchases > 0
        then round(st.coupon_purchases::numeric / st.total_purchases * 100, 1)
        else 0
    end as coupon_usage_rate_pct,
    case
        when st.total_revenue + st.total_discounts_given > 0
        then round(st.total_discounts_given / (st.total_revenue + st.total_discounts_given) * 100, 1)
        else 0
    end as discount_impact_pct
from summary_by_type st
order by st.total_revenue desc