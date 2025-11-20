-- Staging model: Clean and standardize activity weather data
-- Source: bronze_activity_weather table from Garmin API

SELECT
    activityId as activity_id,

    -- Temperature (convert from Fahrenheit to Celsius)
    ROUND((temp - 32) * 5.0 / 9.0, 1) as temperature_c,
    ROUND((apparentTemp - 32) * 5.0 / 9.0, 1) as feels_like_c,
    ROUND((dewPoint - 32) * 5.0 / 9.0, 1) as dew_point_c,

    -- Humidity
    ROUND(relativeHumidity, 0) as humidity_percent,

    -- Wind
    ROUND(windSpeed * 1.60934, 1) as wind_speed_kmh,  -- Convert mph to km/h
    windDirectionCompassPoint as wind_direction,

    -- Weather condition
    json_extract(weatherTypeDTO, '$.desc') as weather_condition,

    -- Location (where weather was measured)
    ROUND(latitude, 6) as weather_latitude,
    ROUND(longitude, 6) as weather_longitude,

    -- Timestamp (convert from ISO format to SQLite datetime)
    DATETIME(SUBSTR(issueDate, 1, 19)) as weather_timestamp,

    -- Metadata
    CURRENT_TIMESTAMP as dbt_loaded_at

FROM {{ source('main', 'bronze_activity_weather') }}
WHERE temp IS NOT NULL  -- Only include activities with actual weather data
