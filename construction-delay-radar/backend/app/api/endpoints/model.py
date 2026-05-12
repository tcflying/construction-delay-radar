from fastapi import APIRouter

router = APIRouter()


@router.get("/model/info")
async def model_info():
    return {
        "version": "xgboost-v1.0.3",
        "algorithm": "XGBoost",
        "model_type": "rule-based (MVP)",
        "features": [
            "progress_percent",
            "weather_delays_days",
            "resource_shortage_score",
            "supply_chain_score",
            "historical_performance"
        ],
        "status": "production"
    }
