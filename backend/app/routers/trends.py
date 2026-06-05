"""
GET /api/trends  — historical data for charts.
GET /api/latest  — most recent reading + prediction.
"""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.reading import SensorReading
from app.schemas.prediction import ReadingOut

router = APIRouter()


def average_readings(group: list[SensorReading], timestamp: datetime) -> ReadingOut:
    last_r = group[-1]
    
    # Calculate averages for numeric fields
    numeric_fields = [
        'air_temperature', 'humidity', 'co2_level', 'light_intensity',
        'soil_moisture', 'soil_ph', 'soil_temperature', 'ec_conductivity',
        'nitrogen', 'phosphorus', 'potassium', 'ventilation_rate',
        'outside_temperature', 'outside_humidity', 'wind_speed',
        'leaf_wetness_hours', 'previous_irrigation_mm', 'health_score',
        'disease_risk_score'
    ]
    
    avgs = {}
    for field in numeric_fields:
        vals = [getattr(r, field) for r in group if getattr(r, field) is not None]
        avgs[field] = sum(vals) / len(vals) if vals else 0.0
        
    return ReadingOut(
        id=last_r.id,
        timestamp=timestamp.isoformat() if timestamp else "",
        air_temperature=round(avgs['air_temperature'], 2),
        humidity=round(avgs['humidity'], 2),
        co2_level=round(avgs['co2_level'], 2),
        light_intensity=round(avgs['light_intensity'], 2),
        soil_moisture=round(avgs['soil_moisture'], 2),
        soil_ph=round(avgs['soil_ph'], 2),
        soil_temperature=round(avgs['soil_temperature'], 2),
        ec_conductivity=round(avgs['ec_conductivity'], 2),
        nitrogen=round(avgs['nitrogen'], 2),
        phosphorus=round(avgs['phosphorus'], 2),
        potassium=round(avgs['potassium'], 2),
        ventilation_rate=round(avgs['ventilation_rate'], 2),
        outside_temperature=round(avgs['outside_temperature'], 2),
        outside_humidity=round(avgs['outside_humidity'], 2),
        wind_speed=round(avgs['wind_speed'], 2),
        crop_type=last_r.crop_type or "",
        growth_stage=last_r.growth_stage or "",
        leaf_wetness_hours=round(avgs['leaf_wetness_hours'], 2),
        previous_irrigation_mm=round(avgs['previous_irrigation_mm'], 2),
        health_score=round(avgs['health_score'], 2) if avgs['health_score'] else None,
        health_category=last_r.health_category,
        disease_risk_score=round(avgs['disease_risk_score'], 2) if avgs['disease_risk_score'] else None,
        disease_risk_level=last_r.disease_risk_level,
        irrigation_need=last_r.irrigation_need,
    )


@router.get("/trends", response_model=list[ReadingOut])
async def get_trends(
    range: str = Query("hours", description="Trend range: minutes, hours, days"),
    db: Session = Depends(get_db),
):
    """
    Get historical sensor readings for the specified time range and resolution.

    Used by the frontend to render trend charts.
    """
    if range not in ["minutes", "hours", "days"]:
        range = "hours"

    now = datetime.now(timezone.utc)

    if range == "minutes":
        # Look back 60 minutes
        since = now - timedelta(minutes=60)
        readings = (
            db.query(SensorReading)
            .filter(SensorReading.timestamp >= since)
            .order_by(SensorReading.timestamp.asc())
            .all()
        )
        return [
            ReadingOut(
                id=r.id,
                timestamp=r.timestamp.isoformat() if r.timestamp else "",
                air_temperature=r.air_temperature,
                humidity=r.humidity,
                co2_level=r.co2_level,
                light_intensity=r.light_intensity,
                soil_moisture=r.soil_moisture,
                soil_ph=r.soil_ph,
                soil_temperature=r.soil_temperature,
                ec_conductivity=r.ec_conductivity,
                nitrogen=r.nitrogen,
                phosphorus=r.phosphorus,
                potassium=r.potassium,
                ventilation_rate=r.ventilation_rate,
                outside_temperature=r.outside_temperature,
                outside_humidity=r.outside_humidity,
                wind_speed=r.wind_speed,
                crop_type=r.crop_type,
                growth_stage=r.growth_stage,
                leaf_wetness_hours=r.leaf_wetness_hours,
                previous_irrigation_mm=r.previous_irrigation_mm,
                health_score=r.health_score,
                health_category=r.health_category,
                disease_risk_score=r.disease_risk_score,
                disease_risk_level=r.disease_risk_level,
                irrigation_need=r.irrigation_need,
            )
            for r in readings
        ]

    elif range == "hours":
        # Look back 24 hours
        since = now - timedelta(hours=24)
        readings = (
            db.query(SensorReading)
            .filter(SensorReading.timestamp >= since)
            .order_by(SensorReading.timestamp.asc())
            .all()
        )
        
        # Group by hour
        hourly_data = {}
        for r in readings:
            if not r.timestamp:
                continue
            # Truncate to hour
            key = r.timestamp.replace(minute=0, second=0, microsecond=0)
            if key not in hourly_data:
                hourly_data[key] = []
            hourly_data[key].append(r)
            
        result = []
        for key in sorted(hourly_data.keys()):
            group = hourly_data[key]
            result.append(average_readings(group, key))
        return result

    else:  # range == "days"
        # Look back 30 days
        since = now - timedelta(days=30)
        readings = (
            db.query(SensorReading)
            .filter(SensorReading.timestamp >= since)
            .order_by(SensorReading.timestamp.asc())
            .all()
        )
        
        # Group by day
        daily_data = {}
        for r in readings:
            if not r.timestamp:
                continue
            # Truncate to day
            key = r.timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
            if key not in daily_data:
                daily_data[key] = []
            daily_data[key].append(r)
            
        result = []
        for key in sorted(daily_data.keys()):
            group = daily_data[key]
            result.append(average_readings(group, key))
        return result


@router.get("/latest", response_model=ReadingOut | None)
async def get_latest(db: Session = Depends(get_db)):
    """
    Get the most recent sensor reading and its predictions.
    Returns null if no readings exist yet.
    """
    reading = (
        db.query(SensorReading)
        .order_by(desc(SensorReading.timestamp))
        .first()
    )

    if not reading:
        return None

    return ReadingOut(
        id=reading.id,
        timestamp=reading.timestamp.isoformat() if reading.timestamp else "",
        air_temperature=reading.air_temperature,
        humidity=reading.humidity,
        co2_level=reading.co2_level,
        light_intensity=reading.light_intensity,
        soil_moisture=reading.soil_moisture,
        soil_ph=reading.soil_ph,
        soil_temperature=reading.soil_temperature,
        ec_conductivity=reading.ec_conductivity,
        nitrogen=reading.nitrogen,
        phosphorus=reading.phosphorus,
        potassium=reading.potassium,
        ventilation_rate=reading.ventilation_rate,
        outside_temperature=reading.outside_temperature,
        outside_humidity=reading.outside_humidity,
        wind_speed=reading.wind_speed,
        crop_type=reading.crop_type,
        growth_stage=reading.growth_stage,
        leaf_wetness_hours=reading.leaf_wetness_hours,
        previous_irrigation_mm=reading.previous_irrigation_mm,
        health_score=reading.health_score,
        health_category=reading.health_category,
        disease_risk_score=reading.disease_risk_score,
        disease_risk_level=reading.disease_risk_level,
        irrigation_need=reading.irrigation_need,
    )
