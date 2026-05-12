from fastapi import APIRouter, HTTPException

from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.services.ml_service import MLService

router = APIRouter()
ml_service = MLService()


@router.post("/", response_model=PredictionResponse)
async def predict_delay(request: PredictionRequest):
    try:
        return await ml_service.predict(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.get("/factors")
async def get_risk_factors():
    return {
        "factors": [
            {"id": "weather", "name": "Weather Delays", "weight": 0.35},
            {"id": "resource_shortage", "name": "Resource Shortage", "weight": 0.25},
            {"id": "supply_chain", "name": "Supply Chain", "weight": 0.20},
            {"id": "labor", "name": "Labor Availability", "weight": 0.15},
            {"id": "design_changes", "name": "Design Changes", "weight": 0.05},
        ]
    }
