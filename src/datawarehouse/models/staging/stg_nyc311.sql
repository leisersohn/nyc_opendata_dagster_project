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
    select * from {{ source('raw', 'nyc311_csv') }}
    {% if is_incremental() %}
    where partition_date = '{{ var("partition_date") }}'
    {% endif %}
),

cleaned as (
    select
        -- Clean and validate agency_name
        case 
            when agency_name is null or trim(agency_name) = '' then 'Unknown'
            else trim(agency_name)
        end as agency_name,
        
        -- Clean and validate complaint_type
        case 
            when complaint_type is null or trim(complaint_type) = '' then 'Unknown'
            else trim(complaint_type)
        end as complaint_type,
        
        -- Clean descriptor
        case 
            when descriptor is null then 'No description provided'
            else trim(descriptor)
        end as descriptor,
        
        -- Clean location_type
        case 
            when location_type is null or trim(location_type) = '' then 'Unknown'
            else trim(location_type)
        end as location_type,
        
        -- Use partition_date from source
        try_cast(partition_date as date) as partition_date,
        
        -- Add metadata
        current_timestamp as _loaded_at,
        'dbt' as _loaded_by
        
    from source
)

select * from cleaned 