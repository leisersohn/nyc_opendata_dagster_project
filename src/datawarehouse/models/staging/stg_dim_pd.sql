{{
  config(
    materialized='table',
    pre_hook="{% if adapter.get_relation(this.database, this.schema, this.name) %}truncate table {{ this }}{% endif %}"
  )
}}

with source as (
    select distinct
        pd_cd,
        pd_desc
    from {{ source('raw', 'nypd_arrest_json') }}
    where pd_cd is not null
),

cleaned as (
    select
        pd_cd as pd_id,
        pd_desc as pd_desc,
        current_timestamp as _loaded_at,
        'dbt' as _loaded_by
    from source
)

select * from cleaned 