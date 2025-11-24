-- Marts model: Monthly KPIs by activity category for dashboard cards
-- Purpose: Pre-aggregated metrics for high-level dashboard overview

WITH activities AS (
    SELECT * FROM {{ ref('int_activities_enriched') }}
),

categorized_activities AS (
    SELECT
        -- Time dimensions
        STRFTIME('%Y-%m', start_date) as year_month,
        CAST(STRFTIME('%Y', start_date) AS INTEGER) as year,
        CAST(STRFTIME('%m', start_date) AS INTEGER) as month,

        -- Activity categorization
        CASE
            WHEN activity_type_key IN ('running', 'trail_running') THEN 'Running'
            WHEN activity_type_key IN ('cycling') THEN 'Cycling'
            WHEN activity_type_key IN ('lap_swimming', 'open_water_swimming', 'swimming') THEN 'Swimming'
            WHEN activity_type_key IN ('strength_training', 'indoor_cardio') THEN 'Strength'
            WHEN activity_type_key IN ('multi_sport') THEN 'Multi-Sport'
            ELSE 'Other'
        END as activity_category,

        -- Metrics to aggregate
        distance_km,
        duration_minutes,
        total_calories

    FROM activities
)

SELECT
    year_month,
    year,
    month,
    activity_category,

    -- Count metrics
    COUNT(*) as activity_count,

    -- Duration metrics (multiple formats for dashboard flexibility)
    ROUND(SUM(duration_minutes), 1) as total_duration_minutes,
    ROUND(SUM(duration_minutes) / 60.0, 1) as total_duration_hours,
    CAST(SUM(duration_minutes) / 60 AS INTEGER) as total_duration_hours_whole,
    CAST(SUM(duration_minutes) % 60 AS INTEGER) as total_duration_minutes_remainder,
    PRINTF('%dh %02dm',
        CAST(SUM(duration_minutes) / 60 AS INTEGER),
        CAST(SUM(duration_minutes) % 60 AS INTEGER)
    ) as total_duration_formatted,

    ROUND(AVG(duration_minutes), 1) as avg_duration_minutes,

    -- Distance metrics (only meaningful for distance-based activities)
    ROUND(SUM(distance_km), 2) as total_distance_km,
    ROUND(AVG(CASE WHEN distance_km > 0 THEN distance_km ELSE NULL END), 2) as avg_distance_km,

    -- Calorie metrics
    ROUND(SUM(total_calories), 0) as total_calories,
    ROUND(AVG(total_calories), 0) as avg_calories,

    -- Metadata
    CURRENT_TIMESTAMP as dbt_loaded_at

FROM categorized_activities
GROUP BY year_month, year, month, activity_category
ORDER BY year DESC, month DESC, activity_category
