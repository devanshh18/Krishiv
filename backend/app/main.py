"""Krishiv — Greenhouse Intelligence System API."""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.config import settings
from app.database import create_tables, get_db
from app.ml.engine import ml_engine
from app.models.reading import SensorReading
from app.schemas.prediction import PredictionResponse, Alert, ReadingOut
from app.rules.recommendations import generate_alerts_and_recommendations
from app.routers import predict, readings, trends, predict_disease, predict_irrigation
from app.simulator import simulator_loop

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app):
    """Runs on startup and shutdown."""

    # Startup
    logger.info("Starting Krishiv API...")

    logger.info("Creating database tables...")
    create_tables()

    logger.info("Loading ML models...")
    ml_engine.load_models()

    logger.info("Starting IoT simulator (60s interval)...")
    simulator_task = asyncio.create_task(simulator_loop())

    logger.info("=" * 50)
    logger.info("  Krishiv API is ready!")
    logger.info("  Docs: http://localhost:8000/docs")
    logger.info("=" * 50)

    yield

    # Shutdown
    logger.info("Shutting down...")
    simulator_task.cancel()
    try:
        await simulator_task
    except asyncio.CancelledError:
        pass
    logger.info("Goodbye.")


# Create the FastAPI app
app = FastAPI(
    title="Krishiv — Greenhouse Intelligence System",
    description="ML-powered API for greenhouse monitoring.",
    version="2.0.0",
    lifespan=lifespan,
)

# Allow frontend (localhost:5173) to make requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all route handlers
app.include_router(predict.router, prefix="/api", tags=["Predictions"])
app.include_router(predict_disease.router, prefix="/api", tags=["Disease"])
app.include_router(predict_irrigation.router, prefix="/api", tags=["Irrigation"])
app.include_router(readings.router, prefix="/api", tags=["Readings"])
app.include_router(trends.router, prefix="/api", tags=["Trends"])


@app.get("/api/latest-dashboard", tags=["Dashboard"])
async def get_latest_dashboard(db: Session = Depends(get_db)):
    """
    Get the most recent sensor reading with full ML predictions,
    health breakdown, alerts, and recommendations.
    The Dashboard page polls this endpoint every 60 seconds.
    """
    # Get the latest reading from the database
    reading = (
        db.query(SensorReading)
        .order_by(desc(SensorReading.timestamp))
        .first()
    )

    if not reading:
        return None

    # Build a sensor data dict from the database row
    sensor_data = {
        'air_temperature': reading.air_temperature,
        'humidity': reading.humidity,
        'co2_level': reading.co2_level,
        'light_intensity': reading.light_intensity,
        'soil_moisture': reading.soil_moisture,
        'soil_ph': reading.soil_ph,
        'soil_temperature': reading.soil_temperature,
        'ec_conductivity': reading.ec_conductivity,
        'nitrogen': reading.nitrogen,
        'phosphorus': reading.phosphorus,
        'potassium': reading.potassium,
        'ventilation_rate': reading.ventilation_rate,
        'outside_temperature': reading.outside_temperature,
        'outside_humidity': reading.outside_humidity,
        'wind_speed': reading.wind_speed,
        'crop_type': reading.crop_type,
        'growth_stage': reading.growth_stage,
        'leaf_wetness_hours': reading.leaf_wetness_hours,
        'previous_irrigation_mm': reading.previous_irrigation_mm,
        'light_hours': 12.0,
    }

    # Run all 3 ML models on this data
    results = ml_engine.predict_all(sensor_data)

    # Generate alerts and recommendations from the rule engine
    alerts, recommendations = generate_alerts_and_recommendations(
        sensor_data,
        results['health'],
        results['disease'],
        results['irrigation'],
    )

    # Convert alert dicts to Alert objects
    alert_objects = []
    for alert in alerts:
        alert_objects.append(Alert(**alert))

    return {
        "reading": {
            "id": reading.id,
            "timestamp": reading.timestamp.isoformat() if reading.timestamp else "",
            **sensor_data,
        },
        "health": results['health'],
        "disease": results['disease'],
        "irrigation": results['irrigation'],
        "alerts": alert_objects,
        "recommendations": recommendations,
    }


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "name": "Krishiv — Greenhouse Intelligence System",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
    }
