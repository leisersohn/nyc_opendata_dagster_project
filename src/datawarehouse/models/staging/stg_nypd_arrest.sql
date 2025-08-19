{{
  config(
    materialized='incremental',
    partition_by={
        "field": "arrest_date",
        "data_type": "date",
        "granularity": "day"
    },
    pre_hook="""
        {% if execute %}
            {% if adapter.get_relation(this.database, this.schema, this.name) %}
                truncate table {{ this }}
            {% endif %}
        {% endif %}
    """
  )
}}

with source as (
    select *
    from {{ source('raw', 'nypd_arrest_json') }}
    where arrest_date = '{{ var("partition_date") }}'
),

cleaned as (
    select
        arrest_key,
        arrest_date,
        pd_cd as pd_id,
        pd_desc,
        ky_cd as ky_id,
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
        current_timestamp as _loaded_at,
        'dbt' as _loaded_by
    from source
)

select * from cleaned 