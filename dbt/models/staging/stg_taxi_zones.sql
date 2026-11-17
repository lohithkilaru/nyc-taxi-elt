select
    cast(locationid as integer)     as zone_id,
    borough,
    zone                            as zone_name,
    service_zone
from {{ ref('taxi_zone_lookup') }}