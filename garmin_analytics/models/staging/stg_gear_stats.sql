-- Staging model: Clean and standardize raw gear statistics
-- Source: bronze_gear_stats table from Garmin API

SELECT
    uuid as gear_id,  -- Match the column name from stg_gear_list
    
    -- Convert Unix timestamps (milliseconds) to readable dates
    DATE(updateDate / 1000, 'unixepoch') as updated_at,
    
    -- Convert distance from meters to kilometers
    ROUND(totalDistance / 1000, 2) as total_distance_km,
    
    totalActivities as total_activities,
    
    -- Metadata
    CURRENT_TIMESTAMP as dbt_loaded_at
    
FROM {{ source('main', 'bronze_gear_stats') }}