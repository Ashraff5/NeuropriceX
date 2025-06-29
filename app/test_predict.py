import requests

url = "http://127.0.0.1:8000/predict"

payload = {
    "event_id": "E101",
    "user_id": "U001",
    "time_to_event": 3,
    "seat_tier": "VIP",
    "historical_demand": 0.85
}

response = requests.post(url, json=payload)

print("STATUS CODE:", response.status_code)
print("RESPONSE:", response.json())