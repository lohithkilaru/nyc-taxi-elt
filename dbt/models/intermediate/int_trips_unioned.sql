select * from {{ ref('stg_yellow_trips') }}
union all
select * from {{ ref('stg_green_trips') }}