#!/usr/bin/env python3
"""
Direct test of the export function
"""
import datetime
import sys
import os

# Add the current directory to the path so we can import from test.py
sys.path.append(os.getcwd())

# Import the functions from test.py
from test import init_api, export_activities_to_csv

def test_export():
    """Test the export function directly."""
    print("Testing Garmin export function...")
    
    # Initialize API
    api = init_api(None, None)
    
    if not api:
        print("Could not login to Garmin Connect.")
        return False
    
    # Test export for September 2025 (where we know there's running data)
    start_date = datetime.date(2025, 9, 20)
    end_date = datetime.date(2025, 9, 27)
    
    print(f"Exporting activities from {start_date} to {end_date}...")
    
    try:
        export_activities_to_csv(api, start_date.isoformat(), end_date.isoformat(), "test_export.csv")
        print("Export completed successfully!")
        return True
    except Exception as e:
        print(f"Export failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_export()
    if success:
        print("\nExport function is working correctly!")
    else:
        print("\nExport function has issues.")
