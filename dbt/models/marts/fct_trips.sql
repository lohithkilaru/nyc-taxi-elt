{{
    config(
        materialized='incremental',
        incremental_strategy='delete+insert',
        unique_key='source_month'
    )
}}

with trips as (
    select * from {{ ref('int_trips_validated') }}

    {% if is_incremental() %}
    where source_month in (
        select distinct source_month from {{ ref('int_trips_validated') }}
        where loaded_at > (
            select coalesce(max(loaded_at), '1900-01-01'::timestamp_ltz) from {{ this }}
        )
    )
    {% endif %}
)


select
    -- primary key
    trip_id,

    -- keys to dimensions
    to_number(to_char(pickup_at::date, 'YYYYMMDD'))  as pickup_date_key,
    pickup_zone_id,
    dropoff_zone_id,
    vendor_id,
    payment_type_id,
    rate_code_id,

    -- trip attributes
    service_type,
    pickup_at,
    dropoff_at,
    hour(pickup_at)                                  as pickup_hour,
    trip_type,
    store_and_fwd_flag,

    -- measures: trip
    passenger_count,
    trip_distance_mi,
    trip_duration_min,
    round(trip_distance_mi / nullif(trip_duration_min, 0) * 60, 2) as avg_speed_mph,

    -- measures: money
    fare_amount,
    extra_amount,
    mta_tax,
    tip_amount,
    tolls_amount,
    improvement_surcharge,
    congestion_surcharge,
    airport_fee,
    cbd_congestion_fee,
    ehail_fee,
    total_amount,

    -- lineage, used for incremental loads
    source_month,
    source_file,
    loaded_at

from trips