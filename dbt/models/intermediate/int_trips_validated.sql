{{

    config(
        materialized = 'incremental',
        incremental_strategy = 'delete+insert',
        unique_key = 'source_month'
    )
}}

select * exclude (reject_reason)
from {{ ref('int_trips_checked') }}
where reject_reason is null

{% if is_incremental() %}
and source_month in (
    select distinct source_month
    from {{ ref('int_trips_checked') }}
    where loaded_at > (
        select coalesce(max(loaded_at), '1900-01-01':: timestamp_ltz) from {{ this }}
    )
)
{% endif %}