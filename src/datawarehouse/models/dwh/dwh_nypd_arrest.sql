{{
  config(
    materialized='incremental',
    partition_by={
        "field": "partition_date",
        "data_type": "date",
        "granularity": "day"
    },
    on_schema_change='sync_all_columns',
    pre_hook="""
        {% if execute %}
            {% if adapter.get_relation(this.database, this.schema, this.name) %}
                delete from {{ this }} where partition_date = '{{ var('partition_date') }}'
            {% endif %}
        {% endif %}
    """
  )
}}

with staging as (
    select * from {{ ref('stg_nypd_arrest') }}
),

-- Join with dimension tables to get surrogate keys and current descriptions
enriched as (
    select
        s.arrest_key,
        s.arrest_date,
        pd.pd_sk,
        ky.ky_sk,
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
    left join {{ ref('dwh_dim_pd_current') }} pd on s.pd_id = pd.pd_id
    left join {{ ref('dwh_dim_ky_current') }} ky on s.ky_id = ky.ky_id
)

select * from enriched 