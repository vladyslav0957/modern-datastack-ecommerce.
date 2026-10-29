{{ config(materialized='table') }}

with stg_movies as (
    select * from {{ ref('stg_movies') }}
),
stg_directors as (
    select * from {{ ref('stg_directors') }}
)
select
    m.movie_id,
    m.title,
    m.genre,
    m.release_year,
    m.price,
    d.director_name
from stg_movies m
left join stg_directors d on m.director_id = d.director_id