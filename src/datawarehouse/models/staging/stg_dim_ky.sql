{{
  config(
    materialized='table',
    pre_hook="{% if adapter.get_relation(this.database, this.schema, this.name) %}truncate table {{ this }}{% endif %}"
  )
}}

with source as (
    select distinct
        ky_cd,
        ofns_desc
    from {{ source('raw', 'nypd_arrest_json') }}
    where ky_cd is not null
),

cleaned as (
    select
        ky_cd as ky_id,
        ofns_desc as ky_desc,
        current_timestamp as _loaded_at,
        'dbt' as _loaded_by
    from source
)

select * from cleaned 