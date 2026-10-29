with source as (
    select * from {{ source('raw_ecommerce', 'views') }}
)
select
    view_id,
    subscriber_id,
    movie_id,
    cast(view_date as timestamp) as view_at,
    cast(watch_duration_minutes as integer) as watch_time_minutes
from source