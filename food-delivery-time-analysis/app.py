"""Interactive Streamlit dashboard for food delivery time analysis."""

from pathlib import Path
import sqlite3

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Food Delivery Analytics",
    page_icon="🍱",
    layout="wide",
)

ROOT = Path(__file__).resolve().parent
LOCAL_DATA = ROOT / "zomato_cleaned.csv"
DATA_URL = (
    "https://huggingface.co/datasets/allenborochin/zomato_delivery_EDA/"
    "resolve/main/zomato_cleaned.csv?download=true"
)


@st.cache_data(show_spinner="Loading the delivery dataset…")
def load_data():
    source = LOCAL_DATA if LOCAL_DATA.exists() else DATA_URL
    frame = pd.read_csv(source)
    text_columns = frame.select_dtypes(include=["object", "str"]).columns
    for column in text_columns:
        frame[column] = frame[column].str.strip()
    frame = frame.drop_duplicates()
    frame = frame.dropna(
        subset=["ID", "Weather_conditions", "Road_traffic_density", "Time_taken (min)"]
    ).copy()
    frame["distance_band"] = pd.cut(
        frame["distance_km"],
        bins=[0, 5, 10, 15, float("inf")],
        labels=["0–5 km", "5–10 km", "10–15 km", "15+ km"],
        include_lowest=True,
    ).astype("string")
    return frame


st.title("🍱 Food Delivery Time Analysis")
st.caption(
    "Explore how traffic, weather, trip distance, and operating conditions relate "
    "to delivery time across 38,964 food deliveries in India."
)

try:
    data = load_data()
except Exception as error:
    st.error("The dataset could not be loaded. Check the source link or try again later.")
    st.caption(f"Details: {error}")
    st.stop()

with st.sidebar:
    st.header("Filter deliveries")
    city_options = ["All"] + sorted(data["City"].dropna().unique().tolist())
    traffic_options = ["All"] + sorted(data["Road_traffic_density"].dropna().unique().tolist())
    weather_options = ["All"] + sorted(data["Weather_conditions"].dropna().unique().tolist())
    vehicle_options = ["All"] + sorted(data["Type_of_vehicle"].dropna().unique().tolist())
    selected_city = st.selectbox("City type", city_options)
    selected_traffic = st.selectbox("Traffic", traffic_options)
    selected_weather = st.selectbox("Weather", weather_options)
    selected_vehicle = st.selectbox("Vehicle", vehicle_options)

filtered = data.copy()
if selected_city != "All":
    filtered = filtered[filtered["City"] == selected_city]
if selected_traffic != "All":
    filtered = filtered[filtered["Road_traffic_density"] == selected_traffic]
if selected_weather != "All":
    filtered = filtered[filtered["Weather_conditions"] == selected_weather]
if selected_vehicle != "All":
    filtered = filtered[filtered["Type_of_vehicle"] == selected_vehicle]

if filtered.empty:
    st.warning("No deliveries match these filters. Choose different filters in the sidebar.")
    st.stop()

# Use SQLite for the dashboard summaries, keeping the query work visible and reusable.
with sqlite3.connect(":memory:") as connection:
    filtered.to_sql("deliveries", connection, index=False, if_exists="replace")
    totals = pd.read_sql_query(
        '''SELECT COUNT(*) AS orders,
                  ROUND(AVG("Time_taken (min)"), 2) AS average_minutes,
                  ROUND(AVG(distance_km), 2) AS average_distance_km,
                  ROUND(AVG(Delivery_person_Ratings), 2) AS average_courier_rating
           FROM deliveries''',
        connection,
    ).iloc[0]
    by_traffic = pd.read_sql_query(
        '''SELECT Road_traffic_density AS category,
                  COUNT(*) AS orders,
                  ROUND(AVG("Time_taken (min)"), 2) AS average_minutes
           FROM deliveries
           GROUP BY Road_traffic_density
           ORDER BY average_minutes DESC''',
        connection,
    )
    by_weather = pd.read_sql_query(
        '''SELECT Weather_conditions AS category,
                  COUNT(*) AS orders,
                  ROUND(AVG("Time_taken (min)"), 2) AS average_minutes
           FROM deliveries
           GROUP BY Weather_conditions
           ORDER BY average_minutes DESC''',
        connection,
    )
    by_distance = pd.read_sql_query(
        '''SELECT distance_band AS category,
                  COUNT(*) AS orders,
                  ROUND(AVG("Time_taken (min)"), 2) AS average_minutes
           FROM deliveries
           WHERE distance_band IS NOT NULL
           GROUP BY distance_band
           ORDER BY CASE distance_band
               WHEN '0–5 km' THEN 1 WHEN '5–10 km' THEN 2
               WHEN '10–15 km' THEN 3 ELSE 4 END''',
        connection,
    )
    by_city = pd.read_sql_query(
        '''SELECT City AS category,
                  COUNT(*) AS orders,
                  ROUND(AVG("Time_taken (min)"), 2) AS average_minutes
           FROM deliveries
           GROUP BY City
           ORDER BY average_minutes DESC''',
        connection,
    )

st.subheader("Delivery overview")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Orders", f"{int(totals['orders']):,}")
k2.metric("Average delivery", f"{totals['average_minutes']:.2f} min")
k3.metric("Average distance", f"{totals['average_distance_km']:.2f} km")
k4.metric("Average courier rating", f"{totals['average_courier_rating']:.2f} / 5")

left, right = st.columns(2)
with left:
    st.subheader("Delivery time by traffic")
    st.bar_chart(by_traffic.set_index("category")["average_minutes"])
    st.caption("Average delivery time in minutes")
    st.dataframe(by_traffic, hide_index=True, use_container_width=True)
with right:
    st.subheader("Delivery time by weather")
    st.bar_chart(by_weather.set_index("category")["average_minutes"])
    st.caption("Average delivery time in minutes")
    st.dataframe(by_weather, hide_index=True, use_container_width=True)

left, right = st.columns(2)
with left:
    st.subheader("Delivery time by trip distance")
    st.bar_chart(by_distance.set_index("category")["average_minutes"])
    st.caption("Average delivery time in minutes")
    st.dataframe(by_distance, hide_index=True, use_container_width=True)
with right:
    st.subheader("Delivery time by city type")
    st.bar_chart(by_city.set_index("category")["average_minutes"])
    st.caption("Average delivery time in minutes")
    st.dataframe(by_city, hide_index=True, use_container_width=True)

correlation = filtered["distance_km"].corr(filtered["Time_taken (min)"])
st.info(
    f"In the currently selected deliveries, distance and delivery time have a "
    f"correlation of {correlation:.3f}. This shows an association in this dataset; "
    "it does not prove that distance alone causes longer delivery times."
)

with st.expander("See the SQL used for these summaries"):
    st.code(
        '''SELECT Road_traffic_density,
       COUNT(*) AS orders,
       ROUND(AVG("Time_taken (min)"), 2) AS average_minutes
FROM deliveries
GROUP BY Road_traffic_density
ORDER BY average_minutes DESC;''',
        language="sql",
    )

with st.expander("View sample records and download data"):
    st.dataframe(filtered.head(100), hide_index=True, use_container_width=True)
    st.download_button(
        "Download the filtered records as CSV",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="food_delivery_filtered.csv",
        mime="text/csv",
    )

st.markdown(
    "Dataset: [Zomato Delivery Operations — EDA & Dataset]("
    "https://huggingface.co/datasets/allenborochin/zomato_delivery_EDA), "
    "published by allenborochin on Hugging Face. The source data is already cleaned. "
    "Findings are descriptive and dataset-specific."
)

