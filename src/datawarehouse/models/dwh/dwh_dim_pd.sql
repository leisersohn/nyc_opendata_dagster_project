{{
  config(
    materialized='incremental',
    on_schema_change='sync_all_columns',
    unique_key='pd_id'
  )
}}

with staging as (
    select * from {{ ref('stg_dim_pd') }}
),

existing_dim as (
    select * from {{ this }}
),

-- SCD Type 1
final as (
    -- Get records last status from staging
    select
        *
    from
        staging

    UNION ALL

    -- Keep deleted records from DWH
    select
        e.*
    from
        existing_dim e
        left join staging s on (e.pd_id = s.pd_id)
    where
        s.pd_id is null        
)

select * from final 