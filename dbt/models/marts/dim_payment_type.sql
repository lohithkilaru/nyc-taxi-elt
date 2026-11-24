with known as (

    select payment_type_id, payment_type_name
    from {{ ref('payment_type_lookup') }}

),


unseen as (

    select distinct
        payment_type_id,
        'Unknown (code ' || payment_type_id || ')' as payment_type_name
    from {{ ref('int_trips_validated') }}
    where payment_type_id is not null
      and payment_type_id not in (select payment_type_id from known)

)

select * from known
union all
select * from unseen