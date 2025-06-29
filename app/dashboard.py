# app/dashboard.py

import streamlit as st
import requests
import pandas as pd
import altair as alt

st.set_page_config(page_title="NeuroPriceX Dashboard", layout="wide")
st.title("🎟️ NeuroPriceX — Smart Ticket Pricing")
# --- Sidebar filters ---
st.sidebar.header("🔍 Filter Logs")
selected_user = st.sidebar.text_input("Filter by User ID (optional)", value="")
selected_event = st.sidebar.text_input("Filter by Event ID (optional)", value="")

# ------------------------------
# Smart Price Simulator 🔮
# ------------------------------
st.subheader("💡 Smart Price Simulator")

with st.form("predict_form"):
    event_id = st.text_input("Event ID", value="E101")
    user_id = st.text_input("User ID", value="U001")
    time_to_event = st.slider("⏳ Days until event", 0, 30, 3)
    seat_tier = st.selectbox("🎫 Seat Tier", ["Regular", "Premium", "VIP"])
    historical_demand = st.slider("🔥 Historical Demand", 0.0, 1.0, 0.85, step=0.05)

    submitted = st.form_submit_button("Predict Price")

if submitted:
    payload = {
        "event_id": event_id,
        "user_id": user_id,
        "time_to_event": time_to_event,
        "seat_tier": seat_tier,
        "historical_demand": historical_demand,
    }
    try:
        res = requests.post("http://localhost:8000/predict", json=payload).json()
        st.success(f"💰 Predicted Price: ₹{res['predicted_price']}")
        st.info(f"🧠 Explanation: {res['explanation']}")
    except Exception as e:
        st.error(f"Prediction failed: {e}")

# ------------------------------
# Recent Logs Table 📜
# ------------------------------
st.subheader("📜 Recent Predictions Log")

try:
    params = {"limit": 20}
    if selected_user:
        params["user_id"] = selected_user
    if selected_event:
        params["event_id"] = selected_event

    logs = requests.get("http://localhost:8000/history", params=params).json()
    df = pd.DataFrame(logs)
    st.dataframe(df)
except Exception as e:
    st.warning("Couldn’t load history. Is the server running?")

# ------------------------------
# Price by Seat Tier Chart 📈
# ------------------------------
st.subheader("📊 Price by Tier (from recent history)")

if not df.empty:
    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("seat_tier:N", title="Seat Tier"),
            y=alt.Y("predicted_price:Q", aggregate="mean", title="Avg Predicted Price"),
            tooltip=["seat_tier", "predicted_price"]
        )
        .properties(width=600, height=400)
    )
    st.altair_chart(chart)
else:
    st.write("No log data available for chart.")