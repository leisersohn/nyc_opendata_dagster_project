{{
  config(
    materialized='incremental',
    partition_by={
        "field": "partition_date",
        "data_type": "date",
        "granularity": "day"
    },
    on_schema_change='sync_all_columns'
  )
}}

with source as (
    select * from {{ source('raw', 'nypd_arrest_json') }}
    {% if is_incremental() %}
    where partition_date = '{{ var("partition_date") }}'
    {% endif %}
),

cleaned as (
    select
        arrest_key,
        arrest_date,
        pd_cd,
        pd_desc,
        ky_cd,
        ofns_desc,
        law_code,
        law_cat_cd,
        arrest_boro,
        arrest_precinct,
        jurisdiction_code,
        age_group,
        perp_sex,
        perp_race,
        x_coord_cd,
        y_coord_cd,
        latitude,
        longitude,
        geocoded_column,
        partition_date,
        -- Use partition_date from source
        try_cast(partition_date as date) as partition_date, -- Add metadata on partition from source
        current_timestamp as _loaded_at, -- Add metadata on load time
        'dbt' as _loaded_by -- Add metadata on load system
    from source
)

select * from cleaned 