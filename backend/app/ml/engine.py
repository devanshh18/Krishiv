"""ML Engine — loads trained models and runs predictions."""

import os
import logging

import joblib
import numpy as np

from app.config import settings
from app.ml.feature_eng import prepare_features, calculate_vpd
from app.schemas.prediction import (
    HealthResult, DiseaseResult, IrrigationResult,
    ParameterBreakdown,
)

logger = logging.getLogger(__name__)


class MLEngine:
    """Loads .pkl models at startup and runs predictions."""

    def __init__(self):
        self.health_model = None
        self.disease_model = None
        self.irrigation_model = None
        self.preprocessor = None
        self.loaded = False

    def load_models(self):
        """Load all 3 models and the preprocessor from disk."""
        model_dir = settings.model_dir_abs
        logger.info(f"Loading ML models from: {model_dir}")

        self.health_model = joblib.load(os.path.join(model_dir, 'health_model.pkl'))
        self.disease_model = joblib.load(os.path.join(model_dir, 'disease_model.pkl'))
        self.irrigation_model = joblib.load(os.path.join(model_dir, 'irrigation_model.pkl'))
        self.preprocessor = joblib.load(os.path.join(model_dir, 'preprocessor.pkl'))

        self.loaded = True
        logger.info("All 3 ML models + preprocessor loaded successfully")

    def predict_all(self, sensor_data):
        """Run all 3 models on the sensor data and return results."""
        if not self.loaded:
            raise RuntimeError("Models not loaded. Call load_models() first.")

        # Calculate VPD if not already provided
        if sensor_data.get('vpd') is None:
            sensor_data['vpd'] = calculate_vpd(
                sensor_data['air_temperature'], sensor_data['humidity']
            )

        # Convert raw sensor dict into feature arrays for each model
        X_health, X_disease, X_irrigation = prepare_features(sensor_data, self.preprocessor)

        # Run each model
        health_score = float(np.clip(self.health_model.predict(X_health)[0], 0, 100))
        disease_risk = float(np.clip(self.disease_model.predict(X_disease)[0], 0, 100))
        irrigation_index = int(self.irrigation_model.predict(X_irrigation)[0])

        # Convert irrigation number back to text label (0=High, 1=Low, 2=Medium)
        irrigation_classes = self.preprocessor['label_encoder_classes']
        irrigation_need = irrigation_classes[irrigation_index]

        # Build detailed result objects
        health_result = self.build_health_result(sensor_data, health_score)
        disease_result = self.build_disease_result(sensor_data, disease_risk)
        irrigation_result = self.build_irrigation_result(sensor_data, irrigation_need)

        return {
            'health': health_result,
            'disease': disease_result,
            'irrigation': irrigation_result,
        }

    def predict_disease_only(self, sensor_data):
        """Run only the disease model. Fills default values for missing fields."""
        if not self.loaded:
            raise RuntimeError("Models not loaded. Call load_models() first.")

        data = sensor_data.copy()

        # Calculate VPD if not provided
        if data.get('vpd') is None:
            data['vpd'] = calculate_vpd(data['air_temperature'], data['humidity'])

        # The disease form only asks for ~11 fields, but the model needs
        # all features. Fill the rest with safe neutral values.
        data.setdefault('light_intensity', 20000)
        data.setdefault('soil_ph', 6.5)
        data.setdefault('soil_temperature', data['air_temperature'] - 3)
        data.setdefault('ec_conductivity', 2.0)
        data.setdefault('nitrogen', 200)
        data.setdefault('phosphorus', 45)
        data.setdefault('potassium', 200)
        data.setdefault('light_hours', 12)
        data.setdefault('previous_irrigation_mm', 50)

        _, X_disease, _ = prepare_features(data, self.preprocessor)
        disease_risk = float(np.clip(self.disease_model.predict(X_disease)[0], 0, 100))
        return self.build_disease_result(data, disease_risk)

    def predict_irrigation_only(self, sensor_data):
        """Run only the irrigation model. Fills default values for missing fields."""
        if not self.loaded:
            raise RuntimeError("Models not loaded. Call load_models() first.")

        data = sensor_data.copy()

        # Calculate VPD if not provided
        if data.get('vpd') is None:
            data['vpd'] = calculate_vpd(data['air_temperature'], data['humidity'])

        # Fill defaults for fields not in the irrigation input form
        data.setdefault('co2_level', 1000)
        data.setdefault('light_intensity', 20000)
        data.setdefault('soil_temperature', data['air_temperature'] - 3)
        data.setdefault('nitrogen', 200)
        data.setdefault('phosphorus', 45)
        data.setdefault('potassium', 200)
        data.setdefault('light_hours', 12)
        data.setdefault('ventilation_rate', 40)
        data.setdefault('outside_humidity', 50)
        data.setdefault('leaf_wetness_hours', 2)

        _, _, X_irrigation = prepare_features(data, self.preprocessor)
        irrigation_index = int(self.irrigation_model.predict(X_irrigation)[0])
        irrigation_classes = self.preprocessor['label_encoder_classes']
        irrigation_need = irrigation_classes[irrigation_index]
        return self.build_irrigation_result(data, irrigation_need)

    # --- Health Result ---

    def build_health_result(self, data, score):
        """Create health result with category and per-parameter breakdown."""
        # Determine category from score
        if score >= 80:
            category = "Excellent"
        elif score >= 70:
            category = "Good"
        elif score >= 60:
            category = "Moderate"
        elif score >= 50:
            category = "Fair"
        else:
            category = "Poor"

        breakdown = self.get_health_breakdown(data)
        return HealthResult(score=round(score, 1), category=category, breakdown=breakdown)

    def get_health_breakdown(self, data):
        """
        Score each sensor parameter individually.
        Each parameter has an optimal range, suboptimal range, and poor range.
        Points are awarded based on where the value falls.
        """
        breakdown = {}

        # Air Temperature (max 15 points)
        temp = data['air_temperature']
        if 20 <= temp <= 28:
            points, status = 15, "optimal"
        elif 16 <= temp < 20 or 28 < temp <= 32:
            points, status = 10, "suboptimal"
        else:
            points, status = 5, "poor"
        breakdown['air_temperature'] = ParameterBreakdown(
            value=temp, status=status, points=points, max_points=15)

        # Humidity (max 12 points)
        hum = data['humidity']
        if 50 <= hum <= 70:
            points, status = 12, "optimal"
        elif 40 <= hum < 50 or 70 < hum <= 80:
            points, status = 8, "suboptimal"
        else:
            points, status = 4, "poor"
        breakdown['humidity'] = ParameterBreakdown(
            value=hum, status=status, points=points, max_points=12)

        # CO2 Level (max 12 points)
        co2 = data['co2_level']
        if 800 <= co2 <= 1200:
            points, status = 12, "optimal"
        elif 400 <= co2 < 800 or 1200 < co2 <= 1500:
            points, status = 8, "suboptimal"
        else:
            points, status = 4, "poor"
        breakdown['co2_level'] = ParameterBreakdown(
            value=co2, status=status, points=points, max_points=12)

        # Light Intensity (max 10 points)
        light = data['light_intensity']
        if 15000 <= light <= 30000:
            points, status = 10, "optimal"
        elif 10000 <= light < 15000 or 30000 < light <= 45000:
            points, status = 7, "suboptimal"
        else:
            points, status = 3, "poor"
        breakdown['light_intensity'] = ParameterBreakdown(
            value=light, status=status, points=points, max_points=10)

        # Soil Moisture (max 10 points)
        moisture = data['soil_moisture']
        if 40 <= moisture <= 60:
            points, status = 10, "optimal"
        elif 30 <= moisture < 40 or 60 < moisture <= 70:
            points, status = 7, "suboptimal"
        else:
            points, status = 3, "poor"
        breakdown['soil_moisture'] = ParameterBreakdown(
            value=moisture, status=status, points=points, max_points=10)

        # Soil pH (max 10 points)
        ph = data['soil_ph']
        if 6.0 <= ph <= 6.8:
            points, status = 10, "optimal"
        elif 5.5 <= ph < 6.0 or 6.8 < ph <= 7.5:
            points, status = 7, "suboptimal"
        else:
            points, status = 3, "poor"
        breakdown['soil_ph'] = ParameterBreakdown(
            value=ph, status=status, points=points, max_points=10)

        # Soil Temperature (max 8 points)
        soil_temp = data['soil_temperature']
        if 18 <= soil_temp <= 24:
            points, status = 8, "optimal"
        elif 15 <= soil_temp < 18 or 24 < soil_temp <= 28:
            points, status = 5, "suboptimal"
        else:
            points, status = 2, "poor"
        breakdown['soil_temperature'] = ParameterBreakdown(
            value=soil_temp, status=status, points=points, max_points=8)

        # EC Conductivity (max 8 points)
        ec = data['ec_conductivity']
        if 1.5 <= ec <= 2.5:
            points, status = 8, "optimal"
        elif 1.0 <= ec < 1.5 or 2.5 < ec <= 3.5:
            points, status = 5, "suboptimal"
        else:
            points, status = 2, "poor"
        breakdown['ec_conductivity'] = ParameterBreakdown(
            value=ec, status=status, points=points, max_points=8)

        # VPD (max 8 points)
        vpd = data.get('vpd', 1.0)
        if 0.8 <= vpd <= 1.2:
            points, status = 8, "optimal"
        elif 0.5 <= vpd < 0.8 or 1.2 < vpd <= 1.5:
            points, status = 5, "suboptimal"
        else:
            points, status = 2, "poor"
        breakdown['vpd'] = ParameterBreakdown(
            value=vpd, status=status, points=points, max_points=8)

        # NPK Balance (max 7 points) — count how many nutrients are in range
        n_val = data['nitrogen']
        p_val = data['phosphorus']
        k_val = data['potassium']

        in_range_count = 0
        if 150 <= n_val <= 250:
            in_range_count += 1
        if 30 <= p_val <= 60:
            in_range_count += 1
        if 150 <= k_val <= 250:
            in_range_count += 1

        if in_range_count == 3:
            points, status = 7, "optimal"
        elif in_range_count == 2:
            points, status = 5, "suboptimal"
        elif in_range_count == 1:
            points, status = 3, "poor"
        else:
            points, status = 1, "poor"

        npk_ratio = round(n_val / (p_val + k_val + 0.001), 2)
        breakdown['npk_balance'] = ParameterBreakdown(
            value=npk_ratio, status=status, points=points, max_points=7)

        return breakdown

    # --- Disease Result ---

    def build_disease_result(self, data, risk_score):
        """Create disease result with risk level and warnings."""
        # Determine risk level from score
        if risk_score >= 75:
            risk_level = "Critical"
        elif risk_score >= 60:
            risk_level = "High"
        elif risk_score >= 40:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        # Generate specific disease warnings based on sensor conditions
        warnings = []

        if data['humidity'] > 80 and data.get('vpd', 1.0) < 0.5:
            warnings.append(
                f"High risk of Powdery Mildew — humidity {data['humidity']:.0f}% with low VPD"
            )

        if data['humidity'] > 85 and data['leaf_wetness_hours'] > 6:
            warnings.append(
                f"High risk of Botrytis (gray mold) — humidity {data['humidity']:.0f}% "
                f"with {data['leaf_wetness_hours']:.0f}h leaf wetness"
            )

        if data['soil_moisture'] > 70:
            warnings.append(
                f"Root rot risk — soil moisture at {data['soil_moisture']:.0f}%"
            )

        if data['ventilation_rate'] < 10 and data['humidity'] > 75:
            warnings.append(
                "Poor ventilation with high humidity — fungal spread likely"
            )

        if risk_score >= 60 and len(warnings) == 0:
            warnings.append("Elevated disease risk — monitor crops closely")

        return DiseaseResult(
            risk_score=round(risk_score, 1),
            risk_level=risk_level,
            warnings=warnings,
        )

    # --- Irrigation Result ---

    def build_irrigation_result(self, data, need):
        """Create irrigation result with a recommendation message."""
        soil_moisture = data['soil_moisture']

        if need == 'High':
            recommendation = f"Irrigate immediately — soil moisture at {soil_moisture:.0f}%"
        elif need == 'Medium':
            recommendation = f"Irrigate within 2-3 hours — soil moisture at {soil_moisture:.0f}%"
        else:
            recommendation = f"No irrigation needed — soil moisture sufficient at {soil_moisture:.0f}%"

        return IrrigationResult(need=need, recommendation=recommendation)


# Create a single instance that the whole app uses
ml_engine = MLEngine()
