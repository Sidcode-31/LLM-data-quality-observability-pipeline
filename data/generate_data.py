import os
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

os.makedirs("data/raw", exist_ok=True)
random.seed(42)
np.random.seed(42)

start_date = datetime(2026, 11, 1)

# Generate 30 days of clean historical data (~10 Lakh INR/day)
for day_idx in range(30):
    current_date = start_date + timedelta(days=day_idx)
    date_str = current_date.strftime("%Y_%m_%d")
    num_rows = random.randint(480, 520)
    
    df = pd.DataFrame({
        "transaction_id": [f"TXN_{date_str}_{i:04d}" for i in range(num_rows)],
        "customer_id": [f"CUST_{random.randint(1000, 9999)}" for _ in range(num_rows)],
        "email": [f"user{random.randint(1, 5000)}@example.com" for _ in range(num_rows)],
        "amount": np.round(np.random.normal(loc=2000, scale=300, size=num_rows), 2),
        "created_at": [current_date.strftime("%Y-%m-%d %H:%M:%S")] * num_rows
    })
    df["amount"] = df["amount"].clip(lower=100.0)
    df.to_csv(f"data/raw/orders_{date_str}.csv", index=False)

# Generate Day 31 broken file (~1 Lakh INR + DQ violations)
broken_date = "2026_12_01"
num_broken = 120
df_broken = pd.DataFrame({
    "transaction_id": [f"TXN_{broken_date}_{i:04d}" for i in range(num_broken)],
    "customer_id": [f"CUST_{random.randint(1000, 9999)}" for _ in range(num_broken)],
    "email": [f"user{random.randint(1, 5000)}@example.com" for _ in range(num_broken)],
    "amount": np.round(np.random.normal(loc=850, scale=150, size=num_broken), 2),
    "created_at": ["2026-12-01 10:00:00"] * num_broken
})

# Inject DQ errors
df_broken.loc[0:14, "customer_id"] = None                        # Null customer_ids
df_broken.loc[15:24, "transaction_id"] = df_broken.loc[0, "transaction_id"]  # Duplicates
df_broken.loc[25:34, "amount"] = -150.00                         # Negative prices
df_broken.loc[35:44, "email"] = "invalid-email-format"           # Bad emails

df_broken.to_csv(f"data/raw/orders_{broken_date}_broken.csv", index=False)
print("Generated 30 clean files and 1 broken file in data/raw/")