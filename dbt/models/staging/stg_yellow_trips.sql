with source as (

    select * from {{ source('raw', 'yellow_trips') }}

),

renamed as (

    select
        'yellow'                                        as service_type,
        cast(vendorid as integer)                       as vendor_id,
        cast(tpep_pickup_datetime as timestamp_ntz)     as pickup_at,
        cast(tpep_dropoff_datetime as timestamp_ntz)    as dropoff_at,
        cast(passenger_count as integer)                as passenger_count,
        cast(trip_distance as number(10, 2))            as trip_distance_mi,
        cast(ratecodeid as integer)                     as rate_code_id,
        cast(store_and_fwd_flag as varchar)             as store_and_fwd_flag,
        cast(pulocationid as integer)                   as pickup_zone_id,
        cast(dolocationid as integer)                   as dropoff_zone_id,
        cast(payment_type as integer)                   as payment_type_id,
        cast(fare_amount as number(12, 2))              as fare_amount,
        cast(extra as number(12, 2))                    as extra_amount,
        cast(mta_tax as number(12, 2))                  as mta_tax,
        cast(tip_amount as number(12, 2))               as tip_amount,
        cast(tolls_amount as number(12, 2))             as tolls_amount,
        cast(improvement_surcharge as number(12, 2))    as improvement_surcharge,
        cast(congestion_surcharge as number(12, 2))     as congestion_surcharge,
        cast(airport_fee as number(12, 2))              as airport_fee,
        cast(cbd_congestion_fee as number(12, 2))       as cbd_congestion_fee,
        cast(null as number(12, 2))                     as ehail_fee,
        cast(total_amount as number(12, 2))             as total_amount,
        cast(null as integer)                           as trip_type,
        _source_file                                    as source_file,
        to_date(regexp_substr(_source_file, '[0-9]{4}-[0-9]{2}') || '-01') as source_month,
        _loaded_at                                      as loaded_at

    from source

)

select * from renamed