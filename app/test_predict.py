import requests

payload = {
    "event_id": "E101",
    "user_id": "U001",
    "time_to_event": 3,
    "seat_tier": "VIP",
    "historical_demand": 0.84
}

response = requests.post("http://127.0.0.1:8000/predict", json=payload)
print(response.status_code)
print(response.json())
