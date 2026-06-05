"""SensorReading ORM model."""

from datetime import datetime

from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.sql import func

from app.database import Base


class SensorReading(Base):
    """Stores a greenhouse sensor snapshot + prediction results."""

    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Sensor readings
    air_temperature = Column(Float)
    humidity = Column(Float)
    co2_level = Column(Float)
    light_intensity = Column(Float)
    soil_moisture = Column(Float)
    soil_ph = Column(Float)
    soil_temperature = Column(Float)
    ec_conductivity = Column(Float)
    nitrogen = Column(Float)
    phosphorus = Column(Float)
    potassium = Column(Float)
    ventilation_rate = Column(Float)
    outside_temperature = Column(Float)
    outside_humidity = Column(Float)
    wind_speed = Column(Float)
    crop_type = Column(String(50))
    growth_stage = Column(String(50))
    leaf_wetness_hours = Column(Float)
    previous_irrigation_mm = Column(Float)

    # Prediction results (stored alongside sensor data)
    health_score = Column(Float)
    health_category = Column(String(20))
    disease_risk_score = Column(Float)
    disease_risk_level = Column(String(20))
    irrigation_need = Column(String(20))

    def __repr__(self):
        return (
            f"<SensorReading(id={self.id}, "
            f"temp={self.air_temperature}, "
            f"health={self.health_score})>"
        )
