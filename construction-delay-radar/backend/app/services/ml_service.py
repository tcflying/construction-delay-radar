from app.schemas.prediction import PredictionRequest, PredictionResponse, RiskFactor
from app.services.ml_model import MLModel


class MLService:
    def __init__(self):
        self.model = MLModel()

    async def predict(self, request: PredictionRequest) -> PredictionResponse:
        features = [
            request.progress_percent / 100.0,
            request.weather_delays_days / 30.0,
            request.resource_shortage_score,
            request.supply_chain_score,
            request.historical_performance,
        ]

        delay, confidence = self.model.predict_delay(features)
        factors = self._compute_factors(request, delay)
        risk_level = self._compute_risk_level(delay, confidence)
        recommendations = self._compute_recommendations(risk_level, factors)

        return PredictionResponse(
            predicted_delay_days=int(delay),
            confidence=round(confidence, 2),
            risk_level=risk_level,
            factors=factors,
            recommendations=recommendations,
        )

    def _compute_factors(self, request: PredictionRequest, delay: float):
        total = (
            request.weather_delays_days * 0.35
            + request.resource_shortage_score * 0.25 * 30
            + request.supply_chain_score * 0.20 * 30
        )
        return [
            RiskFactor(name="weather", impact=round(request.weather_delays_days * 0.35 / max(total, 1), 2)),
            RiskFactor(name="resource_shortage", impact=round(request.resource_shortage_score * 0.25 / max(total, 1), 2)),
            RiskFactor(name="supply_chain", impact=round(request.supply_chain_score * 0.20 / max(total, 1), 2)),
        ]

    def _compute_risk_level(self, delay: float, confidence: float) -> str:
        if delay > 20 or (delay > 10 and confidence > 0.85):
            return "HIGH"
        elif delay > 7:
            return "MEDIUM"
        return "LOW"

    def _compute_recommendations(self, risk_level: str, factors: list):
        recs = []
        if risk_level == "HIGH":
            recs.append("Add 2-week buffer to timeline")
            recs.append("Source alternative suppliers for critical materials")
        elif risk_level == "MEDIUM":
            recs.append("Monitor weather forecasts closely")
            recs.append("Review resource allocation")
        return recs
