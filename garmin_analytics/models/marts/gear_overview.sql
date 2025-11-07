-- Marts model: Complete gear overview with usage statistics
-- Business-ready table combining gear details with usage metrics

SELECT
    -- Gear identification
    list.gear_id,
    list.gear_type,
    list.gear_name,
    list.status,
    
    -- Dates
    list.start_date,
    list.end_date,
    stats.updated_at as stats_last_updated,
    
    -- Usage metrics
    stats.total_distance_km,
    stats.total_activities,
    list.max_distance_km,
    
    -- Derived metrics: How much life is left in the gear?
    CASE 
        WHEN list.max_distance_km IS NOT NULL THEN 
            ROUND((stats.total_distance_km / list.max_distance_km) * 100, 1)
        ELSE NULL
    END as pct_of_max_distance_used,
    
    CASE 
        WHEN list.max_distance_km IS NOT NULL THEN
            ROUND(list.max_distance_km - stats.total_distance_km, 2)
        ELSE NULL
    END as remaining_distance_km,
    
    -- How long has this gear been in use?
     CAST(JULIANDAY('now') - JULIANDAY(list.start_date) AS INTEGER) as days_since_first_use,
    
    -- Metadata
    CURRENT_TIMESTAMP as dbt_loaded_at

FROM {{ ref('stg_gear_list') }} as list
INNER JOIN {{ ref('stg_gear_stats') }} as stats
    ON list.gear_id = stats.gear_id