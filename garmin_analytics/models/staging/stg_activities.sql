-- models/staging/stg_activities.sql
-- Staging model: Clean and standardize activity data from Garmin Connect

SELECT
    -- IDs
    activityId as activity_id,
    ownerId as owner_id,
    deviceId as device_id,
    sportTypeId as sport_type_id,
    
    -- Activity Info
    activityName as activity_name,
    json_extract(activityType, '$.typeKey') as activity_type_key,  -- ✅ Extract from JSON
    locationName as location_name,
    
    -- Timestamps (convert to proper dates)
    DATE(startTimeLocal) as start_date,
    TIME(startTimeLocal) as start_time_local,
    TIME(datetime(startTimeLocal, '+' || CAST(duration AS INTEGER) || ' seconds')) as end_time_local,
    
    -- Distances & Durations (convert to readable units)
    ROUND(distance / 1000, 2) as distance_km,
    ROUND(duration / 60, 1) as duration_minutes,
    ROUND(elapsedDuration / 60, 1) as elapsed_duration_minutes,
    ROUND(movingDuration / 60, 1) as moving_duration_minutes,
    
    -- Elevation
    ROUND(elevationGain, 1) as elevation_gain_m,
    ROUND(elevationLoss, 1) as elevation_loss_m,
    ROUND(minElevation, 1) as min_elevation_m,
    ROUND(maxElevation, 1) as max_elevation_m,
    
    -- Speed (convert from m/s to km/h)
    ROUND(averageSpeed * 3.6, 2) as avg_speed_kmh,
    ROUND(maxSpeed * 3.6, 2) as max_speed_kmh,

    -- Pace (min/km - useful for running)
    CASE
        WHEN averageSpeed > 0 THEN ROUND(1000.0 / (averageSpeed * 60), 2)
        ELSE NULL
    END as avg_pace_min_per_km,
    CASE
        WHEN maxSpeed > 0 THEN ROUND(1000.0 / (maxSpeed * 60), 2)
        ELSE NULL
    END as max_pace_min_per_km,

    -- Pace formatted as MM:SS (for display)
    CASE
        WHEN averageSpeed > 0 THEN
            PRINTF('%d:%02d',
                CAST(1000.0 / (averageSpeed * 60) AS INTEGER),
                CAST((1000.0 / (averageSpeed * 60) - CAST(1000.0 / (averageSpeed * 60) AS INTEGER)) * 60 AS INTEGER)
            )
        ELSE NULL
    END as avg_pace_formatted,
    CASE
        WHEN maxSpeed > 0 THEN
            PRINTF('%d:%02d',
                CAST(1000.0 / (maxSpeed * 60) AS INTEGER),
                CAST((1000.0 / (maxSpeed * 60) - CAST(1000.0 / (maxSpeed * 60) AS INTEGER)) * 60 AS INTEGER)
            )
        ELSE NULL
    END as max_pace_formatted,
    
    -- Heart Rate
    ROUND(averageHR, 0) as avg_heart_rate,
    ROUND(maxHR, 0) as max_heart_rate,
    ROUND(hrTimeInZone_1, 0) as hr_zone_1_seconds,
    ROUND(hrTimeInZone_2, 0) as hr_zone_2_seconds,
    ROUND(hrTimeInZone_3, 0) as hr_zone_3_seconds,
    ROUND(hrTimeInZone_4, 0) as hr_zone_4_seconds,
    ROUND(hrTimeInZone_5, 0) as hr_zone_5_seconds,
    
    -- Running Metrics
    ROUND(averageRunningCadenceInStepsPerMinute, 0) as avg_cadence_spm,
    ROUND(maxRunningCadenceInStepsPerMinute, 0) as max_cadence_spm,
    ROUND(avgStrideLength, 2) as avg_stride_length_m,
    ROUND(steps, 0) as total_steps,
    
    -- Training Effect
    ROUND(aerobicTrainingEffect, 1) as aerobic_training_effect,
    ROUND(anaerobicTrainingEffect, 1) as anaerobic_training_effect,
    ROUND(vO2MaxValue, 1) as vo2_max,

    -- Calories
    ROUND(calories, 0) as total_calories,
    ROUND(bmrCalories, 0) as bmr_calories,

    -- Location
    ROUND(startLatitude, 6) as start_latitude,
    ROUND(startLongitude, 6) as start_longitude,
    
    -- Owner info
    ownerFullName as owner_name,
    ownerProfileImageUrlLarge as owner_profile_image_url,
    
    -- Metadata
    CURRENT_TIMESTAMP as dbt_loaded_at

FROM {{ source('main', 'bronze_activities') }}