"""
POST /api/predict — runs all 3 ML models + rule engine.
"""

from fastapi import APIRouter

from app.schemas.reading import SensorInput
from app.schemas.prediction import PredictionResponse, Alert
from app.ml.engine import ml_engine
from app.rules.recommendations import generate_alerts_and_recommendations

router = APIRouter()


@router.post("/predict", response_model=PredictionResponse)
async def predict(sensor_input: SensorInput):
    """
    Run all 3 ML models on the provided sensor data.

    Returns health score, disease risk, irrigation need,
    plus alerts and actionable recommendations.
    """
    # Convert Pydantic model to dict
    sensor_data = sensor_input.model_dump()

    # Run ML predictions
    results = ml_engine.predict_all(sensor_data)

    # Generate alerts and recommendations via rule engine
    alerts, recommendations = generate_alerts_and_recommendations(
        sensor_data,
        results['health'],
        results['disease'],
        results['irrigation'],
    )

    # Build response
    return PredictionResponse(
        health=results['health'],
        disease=results['disease'],
        irrigation=results['irrigation'],
        alerts=[Alert(**a) for a in alerts],
        recommendations=recommendations,
    )
