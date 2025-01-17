# Import Libraries
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
st.title("Ride-Hailing Daily Report with Projections & P&L")
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

# P&L Variables
incentive_cost = 0.3 * filtered_data['fare'][filtered_data['incentive_applied'] == 1].sum()
operational_cost = 0.1 * filtered_data['fare'].sum()  # 10% operational costs
total_revenue = filtered_data['fare'].sum()
profit = total_revenue - (incentive_cost + operational_cost)

# P&L Report
st.subheader(f"P&L Report for {selected_date_str}{' in ' + selected_city if selected_city != 'All' else ''}")
pnl_data = {
    "Total Revenue": [f"₹{total_revenue:,.2f}"],
    "Incentive Costs": [f"₹{incentive_cost:,.2f}"],
    "Operational Costs": [f"₹{operational_cost:,.2f}"],
    "Net Profit": [f"₹{profit:,.2f}"]
}
st.table(pd.DataFrame(pnl_data))

# Graph: Daily Revenue Trends
st.subheader("Daily Revenue Trends")
historical_trend = df_rides.groupby('date')['fare'].sum()
fig, ax = plt.subplots()
historical_trend.plot(kind='line', ax=ax, color='green')
ax.set_title("Daily Revenue Trends")
ax.set_ylabel("Revenue (₹)")
ax.set_xlabel("Date")
st.pyplot(fig)

# Graph: City-wise Revenue Contribution (Pie Chart)
if selected_city == "All":
    st.subheader("City-wise Revenue Contribution")
    city_revenue = df_rides.groupby('city')['fare'].sum()
    fig, ax = plt.subplots()
    city_revenue.plot(kind='pie', autopct='%1.1f%%', ax=ax, legend=False)
    ax.set_ylabel("")
    st.pyplot(fig)

# Driver Acceptance Rate
st.subheader("Driver Acceptance Rates")
acceptance_rate = filtered_data.groupby('city')['driver_acceptance'].mean() * 100
fig, ax = plt.subplots()
acceptance_rate.plot(kind='bar', ax=ax, color='skyblue')
ax.set_title("Driver Acceptance Rates by City")
ax.set_ylabel("Acceptance Rate (%)")
ax.set_xlabel("City")
st.pyplot(fig)

# Projections
st.subheader("Revenue Projections")
historical_data = df_rides.groupby('date')['fare'].sum()
daily_growth_rate = historical_data.pct_change().mean()
projected_revenue = historical_data[-1] * (1 + daily_growth_rate) ** np.arange(1, 31)

fig, ax = plt.subplots()
pd.Series(projected_revenue).plot(kind='line', ax=ax, color='orange')
ax.set_title("Projected Revenue (Next 30 Days)")
ax.set_ylabel("Projected Revenue (₹)")
ax.set_xlabel("Days from Today")
st.pyplot(fig)

# Actionables
st.subheader("Actionable Insights")
actionables = [
    "- Optimize incentive programs in cities with low driver acceptance rates.",
    "- Increase focus on high-growth cities (e.g., Mumbai, Delhi).",
    "- Consider scaling operations in ROI cities with consistent growth.",
    f"- Expand pilot onboarding in {selected_city if selected_city != 'All' else 'selected cities like Chennai'}."
]
st.markdown("\n".join(actionables))
