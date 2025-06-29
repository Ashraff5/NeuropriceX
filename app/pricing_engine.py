import pandas as pd
import csv
from datetime import datetime
import os

# Make sure logs folder exists
os.makedirs("logs", exist_ok=True)

# Load data at module level
events = pd.read_csv("data/events.csv")
users = pd.read_csv("data/users.csv")

def get_dynamic_price(data):
    event_id = data["event_id"]
    user_id = data["user_id"]
    time_to_event = data["time_to_event"]
    seat_tier = data["seat_tier"]
    demand = data["historical_demand"]

    # Debugging output (optional)
    print("EVENT ID RECEIVED:", event_id)
    print("USER ID RECEIVED:", user_id)
    print("ALL EVENT IDs:", events["event_id"].tolist())
    print("ALL USER IDs:", users["user_id"].tolist())

    # Validate presence of event_id and user_id
    event_match = events[events["event_id"] == event_id]
    user_match = users[users["user_id"] == user_id]

    if event_match.empty:
        return {"error": f"❌ Event ID '{event_id}' not found in dataset."}
    if user_match.empty:
        return {"error": f"❌ User ID '{user_id}' not found in dataset."}

    base_price = event_match["base_price"].iloc[0]
    loyalty = user_match["loyalty_score"].iloc[0]

    # Smart pricing logic
    tier_multiplier = {"Regular": 1.0, "Premium": 1.5, "VIP": 2.0}.get(seat_tier, 1.0)
    urgency = 1 / (time_to_event + 1)
    demand_factor = 1 + 0.4 * demand
    loyalty_boost = 1 + (loyalty / 100)

    final_price = base_price * tier_multiplier * (1 + urgency) * demand_factor * loyalty_boost
    # Define the explanation BEFORE logging or returning
    explanation = (
        f"Price increased due to {seat_tier} seat, "
        f"{'high' if demand > 0.6 else 'moderate'} demand, "
        f"{'low' if time_to_event < 3 else 'medium'} time remaining, "
        f"and user loyalty score of {loyalty}."
)
# Log the prediction before returning
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "event_id": event_id,
        "user_id": user_id,
        "time_to_event": time_to_event,
        "seat_tier": seat_tier,
        "historical_demand": demand,
        "loyalty_score": loyalty,
        "predicted_price": round(final_price, 2),
        "explanation": explanation
}

    log_file = "logs/predictions.csv"
    with open(log_file, mode="a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=log_entry.keys())
        if os.stat(log_file).st_size == 0:
            writer.writeheader()
        writer.writerow(log_entry)
    # Return the prediction and explanation
    print("Logged prediction to", log_file)
    return {
         "predicted_price": round(final_price, 2),
        "explanation": explanation
}




   

   
    



