# extract_activity_weather.py

import sqlite3
import os
import pandas as pd
from garminconnect import Garmin
import json
import time

def init_api():
    """Initialize Garmin API using stored tokens"""
    tokenstore = os.path.expanduser("~/.garminconnect")
    api = Garmin()
    api.login(tokenstore)
    return api

def extract_and_load_activity_weather():
    """Extract activity weather data and load to database"""

    api = init_api()

    # Get all 2025 activities
    activities = api.get_activities(0, 500)
    df_activities = pd.DataFrame(activities)
    df_activities['year'] = pd.to_datetime(df_activities['startTimeLocal']).dt.year
    df_2025 = df_activities[df_activities['year'] == 2025]

    # Extract weather for each activity
    weather_results = []

    for activity in df_2025.to_dict('records'):
        activity_id = activity['activityId']

        try:
            weather = api.get_activity_weather(activity_id)

            if weather:
                if isinstance(weather, dict):
                    weather['activityId'] = activity_id
                    weather_results.append(weather)
                elif isinstance(weather, list):
                    for w in weather:
                        w['activityId'] = activity_id
                        weather_results.append(w)
        except:
            pass  # Activity has no weather (indoor or no GPS)

        time.sleep(0.1)

    # Convert to DataFrame
    df_weather = pd.DataFrame(weather_results)

    # Convert complex fields to JSON
    for col in df_weather.columns:
        if df_weather[col].apply(lambda x: isinstance(x, (dict, list))).any():
            df_weather[col] = df_weather[col].apply(
                lambda x: json.dumps(x) if isinstance(x, (dict, list)) else x
            )

    # Save
    conn = sqlite3.connect('data/garmin.db')
    df_weather.to_sql('bronze_activity_weather', conn, if_exists='replace', index=False)
    conn.close()

    print(f"Loaded {len(df_weather)} activity-weather records")
    return True

if __name__ == "__main__":
    try:
        extract_and_load_activity_weather()
    except Exception as e:
        print(f"Error: {e}")
        raise  # Let GitHub Actions see the failure