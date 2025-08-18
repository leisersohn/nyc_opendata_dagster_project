{{ config(materialized='view') }}

select *
from {{ ref('dwh_dim_pd') }}
where is_current = 1