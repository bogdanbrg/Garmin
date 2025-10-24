#!/usr/bin/env python3
"""
Minimal Garmin Connect API Demo
================================
Only uses actually required dependencies!

Installation:
pip3 install garminconnect

That's it! Just one package.

Environment Variables (optional):
export EMAIL=<your garmin email>
export PASSWORD=<your garmin password>
"""

import datetime
import json
import os
from getpass import getpass
from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
    GarminConnectConnectionError,
)

# ============================================================================
# Configuration
# ============================================================================

class Config:
    """Simple configuration"""
    def __init__(self):
        self.email = os.getenv("EMAIL")
        self.password = os.getenv("PASSWORD")
        self.tokenstore = os.path.expanduser("~/.garminconnect")
        
        # Dates
        self.today = datetime.date.today()
        self.week_start = self.today - datetime.timedelta(days=7)
        
        # Output directory
        self.output_dir = "garmin_data"
        os.makedirs(self.output_dir, exist_ok=True)

config = Config()

# ============================================================================
# Menu Structure
# ============================================================================

menu_options = {
    "1": {"name": "User Profile", "action": "get_profile"},
    "2": {"name": "Today's Summary", "action": "get_summary"},
    "3": {"name": "Today's Steps", "action": "get_steps"},
    "4": {"name": "Today's Heart Rate", "action": "get_heart_rate"},
    "5": {"name": "Recent Activities", "action": "get_activities"},
    "6": {"name": "Sleep Data", "action": "get_sleep"},
    "7": {"name": "Body Battery (7 days)", "action": "get_body_battery"},
    "8": {"name": "Create Health Report", "action": "create_report"},
    "q": {"name": "Quit", "action": "quit"},
}

# ============================================================================
# API Helper Functions
# ============================================================================

def safe_api_call(api_method, *args, **kwargs):
    """Call API method safely with error handling"""
    try:
        result = api_method(*args, **kwargs)
        return True, result, None
    except Exception as e:
        return False, None, str(e)

def display_data(title, data):
    """Display data in a formatted way"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    
    if data is None:
        print("  No data available")
    else:
        formatted = json.dumps(data, indent=2, default=str)
        print(formatted)
    
    # Save to file
    filename = os.path.join(config.output_dir, "last_response.json")
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    print(f"\n💾 Saved to: {filename}")
    print("="*60)

# ============================================================================
# API Actions
# ============================================================================

def get_profile(api):
    """Get user profile"""
    success, data, error = safe_api_call(api.get_full_name)
    if success:
        print(f"\n👤 User: {data}")
    
    success, data, error = safe_api_call(api.get_user_profile)
    if success:
        display_data("User Profile", data)
    else:
        print(f"❌ Error: {error}")

def get_summary(api):
    """Get today's summary"""
    today = config.today.isoformat()
    success, data, error = safe_api_call(api.get_user_summary, today)
    
    if success:
        print(f"\n📊 Summary for {today}")
        print(f"  Steps: {data.get('totalSteps', 0):,}")
        print(f"  Calories: {data.get('totalKilocalories', 0)}")
        print(f"  Distance: {data.get('totalDistanceMeters', 0)/1000:.2f} km")
        display_data(f"Full Summary - {today}", data)
    else:
        print(f"❌ Error: {error}")

def get_steps(api):
    """Get today's steps"""
    today = config.today.isoformat()
    success, data, error = safe_api_call(api.get_steps_data, today)
    
    if success:
        display_data(f"Steps Data - {today}", data)
    else:
        print(f"❌ Error: {error}")

def get_heart_rate(api):
    """Get today's heart rate"""
    today = config.today.isoformat()
    success, data, error = safe_api_call(api.get_heart_rates, today)
    
    if success:
        print(f"\n❤️  Heart Rate for {today}")
        print(f"  Resting: {data.get('restingHeartRate', 'N/A')} bpm")
        print(f"  Max: {data.get('maxHeartRate', 'N/A')} bpm")
        display_data(f"Heart Rate - {today}", data)
    else:
        print(f"❌ Error: {error}")

