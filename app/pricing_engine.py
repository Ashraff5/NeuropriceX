import pandas as pd
from datetime import datetime
import os
from db import PredictionLog, SessionLocal
from sqlalchemy.exc import SQLAlchemyError

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

events_path = os.path.join(BASE_DIR, "data", "events.csv")
users_path = os.path.join(BASE_DIR, "data", "users.csv")

events = pd.read_csv(events_path)
users = pd.read_csv(users_path)

def log_prediction_to_db(log_entry):
    session = None
    try:
        session = SessionLocal()
        prediction = PredictionLog(**log_entry)
        session.add(prediction)
        session.commit()
        print("✅ Prediction logged to database.")
    except SQLAlchemyError as e:
        if session:
            session.rollback()
        print("❌ Failed to log prediction:", e)
    finally:
        if session:
            session.close()

def get_dynamic_price(data):
    event_id = data["event_id"]
    user_id = data["user_id"]
    time_to_event = data["time_to_event"]
    seat_tier = data["seat_tier"]
    demand = data["historical_demand"]

    # Validate inputs
    event_match = events[events["event_id"] == event_id]
    user_match = users[users["user_id"] == user_id]

    if event_match.empty:
        return {"error": f"❌ Event ID '{event_id}' not found in dataset."}
    if user_match.empty:
        return {"error": f"❌ User ID '{user_id}' not found in dataset."}

    base_price = event_match["base_price"].iloc[0]
    loyalty = user_match["loyalty_score"].iloc[0]

    # Pricing formula
    tier_multiplier = {"Regular": 1.0, "Premium": 1.5, "VIP": 2.0}.get(seat_tier, 1.0)
    urgency = 1 / (time_to_event + 1)
    demand_factor = 1 + 0.4 * demand
    loyalty_boost = 1 + (loyalty / 100)

    final_price = round(base_price * tier_multiplier * (1 + urgency) * demand_factor * loyalty_boost, 2)

    explanation = (
        f"Price increased due to {seat_tier} seat, "
        f"{'high' if demand > 0.6 else 'moderate'} demand, "
        f"{'low' if time_to_event < 3 else 'medium'} time remaining, "
        f"and user loyalty score of {loyalty}."
    )

    # Build log entry
    log_entry = {
        "timestamp": datetime.utcnow(),
        "event_id": event_id,
        "user_id": user_id,
        "time_to_event": time_to_event,
        "seat_tier": seat_tier,
        "historical_demand": demand,
        "loyalty_score": loyalty,
        "predicted_price": final_price,
        "explanation": explanation
    }

    # Log to DB
    log_prediction_to_db(log_entry)

    return {
        "predicted_price": final_price,
        "explanation": explanation
    }