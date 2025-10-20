#!/usr/bin/env python3
"""
Test script to export activities with cadence data
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
startdate = today - datetime.timedelta(days=7)  # Last 7 days for testing
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

def export_activities_to_csv(api, start_date, end_date, output_file="garmin_activities_with_cadence.csv"):
    """Export all activities to a single CSV file with cadence data."""
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
        
        # Define CSV headers - WITH CADENCE FIELDS
        headers = [
            'Activity ID',
            'Activity Name',
            'Activity Type',
            'Start Time',
            'Duration (seconds)',
            'Distance (meters)',
            'Calories',
            'Average Heart Rate',
            'Max Heart Rate',
            'Average Speed (m/s)',
            'Max Speed (m/s)',
            'Elevation Gain (m)',
            'Location Name',
            'Average Running Cadence (spm)',  # Steps per minute
            'Max Running Cadence (spm)',      # Steps per minute
            'Average Swim Cadence (spm)',     # Strokes per minute
            'Max Swim Cadence (spm)',         # Strokes per minute
            'Max Double Cadence'              # General cadence metric
        ]
        
        # Write to CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            
            for i, activity in enumerate(activities):
                try:
                    # Extract data with safe get methods
                    row = [
                        activity.get('activityId', ''),
                        activity.get('activityName', ''),
                        activity.get('activityType', {}).get('typeKey', '') if isinstance(activity.get('activityType'), dict) else activity.get('activityType', ''),
                        activity.get('startTimeLocal', ''),
                        activity.get('duration', ''),
                        f"{float(activity.get('distance', 0)):.6f}" if activity.get('distance') else '',
                        activity.get('calories', ''),
                        activity.get('averageHR', ''),
                        activity.get('maxHR', ''),
                        activity.get('averageSpeed', ''),
                        activity.get('maxSpeed', ''),
                        activity.get('elevationGain', ''),
                        activity.get('locationName', ''),
                        activity.get('averageRunningCadenceInStepsPerMinute', ''),  # Running cadence
                        activity.get('maxRunningCadenceInStepsPerMinute', ''),      # Max running cadence
                        activity.get('averageSwimCadenceInStrokesPerMinute', ''),   # Swimming cadence
                        activity.get('maxSwimCadenceInStrokesPerMinute', ''),       # Max swimming cadence
                        activity.get('maxDoubleCadence', '')                        # General cadence
                    ]
                    writer.writerow(row)
                except Exception as e:
                    print(f"Error processing activity {i}: {e}")
                    print(f"Activity data: {activity}")
                    continue
        
        print(f"Successfully exported {len(activities)} activities to {output_file}")
        
        # Show sample of cadence data
        print("\n=== CADENCE DATA SAMPLE ===")
        cadence_activities = [a for a in activities if any([
            a.get('averageRunningCadenceInStepsPerMinute'),
            a.get('maxRunningCadenceInStepsPerMinute'),
            a.get('averageSwimCadenceInStrokesPerMinute'),
            a.get('maxSwimCadenceInStrokesPerMinute'),
            a.get('maxDoubleCadence')
        ])]
        
        if cadence_activities:
            print(f"Found {len(cadence_activities)} activities with cadence data:")
            for i, activity in enumerate(cadence_activities[:3]):  # Show first 3
                print(f"\nActivity {i+1}: {activity.get('activityName', 'Unknown')} ({activity.get('activityType', {}).get('typeKey', 'Unknown')})")
                print(f"  Running Cadence: {activity.get('averageRunningCadenceInStepsPerMinute', 'N/A')} avg, {activity.get('maxRunningCadenceInStepsPerMinute', 'N/A')} max")
                print(f"  Swim Cadence: {activity.get('averageSwimCadenceInStrokesPerMinute', 'N/A')} avg, {activity.get('maxSwimCadenceInStrokesPerMinute', 'N/A')} max")
                print(f"  Max Double Cadence: {activity.get('maxDoubleCadence', 'N/A')}")
        else:
            print("No activities found with cadence data in this date range.")
        
    except Exception as err:
        logger.error(f"Error exporting activities: {err}")
        import traceback
        traceback.print_exc()

def main():
    """Main function to test cadence export."""
    print("\n*** Garmin Connect CSV Export Tool - CADENCE TEST ***\n")
    
    # Initialize API
    global api
    api = init_api(email, password)
    
    if not api:
        print("Could not login to Garmin Connect. Please try again.")
        return
    
    # Export from March 17, 2025 (where we know there's data)
    start_date = datetime.date(2025, 3, 17)
    end_date = datetime.date(2025, 3, 18)
    export_activities_to_csv(api, start_date.isoformat(), end_date.isoformat(), "garmin_activities_with_cadence_test.csv")

if __name__ == "__main__":
    main()
