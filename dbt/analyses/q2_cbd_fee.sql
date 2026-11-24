select
    z.zone_name,
    z.borough,
    sum(a.trips_with_cbd_fee)                                  as trips_paying_fee,
    round(100 * sum(a.trips_with_cbd_fee) / sum(a.trips), 1)   as pct_trips_paying,
    sum(a.cbd_fee_total)                                       as total_fee,
    round(sum(a.cbd_fee_total) / nullif(sum(a.trips_with_cbd_fee), 0), 2) as avg_fee_when_paid
from {{ ref('agg_daily_zone_revenue') }} a
join {{ ref('dim_zone') }} z on a.pickup_zone_id = z.zone_id
group by 1, 2
order by total_fee desc
limit 20