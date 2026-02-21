import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

all_df = pd.read_csv("data.csv")

all_df["datetime"] = pd.to_datetime(all_df["datetime"])

min_date = all_df["datetime"].min().date()
max_date = all_df["datetime"].max().date()

with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")

    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

filtered_df = all_df[
    (all_df["datetime"].dt.date >= start_date) &
    (all_df["datetime"].dt.date <= end_date)
]

# Data Creation
def create_daily_pm25_df(df):
    daily_pm25_df = df.resample(rule='D', on='datetime').agg({
        "PM2.5": "mean"
    })

    daily_pm25_df = daily_pm25_df.reset_index()

    daily_pm25_df.rename(columns={
        "PM2.5": "avg_pm25"
    }, inplace=True)

    return daily_pm25_df

# Visualization
daily_pm25_df = create_daily_pm25_df(filtered_df)

st.subheader("📈 PM2.5 Daily Trend")

if daily_pm25_df.empty:
    st.warning("No data available.")
else:
    st.line_chart(
        daily_pm25_df,
        x="datetime",
        y="avg_pm25",
        use_container_width=True
    )