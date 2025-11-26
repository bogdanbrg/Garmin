-- Marts model: Detailed activity view with categorization
-- Purpose: Comprehensive activity details for filterable data tables and detailed exploration
-- This mart provides all activity details with consistent categorization matching the KPI dashboard

WITH activities AS (
    SELECT * FROM {{ ref('int_activities_enriched') }}
)

SELECT
    -- Activity identifiers
    activity_id,
    activity_name,
    activity_type_key,

    -- Activity categorization (same logic as KPI table)
    CASE
        WHEN activity_type_key IN ('running', 'trail_running') THEN 'Running'
        WHEN activity_type_key IN ('cycling') THEN 'Cycling'
        WHEN activity_type_key IN ('lap_swimming', 'open_water_swimming', 'swimming') THEN 'Swimming'
        WHEN activity_type_key IN ('strength_training', 'indoor_cardio') THEN 'Strength'
        WHEN activity_type_key IN ('multi_sport') THEN 'Multi-Sport'
        ELSE 'Other'
    END as activity_category,

    -- Time dimensions
    start_date,
    CAST(STRFTIME('%Y', start_date) AS INTEGER) as year,
    CAST(STRFTIME('%m', start_date) AS INTEGER) as month,
    CAST(STRFTIME('%d', start_date) AS INTEGER) as day,
    STRFTIME('%Y-%m', start_date) as year_month,
    CASE CAST(STRFTIME('%w', start_date) AS INTEGER)
        WHEN 0 THEN 'Sunday'
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
    END as day_of_week,

    -- Performance metrics
    distance_km,
    duration_minutes,

    -- Formatted duration for display (e.g., "1h 30m")
    PRINTF('%dh %02dm',
        CAST(duration_minutes / 60 AS INTEGER),
        CAST(duration_minutes % 60 AS INTEGER)
    ) as duration_formatted,

    avg_speed_kmh,
    avg_pace_formatted,
    elevation_gain_m,
    total_calories,

    -- Heart rate metrics
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

    -- Distance categorization
    CASE
        WHEN distance_km = 0 THEN 'No distance recorded'
        WHEN distance_km >= 20 THEN '20K+'
        WHEN distance_km >= 15 THEN '15K-20K'
        WHEN distance_km >= 10 THEN '10K-15K'
        WHEN distance_km >= 5 THEN '5K-10K'
        WHEN distance_km >= 1 THEN '1K-5K'
        ELSE 'Under 1K'
    END as distance_category,

    -- Temperature categorization
    CASE
        WHEN temperature_c IS NULL THEN NULL
        WHEN temperature_c > 25 THEN 'Hot'
        WHEN temperature_c > 15 THEN 'Moderate'
        WHEN temperature_c > 5 THEN 'Cool'
        ELSE 'Cold'
    END as temperature_category,

    -- Gear information
    gear_name,

    -- Metadata
    CURRENT_TIMESTAMP as dbt_loaded_at

FROM activities
ORDER BY start_date DESC
