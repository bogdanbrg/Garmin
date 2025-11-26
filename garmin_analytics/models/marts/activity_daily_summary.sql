-- Marts model: Daily activity summary for calendar heatmap
-- One row per date with simple aggregated metrics
-- Includes ALL activity types (Running, Cycling, Swimming, Strength, etc.)

WITH enriched_activities AS (
    SELECT * FROM {{ ref('int_activities_enriched') }}
)

SELECT
    DATE(start_date) as activity_date,

    -- Time-based fields for easy filtering
    CAST(strftime('%Y', start_date) AS INTEGER) as year,
    CAST(strftime('%m', start_date) AS INTEGER) as month,
    CAST(strftime('%d', start_date) AS INTEGER) as day,
    CAST(strftime('%w', start_date) AS INTEGER) as day_of_week, -- 0=Sunday, 6=Saturday

    -- Overall metrics (all activities combined)
    ROUND(SUM(duration_minutes), 1) as total_duration_minutes,

    -- Formatted duration for tooltips (e.g., "1h 30m")
    PRINTF('%dh %02dm',
        CAST(SUM(duration_minutes) / 60 AS INTEGER),
        CAST(SUM(duration_minutes) % 60 AS INTEGER)
    ) as total_duration_formatted,

    ROUND(SUM(distance_km), 2) as total_distance_km,
    ROUND(SUM(total_calories), 0) as total_calories,

    -- Metadata
    CURRENT_TIMESTAMP as dbt_loaded_at

FROM enriched_activities
GROUP BY DATE(start_date)
ORDER BY activity_date DESC
