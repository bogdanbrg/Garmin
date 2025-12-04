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
),

-- Manual adjustments for multisport activity splits
-- These are one-off entries to allocate multisport distances to individual sport categories
multisport_adjustments AS (
    -- Ironman 70.3 Jönköping (July 2025) - Activity ID: 19650257049
    -- Swim split
    SELECT '2025-07' as year_month, 2025 as year, 7 as month, 'Swimming' as activity_category,
           0 as activity_count, 1.99 as distance_km, 45.58 as duration_minutes, 386 as total_calories
    UNION ALL
    -- Bike split
    SELECT '2025-07' as year_month, 2025 as year, 7 as month, 'Cycling' as activity_category,
           0 as activity_count, 89.80 as distance_km, 165.09 as duration_minutes, 982 as total_calories
    UNION ALL
    -- Run split
    SELECT '2025-07' as year_month, 2025 as year, 7 as month, 'Running' as activity_category,
           0 as activity_count, 20.64 as distance_km, 100.56 as duration_minutes, 1421 as total_calories

    UNION ALL

    -- Copenhagen Multisport (June 2025) - Activity ID: 19579526871
    -- Swim split
    SELECT '2025-06' as year_month, 2025 as year, 6 as month, 'Swimming' as activity_category,
           0 as activity_count, 1.85 as distance_km, 48.72 as duration_minutes, 354 as total_calories
    UNION ALL
    -- Bike split
    SELECT '2025-06' as year_month, 2025 as year, 6 as month, 'Cycling' as activity_category,
           0 as activity_count, 53.98 as distance_km, 121.09 as duration_minutes, 840 as total_calories
    UNION ALL
    -- Run split
    SELECT '2025-06' as year_month, 2025 as year, 6 as month, 'Running' as activity_category,
           0 as activity_count, 5.27 as distance_km, 24.28 as duration_minutes, 353 as total_calories
),

aggregated_activities AS (
    SELECT
        year_month,
        year,
        month,
        activity_category,
        SUM(activity_count) as activity_count,
        SUM(distance_km) as distance_km,
        SUM(duration_minutes) as duration_minutes,
        SUM(total_calories) as total_calories
    FROM (
        SELECT
            year_month,
            year,
            month,
            activity_category,
            1 as activity_count,
            distance_km,
            duration_minutes,
            total_calories
        FROM categorized_activities

        UNION ALL

        SELECT
            year_month,
            year,
            month,
            activity_category,
            activity_count,
            distance_km,
            duration_minutes,
            total_calories
        FROM multisport_adjustments
    )
    GROUP BY year_month, year, month, activity_category
)

SELECT
    year_month,
    year,
    month,
    activity_category,

    -- Count metrics
    activity_count,

    -- Duration metrics (multiple formats for dashboard flexibility)
    ROUND(duration_minutes, 1) as total_duration_minutes,
    ROUND(duration_minutes / 60.0, 1) as total_duration_hours,
    CAST(duration_minutes / 60 AS INTEGER) as total_duration_hours_whole,
    CAST(duration_minutes % 60 AS INTEGER) as total_duration_minutes_remainder,
    PRINTF('%dh %02dm',
        CAST(duration_minutes / 60 AS INTEGER),
        CAST(duration_minutes % 60 AS INTEGER)
    ) as total_duration_formatted,

    ROUND(duration_minutes / NULLIF(activity_count, 0), 1) as avg_duration_minutes,

    -- Distance metrics (only meaningful for distance-based activities)
    ROUND(distance_km, 2) as total_distance_km,
    ROUND(distance_km / NULLIF(activity_count, 0), 2) as avg_distance_km,

    -- Calorie metrics
    ROUND(total_calories, 0) as total_calories,
    ROUND(total_calories / NULLIF(activity_count, 0), 0) as avg_calories,

    -- Metadata
    CURRENT_TIMESTAMP as dbt_loaded_at

FROM aggregated_activities
ORDER BY year DESC, month DESC, activity_category
