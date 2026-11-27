with raw as (

    select
        source_file,
        count(*) as raw_rows
    from {{ ref('stg_yellow_trips') }}
    group by 1
    union all
    select
        source_file,
        count(*) as raw_rows
    from {{ ref('stg_green_trips') }}
    group by 1

),

validated as (

    select
        source_file,
        count(*) as validated_rows
    from {{ ref('int_trips_validated') }}
    group by 1

),

rejected as (

    select
        source_file,
        count(*) as rejected_rows
    from {{ ref('int_trip_rejects') }}
    group by 1

)

select
    raw.source_file,
    raw.raw_rows,
    coalesce(validated.validated_rows, 0) as validated_rows,
    coalesce(rejected.rejected_rows, 0) as rejected_rows
from raw
left join validated on raw.source_file = validated.source_file
left join rejected using (source_file)
where raw.raw_rows != coalesce(validated.validated_rows, 0) + coalesce(rejected.rejected_rows, 0)
