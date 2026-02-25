import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import numpy as np

st.set_page_config(layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("dashboard/data.csv")
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
        df[df["Cluster Label"] == category]
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
    fig, ax = plt.subplots(1, 2, figsize=(14, 7))

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
        <h4 style="color:#D32F2F;">Worst Station</h4>
        <p style="font-size:14px; font-weight:bold; margin:0;">
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
        <h4 style="color:#2E7D32;">Best Station</h4>
        <p style="font-size:14px; font-weight:bold; margin:0;">
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

category_colors = {
    "Low Pollution": "#2E7D32",
    "Moderate Pollution": "#F9A825",
    "High Pollution": "#EF6C00",
}

# AQI DISTRIBUTION
def show_aqi_distribution(filtered_df, category_colors):

    st.markdown(
        """
        <h3 style="text-align:center; margin-bottom:20px;">
            AQI Distribution
        </h3>
        """,
        unsafe_allow_html=True
    )

    category_order = ["Low Pollution", "Moderate Pollution", "High Pollution"]

    aqi_counts = (
        filtered_df["Cluster Label"]
        .value_counts(normalize=True) * 100
    )

    aqi_counts = (
        aqi_counts
        .reindex(category_order)
        .reset_index()
    )

    aqi_counts.columns = ["Cluster Label", "percentage"]

    colors = [
        category_colors.get(cat, "#D3D3D3")
        for cat in aqi_counts["Cluster Label"]
    ]

    col_chart, col_detail = st.columns([3, 1])

    # Chart Section
    with col_chart:
        fig, ax = plt.subplots(figsize=(6,5))

        sns.barplot(
            data=aqi_counts,
            x="Cluster Label",
            y="percentage",
            palette=colors,
            ax=ax
        )

        ax.set_ylabel("Percentage (%)")
        ax.set_xlabel("")
        ax.set_title("Distribution by AQI Category",
                     fontsize=12,
                     weight="bold")

        plt.xticks(rotation=20)
        sns.despine()
        plt.tight_layout()

        st.pyplot(fig)

    # Detail Section
    with col_detail:
        st.markdown("#### Summary")

        for _, row in aqi_counts.iterrows():
            category = row["Cluster Label"]
            percent = row["percentage"]

            st.metric(
                label=category,
                value=f"{percent:.1f}%"
            )

def show_top_station(filtered_df, category, category_colors):

    st.markdown(f"### {category}")

    top_df = get_top_stations_by_category(filtered_df, category)

    if top_df.empty:
        st.info("No data")
        return

    color = category_colors.get(category, "#000000")

    palette = [color] + ["#E8E8E8"] * (len(top_df) - 1)

    # Chart Section
    fig, ax = plt.subplots(figsize=(4,3))

    sns.barplot(
        data=top_df,
        x="count",
        y="station",
        palette=palette,
        ax=ax
    )

    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.tick_params(labelsize=8)
    sns.despine(left=True, bottom=True)

    plt.tight_layout()
    st.pyplot(fig)

    # Detail Section
    total_count = int(top_df["count"].sum())
    unique_station = int(top_df["station"].nunique())
    top_station_name = top_df.iloc[0]["station"]
    top_value = int(top_df.iloc[0]["count"])

    colA, colB = st.columns(2)

    with colA:
        st.metric("Total Records", f"{total_count:,}")

    with colB:
        st.metric("Stations Shown", unique_station)

    st.metric(
        "Top Station",
        top_station_name,
        f"{top_value:,} records"
    )

# Centered AQI Distribution
sp1, col_center, sp2 = st.columns([1,2,1])

with col_center:
    show_aqi_distribution(filtered_df, category_colors)

st.markdown(
    """
    <h3 style="text-align:center; margin-top:20px; margin-bottom:20px;">
        AQI Category Distribution per Station
    </h3>
    """,
    unsafe_allow_html=True
)

# Low | Moderate | High
col1, col2, col3 = st.columns(3)

with col1:
    show_top_station(filtered_df, "Low Pollution", category_colors)

with col2:
    show_top_station(filtered_df, "Moderate Pollution", category_colors)

with col3:
    show_top_station(filtered_df, "High Pollution", category_colors)

# TIME OF DAY ANALYSIS
st.markdown(
    """
    <h1 style="text-align:center; margin-top:40px; margin-bottom:20px;">
        PM2.5 by Time of Day
    </h1>
    """,
    unsafe_allow_html=True
)

time_order = ["Pagi", "Siang", "Sore", "Malam"]

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