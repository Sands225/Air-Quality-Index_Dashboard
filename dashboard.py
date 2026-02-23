import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

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

station_summary = (
    filtered_df
    .groupby("station")["PM2.5"]
    .mean()
    .reset_index()
    .rename(columns={"PM2.5": "avg_pm25"})
)

top5_worst = (
    station_summary
    .sort_values(by="avg_pm25", ascending=False)
    .head(5)
    .set_index("station")
)

top5_best = (
    station_summary
    .sort_values(by="avg_pm25", ascending=True)
    .head(5)
    .set_index("station")
)

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

## Station-wise PM2.5 Analysis
st.subheader("Worst and Best Air Quality Stations")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(16, 6))

colors = ["#90CAF9"] + ["#D3D3D3"] * 4

# 🔺 Worst (Highest PM2.5)
sns.barplot(
    x="avg_pm25",
    y="station",
    data=top5_worst,
    palette=colors,
    ax=ax[0]
)

ax[0].set_title("Worst Air Quality Stations")
ax[0].set_xlabel("Average PM2.5")
ax[0].set_ylabel("")

# 🔻 Best (Lowest PM2.5)
sns.barplot(
    x="avg_pm25",
    y="station",
    data=top5_best,
    palette=colors,
    ax=ax[1]
)

# Reverse X-axis to match your reference image
ax[1].invert_xaxis()

ax[1].set_title("Best Air Quality Stations")
ax[1].set_xlabel("Average PM2.5")
ax[1].set_ylabel("")

plt.tight_layout()

st.pyplot(fig)

st.subheader("Distribution of AQI Categories")

# Count AQI categories
aqi_counts = (
    filtered_df["AQI_Category"]
    .value_counts()
    .reset_index()
)

aqi_counts.columns = ["AQI_Category", "count"]

# Create blue gradient palette
colors = sns.color_palette("Blues", n_colors=len(aqi_counts))

fig, ax = plt.subplots(figsize=(10, 6))

sns.barplot(
    x="AQI_Category",
    y="count",
    data=aqi_counts,
    palette=colors,
    ax=ax
)

ax.set_title("Distribution of AQI Categories")
ax.set_xlabel("AQI Category")
ax.set_ylabel("Count")

plt.tight_layout()
st.pyplot(fig)

def get_top5_by_category(df, category):
    category_df = df[df["AQI_Category"] == category]

    top5 = (
        category_df
        .groupby("station")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        .head(5)
    )

    return top5

top_good = get_top5_by_category(filtered_df, "Good")
top_moderate = get_top5_by_category(filtered_df, "Moderate")
top_unhealthy = get_top5_by_category(filtered_df, "Unhealthy")
top_hazardous = get_top5_by_category(filtered_df, "Hazardous")

st.subheader("Top 5 Stations per AQI Category")

fig, ax = plt.subplots(nrows=2, ncols=2, figsize=(16, 10))

# Color palette per category
palette = {
    "Good": "#2E7D32",
    "Moderate": "#FDD835",
    "Unhealthy": "#FB8C00",
    "Hazardous": "#E53935"
}

# --- Good ---
sns.barplot(
    data=top_good,
    x="count",
    y="station",
    color=palette["Good"],
    ax=ax[0,0]
)
ax[0,0].set_title("Top 5 Good AQI")

# --- Moderate ---
sns.barplot(
    data=top_moderate,
    x="count",
    y="station",
    color=palette["Moderate"],
    ax=ax[0,1]
)
ax[0,1].set_title("Top 5 Moderate AQI")

# --- Unhealthy ---
sns.barplot(
    data=top_unhealthy,
    x="count",
    y="station",
    color=palette["Unhealthy"],
    ax=ax[1,0]
)
ax[1,0].set_title("Top 5 Unhealthy AQI")

# --- Hazardous ---
sns.barplot(
    data=top_hazardous,
    x="count",
    y="station",
    color=palette["Hazardous"],
    ax=ax[1,1]
)
ax[1,1].set_title("Top 5 Hazardous AQI")

for a in ax.flat:
    a.set_xlabel("Count")
    a.set_ylabel("")
    a.tick_params(axis='y', labelsize=9)

plt.tight_layout()
st.pyplot(fig)

pm25_waktu = (
    filtered_df
    .groupby("waktu")["PM2.5"]
    .mean()
    .reset_index()
    .rename(columns={"PM2.5": "avg_pm25"})
)
pm25_waktu = pm25_waktu.sort_values("avg_pm25", ascending=False)

st.subheader("📊 Average PM2.5 by Time of Day")

col1, col2 = st.columns([2,1])  # kiri lebih besar

# -------------------
# 📊 LEFT SIDE (Chart)
# -------------------
with col1:
    fig, ax = plt.subplots(figsize=(8,5))

    sns.barplot(
        data=pm25_waktu,
        x="avg_pm25",
        y="waktu",
        palette="Blues_r",
        ax=ax
    )

    ax.set_xlabel("Average PM2.5")
    ax.set_ylabel("")
    ax.set_title("Average PM2.5 by Time Category")

    plt.tight_layout()
    st.pyplot(fig)

# -------------------
# 📋 RIGHT SIDE (Text Summary)
# -------------------
with col2:
    st.markdown("### 📌 Detail")

    for _, row in pm25_waktu.iterrows():
        st.markdown(f"""
        **{row['waktu'].capitalize()}**  
        PM2.5: **{row['avg_pm25']:.2f}**
        """)