with source as (
    select * from {{ source('raw_ecommerce', 'ratings') }}
)
select
    rating_id as review_id,
    subscriber_id,
    movie_id,
    score as rating,
    coalesce(comment, 'Без коментаря') as comment,
    cast(rating_date as timestamp) as review_at
from source