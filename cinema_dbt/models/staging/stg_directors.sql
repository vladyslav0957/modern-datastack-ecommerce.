with source as (
    select * from {{ source('raw_ecommerce', 'directors') }}
)
select
    director_id,
    director_name,
    country
from source