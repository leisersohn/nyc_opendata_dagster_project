{{ config(materialized='table') }}

with snap as (
  select
    *,
    case when dbt_valid_to is null then 1 else 0 end as is_current,
    {{ dbt_utils.generate_surrogate_key(['pd_id','dbt_valid_from']) }} as pd_sk
  from {{ ref('dim_pd_snapshot') }}
)

select
  pd_sk,
  pd_id,
  pd_desc,
  dbt_valid_from as valid_from,
  dbt_valid_to   as valid_to,
  is_current
from snap