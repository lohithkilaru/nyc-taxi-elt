select
    zone_id,
    zone_name,
    borough,
    service_zone,
    zone_name ilike '%airport%' as is_airport
from {{ ref('stg_taxi_zones') }}