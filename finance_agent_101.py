import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Synthetic Data Generation
def generate_synthetic_data(num_days=30, num_rides_per_day=10000):
    cities = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Ahmedabad", "ROI"]
    city_weights = [0.25, 0.22, 0.18, 0.15, 0.08, 0.07, 0.05, 0.20]
    city_weights = np.array(city_weights) / sum(city_weights)
    
    start_date = datetime.now() - timedelta(days=num_days)
    total_rides = num_days * num_rides_per_day
    
    dates = np.repeat(
        [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(num_days)],
        num_rides_per_day
    )
    times = pd.to_timedelta(np.random.randint(0, 86400, total_rides), unit='s').astype(str)
    cities_array = np.random.choice(cities, size=total_rides, p=city_weights)
    driver_ids = np.random.randint(1, 10000, total_rides)
    customer_ids = np.random.randint(1, 10000, total_rides)
    base_fares = np.where(cities_array == "ROI", 20, 30)
    fare_variation = np.where(
        cities_array == "ROI", 
        np.random.uniform(-5, 10, total_rides), 
        np.random.uniform(-10, 15, total_rides)
    )
    fares = np.round(base_fares + fare_variation, 2)
    driver_acceptance = np.random.choice([1, 0], total_rides, p=[0.6, 0.4])
    incentive_applied = np.random.choice([1, 0], total_rides, p=[0.3, 0.7])
    
    df_rides = pd.DataFrame({
        'ride_id': np.arange(total_rides),
        'date': dates,
        'time': times,
        'city': cities_array,
        'driver_id': driver_ids,
        'customer_id': customer_ids,
        'fare': fares,
        'driver_acceptance': driver_acceptance,
        'incentive_applied': incentive_applied
    })
    return df_rides

# Generate synthetic data
df_rides = generate_synthetic_data()

# Streamlit App
st.title("Ride-Hailing Daily Report")
st.sidebar.header("Options")

# Date Selection
selected_date = st.sidebar.date_input("Select Date for Report", datetime.now().date() - timedelta(days=1))
selected_date_str = selected_date.strftime("%Y-%m-%d")

# City Dropdown Selection
cities = sorted(df_rides['city'].unique())
selected_city = st.sidebar.selectbox("Select City", ["All"] + cities)

# Filter Data for Selected Date and City
filtered_data = df_rides[df_rides['date'] == selected_date_str]
if selected_city != "All":
    filtered_data = filtered_data[filtered_data['city'] == selected_city]

# Generate Report
st.subheader(f"Report for {selected_date_str}{' in ' + selected_city if selected_city != 'All' else ''}")

# Daily Revenue Metrics
daily_revenue = filtered_data['fare'].sum()
city_revenue = filtered_data.groupby('city')['fare'].sum().reset_index()
city_revenue.columns = ['City', 'Revenue']

# Display Metrics
st.write(f"**Total Revenue for {selected_date_str}:** ₹{daily_revenue:,.2f}")
if selected_city == "All":
    st.write("**City-wise Revenue Breakdown:**")
    st.table(city_revenue)
else:
    st.write(f"**Revenue in {selected_city}:** ₹{daily_revenue:,.2f}")

# Historical Analysis
st.subheader("Historical Analysis")

# Historical Revenue Trends
if selected_city == "All":
    historical_trend = df_rides.groupby('date')['fare'].sum()
else:
    historical_trend = df_rides[df_rides['city'] == selected_city].groupby('date')['fare'].sum()

# Visualization: Historical Revenue Trend
fig, ax = plt.subplots()
historical_trend.plot(kind='line', ax=ax, color='green')
ax.set_title(f"Historical Revenue Trend{' in ' + selected_city if selected_city != 'All' else ''}")
ax.set_ylabel('Revenue (₹)')
ax.set_xlabel('Date')
st.pyplot(fig)

# City-wise Revenue Visualization
if selected_city == "All":
    st.subheader("City-wise Revenue Distribution")
    fig, ax = plt.subplots()
    city_revenue.plot(kind='bar', x='City', y='Revenue', color='skyblue', ax=ax)
    ax.set_ylabel('Revenue (₹)')
    st.pyplot(fig)

# New Initiatives
st.subheader("New Initiatives Based on Analysis")
initiatives = [
    "- Optimize driver incentives in underperforming cities.",
    "- Target high-growth cities with increased marketing efforts.",
    "- Adjust fare policies to increase revenue in price-sensitive regions.",
    f"- Pilot new onboarding strategies in {selected_city if selected_city != 'All' else 'specific cities like Chennai'}."
]
st.markdown("\n".join(initiatives))
