-- Marts model: Activity summary with weather and gear context
-- Business-ready table for analyzing activity performance
-- Uses intermediate layer for cleaner dependencies

WITH enriched_activities AS (
    SELECT * FROM {{ ref('int_activities_enriched') }}
)

SELECT
    activity_id,
    activity_name,
    activity_type_key,
    start_date,

    -- Performance metrics
    distance_km,
    duration_minutes,
    avg_speed_kmh,
    avg_pace_formatted,
    elevation_gain_m,
    total_calories,

    -- Heart rate
    avg_heart_rate,
    max_heart_rate,

    -- Training effect
    aerobic_training_effect,
    anaerobic_training_effect,

    -- Weather context
    temperature_c,
    feels_like_c,
    weather_condition,
    wind_speed_kmh,

    -- Gear used
    gear_name,

    -- Derived fields: Performance categorization
    CASE
        WHEN distance_km >= 20 THEN '20K+'
        WHEN distance_km >= 15 THEN '15K-20K'
        WHEN distance_km >= 10 THEN '10K-15K'
        WHEN distance_km >= 5 THEN '5K-10K'
        WHEN distance_km >= 1 THEN '1K-5K'
        ELSE 'Short Run'
    END as distance_category,

    -- Weather impact indicator
    CASE
        WHEN temperature_c IS NULL THEN NULL
        WHEN temperature_c > 25 THEN 'Hot'
        WHEN temperature_c > 15 THEN 'Moderate'
        WHEN temperature_c > 5 THEN 'Cool'
        ELSE 'Cold'
    END as temperature_category,

    -- Metadata
    CURRENT_TIMESTAMP as dbt_loaded_at

FROM enriched_activities
WHERE distance_km > 0  -- Filter out activities with no distance (e.g., strength training)
