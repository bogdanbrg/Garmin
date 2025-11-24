# Garmin Activity Dashboard

A Streamlit dashboard for visualizing your Garmin fitness data.

## Features

- **📊 Overview**: High-level KPIs and activity trends across all sports
- **🏃 Running**: Detailed running analytics with weather impact analysis
- **🚴 Cycling**: Cycling performance metrics and trends
- **⚙️ Gear Tracker**: Monitor gear usage and lifecycle

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure your data is up to date by running the extraction scripts and dbt models:
```bash
# From the Garmin directory
python extract_activities.py
python extract_activity_gear.py
python extract_activity_weather.py
python extract_gear.py

# Run dbt to refresh marts
cd garmin_analytics
dbt run
```

3. Run the dashboard:
```bash
cd dashboard
streamlit run app.py
```

4. Open your browser to `http://localhost:8501`

## Data Refresh

The dashboard caches data for 5 minutes (300 seconds). To force a refresh:
- Use the "Clear cache" option in the Streamlit menu (☰)
- Or restart the dashboard

## Dashboard Pages

### Overview
- Total activities, distance, training time, and calories
- Activity breakdown by category (Running, Cycling, Swimming, Strength, etc.)
- Monthly trends for activity count and distance

### Running
- Running-specific KPIs
- Distance distribution by category
- Weather impact analysis (temperature vs speed)
- Recent runs table

### Cycling
- Cycling-specific KPIs
- Monthly distance trends
- Speed distribution
- Recent rides table

### Gear Tracker
- Active gear with usage statistics
- Progress bars showing gear lifecycle
- Retired gear history
