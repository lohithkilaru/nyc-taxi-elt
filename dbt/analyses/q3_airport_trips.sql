select
    case
        when pz.is_airport then 'From airport'
        when dz.is_airport then 'To airport'
        else 'Non-airport'
    end as trip_category,
    count(*) as trips,
    round(100 * count(*) / sum(count(*)) over (), 2) as pct_of_trips,
    round(avg(f.total_amount), 2) as avg_revenue,
    sum(f.total_amount) as total_revenue
from {{ ref('fct_trips') }} as f
inner join {{ ref('dim_zone') }} as pz on f.pickup_zone_id = pz.zone_id
inner join {{ ref('dim_zone') }} as dz on f.dropoff_zone_id = dz.zone_id
group by 1
order by trips desc
