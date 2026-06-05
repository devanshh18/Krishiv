"""Feature engineering for inference — mirrors the training pipeline."""

import math
import numpy as np


def calculate_vpd(air_temperature, humidity):
    """
    Calculate Vapor Pressure Deficit (VPD) using the Tetens formula.
    VPD tells us how much moisture the air can still absorb.
    Result is clamped between 0.2 and 2.5 kPa.
    """
    # Saturation vapor pressure (how much moisture air CAN hold at this temp)
    svp = 0.6108 * np.exp((17.27 * air_temperature) / (air_temperature + 237.3))

    # VPD = how much MORE moisture the air can hold
    vpd = svp * (1 - humidity / 100)

    # Keep it within realistic bounds
    return float(np.clip(vpd, 0.2, 2.5))


def fill_missing_values(data, preprocessor):
    """
    Replace any missing (None or NaN) sensor values with the
    median values from training data.

    This way the model always gets valid numbers even if a sensor fails.
    """
    # Get the medians that were calculated during training
    medians = preprocessor.get("imputer_medians", {})

    # Fallback defaults in case the preprocessor doesn't have medians
    defaults = {
        "air_temperature": 25.0, "humidity": 60.0, "co2_level": 900.0,
        "light_intensity": 18000.0, "soil_moisture": 45.0, "soil_ph": 6.4,
        "soil_temperature": 22.0, "ec_conductivity": 2.0,
        "nitrogen": 190.0, "phosphorus": 42.0, "potassium": 185.0,
        "vpd": 1.0, "light_hours": 12.0, "ventilation_rate": 40.0,
        "outside_temperature": 30.0, "outside_humidity": 50.0,
        "wind_speed": 8.0, "leaf_wetness_hours": 1.5,
        "previous_irrigation_mm": 50.0,
    }

    for key, default_value in defaults.items():
        value = data.get(key)
        is_missing = value is None or (isinstance(value, float) and math.isnan(value))
        if is_missing:
            data[key] = medians.get(key, default_value)

    return data


def prepare_features(sensor_data, preprocessor):
    """
    Convert raw sensor readings into feature arrays for the 3 models.

    This does the same feature engineering as train_models.py:
    1. Fill missing values
    2. Create 7 engineered features
    3. Encode growth stage and crop type
    4. Build numpy arrays in the exact order each model expects

    Returns (X_health, X_disease, X_irrigation) as numpy arrays.
    """
    data = sensor_data.copy()

    # Calculate VPD if not provided
    if data.get('vpd') is None:
        data['vpd'] = calculate_vpd(data['air_temperature'], data['humidity'])

    # Fill any missing sensor values
    data = fill_missing_values(data, preprocessor)

    # Create the same 7 engineered features as during training
    data['temp_differential'] = data['air_temperature'] - data['soil_temperature']

    data['heat_stress_index'] = max(data['air_temperature'] - 30, 0) * data['humidity'] / 100

    data['npk_balance'] = data['nitrogen'] / (data['phosphorus'] + data['potassium'] + 0.001)

    data['moisture_ec_ratio'] = data['soil_moisture'] / (data['ec_conductivity'] + 0.01)

    data['light_efficiency'] = data['light_intensity'] * data['light_hours'] / 1000

    data['drought_index'] = max(40 - data['soil_moisture'], 0) / 40

    data['humidity_co2_interaction'] = data['humidity'] * (data['co2_level'] / 1000)

    # Encode growth stage as a number (Seedling=1, Vegetative=2, etc.)
    stage_map = preprocessor['growth_stage_map']
    data['growth_stage_encoded'] = stage_map.get(data['growth_stage'], 3)

    # One-hot encode crop type (set matching crop column to 1, rest to 0)
    crop_type = data['crop_type']
    for col in preprocessor['crop_columns']:
        crop_name = col.replace('crop_', '')
        if crop_type == crop_name:
            data[col] = 1
        else:
            data[col] = 0

    # Build feature arrays in the exact order each model was trained on
    health_features = []
    for feature_name in preprocessor['model1_features']:
        health_features.append(data[feature_name])

    disease_features = []
    for feature_name in preprocessor['model2_features']:
        disease_features.append(data[feature_name])

    irrigation_features = []
    for feature_name in preprocessor['model3_features']:
        irrigation_features.append(data[feature_name])

    X_health = np.array([health_features])
    X_disease = np.array([disease_features])
    X_irrigation = np.array([irrigation_features])

    return X_health, X_disease, X_irrigation
