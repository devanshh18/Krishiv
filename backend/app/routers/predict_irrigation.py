"""
POST /api/predict/irrigation — runs only the irrigation model.
"""

from fastapi import APIRouter

from app.schemas.irrigation_input import IrrigationInput
from app.schemas.prediction import IrrigationResult, Alert
from app.ml.engine import ml_engine
from app.rules.recommendations import generate_irrigation_recommendations

router = APIRouter()


@router.post("/predict/irrigation")
async def predict_irrigation(irrigation_input: IrrigationInput):
    """
    Run the irrigation model on the provided sensor data.

    Returns irrigation need level, recommendation,
    plus irrigation-specific alerts and recommendations.
    """
    sensor_data = irrigation_input.model_dump()

    # Auto-calculate VPD if not provided (needed by ML engine)
    if sensor_data.get('vpd') is None:
        from app.ml.feature_eng import calculate_vpd
        sensor_data['vpd'] = calculate_vpd(
            sensor_data['air_temperature'], sensor_data['humidity']
        )

    # Run irrigation prediction
    irrigation_result = ml_engine.predict_irrigation_only(sensor_data)

    # Generate irrigation-focused alerts and recommendations
    alerts, recommendations = generate_irrigation_recommendations(
        sensor_data, irrigation_result
    )

    return {
        "irrigation": irrigation_result,
        "alerts": [Alert(**a) for a in alerts],
        "recommendations": recommendations,
    }
