select
    pickup_date_key,
    pickup_zone_id,
    service_type,
    count(*) as trips,
    sum(total_amount) as total_revenue,
    sum(fare_amount) as fare_revenue,
    sum(tip_amount) as tip_revenue,
    sum(cbd_congestion_fee) as cbd_congestion_revenue,
    count_if(cbd_congestion_fee > 0) as trips_with_cbd_fee,
    sum(airport_fee) as airport_fee_total,
    avg(trip_distance_mi) as avg_distance_mi,
    avg(total_amount) as avg_revenue_per_trip
from
    {{ ref('fct_trips') }}
group by 1, 2, 3
