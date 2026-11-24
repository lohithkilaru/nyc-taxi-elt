select
    pickup_date_key,
    pickup_hour,
    service_type,

    count(*)                                  as trips,
    sum(total_amount)                         as total_revenue,
    sum(tip_amount)                           as tip_revenue,
    sum(fare_amount)                          as fare_revenue,
    avg(trip_duration_min)                    as avg_duration_min,
    avg(avg_speed_mph)                        as avg_speed_mph,
    sum(passenger_count)                      as passengers

from {{ ref('fct_trips') }}
group by 1, 2, 3