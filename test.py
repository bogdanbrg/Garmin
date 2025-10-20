#!/usr/bin/env python3
"""
Modified Garmin Connect script to export activities as a single CSV file
Enhanced with debugging and error handling
MODIFIED: Exports raw data without transformations
"""
import datetime
import json
import logging
import os
import sys
from getpass import getpass
import csv

import readchar
import requests
from garth.exc import GarthHTTPError

from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
email = os.getenv("EMAIL")
password = os.getenv("PASSWORD")
tokenstore = os.getenv("GARMINTOKENS") or "~/.garminconnect"
tokenstore_base64 = os.getenv("GARMINTOKENS_BASE64") or "~/.garminconnect_base64"
api = None

# Configuration
today = datetime.date.today()
startdate = today - datetime.timedelta(days=30)  # Changed to 30 days for more data
activitytype = ""  # All activity types

def get_credentials():
    """Get user credentials."""
    email = input("Login e-mail: ")
    password = getpass("Enter password: ")
    return email, password

def get_mfa():
    """Get MFA."""
    return input("MFA one-time code: ")

def init_api(email, password):
    """Initialize Garmin API with your credentials."""
    try:
        print(f"Trying to login to Garmin Connect using token data from directory '{tokenstore}'...\n")
        garmin = Garmin()
        garmin.login(tokenstore)
    except (FileNotFoundError, GarthHTTPError, GarminConnectAuthenticationError):
        print("Login tokens not present, login with your Garmin Connect credentials to generate them.\n")
        try:
            if not email or not password:
                email, password = get_credentials()
            
            garmin = Garmin(email=email, password=password, is_cn=False, return_on_mfa=True)
            result1, result2 = garmin.login()
            if result1 == "needs_mfa":
                mfa_code = get_mfa()
                garmin.resume_login(result2, mfa_code)
            
            garmin.garth.dump(tokenstore)
            print(f"Oauth tokens stored in '{tokenstore}' directory for future use.\n")
            
            token_base64 = garmin.garth.dumps()
            dir_path = os.path.expanduser(tokenstore_base64)
            with open(dir_path, "w") as token_file:
                token_file.write(token_base64)
            
            garmin.login(tokenstore)
        except Exception as err:
            logger.error(err)
            return None
    
    return garmin

