# extract_gear.py

import sqlite3
import pandas as pd
from garminconnect import Garmin
from datetime import datetime
import os
import sys
from getpass import getpass

def init_api():
    """Initialize Garmin API using environment variables or stored tokens"""
    email = os.getenv('GARMIN_EMAIL')
    password = os.getenv('GARMIN_PASSWORD')

    if email and password:
        # Use email/password authentication (for GitHub Actions)
        print("  → Logging in with environment credentials...")
        api = Garmin(email=email, password=password)
        api.login()
        print("  ✅ Logged in using environment credentials")
        return api
    else:
        # Use stored tokens (for local development)
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

def extract_and_load_gear():
    """
    Extract ALL gear-related data
    """
    try:
        print(f"🔄 Starting gear extraction at {datetime.now()}")
        
        # Connect using tokens
        api = init_api()
        
        # Get profile number
        device_info = api.get_device_last_used()
        user_profile_number = device_info.get("userProfileNumber")
        
        # ========================================
        # TABLE 1: Gear List
        # ========================================
        print("  → Extracting gear list...")
        gear_list = api.get_gear(user_profile_number)
        df_gear = pd.DataFrame(gear_list)
        print(f"  ✅ Found {len(df_gear)} gear items")
        
        # ========================================
        # TABLE 2: Gear Stats
        # ========================================
        print("  → Extracting gear stats...")
        gear_stats_list = []
        for gear_item in gear_list:
            gear_uuid = gear_item['uuid']
            try:
                stats = api.get_gear_stats(gear_uuid)
                gear_stats_list.append(stats)
            except Exception as e:
                print(f"    ⚠️  Warning: Could not get stats for {gear_uuid}: {e}")
        
        df_gear_stats = pd.DataFrame(gear_stats_list)
        print(f"  ✅ Found stats for {len(df_gear_stats)} items")
        
        # ========================================
        # Load to Database
        # ========================================
        print("  → Loading to database...")
        db_path = 'data/garmin.db'
        conn = sqlite3.connect(db_path)
        
        df_gear.to_sql('bronze_gear_list', conn, if_exists='replace', index=False)
        df_gear_stats.to_sql('bronze_gear_stats', conn, if_exists='replace', index=False)
        
        conn.close()
        print(f"  ✅ Both tables loaded to {db_path}")
        
        print(f"✅ Gear extraction complete at {datetime.now()}")
        return True
        
    except Exception as e:
        print(f"❌ Error during gear extraction: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = extract_and_load_gear()
    sys.exit(0 if success else 1)