with source as (
    select * from {{ source('raw_ecommerce', 'reviews') }}
)

select
    review_id,
    user_id as subscriber_id,
    product_id as movie_id,
    rating,
    coalesce(comment, 'Без коментаря') as comment,
    current_timestamp as review_at
from source