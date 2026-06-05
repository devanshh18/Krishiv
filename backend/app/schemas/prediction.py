"""
Pydantic schemas for prediction response output.
"""

from typing import Optional
from pydantic import BaseModel


class ParameterBreakdown(BaseModel):
    """Health score breakdown for a single parameter."""
    value: float
    status: str  # "optimal", "suboptimal", "poor"
    points: int
    max_points: int


class HealthResult(BaseModel):
    """Health score prediction result."""
    score: float
    category: str  # Excellent/Good/Moderate/Fair/Poor
    breakdown: dict[str, ParameterBreakdown]


class DiseaseResult(BaseModel):
    """Disease risk prediction result."""
    risk_score: float
    risk_level: str  # Low/Medium/High/Critical
    warnings: list[str]


class IrrigationResult(BaseModel):
    """Irrigation need prediction result."""
    need: str  # Low/Medium/High
    recommendation: str


class Alert(BaseModel):
    """A single alert notification."""
    type: str  # "info", "warning", "danger"
    message: str


class PredictionResponse(BaseModel):
    """Full prediction response combining all 3 models + alerts."""
    health: HealthResult
    disease: DiseaseResult
    irrigation: IrrigationResult
    alerts: list[Alert]
    recommendations: list[str]


class ReadingStored(BaseModel):
    """Response after storing a sensor reading."""
    status: str
    id: int


class ReadingOut(BaseModel):
    """A sensor reading returned from the database."""
    id: int
    timestamp: str
    air_temperature: Optional[float] = None
    humidity: Optional[float] = None
    co2_level: Optional[float] = None
    light_intensity: Optional[float] = None
    soil_moisture: Optional[float] = None
    soil_ph: Optional[float] = None
    soil_temperature: Optional[float] = None
    ec_conductivity: Optional[float] = None
    nitrogen: Optional[float] = None
    phosphorus: Optional[float] = None
    potassium: Optional[float] = None
    ventilation_rate: Optional[float] = None
    outside_temperature: Optional[float] = None
    outside_humidity: Optional[float] = None
    wind_speed: Optional[float] = None
    crop_type: Optional[str] = None
    growth_stage: Optional[str] = None
    leaf_wetness_hours: Optional[float] = None
    previous_irrigation_mm: Optional[float] = None
    health_score: Optional[float] = None
    health_category: Optional[str] = None
    disease_risk_score: Optional[float] = None
    disease_risk_level: Optional[str] = None
    irrigation_need: Optional[str] = None

    model_config = {"from_attributes": True}
