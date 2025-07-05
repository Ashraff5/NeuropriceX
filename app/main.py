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

from sqlalchemy.orm import Session
from fastapi import Depends

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/history")
def get_prediction_history(
    limit: int = 100,
    user_id: Optional[str] = None,
    event_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(PredictionLog)

    if user_id:
        query = query.filter(PredictionLog.user_id == user_id)
    if event_id:
        query = query.filter(PredictionLog.event_id == event_id)

    logs = query.order_by(PredictionLog.timestamp.desc()).limit(limit).all()
    results = [log.__dict__ for log in logs]

    for r in results:
        r.pop("_sa_instance_state", None)

    return results

    
    # Apply optional filters
           
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
