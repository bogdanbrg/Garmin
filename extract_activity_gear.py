# extract_activity_gear.py

import sqlite3
import os
import pandas as pd
from garminconnect import Garmin
import json
import time

def init_api():
    """Initialize Garmin API using environment variables or stored tokens"""
    email = os.getenv('GARMIN_EMAIL')
    password = os.getenv('GARMIN_PASSWORD')

    api = Garmin()

    if email and password:
        # Use email/password authentication (for GitHub Actions)
        api.login(email, password)
    else:
        # Use stored tokens (for local development)
        tokenstore = os.path.expanduser("~/.garminconnect")
        api.login(tokenstore)

    return api

def extract_and_load_activity_gear():
    """Extract activity gear data and load to database"""
    
    api = init_api()
    
    # Get all 2025 activities
    activities = api.get_activities(0, 500)
    df_activities = pd.DataFrame(activities)
    df_activities['year'] = pd.to_datetime(df_activities['startTimeLocal']).dt.year
    df_2025 = df_activities[df_activities['year'] == 2025]
    
    # Extract gear for each activity
    gear_results = []
    
    for activity in df_2025.to_dict('records'):
        activity_id = activity['activityId']
        
        try:
            gear = api.get_activity_gear(activity_id)
            
            if gear:
                if isinstance(gear, dict):
                    gear['activityId'] = activity_id
                    gear_results.append(gear)
                elif isinstance(gear, list):
                    for g in gear:
                        g['activityId'] = activity_id
                        gear_results.append(g)
        except:
            pass  # Activity has no gear
        
        time.sleep(0.1)
    
    # Convert to DataFrame
    df_gear = pd.DataFrame(gear_results)
    
    # Convert complex fields to JSON
    for col in df_gear.columns:
        if df_gear[col].apply(lambda x: isinstance(x, (dict, list))).any():
            df_gear[col] = df_gear[col].apply(
                lambda x: json.dumps(x) if isinstance(x, (dict, list)) else x
            )
    
    # Save
    conn = sqlite3.connect('data/garmin.db')
    df_gear.to_sql('bronze_activity_gear', conn, if_exists='replace', index=False)
    conn.close()
    
    print(f"✅ Loaded {len(df_gear)} activity-gear records")
    return True

if __name__ == "__main__":
    try:
        extract_and_load_activity_gear()
    except Exception as e:
        print(f"❌ Error: {e}")
        raise  # Let GitHub Actions see the failure