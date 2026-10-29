with source as (
    select * from {{ source('raw_ecommerce', 'subscribers') }}
),
cleaned as (
    select
        subscriber_id,
        full_name,
        coalesce(email, 'no_email@cinema.com') as email,
        city,
        subscription_tier as plan_type,
        cast(registration_date as date) as registration_date,
        row_number() over (
            partition by subscriber_id 
            order by registration_date desc
        ) as rn
    from source
)
select
    subscriber_id,
    full_name,
    email,
    city,
    plan_type,
    registration_date
from cleaned
where rn = 1