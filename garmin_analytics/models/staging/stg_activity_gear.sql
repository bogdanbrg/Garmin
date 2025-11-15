-- Staging model: Clean and standardize activity-gear relationships
-- Source: bronze_activity_gear table from Garmin API

SELECT
    activityId as activity_id,
    uuid as gear_id,  -- Match naming from stg_gear_list
    gearPk as gear_pk,
    userProfilePk as user_profile_pk,
    customMakeModel as gear_name,
    
    -- Metadata
    CURRENT_TIMESTAMP as dbt_loaded_at
    
FROM {{ source('main', 'bronze_activity_gear') }}