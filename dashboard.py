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

def create_pm25_aggregation(df, freq):
    agg_df = (
        df
        .resample(rule=freq, on="datetime")
        .agg({"PM2.5": "mean"})
        .reset_index()
        .rename(columns={"PM2.5": "avg_pm25"})
    )

    if freq == "Y":
        agg_df["period"] = agg_df["datetime"].dt.year

    elif freq == "M":
        agg_df["period"] = agg_df["datetime"].dt.strftime("%Y-%m")

    elif freq == "D":
        agg_df["period"] = agg_df["datetime"].dt.date

    elif freq == "H":
        agg_df["period"] = agg_df["datetime"].dt.hour

    return agg_df[["period", "avg_pm25"]]

# Visualization
## Daily PM2.5 Metrics
daily_pm25_df = create_daily_pm25_df(filtered_df)

col1, col2, col3 = st.columns(3)

col1.metric("Avg PM2.5", f"{daily_pm25_df['avg_pm25'].mean():.2f}")
col3.metric("Min PM2.5", f"{daily_pm25_df['avg_pm25'].min():.2f}")
col2.metric("Max PM2.5", f"{daily_pm25_df['avg_pm25'].max():.2f}")

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

# PM2.5 Trend Analysis
yearly_df  = create_pm25_aggregation(filtered_df, "Y")
monthly_df = create_pm25_aggregation(filtered_df, "M")

st.subheader("📊 PM2.5 Trend Analysis")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📅 Yearly Trend")
    st.line_chart(yearly_df, x="period", y="avg_pm25", use_container_width=True)

with col2:
    st.markdown("### 🗓 Monthly Trend")
    st.line_chart(monthly_df, x="period", y="avg_pm25", use_container_width=True)