with source as (
    select * from {{ source('raw_ecommerce', 'movies') }}
),
cleaned as (
    select
        movie_id,
        director_id,
        title,
        genre,
        release_year,
        price_per_view as price
    from source
    where price_per_view > 0
)
select * from cleaned