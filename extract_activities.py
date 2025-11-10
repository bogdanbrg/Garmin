# extract_activities.py

import sqlite3
import pandas as pd
from garminconnect import Garmin
from datetime import datetime, date
import os
import sys
import time
from getpass import getpass

def init_api():
    """Initialize Garmin API using stored tokens"""
    tokenstore = os.path.expanduser("~/.garminconnect")

    try:
        print(f"  → Attempting login using stored tokens...")
        api = Garmin()
        api.login(tokenstore)
        print("  ✅ Logged in using stored tokens")
        return api
    except Exception as e:
        print(f"  ⚠️  Token login failed: {e}")
        print("  → Requesting fresh login credentials...")
        return fresh_login(tokenstore)

def fresh_login(tokenstore):
    """Perform fresh login with credentials"""
    email = input("Email address: ").strip()
    password = getpass("Password: ")

    print("  → Logging in with credentials...")
    api = Garmin(email=email, password=password, is_cn=False, return_on_mfa=True)
    result1, result2 = api.login()

    if result1 == "needs_mfa":
        print("  → Multi-factor authentication required")
        mfa_code = input("MFA one-time code: ")
        api.resume_login(result2, mfa_code)
        print("  ✅ MFA authentication successful!")

    api.garth.dump(tokenstore)
    print(f"  ✅ Tokens saved to: {tokenstore}")
    return api

def extract_and_load_activities():
    """
    Extract ALL activities data for year 2025
    """
    try:
        print(f"🔄 Starting activities extraction at {datetime.now()}")

        # Connect using tokens
        api = init_api()

        # ========================================
        # TABLE 1: Activities List
        # ========================================
        print("  → Extracting activities for 2025...")

        # Fetch activities in batches (Garmin API limits response size)
        all_activities = []
        batch_size = 100
        start_index = 0

        while True:
            print(f"    Fetching batch {start_index // batch_size + 1} (activities {start_index} to {start_index + batch_size})...")
            batch = api.get_activities(start_index, batch_size)

            if not batch:
                print(f"    ✅ No more activities found")
                break

            # Filter for 2025 activities only
            for activity in batch:
                start_time = activity.get('startTimeLocal', '')
                if start_time.startswith('2025'):
                    all_activities.append(activity)
                elif start_time < '2025':
                    # We've gone past 2025, stop fetching
                    print(f"    ✅ Reached activities before 2025, stopping")
                    batch = []  # Signal to break outer loop
                    break

            if len(batch) < batch_size:
                # Last batch, no more activities
                print(f"    ✅ Fetched all available activities")
                break

            start_index += batch_size
            time.sleep(1)  # Be nice to Garmin's servers

        df_activities = pd.DataFrame(all_activities)
        print(f"  ✅ Found {len(df_activities)} activities for 2025")

        if len(df_activities) == 0:
            print("  ⚠️  No activities found for 2025")
            return False

        # ========================================
        # TABLE 2: Activity Weather (Optional)
        # ========================================
        print("  → Extracting weather data for activities...")
        weather_data = []

        # Only fetch weather for a subset to avoid rate limits
        # You can increase this number or remove the limit
        max_weather_fetch = min(50, len(df_activities))  # Fetch weather for first 50 activities

        for i in range(max_weather_fetch):
            activity_id = df_activities.iloc[i]['activityId']
            activity_name = df_activities.iloc[i].get('activityName', 'Unnamed')

            try:
                weather = api.get_activity_weather(activity_id)
                weather['activityId'] = activity_id
                weather_data.append(weather)

                if (i + 1) % 10 == 0:
                    print(f"    Progress: {i + 1}/{max_weather_fetch} weather records fetched")

                time.sleep(0.5)  # Be nice to Garmin's servers

            except Exception as e:
                # Some activities don't have weather data, that's OK
                pass

        if weather_data:
            df_weather = pd.DataFrame(weather_data)
            print(f"  ✅ Found weather data for {len(df_weather)} activities")
        else:
            df_weather = pd.DataFrame()
            print(f"  ⚠️  No weather data available")

        # ========================================
        # Load to Database
        # ========================================
        print("  → Loading to database...")
        db_path = 'data/garmin.db'
        conn = sqlite3.connect(db_path)

        # Load activities
        df_activities.to_sql('bronze_activities', conn, if_exists='replace', index=False)
        print(f"    ✅ bronze_activities: {len(df_activities)} records")

        # Load weather if available
        if len(df_weather) > 0:
            df_weather.to_sql('bronze_activity_weather', conn, if_exists='replace', index=False)
            print(f"    ✅ bronze_activity_weather: {len(df_weather)} records")

        conn.close()
        print(f"  ✅ All tables loaded to {db_path}")

        # ========================================
        # Summary
        # ========================================
        print("\n" + "="*60)
        print("📊 EXTRACTION SUMMARY")
        print("="*60)
        print(f"  Total activities (2025): {len(df_activities)}")
        print(f"  Weather records: {len(df_weather) if len(df_weather) > 0 else 0}")
        print(f"  Date range: {df_activities['startTimeLocal'].min()} to {df_activities['startTimeLocal'].max()}")

        if 'distance' in df_activities.columns:
            total_distance = df_activities['distance'].sum() / 1000
            print(f"  Total distance: {total_distance:.2f} km")

        if 'duration' in df_activities.columns:
            total_duration = df_activities['duration'].sum() / 3600
            print(f"  Total duration: {total_duration:.1f} hours")

        print("="*60)
        print(f"✅ Activities extraction complete at {datetime.now()}")
        return True

    except Exception as e:
        print(f"❌ Error during activities extraction: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = extract_and_load_activities()
    sys.exit(0 if success else 1)
