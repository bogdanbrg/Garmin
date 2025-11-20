-- Intermediate model: Enrich activities with weather and gear information
-- Purpose: Create a reusable model that combines staging data for downstream marts

WITH activities AS (
    SELECT * FROM {{ ref('stg_activities') }}
),

weather AS (
    SELECT * FROM {{ ref('stg_activity_weather') }}
),

gear AS (
    SELECT * FROM {{ ref('stg_activity_gear') }}
)

SELECT
    -- Activity Info
    a.activity_id,
    a.owner_id,
    a.device_id,
    a.sport_type_id,
    a.activity_name,
    a.activity_type_key,
    a.location_name,

    -- Timing
    a.start_date,
    a.start_time_local,
    a.end_time_local,

    -- Performance Metrics
    a.distance_km,
    a.duration_minutes,
    a.elapsed_duration_minutes,
    a.moving_duration_minutes,
    a.avg_speed_kmh,
    a.max_speed_kmh,
    a.avg_pace_min_per_km,
    a.max_pace_min_per_km,
    a.avg_pace_formatted,
    a.max_pace_formatted,

    -- Elevation
    a.elevation_gain_m,
    a.elevation_loss_m,
    a.min_elevation_m,
    a.max_elevation_m,

    -- Heart Rate
    a.avg_heart_rate,
    a.max_heart_rate,
    a.hr_zone_1_seconds,
    a.hr_zone_2_seconds,
    a.hr_zone_3_seconds,
    a.hr_zone_4_seconds,
    a.hr_zone_5_seconds,

    -- Running Metrics
    a.avg_cadence_spm,
    a.max_cadence_spm,
    a.avg_stride_length_m,
    a.total_steps,

    -- Training Effect
    a.aerobic_training_effect,
    a.anaerobic_training_effect,
    a.vo2_max,

    -- Calories
    a.total_calories,
    a.bmr_calories,

    -- Location
    a.start_latitude,
    a.start_longitude,

    -- Weather Data (LEFT JOIN - not all activities have weather)
    w.temperature_c,
    w.feels_like_c,
    w.dew_point_c,
    w.humidity_percent,
    w.wind_speed_kmh,
    w.wind_direction,
    w.weather_condition,
    w.weather_timestamp,

    -- Gear Data (LEFT JOIN - not all activities use gear)
    g.gear_id,
    g.gear_name,

    -- Owner Info
    a.owner_name,
    a.owner_profile_image_url,

    -- Metadata
    CURRENT_TIMESTAMP as dbt_loaded_at

FROM activities a
LEFT JOIN weather w ON a.activity_id = w.activity_id
LEFT JOIN gear g ON a.activity_id = g.activity_id
