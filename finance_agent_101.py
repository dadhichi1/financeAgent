import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from tabulate import tabulate
from termcolor import colored
import streamlit as st

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
    
    unique_drivers = pd.DataFrame({
        'driver_id': np.unique(driver_ids),
        'city': np.random.choice(cities, len(np.unique(driver_ids))),
        'joining_date': start_date + pd.to_timedelta(
            np.random.randint(0, num_days * 86400, len(np.unique(driver_ids))), unit='s'
        ),
        'status': np.random.choice(['active', 'inactive'], len(np.unique(driver_ids)), p=[0.8, 0.2])
    })
    
    unique_customers = pd.DataFrame({
        'customer_id': np.unique(customer_ids),
        'city': np.random.choice(cities, len(np.unique(customer_ids))),
        'first_ride_date': pd.to_datetime(
            np.random.randint(0, num_days * 86400, len(np.unique(customer_ids))), unit='s'
        ) + pd.Timedelta(days=start_date.day),
        'total_rides': np.random.randint(1, 10, len(np.unique(customer_ids)))
    })
    
    return df_rides, unique_drivers, unique_customers

def generate_daily_report(df_rides, df_drivers, df_customers, date_str, new_initiatives):
    date_ = datetime.strptime(date_str, '%Y-%m-%d')
    last_week_date = (date_ - timedelta(days=7)).strftime('%Y-%m-%d')
    
    daily_data = df_rides[df_rides['date'] == date_str]
    mtd_data = df_rides[df_rides['date'] >= date_.strftime('%Y-%m-01')]
    last_week_daily_data = df_rides[df_rides['date'] == last_week_date]
    
    report = f"**Daily Performance Report for {date_str}**\n\n"
    report += "**--- Revenue Metrics ---**\n"
    
    revenue_data = {
        "Metric": ["Total Revenue", "Last Week Revenue", "MTD Revenue"],
        "Amount": [
            f"${daily_data['fare'].sum():,.2f}",
            f"${last_week_daily_data['fare'].sum():,.2f}",
            f"${mtd_data['fare'].sum():,.2f}"
        ]
    }
    report += tabulate(revenue_data, headers="keys", tablefmt="grid") + "\n\n"
    
    report += "**--- City Revenue Metrics ---**\n"
    city_revenue_data = []
    for city in daily_data["city"].unique():
        city_data = daily_data[daily_data["city"] == city]
        planned_revenue = len(city_data) * (30 if city != "ROI" else 20) * 0.05
        city_revenue_data.append([
            city,
            f"${city_data['fare'].sum():,.2f}",
            f"${planned_revenue:,.2f}",
            '✅' if city_data['fare'].sum() >= planned_revenue else '❌'
        ])
    report += tabulate(city_revenue_data, headers=["City", "Daily Revenue", "Planned Revenue", "Status"], tablefmt="grid") + "\n\n"
    
    report += "**--- New Initiatives ---**\n"
    report += f"{new_initiatives}\n"
    
    return report

# Streamlit app
st.title("Ride-Hailing Daily Report")
st.sidebar.header("Options")

# Generate synthetic data
df_rides, df_drivers, df_customers = generate_synthetic_data()

# Visualization: City-wise Ride Distribution
st.subheader("City-wise Ride Distribution")
fig, ax = plt.subplots()
df_rides['city'].value_counts().plot(kind='bar', color='skyblue', ax=ax)
ax.set_xlabel('City')
ax.set_ylabel('Number of Rides')
st.pyplot(fig)

# Historical Data Visualization: MTD Revenue vs. Last Week Revenue
st.subheader("Historical Revenue Comparison")
mtd_revenue = df_rides[df_rides['date'] >= (datetime.now() - timedelta(days=30)).strftime('%Y-%m-01')]['fare'].sum()
last_week_revenue = df_rides[df_rides['date'] == (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')]['fare'].sum()

fig, ax = plt.subplots()
ax.bar(['MTD', 'Last Week'], [mtd_revenue, last_week_revenue], color=['green', 'red'])
ax.set_ylabel('Revenue ($)')
st.pyplot(fig)

# Historical Data Visualization: Driver Acceptance Rate
st.subheader("Driver Acceptance Rate Over Time")
df_rides['acceptance_rate'] = df_rides.groupby('date')['driver_acceptance'].transform('mean')
fig, ax = plt.subplots()
df_rides.groupby('date')['acceptance_rate'].mean().plot(kind='line', ax=ax, color='purple')
ax.set_ylabel('Acceptance Rate')
st.pyplot(fig)

# Generate Daily Report
date_to_report = df_rides['date'].max()
new_initiatives = "Testing new onboarding in Chennai."

# Display report
report = generate_daily_report(df_rides, df_drivers, df_customers, date_to_report, new_initiatives)
st.subheader(f"Report for {date_to_report}")
st.markdown(report)
