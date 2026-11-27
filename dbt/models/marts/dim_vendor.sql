with known as (

    select
        vendor_id,
        vendor_name
    from {{ ref('vendor_lookup') }}

),

unseen as (

    select distinct
        vendor_id,
        'Unknown (code ' || vendor_id || ')' as vendor_name
    from {{ ref('int_trips_validated') }}
    where
        vendor_id is not null
        and vendor_id not in (select vendor_id from known)

)

select * from known
union all
select * from unseen
