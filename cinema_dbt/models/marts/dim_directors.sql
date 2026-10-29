{{ config(materialized='table') }}

with stg_directors as (
    select * from {{ ref('stg_directors') }}
)
select
    director_id,
    director_name
from stg_directors