with trips as (
    select
        {{ dbt_utils.generate_surrogate_key([
            'service_type', 'vendor_id', 'pickup_at', 'dropoff_at',
            'pickup_zone_id', 'dropoff_zone_id', 'total_amount'
        ]) }} as trip_id,
        *,
        datediff('minute', pickup_at, dropoff_at) as trip_duration_min
    from {{ ref('int_trips_unioned') }}
),

numbered as (
    select
        *,
        row_number() over (partition by source_month, trip_id order by loaded_at) as copy_number
    from trips
)

select
    * exclude (copy_number),
    case
        when pickup_at is null or dropoff_at is null           then 'missing_timestamp'
        when date_trunc('month', pickup_at) != source_month     then 'pickup_outside_file_month'
        when dropoff_at <= pickup_at                            then 'dropoff_not_after_pickup'
        when trip_duration_min > 24 * 60                        then 'trip_over_24h'
        when fare_amount < 0 or total_amount < 0                then 'negative_amount'
        when trip_distance_mi <= 0                              then 'non_positive_distance'
        when copy_number > 1                                    then 'duplicate_trip'
    end as reject_reason
from numbered