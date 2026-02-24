import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import numpy as np

st.set_page_config(layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("data.csv")
    df["datetime"] = pd.to_datetime(df["datetime"])
    return df

all_df = load_data()

min_date = all_df["datetime"].min().date()
max_date = all_df["datetime"].max().date()

with st.sidebar:
    st.image("https://raw.githubusercontent.com/Sands225/Air-Quality-Index_Dashboard/main/logo.png")
    
    st.title("Air Quality Dashboard")

    start_date, end_date = st.date_input(
        label="Select Date Range",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

filtered_df = all_df[
    (all_df["datetime"].dt.date >= start_date) &
    (all_df["datetime"].dt.date <= end_date)
]

if filtered_df.empty:
    st.warning("No data available for selected date range.")
    st.stop()

def aggregate_pm25(df, freq):
    return (
        df.resample(freq, on="datetime")["PM2.5"]
        .mean()
        .reset_index()
        .rename(columns={"PM2.5": "avg_pm25"})
    )

def station_summary(df):
    return (
        df.groupby("station")["PM2.5"]
        .mean()
        .reset_index()
        .rename(columns={"PM2.5": "avg_pm25"})
    )

def get_top_stations_by_category(df, category):
    return (
        df[df["AQI_Category"] == category]
        .groupby("station")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        .head(5)
    )

daily_df = aggregate_pm25(filtered_df, "D")

avg_pm = daily_df["avg_pm25"].mean()
max_pm = daily_df["avg_pm25"].max()
min_pm = daily_df["avg_pm25"].min()

station_df = station_summary(filtered_df)
worst_station = station_df.sort_values("avg_pm25", ascending=False).iloc[0]
best_station = station_df.sort_values("avg_pm25").iloc[0]

peak_day = daily_df.sort_values("avg_pm25", ascending=False).iloc[0]["datetime"].date()

# SIDEBAR
with st.sidebar:
    st.markdown("---")
    st.markdown("## 🔎 Key Insights")

    st.markdown(f"""
    **Peak Pollution Date**  
    {peak_day}

    **Worst Station**  
    {worst_station['station']}  
    PM2.5: {worst_station['avg_pm25']:.2f}

    **Best Station**  
    {best_station['station']}  
    PM2.5: {best_station['avg_pm25']:.2f}

    **Overall Average PM2.5**  
    {avg_pm:.2f}
    """)

# DASHBOARD
st.markdown(
    f"""
    <div style="text-align:center; padding-bottom:20px;">
        <h1 style="margin-bottom:15px; line-height:1.2;">
            Air Quality <br>
            Monitoring Dashboard
        </h1>
        <p style="color:gray; margin-top:10px; margin-bottom: 60px; font-size:16px;">
            Environmental Analytics Report<br>
            {start_date} to {end_date}
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# KPI SECTION
monthly_df = aggregate_pm25(filtered_df, "M")

if len(monthly_df) > 1:
    delta = monthly_df["avg_pm25"].iloc[-1] - monthly_df["avg_pm25"].iloc[-2]
else:
    delta = 0

outer1, col1, col2, col3, outer2 = st.columns([1, 2, 2, 2, 1])

with col1:
    st.markdown(
        f"""
        <div style="text-align:center;">
            <p style="margin-bottom:5px; font-size:16px;">Average PM2.5</p>
            <h2 style="margin:0; ">{avg_pm:.2f}</h2>
            <p style="color:gray; margin-top:5px; color:white; background-color:#f94449; display:inline-block; padding:2px 6px; border-radius:4px; font-size:12px;">
                {delta:.2f} vs prev month
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div style="text-align:center;">
            <p style="margin-bottom:5px; font-size:16px;">Maximum PM2.5</p>
            <h2 style="margin:0;">{max_pm:.2f}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div style="text-align:center;">
            <p style="margin-bottom:5px; font-size:16px;">Minimum PM2.5</p>
            <h2 style="margin:0;">{min_pm:.2f}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

# DAILY TREND
st.markdown(
    """
    <h1 style="text-align:center; margin-top:40px; margin-bottom:20px;">
        Daily PM2.5 Trend
    </h1>
    """,
    unsafe_allow_html=True
)
st.line_chart(daily_df, x="datetime", y="avg_pm25", use_container_width=True)

# YEARLY & MONTHLY TREND
st.markdown(
    """
    <h1 style="text-align:center; margin-top:40px; margin-bottom:20px;">
        Trend Analysis
    </h1>
    """,
    unsafe_allow_html=True
)

yearly_df = aggregate_pm25(filtered_df, "Y")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Yearly Trend")
    st.line_chart(yearly_df, x="datetime", y="avg_pm25", use_container_width=True)

with col2:
    st.markdown("### Monthly Trend")
    st.line_chart(monthly_df, x="datetime", y="avg_pm25", use_container_width=True)

# STATION ANALYSIS
st.markdown(
    """
    <h1 style="text-align:center; margin-top:40px; margin-bottom:20px;">
        Worst & Best Stations
    </h1>
    """,
    unsafe_allow_html=True
)

top5_worst = station_df.sort_values("avg_pm25", ascending=False).head(5)
top5_best = station_df.sort_values("avg_pm25").head(5)

top1_worst = top5_worst.iloc[0]
top1_best = top5_best.iloc[0]

col1, col2 = st.columns([2, 1])

with col1:
    fig, ax = plt.subplots(1, 2, figsize=(14, 5))

    worst_palette = ["#D32F2F"] + ["#D3D3D3"] * (len(top5_worst) - 1)

    sns.barplot(
        data=top5_worst,
        x="avg_pm25",
        y="station",
        palette=worst_palette,
        ax=ax[0]
    )
    ax[0].set_title("Top 5 Worst Stations")
    ax[0].set_xlabel("Average PM2.5")

    best_palette = ["#2E7D32"] + ["#D3D3D3"] * (len(top5_best) - 1)

    sns.barplot(
        data=top5_best,
        x="avg_pm25",
        y="station",
        palette=best_palette,
        ax=ax[1]
    )
    ax[1].invert_xaxis()
    ax[1].set_title("Top 5 Best Stations")
    ax[1].set_xlabel("Average PM2.5")

    plt.tight_layout()
    st.pyplot(fig)

with col2:
    st.markdown("### Station Summary")

    st.markdown(
        f"""
        <h4 style="color:#D32F2F; margin-bottom:5px;">Worst Station</h4>
        <p style="font-size:20px; font-weight:bold; margin:0;">
            {top1_worst['station']}
        </p>
        <p style="margin-top:2px;">
            PM2.5: {top1_worst['avg_pm25']:.2f}
        </p>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <h4 style="color:#2E7D32; margin-bottom:5px;">Best Station</h4>
        <p style="font-size:20px; font-weight:bold; margin:0;">
            {top1_best['station']}
        </p>
        <p style="margin-top:2px;">
            PM2.5: {top1_best['avg_pm25']:.2f}
        </p>
        """,
        unsafe_allow_html=True
    )

# AQI SECTION
st.markdown(
    """
    <h1 style="text-align:center; margin-top:40px; margin-bottom:20px;">
        AQI Distribution & Station Analysis
    </h1>
    """,
    unsafe_allow_html=True
)


col1, col2, col3 = st.columns([1.65, 1, 1])

category_colors = {
    "Good": "#2E7D32",
    "Moderate": "#F9A825",
    "Unhealthy": "#EF6C00",
    "Hazardous": "#C62828"
}


with col1:
    st.markdown("### AQI Distribution")

    category_order = ["Good", "Moderate", "Unhealthy", "Hazardous"]

    aqi_counts = (
        filtered_df["AQI_Category"]
        .value_counts(normalize=True) * 100
    )

    aqi_counts = (
        aqi_counts
        .reindex(category_order)
        .reset_index()
    )

    aqi_counts.columns = ["AQI_Category", "percentage"]

    colors = [category_colors.get(cat, "#D3D3D3") for cat in aqi_counts["AQI_Category"]]

    fig, ax = plt.subplots(figsize=(6,5))

    sns.barplot(
        data=aqi_counts,
        x="AQI_Category",
        y="percentage",
        palette=colors,
        ax=ax
    )

    ax.set_ylabel("Percentage (%)")
    ax.set_xlabel("")
    ax.set_title("Distribution by AQI Category", fontsize=12, weight="bold")

    plt.xticks(rotation=20)
    plt.tight_layout()
    st.pyplot(fig)

with col2:
    for category in ["Good", "Moderate"]:
        top_df = get_top_stations_by_category(filtered_df, category)

        color = category_colors.get(category, "#000000")

        # 🔹 Colored Title
        st.markdown(
            f"<h4 style='color:{color}; margin-bottom:8px;'>{category}</h4>",
            unsafe_allow_html=True
        )

        if top_df.empty:
            st.info("No data")
        else:
            palette = [color] + ["#D3D3D3"] * (len(top_df) - 1)

            fig, ax = plt.subplots(figsize=(5,3))
            sns.barplot(
                data=top_df,
                x="count",
                y="station",
                palette=palette,
                ax=ax
            )
            ax.set_xlabel("")
            ax.set_ylabel("")
            plt.tight_layout()
            st.pyplot(fig)

with col3:
    for category in ["Unhealthy", "Hazardous"]:
        top_df = get_top_stations_by_category(filtered_df, category)

        color = category_colors.get(category, "#000000")

        st.markdown(
            f"<h4 style='color:{color}; margin-bottom:8px;'>{category}</h4>",
            unsafe_allow_html=True
        )

        if top_df.empty:
            st.info("No data")
        else:
            palette = [color] + ["#D3D3D3"] * (len(top_df) - 1)

            fig, ax = plt.subplots(figsize=(5,3))
            sns.barplot(
                data=top_df,
                x="count",
                y="station",
                palette=palette,
                ax=ax
            )
            ax.set_xlabel("")
            ax.set_ylabel("")
            plt.tight_layout()
            st.pyplot(fig)

# TIME OF DAY ANALYSIS
st.markdown(
    """
    <h1 style="text-align:center; margin-top:40px; margin-bottom:20px;">
        PM2.5 by Time of Day
    </h1>
    """,
    unsafe_allow_html=True
)

time_order = ["pagi", "siang", "sore", "malam"]

time_df = (
    filtered_df.groupby("waktu")["PM2.5"]
    .mean()
    .reindex(time_order)
    .reset_index()
    .rename(columns={"PM2.5": "avg_pm25"})
)

highest_time = time_df.sort_values("avg_pm25", ascending=False).iloc[0]
lowest_time = time_df.sort_values("avg_pm25").iloc[0]

col1, col2 = st.columns([1.5, 1])

with col1:
    max_value = time_df["avg_pm25"].max()
    min_value = time_df["avg_pm25"].min()

    colors = []
    for value in time_df["avg_pm25"]:
        if value == max_value:
            colors.append("#C62828")
        elif value == min_value:
            colors.append("#2E7D32")
        else:
            colors.append("#D3D3D3")

    fig, ax = plt.subplots(figsize=(8,5))

    sns.barplot(
        data=time_df,
        x="avg_pm25",
        y="waktu",
        palette=colors,
        ax=ax
    )

    ax.set_xlabel("Average PM2.5")
    ax.set_ylabel("")
    ax.set_title("Average PM2.5 by Time of Day", fontsize=12, weight="bold")

    plt.tight_layout()
    st.pyplot(fig)

with col2:
    st.markdown("### Pollution Summary")

    # Highest Pollution
    st.markdown(
        f"""
        <h4 style="color:#B71C1C; margin-bottom:5px;">
            Highest Pollution
        </h4>
        <p style="color:#E57373; font-weight:bold; margin:0;">
            {highest_time['waktu'].capitalize()}
        </p>
        <p style="color:#EF9A9A; margin-top:2px;">
            PM2.5: {highest_time['avg_pm25']:.2f}
        </p>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Lowest Pollution
    st.markdown(
        f"""
        <h4 style="color:#1B5E20; margin-bottom:5px;">
            Lowest Pollution
        </h4>
        <p style="color:#66BB6A; font-weight:bold; margin:0;">
            {lowest_time['waktu'].capitalize()}
        </p>
        <p style="color:#A5D6A7; margin-top:2px;">
            PM2.5: {lowest_time['avg_pm25']:.2f}
        </p>
        """,
        unsafe_allow_html=True
    )

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; font-size: 12px; color: gray;'>Air Quality Index Dashboard | I Made Sandika Wijaya | Dicoding Data Scientist Final Project</p>",
    unsafe_allow_html=True
)