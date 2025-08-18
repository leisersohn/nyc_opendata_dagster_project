{{ config(materialized='view') }}

select *
from {{ ref('dwh_dim_ky') }}
where is_current = 1