def export_activities_to_csv(api, start_date, end_date, output_file="garmin_activities_raw.csv"):
    """Export all activities to a single CSV file - RAW DATA VERSION."""
    print(f"Fetching activities from {start_date} to {end_date}...")
    
    try:
        # Get activities for the date range
        activities = api.get_activities_by_date(start_date, end_date, activitytype)
        
        # Debug: Save raw response to JSON file for inspection
        debug_file = f"debug_{output_file.replace('.csv', '.json')}"
        with open(debug_file, 'w') as f:
            json.dump(activities, f, indent=2, default=str)
        print(f"Debug: Raw API response saved to {debug_file}")
        
        # Check if activities is a list or dict
        print(f"Debug: Type of activities: {type(activities)}")
        print(f"Debug: Activities structure: {activities if isinstance(activities, dict) and len(str(activities)) < 500 else 'Too large to display'}")
        
        # Handle different response formats
        if isinstance(activities, dict):
            # If it's a dict, look for common keys that might contain the activity list
            if 'activities' in activities:
                activities = activities['activities']
            elif 'activityList' in activities:
                activities = activities['activityList']
            elif 'data' in activities:
                activities = activities['data']
            else:
                print("Debug: Response is a dict but no recognizable activity list found")
                print(f"Debug: Dict keys: {list(activities.keys()) if isinstance(activities, dict) else 'Not a dict'}")
                return
        
        if not activities:
            print("No activities found for the specified date range.")
            return
        
        if not isinstance(activities, list):
            print(f"Error: Expected activities to be a list, got {type(activities)}")
            return
        
        print(f"Found {len(activities)} activities. Exporting to {output_file}...")
        
        # Debug: Print first activity structure
        if activities:
            print("Debug: First activity structure:")
            print(json.dumps(activities[0], indent=2, default=str)[:1000] + "..." if len(json.dumps(activities[0], default=str)) > 1000 else json.dumps(activities[0], indent=2, default=str))
        
        # Define CSV headers - RAW VERSION (no transformations)
        headers = [
            'Activity ID',
            'Activity Name',
            'Activity Type',
            'Start Time',
            'Duration (seconds)',  # RAW: Keep as seconds
            'Distance (meters)',   # RAW: Keep as meters
            'Calories',
            'Average Heart Rate',
            'Max Heart Rate',
            'Average Speed (m/s)', # RAW: Keep as m/s
            'Max Speed (m/s)',     # RAW: Keep as m/s
            'Elevation Gain (m)',
            'Location Name',
            'Average Running Cadence (spm)',  # Steps per minute
        ]
        
        # Write to CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            
            for i, activity in enumerate(activities):
                try:
                    # Extract data with safe get methods - NO TRANSFORMATIONS
                    row = [
                        activity.get('activityId', ''),
                        activity.get('activityName', ''),
                        activity.get('activityType', {}).get('typeKey', '') if isinstance(activity.get('activityType'), dict) else activity.get('activityType', ''),
                        activity.get('startTimeLocal', ''),
                        activity.get('duration', ''),  # RAW: seconds as is
                        f"{float(activity.get('distance', 0)):.6f}" if activity.get('distance') else '',  # Fixed,  # RAW: meters as is
                        activity.get('calories', ''),
                        activity.get('averageHR', ''),
                        activity.get('maxHR', ''),
                        activity.get('averageSpeed', ''),  # RAW: m/s as is
                        activity.get('maxSpeed', ''),     # RAW: m/s as is
                        activity.get('elevationGain', ''),
                        activity.get('locationName', ''),
                        activity.get('averageRunningCadenceInStepsPerMinute', ''),  # Running cadence
                    ]
                    writer.writerow(row)
                except Exception as e:
                    print(f"Error processing activity {i}: {e}")
                    print(f"Activity data: {activity}")
                    continue
        
        print(f"Successfully exported {len(activities)} activities to {output_file}")
        
        # Also create a summary
        print("\n=== ACTIVITY SUMMARY ===")
        print(f"Total Activities: {len(activities)}")
        print(f"Date Range: {start_date} to {end_date}")
        
        # Activity type breakdown
        activity_types = {}
        for activity in activities:
            activity_type = activity.get('activityType', {})
            if isinstance(activity_type, dict):
                activity_type = activity_type.get('typeKey', 'Unknown')
            elif activity_type is None:
                activity_type = 'Unknown'
            activity_types[activity_type] = activity_types.get(activity_type, 0) + 1
        
        print("\nActivity Types:")
        for activity_type, count in sorted(activity_types.items()):
            print(f"  {activity_type}: {count}")
        
        # Show sample raw values for inspection
        if activities:
            print("\n=== SAMPLE RAW VALUES (First Activity) ===")
            sample = activities[0]
            print(f"Duration (raw): {sample.get('duration')} seconds")
            print(f"Distance (raw): {sample.get('distance')} meters")
            print(f"Average Speed (raw): {sample.get('averageSpeed')} m/s")
            print(f"Max Speed (raw): {sample.get('maxSpeed')} m/s")
        
    except Exception as err:
        logger.error(f"Error exporting activities: {err}")
        import traceback
        traceback.print_exc()

def main():
    """Main function with simplified menu."""
    print("\n*** Garmin Connect CSV Export Tool (RAW DATA VERSION) ***\n")
    
    # Initialize API
    global api
    api = init_api(email, password)
    
    if not api:
        print("Could not login to Garmin Connect. Please try again.")
        return
    
    while True:
        print("\nOptions:")
        print("1 -- Export last 30 days of activities to CSV (RAW)")
        print("2 -- Export last 7 days of activities to CSV (RAW)")
        print("3 -- Export last 90 days of activities to CSV (RAW)")
        print("4 -- Export last 120 days of activities to CSV (RAW)")
        print("5 -- Export all activities from a specific date (RAW)")
        print("q -- Quit")
        
        choice = input("\nEnter your choice: ").strip().lower()
        
        if choice == 'q':
            print("Goodbye!")
            break
        elif choice == '1':
            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(days=30)
            export_activities_to_csv(api, start_date.isoformat(), end_date.isoformat(), "garmin_activities_30days_raw.csv")
        elif choice == '2':
            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(days=7)
            export_activities_to_csv(api, start_date.isoformat(), end_date.isoformat(), "garmin_activities_7days_raw.csv")
        elif choice == '3':
            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(days=90)
            export_activities_to_csv(api, start_date.isoformat(), end_date.isoformat(), "garmin_activities_90days_raw.csv")
        elif choice == '4':
            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(days=120)
            export_activities_to_csv(api, start_date.isoformat(), end_date.isoformat(), "garmin_activities_120days_raw.csv")
        elif choice == '5':
            try:
                start_input = input("Enter start date (YYYY-MM-DD): ")
                start_date = datetime.datetime.strptime(start_input, "%Y-%m-%d").date()
                end_date = datetime.date.today()
                filename = f"garmin_activities_from_{start_input}_raw.csv"
                export_activities_to_csv(api, start_date.isoformat(), end_date.isoformat(), filename)
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD format.")
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()