"""
Pydantic schemas for sensor data input validation.
"""

from typing import Literal
from pydantic import BaseModel, Field


class SensorInput(BaseModel):
    """Validates incoming sensor data from the frontend/API client."""

    air_temperature: float = Field(..., ge=0, le=50, description="Air temperature in Celsius")
    humidity: float = Field(..., ge=0, le=100, description="Relative humidity %")
    co2_level: float = Field(..., ge=200, le=2000, description="CO2 in ppm")
    light_intensity: float = Field(..., ge=0, le=50000, description="Light intensity in lux")
    soil_moisture: float = Field(..., ge=0, le=100, description="Soil moisture %")
    soil_ph: float = Field(..., ge=3.0, le=10.0, description="Soil pH value")
    soil_temperature: float = Field(..., ge=0, le=45, description="Soil temperature in Celsius")
    ec_conductivity: float = Field(..., ge=0, le=10, description="EC in mS/cm")
    nitrogen: float = Field(..., ge=0, le=500, description="Nitrogen in mg/kg")
    phosphorus: float = Field(..., ge=0, le=200, description="Phosphorus in mg/kg")
    potassium: float = Field(..., ge=0, le=500, description="Potassium in mg/kg")
    vpd: float = Field(None, ge=0, le=5, description="VPD in kPa (auto-calculated if omitted)")
    light_hours: float = Field(12.0, ge=0, le=24, description="Light hours per day")
    ventilation_rate: float = Field(..., ge=0, le=100, description="Ventilation opening %")
    outside_temperature: float = Field(..., ge=-10, le=55, description="Outside temperature in Celsius")
    outside_humidity: float = Field(..., ge=0, le=100, description="Outside humidity %")
    wind_speed: float = Field(..., ge=0, le=50, description="Wind speed in km/h")
    crop_type: Literal["Tomato", "Cucumber", "Capsicum", "Lettuce", "Chili", "Herbs"] = Field(
        ..., description="Crop type"
    )
    growth_stage: Literal["Seedling", "Vegetative", "Flowering", "Fruiting", "Harvest"] = Field(
        ..., description="Growth stage"
    )
    leaf_wetness_hours: float = Field(0, ge=0, le=24, description="Leaf wetness hours")
    previous_irrigation_mm: float = Field(0, ge=0, le=200, description="Previous irrigation in mm")

    model_config = {"json_schema_extra": {
        "examples": [{
            "air_temperature": 24.0, "humidity": 60.0, "co2_level": 1000,
            "light_intensity": 22000, "soil_moisture": 50.0, "soil_ph": 6.5,
            "soil_temperature": 21.0, "ec_conductivity": 2.0,
            "nitrogen": 200, "phosphorus": 45, "potassium": 200,
            "vpd": 1.0, "light_hours": 14, "ventilation_rate": 50,
            "outside_temperature": 30.0, "outside_humidity": 45.0,
            "wind_speed": 8.0, "crop_type": "Tomato", "growth_stage": "Flowering",
            "leaf_wetness_hours": 1.0, "previous_irrigation_mm": 60.0,
        }]
    }}
