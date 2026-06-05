"""
Pydantic schema for disease-only prediction input.
Accepts only the 13 raw fields required by the disease risk model.
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field


class DiseaseInput(BaseModel):
    """Validates input data for disease risk prediction only."""

    # Climate
    air_temperature: float = Field(..., ge=0, le=50, description="Air temperature in Celsius")
    humidity: float = Field(..., ge=0, le=100, description="Relative humidity %")
    co2_level: float = Field(..., ge=200, le=2000, description="CO2 in ppm")
    vpd: Optional[float] = Field(None, ge=0, le=5, description="VPD in kPa (auto-calculated if omitted)")
    ventilation_rate: float = Field(..., ge=0, le=100, description="Ventilation opening %")

    # Moisture
    soil_moisture: float = Field(..., ge=0, le=100, description="Soil moisture %")
    leaf_wetness_hours: float = Field(0, ge=0, le=24, description="Leaf wetness hours")

    # External
    outside_temperature: float = Field(..., ge=-10, le=55, description="Outside temperature in Celsius")
    outside_humidity: float = Field(..., ge=0, le=100, description="Outside humidity %")
    wind_speed: float = Field(..., ge=0, le=50, description="Wind speed in km/h")

    # Crop Info
    crop_type: Literal["Tomato", "Cucumber", "Capsicum", "Lettuce", "Chili", "Herbs"] = Field(
        ..., description="Crop type"
    )
    growth_stage: Literal["Seedling", "Vegetative", "Flowering", "Fruiting", "Harvest"] = Field(
        ..., description="Growth stage"
    )

    model_config = {"json_schema_extra": {
        "examples": [{
            "air_temperature": 28.0, "humidity": 88.0, "co2_level": 650,
            "ventilation_rate": 8, "soil_moisture": 72.0,
            "leaf_wetness_hours": 8.0, "outside_temperature": 32.0,
            "outside_humidity": 80.0, "wind_speed": 3.0,
            "crop_type": "Tomato", "growth_stage": "Flowering",
        }]
    }}
