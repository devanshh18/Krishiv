"""
POST /api/predict/disease — runs only the disease risk model.
"""

from fastapi import APIRouter

from app.schemas.disease_input import DiseaseInput
from app.schemas.prediction import DiseaseResult, Alert
from app.ml.engine import ml_engine
from app.rules.recommendations import generate_disease_recommendations

router = APIRouter()


@router.post("/predict/disease")
async def predict_disease(disease_input: DiseaseInput):
    """
    Run the disease risk model on the provided sensor data.

    Returns disease risk score, risk level, warnings,
    plus disease-specific alerts and recommendations.
    """
    sensor_data = disease_input.model_dump()

    # Auto-calculate VPD if not provided (needed by recommendations)
    if sensor_data.get('vpd') is None:
        from app.ml.feature_eng import calculate_vpd
        sensor_data['vpd'] = calculate_vpd(
            sensor_data['air_temperature'], sensor_data['humidity']
        )

    # Run disease prediction
    disease_result = ml_engine.predict_disease_only(sensor_data)

    # Generate disease-focused alerts and recommendations
    alerts, recommendations = generate_disease_recommendations(
        sensor_data, disease_result
    )

    return {
        "disease": disease_result,
        "alerts": [Alert(**a) for a in alerts],
        "recommendations": recommendations,
    }
