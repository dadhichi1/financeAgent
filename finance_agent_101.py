import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_synthetic_data(num_days=100, num_rides_per_day=100000):
    cities = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Ahmedabad", "ROI"]
    start_date = datetime.now() - timedelta(days=num_days)
    all_rides_data = []

    all_driver_data = []
    all_customer_data = []
    all_customers = {}
    all_drivers = {}
    
    for day in range(num_days):
        date_ = start_date + timedelta(days=day)
        date_str = date_.strftime("%Y-%m-%d")
        
        for ride_id in range(num_rides_per_day):
            ride_time = date_ + timedelta(seconds=random.randint(0, 86400))
            ride_time_str = ride_time.strftime("%H:%M:%S")
            
            city = random.choices(cities, weights=[0.25, 0.22, 0.18, 0.15, 0.08, 0.07, 0.05, 0.20])[0]
            
            driver_id = f'driver_{random.randint(1, 1000000)}'
            customer_id = f'customer_{random.randint(1, 1000000)}'
            
            if driver_id not in all_drivers:
                all_drivers[driver_id] = {
                    "city": city,
                    "joining_date": (date_ + timedelta(seconds=random.randint(0, 86400)-86400)).strftime("%Y-%m-%d"),
                    "status": 'active' if random.random() > 0.2 else 'inactive'
                }
            
            if customer_id not in all_customers:
                all_customers[customer_id] = {
                    "city": city,
                    "first_ride_date": date_str,
                    "total_rides": 0
                }

            all_customers[customer_id]["total_rides"] += 1

            base_fare = 30 if city != "ROI" else 20
            fare = base_fare + (random.uniform(-10, 15) if city != "ROI" else random.uniform(-5, 10))
            fare = round(fare, 2)
            driver_acceptance = 1 if random.random() < 0.60 else 0
            incentive_applied = 1 if random.random() < 0.3 else 0 
            
            all_rides_data.append({
                'ride_id': ride_id,
                'date': date_str,
                'time': ride_time_str,
                'city': city,
                'driver_id': driver_id,
                'customer_id': customer_id,
                'fare': fare,
                'driver_acceptance': driver_acceptance,
                'incentive_applied': incentive_applied
            })
            
    df_rides = pd.DataFrame(all_rides_data)
    df_drivers = pd.DataFrame(list(all_drivers.items()), columns=["driver_id", "data"])
    df_drivers = pd.concat([df_drivers['driver_id'], df_drivers['data'].apply(pd.Series)], axis=1)
    df_customers = pd.DataFrame(list(all_customers.items()), columns=["customer_id", "data"])
    df_customers = pd.concat([df_customers['customer_id'], df_customers['data'].apply(pd.Series)], axis=1)
        
    return df_rides, df_drivers, df_customers

df_rides, df_drivers, df_customers = generate_synthetic_data()

df_rides.to_csv('rides_data.csv', index=False)
df_drivers.to_csv('driver_data.csv', index=False)
df_customers.to_csv('customer_data.csv', index=False)

print("Synthetic data generated and saved as CSV files.")