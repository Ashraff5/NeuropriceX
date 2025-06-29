from fastapi import FastAPI
from app.pricing_engine import get_dynamic_price

app = FastAPI()

@app.get("/")
def root():
    return {"message": "NeuroPriceX API is live 🚀"}

@app.post("/predict")
def predict_price(data: dict):
    return get_dynamic_price(data)
