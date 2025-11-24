"""
Garmin Activity Dashboard
A Streamlit dashboard for visualizing Garmin fitness data
"""

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# Page configuration
st.set_page_config(
    page_title="My Training Hub",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .big-font {
        font-size: 48px !important;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Database connection
@st.cache_resource
def get_connection():
    # Use absolute path to database
    db_path = 'C:/Users/Svitlana/OneDrive/Garmin/data/garmin.db'
    return sqlite3.connect(db_path, check_same_thread=False)

conn = get_connection()

# Load data functions
@st.cache_data(ttl=300)
def load_kpi_data(year=None):
    query = "SELECT * FROM activity_kpis_monthly"
    if year:
        query += f" WHERE year = {year}"
    query += " ORDER BY year DESC, month DESC"
    return pd.read_sql_query(query, conn)

@st.cache_data(ttl=300)
def load_activity_summary(year=None):
    query = "SELECT * FROM activity_summary"
    if year:
        query += f" WHERE strftime('%Y', start_date) = '{year}'"
    return pd.read_sql_query(query, conn)

@st.cache_data(ttl=300)
def load_gear_overview():
    return pd.read_sql_query("SELECT * FROM gear_overview ORDER BY status, total_distance_km DESC", conn)

# Sidebar
st.sidebar.title("🏃 My Training Hub")
st.sidebar.markdown("---")

# Year filter
current_year = datetime.now().year
years = [2024, 2025]
selected_year = st.sidebar.selectbox("Select Year", years, index=years.index(current_year))

page = st.sidebar.radio(
    "Navigation",
    ["📊 Overview", "🏃 Running", "🚴 Cycling", "⚙️ Gear Tracker"]
)

st.sidebar.markdown("---")
st.sidebar.info(f"📅 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# Load data
df_kpis = load_kpi_data(selected_year)
df_activities = load_activity_summary(selected_year)
df_gear = load_gear_overview()

# ============================================================================
# PAGE: OVERVIEW
# ============================================================================
if page == "📊 Overview":
    st.title(f"📊 Training Overview - {selected_year}")

    # Calculate overall KPIs
    total_activities = df_kpis['activity_count'].sum()
    total_distance = df_kpis['total_distance_km'].sum()
    total_duration_hours = df_kpis['total_duration_hours'].sum()
    total_calories = df_kpis['total_calories'].sum()

    # Top KPI Cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="🏋️ Total Activities",
            value=f"{int(total_activities)}",
            delta=None
        )

    with col2:
        st.metric(
            label="🗺️ Total Distance",
            value=f"{total_distance:,.0f} km",
            delta=None
        )

    with col3:
        hours = int(total_duration_hours)
        minutes = int((total_duration_hours - hours) * 60)
        st.metric(
            label="⏱️ Training Time",
            value=f"{hours}h {minutes}m",
            delta=None
        )

    with col4:
        st.metric(
            label="🔥 Calories Burned",
            value=f"{int(total_calories):,}",
            delta=None
        )

    st.markdown("---")

    # Activity Breakdown by Category
    st.subheader("Activity Breakdown by Category")

    category_summary = df_kpis.groupby('activity_category').agg({
        'activity_count': 'sum',
        'total_distance_km': 'sum',
        'total_duration_hours': 'sum',
        'total_calories': 'sum'
    }).reset_index()

    col1, col2, col3, col4 = st.columns(4)

    for idx, (col, emoji) in enumerate(zip([col1, col2, col3, col4], ['🏃', '🚴', '🏊', '💪'])):
        if idx < len(category_summary):
            row = category_summary.iloc[idx]
            with col:
                st.markdown(f"### {emoji} {row['activity_category']}")
                st.metric("Activities", int(row['activity_count']))
                st.metric("Distance", f"{row['total_distance_km']:.1f} km")
                hours = int(row['total_duration_hours'])
                minutes = int((row['total_duration_hours'] - hours) * 60)
                st.metric("Duration", f"{hours}h {minutes}m")

    st.markdown("---")

    # Monthly Trends
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Monthly Activity Count")
        monthly_counts = df_kpis.groupby(['year_month', 'activity_category'])['activity_count'].sum().reset_index()
        fig = px.line(
            monthly_counts,
            x='year_month',
            y='activity_count',
            color='activity_category',
            markers=True,
            title="Activities per Month by Category"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🗺️ Monthly Distance")
        monthly_distance = df_kpis.groupby(['year_month', 'activity_category'])['total_distance_km'].sum().reset_index()
        fig = px.bar(
            monthly_distance,
            x='year_month',
            y='total_distance_km',
            color='activity_category',
            title="Distance per Month (km)"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# PAGE: RUNNING
# ============================================================================
elif page == "🏃 Running":
    st.title(f"🏃 Running Analytics - {selected_year}")

    # Filter for running activities
    running_kpis = df_kpis[df_kpis['activity_category'] == 'Running']
    running_activities = df_activities[df_activities['activity_type_key'].isin(['running', 'trail_running'])]

    if len(running_activities) == 0:
        st.warning("No running activities found for the selected year.")
    else:
        # Running KPIs
        total_runs = running_kpis['activity_count'].sum()
        total_distance = running_kpis['total_distance_km'].sum()
        total_duration = running_kpis['total_duration_hours'].sum()
        avg_distance = running_activities['distance_km'].mean()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Runs", int(total_runs))
        with col2:
            st.metric("Total Distance", f"{total_distance:.1f} km")
        with col3:
            hours = int(total_duration)
            minutes = int((total_duration - hours) * 60)
            st.metric("Total Duration", f"{hours}h {minutes}m")
        with col4:
            st.metric("Avg Distance", f"{avg_distance:.2f} km")

        st.markdown("---")

        # Charts
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Distance Distribution")
            fig = px.histogram(
                running_activities,
                x='distance_category',
                title="Runs by Distance Category",
                category_orders={'distance_category': ['Short Run', '1K-5K', '5K-10K', '10K-15K', '15K-20K', '20K+']}
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Weather Impact")
            weather_data = running_activities.dropna(subset=['temperature_c'])
            if len(weather_data) > 0:
                fig = px.scatter(
                    weather_data,
                    x='temperature_c',
                    y='avg_speed_kmh',
                    color='weather_condition',
                    title="Temperature vs Speed",
                    labels={'temperature_c': 'Temperature (°C)', 'avg_speed_kmh': 'Speed (km/h)'}
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No weather data available")

        # Recent runs table
        st.subheader("📋 Recent Runs")
        recent_runs = running_activities.sort_values('start_date', ascending=False).head(10)
        display_cols = ['start_date', 'activity_name', 'distance_km', 'duration_minutes', 'avg_speed_kmh', 'total_calories']
        st.dataframe(recent_runs[display_cols], use_container_width=True)

# ============================================================================
# PAGE: CYCLING
# ============================================================================
elif page == "🚴 Cycling":
    st.title(f"🚴 Cycling Analytics - {selected_year}")

    # Filter for cycling activities
    cycling_kpis = df_kpis[df_kpis['activity_category'] == 'Cycling']
    cycling_activities = df_activities[df_activities['activity_type_key'] == 'cycling']

    if len(cycling_activities) == 0:
        st.warning("No cycling activities found for the selected year.")
    else:
        # Cycling KPIs
        total_rides = cycling_kpis['activity_count'].sum()
        total_distance = cycling_kpis['total_distance_km'].sum()
        total_duration = cycling_kpis['total_duration_hours'].sum()
        avg_speed = cycling_activities['avg_speed_kmh'].mean()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Rides", int(total_rides))
        with col2:
            st.metric("Total Distance", f"{total_distance:.1f} km")
        with col3:
            hours = int(total_duration)
            minutes = int((total_duration - hours) * 60)
            st.metric("Total Duration", f"{hours}h {minutes}m")
        with col4:
            st.metric("Avg Speed", f"{avg_speed:.1f} km/h")

        st.markdown("---")

        # Charts
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Monthly Distance")
            fig = px.bar(
                cycling_kpis,
                x='year_month',
                y='total_distance_km',
                title="Cycling Distance per Month"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Speed Distribution")
            fig = px.histogram(
                cycling_activities,
                x='avg_speed_kmh',
                nbins=20,
                title="Speed Distribution (km/h)"
            )
            st.plotly_chart(fig, use_container_width=True)

        # Recent rides table
        st.subheader("📋 Recent Rides")
        recent_rides = cycling_activities.sort_values('start_date', ascending=False).head(10)
        display_cols = ['start_date', 'activity_name', 'distance_km', 'duration_minutes', 'avg_speed_kmh', 'elevation_gain_m']
        st.dataframe(recent_rides[display_cols], use_container_width=True)

# ============================================================================
# PAGE: GEAR TRACKER
# ============================================================================
elif page == "⚙️ Gear Tracker":
    st.title("⚙️ Gear Tracker")

    # Active gear
    st.subheader("🟢 Active Gear")
    active_gear = df_gear[df_gear['status'] == 'active']

    for _, gear in active_gear.iterrows():
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

            with col1:
                st.markdown(f"**{gear['gear_name']}**")
                st.caption(f"Type: {gear['gear_type']}")

            with col2:
                st.metric("Distance", f"{gear['total_distance_km']:.1f} km")

            with col3:
                st.metric("Activities", int(gear['total_activities']))

            with col4:
                if pd.notna(gear['pct_of_max_distance_used']):
                    pct = gear['pct_of_max_distance_used']
                    color = "🟢" if pct < 70 else "🟡" if pct < 90 else "🔴"
                    st.metric("Usage", f"{color} {pct:.0f}%")
                else:
                    st.metric("Usage", "N/A")

            # Progress bar
            if pd.notna(gear['pct_of_max_distance_used']):
                progress = min(gear['pct_of_max_distance_used'] / 100, 1.0)
                st.progress(progress)
                if gear['remaining_distance_km'] > 0:
                    st.caption(f"⚠️ {gear['remaining_distance_km']:.1f} km remaining")

            st.markdown("---")

    # Retired gear
    st.subheader("⚫ Retired Gear")
    retired_gear = df_gear[df_gear['status'] == 'retired']

    if len(retired_gear) > 0:
        for _, gear in retired_gear.iterrows():
            col1, col2, col3 = st.columns([3, 2, 2])

            with col1:
                st.markdown(f"~~{gear['gear_name']}~~ (Retired)")
            with col2:
                st.caption(f"Total: {gear['total_distance_km']:.1f} km")
            with col3:
                st.caption(f"Activities: {int(gear['total_activities'])}")
    else:
        st.info("No retired gear")

# Footer
st.markdown("---")
st.caption("🏃 Built with Streamlit | Data refreshed from Garmin API")
