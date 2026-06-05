"""
POST /api/readings — store sensor snapshots in PostgreSQL.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.reading import SensorInput
from app.schemas.prediction import ReadingStored
from app.models.reading import SensorReading
from app.ml.engine import ml_engine

router = APIRouter()


@router.post("/readings", response_model=ReadingStored)
async def store_reading(sensor_input: SensorInput, db: Session = Depends(get_db)):
    """
    Store a sensor reading in the database along with prediction results.

    The reading is stored with the current timestamp and the prediction
    outputs from all 3 ML models.
    """
    sensor_data = sensor_input.model_dump()

    # Run predictions to store alongside sensor data
    results = ml_engine.predict_all(sensor_data)

    # Create ORM object
    reading = SensorReading(
        # Sensor fields
        air_temperature=sensor_data['air_temperature'],
        humidity=sensor_data['humidity'],
        co2_level=sensor_data['co2_level'],
        light_intensity=sensor_data['light_intensity'],
        soil_moisture=sensor_data['soil_moisture'],
        soil_ph=sensor_data['soil_ph'],
        soil_temperature=sensor_data['soil_temperature'],
        ec_conductivity=sensor_data['ec_conductivity'],
        nitrogen=sensor_data['nitrogen'],
        phosphorus=sensor_data['phosphorus'],
        potassium=sensor_data['potassium'],
        ventilation_rate=sensor_data['ventilation_rate'],
        outside_temperature=sensor_data['outside_temperature'],
        outside_humidity=sensor_data['outside_humidity'],
        wind_speed=sensor_data['wind_speed'],
        crop_type=sensor_data['crop_type'],
        growth_stage=sensor_data['growth_stage'],
        leaf_wetness_hours=sensor_data['leaf_wetness_hours'],
        previous_irrigation_mm=sensor_data['previous_irrigation_mm'],
        # Prediction results
        health_score=results['health'].score,
        health_category=results['health'].category,
        disease_risk_score=results['disease'].risk_score,
        disease_risk_level=results['disease'].risk_level,
        irrigation_need=results['irrigation'].need,
    )

    db.add(reading)
    db.commit()
    db.refresh(reading)

    return ReadingStored(status="stored", id=reading.id)
