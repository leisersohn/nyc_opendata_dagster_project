{% snapshot dim_ky_snapshot %}

{{
  config(
    target_schema='snapshots',
    unique_key='ky_id',
    strategy='check',
    check_cols=['ky_desc']
  )
}}

select
  ky_id,
  ky_desc
from {{ ref('stg_dim_ky') }}

{% endsnapshot %}