{% snapshot dim_pd_snapshot %}

{{
  config(
    target_schema='snapshots',
    unique_key='pd_id',
    strategy='check',
    check_cols=['pd_desc']
  )
}}

select
  pd_id,
  pd_desc
from {{ ref('stg_dim_pd') }}

{% endsnapshot %}