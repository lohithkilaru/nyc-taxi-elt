with by_zone as (

    select
        pickup_zone_id,
        sum(case when service_type = 'yellow' then trips else 0 end) as yellow_trips,
        sum(case when service_type = 'green' then trips else 0 end) as green_trips
    from {{ ref('agg_daily_zone_revenue') }}
    group by 1

)

select
    z.zone_name,
    z.borough,
    b.yellow_trips,
    b.green_trips,
    round(100 * b.green_trips / (b.yellow_trips + b.green_trips), 1) as green_share_pct
from by_zone as b
inner join {{ ref('dim_zone') }} as z on b.pickup_zone_id = z.zone_id
where b.yellow_trips >= 1000 and b.green_trips >= 1000
order by least(b.yellow_trips, b.green_trips) desc
limit 20
