select
    z.zone_name,
    z.borough,
    f.pickup_hour,
    count(*) as trips,
    sum(f.total_amount) as revenue
from {{ ref('fct_trips') }} as f
inner join {{ ref('dim_zone') }} as z on f.pickup_zone_id = z.zone_id
group by 1, 2, 3
order by revenue desc
limit 20
