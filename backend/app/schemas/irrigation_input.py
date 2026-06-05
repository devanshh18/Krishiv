"""
Pydantic schema for irrigation-only prediction input.
Accepts only the 12 raw fields required by the irrigation model.
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field


class IrrigationInput(BaseModel):
    """Validates input data for irrigation advisory prediction only."""

    # Soil
    soil_moisture: float = Field(..., ge=0, le=100, description="Soil moisture %")
    soil_ph: float = Field(..., ge=3.0, le=10.0, description="Soil pH value")
    ec_conductivity: float = Field(..., ge=0, le=10, description="EC in mS/cm")

    # Climate
    air_temperature: float = Field(..., ge=0, le=50, description="Air temperature in Celsius")
    humidity: float = Field(..., ge=0, le=100, description="Relative humidity %")
    vpd: Optional[float] = Field(None, ge=0, le=5, description="VPD in kPa (auto-calculated if omitted)")

    # External
    outside_temperature: float = Field(..., ge=-10, le=55, description="Outside temperature in Celsius")
    wind_speed: float = Field(..., ge=0, le=50, description="Wind speed in km/h")

    # Irrigation History
    previous_irrigation_mm: float = Field(0, ge=0, le=200, description="Previous irrigation in mm")

    # Crop Info
    crop_type: Literal["Tomato", "Cucumber", "Capsicum", "Lettuce", "Chili", "Herbs"] = Field(
        ..., description="Crop type"
    )
    growth_stage: Literal["Seedling", "Vegetative", "Flowering", "Fruiting", "Harvest"] = Field(
        ..., description="Growth stage"
    )

    model_config = {"json_schema_extra": {
        "examples": [{
            "soil_moisture": 22.0, "soil_ph": 6.3, "ec_conductivity": 2.1,
            "air_temperature": 32.0, "humidity": 40.0,
            "outside_temperature": 36.0, "wind_speed": 12.0,
            "previous_irrigation_mm": 15.0,
            "crop_type": "Tomato", "growth_stage": "Fruiting",
        }]
    }}