def get_activities(api):
    """Get recent activities"""
    success, data, error = safe_api_call(api.get_activities, 0, 10)
    
    if success:
        print(f"\n🏃 Found {len(data)} recent activities:")
        for i, activity in enumerate(data, 1):
            name = activity.get('activityName', 'Unnamed')
            activity_type = activity.get('activityType', {}).get('typeKey', 'unknown')
            duration = activity.get('duration', 0) / 60
            print(f"  {i}. {name} ({activity_type}) - {duration:.1f} min")
        display_data("Recent Activities", data)
    else:
        print(f"❌ Error: {error}")

def get_sleep(api):
    """Get sleep data"""
    today = config.today.isoformat()
    success, data, error = safe_api_call(api.get_sleep_data, today)
    
    if success:
        display_data(f"Sleep Data - {today}", data)
    else:
        print(f"❌ Error: {error}")

def get_body_battery(api):
    """Get body battery for last 7 days"""
    start = config.week_start.isoformat()
    end = config.today.isoformat()
    success, data, error = safe_api_call(api.get_body_battery, start, end)
    
    if success:
        display_data(f"Body Battery - {start} to {end}", data)
    else:
        print(f"❌ Error: {error}")

def create_report(api):
    """Create a simple health report"""
    print("\n📊 Creating health report...")
    
    today = config.today.isoformat()
    report = {
        "generated_at": datetime.datetime.now().isoformat(),
        "date": today,
    }
    
    # Get user info
    success, data, _ = safe_api_call(api.get_full_name)
    if success:
        report["user"] = data
    
    # Get today's summary
    success, data, _ = safe_api_call(api.get_user_summary, today)
    if success:
        report["summary"] = data
    
    # Get activities
    success, data, _ = safe_api_call(api.get_activities, 0, 5)
    if success:
        report["recent_activities"] = data
    
    # Save report
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(config.output_dir, f"health_report_{timestamp}.json")
    
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"✅ Report saved to: {filename}")

# ============================================================================
# Authentication
# ============================================================================

def init_api():
    """Initialize Garmin API"""
    # Try stored tokens first
    try:
        print(f"Trying stored tokens from: {config.tokenstore}")
        api = Garmin()
        api.login(config.tokenstore)
        print("✅ Logged in with stored tokens")
        return api
    except:
        print("No valid tokens found, need credentials")
    
    # Get credentials
    email = config.email or input("Email: ")
    password = config.password or getpass("Password: ")
    
    try:
        print("Logging in...")
        api = Garmin(email=email, password=password)
        api.login()
        
        # Save tokens
        api.garth.dump(config.tokenstore)
        print(f"✅ Login successful! Tokens saved to: {config.tokenstore}")
        return api
        
    except GarminConnectAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        return None
    except GarminConnectConnectionError as e:
        print(f"❌ Connection error: {e}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

# ============================================================================
# Main Menu
# ============================================================================

def show_menu():
    """Display menu"""
    print(f"\n{'='*60}")
    print("🏃 GARMIN CONNECT API - MINIMAL VERSION")
    print(f"{'='*60}")
    print("\nOptions (type number and press Enter):")
    
    for key, option in menu_options.items():
        print(f"  [{key}] {option['name']}")
    
    print(f"{'='*60}")

def main():
    """Main program loop"""
    print("\n" + "="*60)
    print("Garmin Connect API Demo - Minimal Dependencies")
    print("Only requires: pip3 install garminconnect")
    print("="*60)
    
    # Login
    api = init_api()
    if not api:
        print("Failed to login. Exiting.")
        return
    
    # Main loop
    while True:
        show_menu()
        
        # Get user choice (using input, not readchar)
        choice = input("\nYour choice: ").strip().lower()
        
        if choice not in menu_options:
            print("❌ Invalid choice, try again")
            continue
        
        action = menu_options[choice]["action"]
        
        if action == "quit":
            print("\n👋 Goodbye!")
            break
        
        # Execute action
        action_map = {
            "get_profile": get_profile,
            "get_summary": get_summary,
            "get_steps": get_steps,
            "get_heart_rate": get_heart_rate,
            "get_activities": get_activities,
            "get_sleep": get_sleep,
            "get_body_battery": get_body_battery,
            "create_report": create_report,
        }
        
        if action in action_map:
            try:
                action_map[action](api)
            except Exception as e:
                print(f"❌ Error: {e}")
        
        # Pause before showing menu again
        input("\n⏸️  Press Enter to continue...")

if __name__ == "__main__":
    main()