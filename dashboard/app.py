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

# Custom CSS for dark theme with Octet Design color palette
# Palette from: https://octet.design/colors/palette/interactive-dashboards-color-palette-1731331224/
# Colors: #171821 (near black bg), #292631 (charcoal), #4d3e50 (deep purple),
#         #7b6e7f (dark purple), #9c526d (magenta accent), #a887ce (primary purple)
st.markdown("""
    <style>
    /* Main theme colors */
    :root {
        --primary-purple: #a887ce;
        --magenta-accent: #9c526d;
        --dark-purple: #7b6e7f;
        --deep-purple: #4d3e50;
        --charcoal: #292631;
        --near-black: #171821;
    }

    /* Background colors */
    .stApp {
        background-color: #171821;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #292631;
    }

    /* Sidebar navigation text - white */
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] a {
        color: #ffffff !important;
    }

    /* Metric cards - purple background with white text */
    [data-testid="stMetric"] {
        background-color: #7b6e7f !important;  /* Dark purple background (less strident) */
        padding: 1.5rem !important;
        border-radius: 10px !important;
        text-align: center !important;  /* Center align content */
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
    }

    [data-testid="stMetricValue"] {
        color: #ffffff !important;  /* White text */
        font-size: 2rem;
        font-weight: bold;
        display: flex !important;
        justify-content: center !important;  /* Center the value */
        width: 100% !important;
    }

    [data-testid="stMetricLabel"] {
        color: #ffffff !important;  /* White text */
        font-size: 1rem;
        text-align: center !important;  /* Center the label */
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }

    /* Headers */
    h1 {
        color: #ffffff !important;  /* White for main title */
        background-color: transparent !important;  /* Remove background box */
        margin-top: -3rem !important;  /* Move title higher */
        padding-top: 1rem !important;
    }

    h2, h3 {
        color: #a887ce !important;  /* Primary purple for other headers */
        margin-top: 0.5rem !important;  /* Reduce top margin */
        margin-bottom: 0.5rem !important;  /* Reduce bottom margin */
    }

    /* Remove background from title container */
    [data-testid="stHeader"] {
        background-color: transparent !important;
    }

    /* Make title element blend with background */
    .main .block-container {
        padding-top: 0rem;
        padding-bottom: 1rem;
    }

    /* Reduce gap between elements */
    .element-container {
        margin-bottom: 0.5rem !important;
    }

    /* Reduce gap after horizontal dividers */
    hr {
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }

    /* General text */
    p, span, div {
        color: #7b6e7f;  /* Dark purple for general text */
    }

    /* Override for metric labels and values - white text on purple background */
    [data-testid="stMetricLabel"] p,
    [data-testid="stMetricLabel"] span,
    [data-testid="stMetricLabel"] div,
    [data-testid="stMetricValue"] p,
    [data-testid="stMetricValue"] span,
    [data-testid="stMetricValue"] div {
        color: #ffffff !important;
        text-align: center !important;  /* Center align text */
    }

    /* Filter labels - white for better readability */
    label {
        color: #ffffff !important;
    }

    /* Selectbox labels specifically */
    [data-testid="stSelectbox"] label {
        color: #ffffff !important;
    }

    /* Override for selectbox label text elements */
    [data-testid="stSelectbox"] label p,
    [data-testid="stSelectbox"] label span,
    [data-testid="stSelectbox"] label div {
        color: #ffffff !important;
    }

    /* Filter input text - white */
    [data-baseweb="select"] {
        color: #ffffff !important;
    }

    /* Multi-select dropdown text - white */
    [data-baseweb="select"] input {
        color: #ffffff !important;
    }

    /* Cards/containers - remove background for now */
    .element-container {
        background-color: transparent;
        border-radius: 10px;
    }

    /* Multi-select styling - purple theme */
    [data-baseweb="tag"] {
        background-color: #4d3e50 !important;  /* Deep purple background */
        color: #ffffff !important;  /* White text */
    }

    /* Multi-select tag text - white */
    [data-baseweb="tag"] span {
        color: #ffffff !important;
    }

    /* Multi-select close button (X) */
    [data-baseweb="tag"] span[role="presentation"] {
        color: #ffffff !important;
    }

    /* Multi-select dropdown styling */
    [data-baseweb="select"] > div {
        background-color: #292631 !important;
        border-color: #7b6e7f !important;
    }

    /* Heatmap container styling - target the element-container that wraps plotly charts */
    .element-container:has(iframe[title*="streamlit_plotly"]) {
        background-color: #292631 !important;  /* Charcoal background */
        padding: 2rem !important;
        border-radius: 10px !important;
        margin-top: 0rem !important;  /* Remove top margin */
        margin-bottom: 0rem !important;  /* Remove bottom margin */
    }

    /* Dataframe table styling */
    [data-testid="stDataFrame"] {
        background-color: #292631 !important;  /* Charcoal background */
        padding: 2rem !important;
        border-radius: 10px !important;
        margin-top: 0rem !important;  /* Remove top margin */
    }

    /* Style dataframe headers */
    [data-testid="stDataFrame"] th {
        background-color: #4d3e50 !important;  /* Deep purple background */
        color: #ffffff !important;  /* White text */
        font-weight: bold !important;
    }

    /* Style dataframe cells */
    [data-testid="stDataFrame"] td {
        color: #ffffff !important;  /* White text */
    }

    /* We'll add back container styling later for specific elements like metrics */
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# DATABASE CONNECTION
# ============================================================================

@st.cache_resource
def get_database_connection():
    """
    Creates and returns a connection to the SQLite database.

    Why @st.cache_resource?
    - This decorator tells Streamlit to create the connection ONCE and reuse it
    - Without caching, a new connection would be created every time the page refreshes
    - Database connections are "resources" that should be shared, not recreated
    - This improves performance and prevents connection leaks

    Returns:
        sqlite3.Connection: Database connection object
    """
    db_path = 'C:/Users/Svitlana/OneDrive/Garmin/data/garmin.db'
    return sqlite3.connect(db_path, check_same_thread=False)

# Create the connection (this will only run once due to caching)
conn = get_database_connection()

# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================

@st.cache_data(ttl=300)
def load_monthly_kpis(year=None):
    """
    Loads monthly KPI data from the activity_kpis_monthly mart.

    Why @st.cache_data (vs @st.cache_resource)?
    - @st.cache_data is for DATA (DataFrames, lists, etc.) that can be pickled
    - @st.cache_resource is for RESOURCES (connections, file handles)
    - Data caching creates a COPY each time, resources are SHARED

    The ttl=300 parameter:
    - ttl = "time to live" in seconds
    - After 300 seconds (5 minutes), the cache expires and fresh data is loaded
    - This balances performance (caching) with freshness (regular updates)
    - Without ttl, data would be cached forever during the session

    Parameters:
        year (int, optional): Filter data for a specific year. If None, loads all years.

    Returns:
        pd.DataFrame: Monthly KPI data with columns like activity_count,
                      total_distance_km, total_duration_hours, etc.
    """
    query = "SELECT * FROM activity_kpis_monthly"

    # Add year filter if specified
    if year:
        query += f" WHERE year = {year}"

    query += " ORDER BY year DESC, month DESC"

    # pd.read_sql_query runs the SQL and returns a pandas DataFrame
    return pd.read_sql_query(query, conn)


@st.cache_data(ttl=300)
def load_activity_summary(year=None):
    """
    Loads detailed activity data from the activity_summary mart.

    This mart includes:
    - Individual activity details (name, type, date)
    - Performance metrics (distance, duration, speed)
    - Weather conditions during the activity
    - Gear used for the activity

    Parameters:
        year (int, optional): Filter activities for a specific year

    Returns:
        pd.DataFrame: Detailed activity data
    """
    query = "SELECT * FROM activity_summary"

    if year:
        # Extract year from start_date column using SQLite's strftime function
        query += f" WHERE strftime('%Y', start_date) = '{year}'"

    query += " ORDER BY start_date DESC"

    return pd.read_sql_query(query, conn)


@st.cache_data(ttl=300)
def load_gear_overview():
    """
    Loads gear tracking data from the gear_overview mart.

    This includes:
    - All your gear (shoes, bikes, etc.)
    - Usage statistics (distance, activities)
    - Lifecycle tracking (wear percentage, remaining life)

    Returns:
        pd.DataFrame: Gear data with status, usage metrics, and lifecycle info
    """
    query = """
        SELECT * FROM gear_overview
        ORDER BY status, total_distance_km DESC
    """

    return pd.read_sql_query(query, conn)


@st.cache_data(ttl=300)
def load_daily_summary(year=None):
    """
    Loads daily activity summary data for calendar heatmap.

    This mart includes:
    - One row per date with aggregated metrics
    - All activity types (including strength training)
    - Duration, distance, and calorie totals

    Parameters:
        year (int, optional): Filter activities for a specific year

    Returns:
        pd.DataFrame: Daily summary data
    """
    query = "SELECT * FROM activity_daily_summary"

    if year:
        query += f" WHERE year = {year}"

    query += " ORDER BY activity_date DESC"

    return pd.read_sql_query(query, conn)


@st.cache_data(ttl=300)
def load_activity_details(year=None, month=None, activity_category=None):
    """
    Loads detailed activity data from the activity_details mart.

    This mart includes:
    - Comprehensive activity details with categorization
    - Performance metrics (distance, duration, speed, pace)
    - Heart rate and training effect data
    - Weather and gear information

    Parameters:
        year (int, optional): Filter activities for a specific year
        month (int, optional): Filter activities for a specific month
        activity_category (str, optional): Filter activities by category

    Returns:
        pd.DataFrame: Detailed activity data
    """
    query = "SELECT * FROM activity_details WHERE 1=1"

    if year:
        query += f" AND year = {year}"

    if month:
        query += f" AND month = {month}"

    if activity_category:
        query += f" AND activity_category = '{activity_category}'"

    query += " ORDER BY start_date DESC"

    return pd.read_sql_query(query, conn)

# ============================================================================
# TITLE
# ============================================================================

st.title("Activity Dashboard")

# ============================================================================
# LOAD DATA
# ============================================================================

# Load the monthly KPI data for all years
# This gets all data from activity_kpis_monthly mart
df_kpis = load_monthly_kpis()

# ============================================================================
# FILTERS
# ============================================================================

# Create three columns for the filters (side by side)
col_filter1, col_filter2, col_filter3 = st.columns(3)

with col_filter1:
    # Year Filter (single-select dropdown)
    # Get unique years from the data and sort them (most recent first)
    available_years = sorted(df_kpis['year'].unique(), reverse=True)

    # Add "All" option at the beginning
    year_options = ['All'] + list(available_years)

    # Create the selectbox
    selected_year = st.selectbox(
        "Select Year",
        year_options,
        index=0  # Start with "All" selected
    )

with col_filter2:
    # Month Filter (single-select dropdown)
    # Get unique months from the data and sort them
    available_months = sorted(df_kpis['month'].unique())

    # Create month names for better display
    # Convert month numbers (1-12) to month names (January-December)
    month_names = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April',
        5: 'May', 6: 'June', 7: 'July', 8: 'August',
        9: 'September', 10: 'October', 11: 'November', 12: 'December'
    }

    # Create display options with month names
    month_display_options = ['All'] + [f"{month_names[m]}" for m in available_months]

    # Create the selectbox
    selected_month_name = st.selectbox(
        "Select Month",
        month_display_options,
        index=0  # Start with "All" selected
    )

    # Convert selected month name back to month number for filtering
    # If "All" is selected, set to None
    reverse_month_map = {v: k for k, v in month_names.items()}
    selected_month = reverse_month_map.get(selected_month_name, None)

with col_filter3:
    # Activity Category Filter (single-select dropdown)
    # Get unique categories from the data and sort them
    available_categories = sorted(df_kpis['activity_category'].unique())

    # Add "All" option
    category_options = ['All'] + available_categories

    # Create the selectbox
    selected_category = st.selectbox(
        "Select Activity Type",
        category_options,
        index=0  # Start with "All" selected
    )

# ============================================================================
# FILTER THE DATA BASED ON USER SELECTION
# ============================================================================

# Start with all data
filtered_df = df_kpis.copy()

# Apply year filter if user selected a specific year
if selected_year != 'All':
    filtered_df = filtered_df[filtered_df['year'] == int(selected_year)]

# Apply month filter if user selected a specific month
if selected_month is not None:
    filtered_df = filtered_df[filtered_df['month'] == selected_month]

# Apply category filter if user selected a specific category
if selected_category != 'All':
    filtered_df = filtered_df[filtered_df['activity_category'] == selected_category]

# ============================================================================
# CALCULATE KPIs FROM FILTERED DATA
# ============================================================================

# Sum up the metrics from all filtered rows
# .sum() adds up all values in that column
total_activities = filtered_df['activity_count'].sum()
total_distance = filtered_df['total_distance_km'].sum()
total_duration_hours = filtered_df['total_duration_hours'].sum()
total_calories = filtered_df['total_calories'].sum()

# Format duration as "XXh XXm" for display
# Example: 123.5 hours → 123h 30m
hours = int(total_duration_hours)
minutes = int((total_duration_hours - hours) * 60)
duration_formatted = f"{hours}h {minutes}m"

# Calculate average hours per week using daily summary data
# Load daily summary for filtered data
if selected_year != 'All':
    df_daily_for_avg = load_daily_summary(year=int(selected_year))
else:
    df_daily_for_avg = load_daily_summary()

# Convert to datetime and extract week number
df_daily_for_avg['activity_date'] = pd.to_datetime(df_daily_for_avg['activity_date'])
df_daily_for_avg['week_number'] = df_daily_for_avg['activity_date'].dt.isocalendar().week
df_daily_for_avg['year'] = df_daily_for_avg['activity_date'].dt.year

# Apply filters if needed
if selected_year != 'All':
    df_daily_for_avg = df_daily_for_avg[df_daily_for_avg['year'] == int(selected_year)]

if selected_month is not None:
    df_daily_for_avg = df_daily_for_avg[df_daily_for_avg['activity_date'].dt.month == selected_month]

# Sum hours per week (group by year and week to handle year boundaries)
weekly_hours = df_daily_for_avg.groupby(['year', 'week_number'])['total_duration_minutes'].sum() / 60.0

# Calculate average hours per week
avg_hours_per_week = weekly_hours.mean() if len(weekly_hours) > 0 else 0

# ============================================================================
# DISPLAY KPI CARDS
# ============================================================================

st.markdown("---")  # Horizontal line separator

# Create 5 columns for the KPI cards
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    # st.metric creates a nice card with label and value
    st.metric(
        label="Total Activities",
        value=f"{int(total_activities):,}"  # :, adds thousand separators
    )

with col2:
    st.metric(
        label="Total Distance",
        value=f"{total_distance:,.1f} km"  # :.1f means 1 decimal place
    )

with col3:
    st.metric(
        label="Training Time",
        value=duration_formatted
    )

with col4:
    st.metric(
        label="Calories Burned",
        value=f"{int(total_calories):,}"
    )

with col5:
    st.metric(
        label="Avg Hours/Week",
        value=f"{avg_hours_per_week:.1f}h"
    )

# ============================================================================
# CALENDAR HEATMAP
# ============================================================================

st.markdown("---")  # Horizontal line separator

# Create a container for the heatmap
with st.container():
    # Load daily summary data for the selected year (or most recent year if "All")
    if selected_year != 'All':
        heatmap_year = int(selected_year)
    else:
        # Use the most recent year with data
        heatmap_year = available_years[0]

    df_daily = load_daily_summary(year=heatmap_year)

    # Convert activity_date to datetime
    df_daily['activity_date'] = pd.to_datetime(df_daily['activity_date'])

    # Create a calendar heatmap using Plotly
    # We'll create a grid where each cell represents a day

    # Create all dates for the year to show empty days too
    import datetime
    start_date = datetime.date(heatmap_year, 1, 1)
    end_date = datetime.date(heatmap_year, 12, 31)
    all_dates = pd.date_range(start_date, end_date, freq='D')

    # Create a complete dataframe with all dates
    df_calendar = pd.DataFrame({'activity_date': all_dates})
    df_calendar = df_calendar.merge(df_daily, on='activity_date', how='left')

    # Fill NaN values with 0 for days without activities
    df_calendar['total_duration_minutes'] = df_calendar['total_duration_minutes'].fillna(0)
    df_calendar['total_duration_formatted'] = df_calendar['total_duration_formatted'].fillna('0h 00m')

    # Add week number and day of week for positioning
    df_calendar['week'] = df_calendar['activity_date'].dt.isocalendar().week
    df_calendar['day_of_week'] = df_calendar['activity_date'].dt.dayofweek  # Monday=0, Sunday=6
    df_calendar['day_name'] = df_calendar['activity_date'].dt.strftime('%a')
    df_calendar['date_str'] = df_calendar['activity_date'].dt.strftime('%b %d')
    df_calendar['month'] = df_calendar['activity_date'].dt.month
    df_calendar['month_name'] = df_calendar['activity_date'].dt.strftime('%B')

    # Create custom hover text
    df_calendar['hover_text'] = df_calendar.apply(
        lambda row: f"{row['date_str']}<br>Duration: {row['total_duration_formatted']}<br>Distance: {row['total_distance_km']:.1f} km"
        if row['total_duration_minutes'] > 0
        else f"{row['date_str']}<br>No activity",
        axis=1
    )

    # Create the heatmap
    fig = go.Figure(data=go.Heatmap(
        x=df_calendar['week'],
        y=df_calendar['day_of_week'],
        z=df_calendar['total_duration_minutes'],
        text=df_calendar['hover_text'],
        hovertemplate='%{text}<extra></extra>',
        colorscale=[
            [0, '#171821'],      # No activity - background color
            [0.01, '#4d3e50'],   # Very light activity - deep purple
            [0.3, '#7b6e7f'],    # Light activity - dark purple
            [0.6, '#9c526d'],    # Moderate activity - magenta
            [1.0, '#a887ce']     # High activity - primary purple
        ],
        showscale=True,
        colorbar=dict(
            title=dict(
                text="Duration<br>(minutes)",
                side="right",
                font=dict(color='#ffffff')
            ),
            tickmode="linear",
            tick0=0,
            dtick=30,
            tickfont=dict(color='#ffffff')
        ),
        xgap=2,  # Add horizontal gap between cells (border effect)
        ygap=2   # Add vertical gap between cells (border effect)
    ))

    # Add month labels at the top
    # Get first week of each month
    month_labels = df_calendar.groupby('month').agg({
        'week': 'first',
        'month_name': 'first'
    }).reset_index()

    # Add month annotations at the top
    for _, row in month_labels.iterrows():
        fig.add_annotation(
            x=row['week'],
            y=-1,  # Position above the heatmap (negative y value puts it at top due to reversed axis)
            text=row['month_name'],
            showarrow=False,
            font=dict(color='#ffffff', size=12),  # White color for month labels
            xanchor='left'
        )

    # Update layout
    fig.update_layout(
        title=dict(
            text='Training Calendar',
            font=dict(color='#a887ce', size=20),
            x=0,  # Left align
            xanchor='left'
        ),
        xaxis=dict(
            title='',  # Remove axis title
            showticklabels=False,  # Hide tick labels
            showgrid=False,  # Hide grid
            zeroline=False,  # Hide zero line
            showline=False,  # Hide axis line
            visible=False  # Hide entire x-axis including ticks
        ),
        yaxis=dict(
            title=dict(
                text="Day of Week",
                font=dict(color='#ffffff')
            ),
            tickfont=dict(color='#ffffff'),
            tickmode='array',
            tickvals=[0, 1, 2, 3, 4, 5, 6],
            ticktext=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            gridcolor='#292631',
            ticks='',  # Hide tick marks
            showline=False,  # Hide axis line
            autorange='reversed'  # Reverse y-axis to have Monday at top
        ),
        plot_bgcolor='#171821',
        paper_bgcolor='#171821',
        height=400,
        margin=dict(l=100, r=100, t=40, b=80)  # Reduced top margin from 80 to 40
    )

    # Display the heatmap
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# MONTHLY ACTIVITY CHARTS
# ============================================================================

# Create two columns for the charts
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    # Stacked bar chart: Time per month by activity category
    st.markdown("""
        <h3 style='color: #a887ce; font-size: 20px; margin-top: 0.5rem; margin-bottom: 0.5rem;'>Time per Month by Activity</h3>
    """, unsafe_allow_html=True)

    # Prepare data for stacked bar chart
    if not filtered_df.empty:
        # Pivot data to get categories as columns
        duration_pivot = filtered_df.pivot_table(
            index='year_month',
            columns='activity_category',
            values='total_duration_hours',
            aggfunc='sum',
            fill_value=0
        ).reset_index()

        # Create stacked bar chart
        fig_duration = go.Figure()

        # Color palette for categories
        colors = {
            'Running': '#a887ce',
            'Cycling': '#9c526d',
            'Swimming': '#7b6e7f',
            'Strength': '#4d3e50',
            'Multi-Sport': '#9c7da8',
            'Other': '#6e5a6e'
        }

        # Add a bar for each category
        for category in duration_pivot.columns[1:]:  # Skip year_month
            if category in colors:
                fig_duration.add_trace(go.Bar(
                    name=category,
                    x=duration_pivot['year_month'],
                    y=duration_pivot[category],
                    marker_color=colors[category],
                    hovertemplate='%{fullData.name}: %{y:.1f} hours<extra></extra>'
                ))

        fig_duration.update_layout(
            barmode='stack',
            xaxis=dict(
                title=dict(text='Month', font=dict(color='#ffffff')),
                tickfont=dict(color='#ffffff'),
                gridcolor='#292631',
                showgrid=False,
                type='category'
            ),
            yaxis=dict(
                title=dict(text='Hours', font=dict(color='#ffffff')),
                tickfont=dict(color='#ffffff'),
                gridcolor='#292631',
                showgrid=False
            ),
            plot_bgcolor='#171821',
            paper_bgcolor='#171821',
            legend=dict(
                font=dict(color='#ffffff'),
                bgcolor='rgba(0,0,0,0)'
            ),
            margin=dict(l=60, r=20, t=20, b=60),
            height=400,
            hoverlabel=dict(
                bgcolor='#ffffff',
                font_size=12,
                font_family="sans-serif",
                font_color='#7b6e7f'
            )
        )

        st.plotly_chart(fig_duration, use_container_width=True)
    else:
        st.info("No data available for the selected filters.")

with chart_col2:
    # Bar chart: Activity count per month by category
    st.markdown("""
        <h3 style='color: #a887ce; font-size: 20px; margin-top: 0.5rem; margin-bottom: 0.5rem;'>Activity Count by Category</h3>
    """, unsafe_allow_html=True)

    # Prepare data for activity count chart
    if not filtered_df.empty:
        # Pivot data to get categories as columns
        count_pivot = filtered_df.pivot_table(
            index='year_month',
            columns='activity_category',
            values='activity_count',
            aggfunc='sum',
            fill_value=0
        ).reset_index()

        # Create stacked bar chart
        fig_count = go.Figure()

        # Add a bar for each category
        for category in count_pivot.columns[1:]:  # Skip year_month
            if category in colors:
                fig_count.add_trace(go.Bar(
                    name=category,
                    x=count_pivot['year_month'],
                    y=count_pivot[category],
                    marker_color=colors[category],
                    hovertemplate='%{fullData.name}: %{y} activities<extra></extra>'
                ))

        fig_count.update_layout(
            barmode='stack',
            xaxis=dict(
                title=dict(text='Month', font=dict(color='#ffffff')),
                tickfont=dict(color='#ffffff'),
                gridcolor='#292631',
                showgrid=False,
                type='category'
            ),
            yaxis=dict(
                title=dict(text='Activity Count', font=dict(color='#ffffff')),
                tickfont=dict(color='#ffffff'),
                gridcolor='#292631',
                showgrid=False
            ),
            plot_bgcolor='#171821',
            paper_bgcolor='#171821',
            legend=dict(
                font=dict(color='#ffffff'),
                bgcolor='rgba(0,0,0,0)'
            ),
            margin=dict(l=60, r=20, t=20, b=60),
            height=400,
            hoverlabel=dict(
                bgcolor='#ffffff',
                font_size=12,
                font_family="sans-serif",
                font_color='#7b6e7f'
            )
        )

        st.plotly_chart(fig_count, use_container_width=True)
    else:
        st.info("No data available for the selected filters.")
