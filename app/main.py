from fastapi import FastAPI
from app.pricing_engine import get_dynamic_price

app = FastAPI()

@app.get("/")
def root():
    return {"message": "NeuroPriceX API is live 🚀"}

@app.post("/predict")
def predict_price(request_data: dict):
    price = get_dynamic_price(request_data)
    return {"predicted_price": price}
