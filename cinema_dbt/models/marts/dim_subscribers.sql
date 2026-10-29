{{ config(materialized='table') }}

with stg_subscribers as (
    select * from {{ ref('stg_subscribers') }}
)
select
    subscriber_id,
    full_name,
    email,
    plan_type,
    registration_date
from stg_subscribers