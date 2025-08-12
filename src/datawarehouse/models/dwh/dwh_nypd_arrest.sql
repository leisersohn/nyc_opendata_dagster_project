{{
  config(
    materialized='incremental',
    partition_by={
        "field": "partition_date",
        "data_type": "date",
        "granularity": "day"
    },
    on_schema_change='sync_all_columns',
    pre_hook="delete from {{ this }} where partition_date = '{{ var('partition_date') }}'"
  )
}}

with staging as (
    select * from {{ ref('stg_nypd_arrest') }}
),

-- Join with dimension tables to get current descriptions
enriched as (
    select
        s.arrest_key,
        s.arrest_date,
        s.pd_id,
        s.ky_id,
        s.law_code,
        s.law_cat_cd,
        s.arrest_boro,
        s.arrest_precinct,
        s.jurisdiction_code,
        s.age_group,
        s.perp_sex,
        s.perp_race,
        s.x_coord_cd,
        s.y_coord_cd,
        s.latitude,
        s.longitude,
        s.geocoded_column,
        '{{ var("partition_date") }}'::date as partition_date,
        s._loaded_at,
        'dbt' as _loaded_by
    from staging s
)

select * from enriched 