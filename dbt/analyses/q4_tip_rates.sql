select
    coalesce(p.payment_type_name, 'Not recorded') as payment_type,
    z.borough,
    case
        when f.pickup_hour between 6 and 11 then 'Morning'
        when f.pickup_hour between 12 and 16 then 'Afternoon'
        when f.pickup_hour between 17 and 21 then 'Evening'
        else 'Night'
    end as time_of_day,
    count(*) as trips,
    round(100 * sum(f.tip_amount) / nullif(sum(f.fare_amount), 0), 1) as tip_rate_pct
from {{ ref('fct_trips') }} as f
left join {{ ref('dim_payment_type') }} as p on f.payment_type_id = p.payment_type_id
inner join {{ ref('dim_zone') }} as z on f.pickup_zone_id = z.zone_id
group by 1, 2, 3
having count(*) > 1000
order by payment_type, borough, time_of_day
