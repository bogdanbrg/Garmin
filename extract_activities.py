import sqlite3
import os
import pandas as pd
from garminconnect import Garmin
import json

def init_api():
    """Initialize Garmin API using environment variables or stored tokens"""
    email = os.getenv('GARMIN_EMAIL')
    password = os.getenv('GARMIN_PASSWORD')

    if email and password:
        # Use email/password authentication (for GitHub Actions)
        api = Garmin(email=email, password=password)
        api.login()
    else:
        # Use stored tokens (for local development)
        tokenstore = os.path.expanduser("~/.garminconnect")
        api = Garmin()
        api.login(tokenstore)

    return api

def extract_and_load_activities():
    """Extract 2025 activities and load to database"""
    
    api = init_api()
    
    # Get all activities at once
    activities = api.get_activities(0, 500)
    
    # Filter to 2025
    df = pd.DataFrame(activities)
    df['year'] = pd.to_datetime(df['startTimeLocal']).dt.year
    df_2025 = df[df['year'] == 2025].drop('year', axis=1)
    
    # Convert complex fields to JSON
    for col in df_2025.columns:
        if df_2025[col].apply(lambda x: isinstance(x, (dict, list))).any():
            df_2025[col] = df_2025[col].apply(
                lambda x: json.dumps(x) if isinstance(x, (dict, list)) else x
            )
    
    # Save
    conn = sqlite3.connect('data/garmin.db')
    df_2025.to_sql('bronze_activities', conn, if_exists='replace', index=False)
    conn.close()
    
    print(f"✅ Loaded {len(df_2025)} activities")
    return True

# ⭐ THIS IS THE IMPORTANT PART - ACTUALLY CALL THE FUNCTION!
extract_and_load_activities()