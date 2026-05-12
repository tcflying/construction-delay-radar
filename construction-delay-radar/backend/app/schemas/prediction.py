from pydantic import BaseModel, Field
from typing import List, Optional


class RiskFactor(BaseModel):
    name: str
    impact: float


class PredictionRequest(BaseModel):
    project_id: str
    progress_percent: int = Field(..., ge=0, le=100)
    weather_delays_days: float = Field(0, ge=0)
    resource_shortage_score: float = Field(..., ge=0, le=1)
    supply_chain_score: float = Field(..., ge=0, le=1)
    historical_performance: float = Field(..., ge=0, le=1)


class PredictionResponse(BaseModel):
    predicted_delay_days: int
    confidence: float = Field(..., ge=0, le=1)
    risk_level: str
    factors: List[RiskFactor]
    recommendations: List[str]
