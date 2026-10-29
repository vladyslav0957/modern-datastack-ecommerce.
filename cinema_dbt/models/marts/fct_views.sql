{{ config(materialized='table') }}

with stg_views as (
    select * from {{ ref('stg_views') }}
),
stg_subscribers as (
    select * from {{ ref('stg_subscribers') }}
),
stg_movies as (
    select * from {{ ref('stg_movies') }}
)
select
    v.view_id,
    v.subscriber_id,
    v.movie_id,
    v.view_at,
    v.watch_time_minutes,
    m.price as movie_price
from stg_views v
join stg_subscribers s on v.subscriber_id = s.subscriber_id
join stg_movies m on v.movie_id = m.movie_id