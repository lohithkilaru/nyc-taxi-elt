with known as (
    select
        rate_code_id,
        rate_code_name
    from {{ ref('rate_code_lookup') }}
),

unseen as (
    select distinct
        rate_code_id,
        'Unknown (code ' || rate_code_id || ')' as rate_code_name
    from {{ ref('int_trips_validated') }}
    where
        rate_code_id is not null
        and rate_code_id not in (select rate_code_id from known)
)

select * from known
union all
select * from unseen
