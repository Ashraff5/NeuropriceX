from db import init_db, PredictionLog, SessionLocal
from fastapi import FastAPI
from pydantic import BaseModel
from pricing_engine import get_dynamic_price

app = FastAPI()
from db import init_db
init_db()

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend URL for tighter security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Input schema using Pydantic
class PredictionRequest(BaseModel):
    event_id: str
    user_id: str
    time_to_event: int
    seat_tier: str
    historical_demand: float

# 🚀 Health check endpoint
@app.get("/")
def root():
    return {"message": "NeuroPriceX API is live 🚀"}

# 🎯 Prediction endpoint
''' app.post("/predict")
def predict_price(payload: PredictionRequest):
    return get_dynamic_price(payload.model_dump()) '''


@app.post("/predict")
def predict_price(payload: PredictionRequest):
    try:
        return get_dynamic_price(payload.dict())
    except Exception as e:
        import traceback
        traceback.print_exc()  # Shows full error in terminal
        return {"error": str(e)}


from fastapi.responses import JSONResponse
import pandas as pd
import os
from typing import Optional


@app.get("/history")
@app.get("/history")
def get_prediction_history(
    limit: int = 20,
    user_id: Optional[str] = None,
    event_id: Optional[str] = None
):

    log_file = "logs/predictions.csv"
    if not os.path.exists(log_file):
        return {"message": "📭 No predictions have been logged yet."}
    
    df = pd.read_csv(log_file)
    
    # Apply optional filters
    if user_id:
        df = df[df["user_id"] == user_id]
    if event_id:
        df = df[df["event_id"] == event_id]

    df = df.sort_values("timestamp", ascending=False).head(limit)
    return JSONResponse(content=df.to_dict(orient="records"))
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
