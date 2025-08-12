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
    unique_key,
    created_date,
    closed_date,
    agency,
    agency_name,
    complaint_type,
    descriptor,
    location_type,
    incident_zip,
    incident_address,
    street_name,
    cross_street_1,
    cross_street_2,
    intersection_street_1,
    intersection_street_2,
    address_type,
    city,
    landmark,
    facility_type,
    status,
    due_date,
    resolution_description,
    resolution_action_updated_date,
    community_board,
    bbl,
    borough,
    x_coordinate_state_plane,
    y_coordinate_state_plane,
    open_data_channel_type,
    park_facility_name,
    park_borough,
    vehicle_type,
    taxi_company_borough,
    taxi_pick_up_location,
    bridge_highway_name,
    bridge_highway_direction,
    road_ramp,
    bridge_highway_segment,
    latitude,
    longitude,
    location,
    -- Use partition_date from source
    try_cast(partition_date as date) as partition_date,
    -- Add metadata
    current_timestamp as _loaded_at,
    'dbt' as _loaded_by
from source
)

select * from cleaned 