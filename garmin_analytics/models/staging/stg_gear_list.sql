-- Staging model: Clean and standardize raw gear data
-- Source: bronze_gear_list table from Garmin API

SELECT
    uuid as gear_id,
    gearTypeName as gear_type,
    customMakeModel as gear_name,

    -- Convert to proper date format (YYYY-MM-DD only, no time)
    DATE(dateBegin) as start_date,
    DATE(dateEnd) as end_date,
    
     -- Convert maximum distance from meters to kilometers
    ROUND(maximumMeters / 1000, 2) as max_distance_km,

    -- Derived field: active vs retired gear
    CASE 
        WHEN dateEnd IS NULL THEN 'active'
        ELSE 'retired'
    END as status,
    
    -- Metadata: when dbt processed this row
    CURRENT_TIMESTAMP as dbt_loaded_at
    
FROM {{ source('main', 'bronze_gear_list') }}