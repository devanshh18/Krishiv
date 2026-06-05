"""
Trains three ML models on the greenhouse sensor dataset:
  1. Health Score      (regression, 0-100)
  2. Disease Risk      (regression, 0-100)
  3. Irrigation Need   (classification, Low/Medium/High)
"""

import os
import time
import warnings

import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    r2_score, mean_absolute_error, mean_squared_error,
    accuracy_score, f1_score, classification_report,
)
from sklearn.ensemble import (
    GradientBoostingRegressor,
    GradientBoostingClassifier,
)

warnings.filterwarnings("ignore", category=FutureWarning)

# Paths
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(ROOT, "data", "greenhouse_data.csv")
MODELS_DIR = os.path.join(ROOT, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

# All 19 raw sensor columns used as input features
BASE_FEATURES = [
    "air_temperature", "humidity", "co2_level", "light_intensity",
    "soil_moisture", "soil_ph", "soil_temperature", "ec_conductivity",
    "nitrogen", "phosphorus", "potassium", "vpd", "light_hours",
    "ventilation_rate", "outside_temperature", "outside_humidity",
    "wind_speed", "leaf_wetness_hours", "previous_irrigation_mm",
]

# Names of the 7 features we create from the raw ones
ENGINEERED_FEATURES = [
    "temp_differential", "heat_stress_index", "npk_balance",
    "moisture_ec_ratio", "light_efficiency", "drought_index",
    "humidity_co2_interaction",
]

# Growth stage mapped to numbers
STAGE_ORDER = {
    "Seedling": 1, "Vegetative": 2, "Flowering": 3,
    "Fruiting": 4, "Harvest": 5,
}


def add_engineered_features(df):
    """Create 7 new features from the raw sensor columns."""
    df = df.copy()

    # Difference between air and soil temperature
    df["temp_differential"] = df["air_temperature"] - df["soil_temperature"]

    # Heat stress: only counts when temp > 30, scaled by humidity
    above_30 = np.maximum(df["air_temperature"] - 30, 0)
    df["heat_stress_index"] = above_30 * df["humidity"] / 100

    # Ratio of nitrogen to (phosphorus + potassium)
    df["npk_balance"] = df["nitrogen"] / (df["phosphorus"] + df["potassium"] + 0.001)

    # Soil moisture relative to EC (salt concentration)
    df["moisture_ec_ratio"] = df["soil_moisture"] / (df["ec_conductivity"] + 0.01)

    # Total light energy = intensity * hours
    df["light_efficiency"] = df["light_intensity"] * df["light_hours"] / 1000

    # How dry the soil is (0 = moist enough, 1 = very dry)
    df["drought_index"] = np.maximum(40 - df["soil_moisture"], 0) / 40

    # Humidity and CO2 interaction (affects photosynthesis)
    df["humidity_co2_interaction"] = df["humidity"] * (df["co2_level"] / 1000)

    # Convert growth stage text to numbers (1-5)
    df["growth_stage_encoded"] = df["growth_stage"].map(STAGE_ORDER)

    # One-hot encode crop type (drop first to avoid dummy variable trap)
    crop_dummies = pd.get_dummies(df["crop_type"], prefix="crop", dtype=int)
    crop_dummies = crop_dummies.iloc[:, 1:]
    df = pd.concat([df, crop_dummies], axis=1)

    return df


def get_crop_columns(df):
    """Get the names of all one-hot crop columns (like crop_Cucumber, crop_Herbs, etc.)"""
    return [col for col in df.columns if col.startswith("crop_") and col != "crop_type"]


# Each model uses a different subset of features.
# Health model uses everything.
# Disease model uses only disease-relevant sensors.
# Irrigation model uses only irrigation-relevant sensors.

def get_health_features(df):
    """All features for the health score model."""
    return BASE_FEATURES + ENGINEERED_FEATURES + ["growth_stage_encoded"] + get_crop_columns(df)

def get_disease_features(df):
    """Selected features for the disease risk model."""
    sensor_cols = [
        "air_temperature", "humidity", "vpd", "ventilation_rate",
        "leaf_wetness_hours", "soil_moisture", "co2_level",
        "outside_temperature", "outside_humidity", "wind_speed",
    ]
    engineered_cols = ["heat_stress_index", "humidity_co2_interaction", "temp_differential"]
    return sensor_cols + engineered_cols + ["growth_stage_encoded"] + get_crop_columns(df)

def get_irrigation_features(df):
    """Selected features for the irrigation model."""
    sensor_cols = [
        "soil_moisture", "soil_ph", "ec_conductivity",
        "air_temperature", "humidity", "previous_irrigation_mm",
        "outside_temperature", "wind_speed", "vpd",
    ]
    engineered_cols = ["drought_index", "moisture_ec_ratio", "heat_stress_index"]
    return sensor_cols + engineered_cols + ["growth_stage_encoded"] + get_crop_columns(df)


def show_top_features(model, feature_names, n=10):
    """Print the most important features used by the model."""
    importances = model.feature_importances_
    sorted_indices = np.argsort(importances)[::-1][:n]
    max_importance = importances[sorted_indices[0]]

    print(f"\n    Top {n} features:")
    for rank, idx in enumerate(sorted_indices, 1):
        bar = "#" * int(importances[idx] / max_importance * 20)
        print(f"      {rank:2d}. {feature_names[idx]:30s}  {importances[idx]:.4f}  {bar}")


def print_section(title):
    """Print a section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def main():
    print_section("Greenhouse Intelligence System — Training Pipeline")
    start_time = time.time()

    # Step 1: Load the dataset
    print("\n[1/6] Loading dataset ...")
    raw_data = pd.read_csv(DATA_PATH)
    print(f"  Loaded {len(raw_data)} rows, {raw_data.shape[1]} columns")

    # Drop rows where labels are missing (these had sensor dropouts)
    total_rows = len(raw_data)
    df = raw_data.dropna(subset=["health_score", "disease_risk_score", "irrigation_need"])
    rows_dropped = total_rows - len(df)
    print(f"  Dropped {rows_dropped} rows with missing labels → {len(df)} usable rows")

    # Step 2: Fill missing sensor values with median
    print("\n[2/6] Imputing missing sensor values (median strategy) ...")
    imputer = SimpleImputer(strategy="median")
    df[BASE_FEATURES] = imputer.fit_transform(df[BASE_FEATURES])
    missing_count = raw_data[BASE_FEATURES].isna().sum().sum()
    print(f"  Filled {missing_count} missing sensor cells")

    # Step 3: Create engineered features
    print("\n[3/6] Engineering features ...")
    df = add_engineered_features(df)
    crop_cols = get_crop_columns(df)
    print(f"  Added {len(ENGINEERED_FEATURES)} engineered features + "
          f"{len(crop_cols)} crop dummies + growth_stage_encoded")

    # Save info needed to recreate the same features during prediction
    preprocessor = {
        "growth_stage_map": STAGE_ORDER,
        "crop_columns": crop_cols,
        "engineered_features": ENGINEERED_FEATURES,
        "imputer_medians": dict(zip(BASE_FEATURES, imputer.statistics_.tolist())),
    }

    # ----- MODEL 1: Health Score (regression) -----
    print_section("Model 1 — Health Score Predictor (Regression)")

    health_features = get_health_features(df)
    X_health = df[health_features].values
    y_health = df["health_score"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X_health, y_health, test_size=0.2, random_state=42)
    print(f"  Features: {len(health_features)}  |  Train: {len(y_train)}  |  Test: {len(y_test)}")

    health_model = GradientBoostingRegressor(
        n_estimators=200, max_depth=4, learning_rate=0.08,
        min_samples_leaf=8, subsample=0.8, random_state=42)
    health_model.fit(X_train, y_train)

    predictions = health_model.predict(X_test)
    health_r2 = r2_score(y_test, predictions)
    health_mae = mean_absolute_error(y_test, predictions)
    health_rmse = np.sqrt(mean_squared_error(y_test, predictions))
    print(f"\n  Test R²  = {health_r2:.4f}")
    print(f"  Test MAE = {health_mae:.4f}")
    print(f"  Test RMSE= {health_rmse:.4f}")

    cv_scores = cross_val_score(health_model, X_health, y_health, cv=5, scoring="r2")
    print(f"  5-fold CV R² = {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

    show_top_features(health_model, health_features)

    joblib.dump(health_model, os.path.join(MODELS_DIR, "health_model.pkl"))
    print(f"\n  Saved → models/health_model.pkl")

    # ----- MODEL 2: Disease Risk (regression) -----
    print_section("Model 2 — Disease Risk Predictor (Regression)")

    disease_features = get_disease_features(df)
    X_disease = df[disease_features].values
    y_disease = df["disease_risk_score"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X_disease, y_disease, test_size=0.2, random_state=42)
    print(f"  Features: {len(disease_features)}  |  Train: {len(y_train)}  |  Test: {len(y_test)}")

    disease_model = GradientBoostingRegressor(
        n_estimators=200, max_depth=4, learning_rate=0.08,
        min_samples_leaf=8, subsample=0.8, random_state=42)
    disease_model.fit(X_train, y_train)

    predictions = disease_model.predict(X_test)
    disease_r2 = r2_score(y_test, predictions)
    disease_mae = mean_absolute_error(y_test, predictions)
    disease_rmse = np.sqrt(mean_squared_error(y_test, predictions))
    print(f"\n  Test R²  = {disease_r2:.4f}")
    print(f"  Test MAE = {disease_mae:.4f}")
    print(f"  Test RMSE= {disease_rmse:.4f}")

    cv_scores = cross_val_score(disease_model, X_disease, y_disease, cv=5, scoring="r2")
    print(f"  5-fold CV R² = {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

    show_top_features(disease_model, disease_features)

    joblib.dump(disease_model, os.path.join(MODELS_DIR, "disease_model.pkl"))
    print(f"\n  Saved → models/disease_model.pkl")

    # ----- MODEL 3: Irrigation Need (classification) -----
    print_section("Model 3 — Irrigation Need Classifier")

    irrigation_features = get_irrigation_features(df)
    X_irrigation = df[irrigation_features].values
    y_irrigation_text = df["irrigation_need"].values

    # Convert text labels (Low/Medium/High) to numbers (0/1/2)
    label_encoder = LabelEncoder()
    y_irrigation = label_encoder.fit_transform(y_irrigation_text)

    X_train, X_test, y_train, y_test = train_test_split(
        X_irrigation, y_irrigation, test_size=0.2, random_state=42, stratify=y_irrigation)
    print(f"  Features: {len(irrigation_features)}  |  Train: {len(y_train)}  |  Test: {len(y_test)}")
    print(f"  Classes:  {label_encoder.classes_.tolist()}")
    print(f"  Train distribution: {np.bincount(y_train).tolist()}")

    irrigation_model = GradientBoostingClassifier(
        n_estimators=200, max_depth=4, learning_rate=0.08,
        min_samples_leaf=8, subsample=0.8, random_state=42)
    irrigation_model.fit(X_train, y_train)

    predictions = irrigation_model.predict(X_test)
    irr_accuracy = accuracy_score(y_test, predictions)
    irr_f1 = f1_score(y_test, predictions, average="weighted")
    print(f"\n  Test Accuracy = {irr_accuracy:.4f}")
    print(f"  Test F1 (wtd) = {irr_f1:.4f}")

    cv_scores = cross_val_score(irrigation_model, X_irrigation, y_irrigation, cv=5, scoring="f1_weighted")
    print(f"  5-fold CV F1  = {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

    print(f"\n  Classification Report:")
    print(classification_report(y_test, predictions, target_names=label_encoder.classes_))

    show_top_features(irrigation_model, irrigation_features)

    joblib.dump(irrigation_model, os.path.join(MODELS_DIR, "irrigation_model.pkl"))
    print(f"\n  Saved → models/irrigation_model.pkl")

    # Save preprocessor (needed by backend to recreate features)
    print(f"\n  Saving preprocessor ...")
    preprocessor["label_encoder_classes"] = label_encoder.classes_.tolist()
    preprocessor["model1_features"] = health_features
    preprocessor["model2_features"] = disease_features
    preprocessor["model3_features"] = irrigation_features
    joblib.dump(preprocessor, os.path.join(MODELS_DIR, "preprocessor.pkl"))
    print(f"  Saved → models/preprocessor.pkl")

    # Print summary
    elapsed = time.time() - start_time
    print_section("Summary")
    print(f"  Model 1 (Health):     R² = {health_r2:.4f}   MAE = {health_mae:.2f}")
    print(f"  Model 2 (Disease):    R² = {disease_r2:.4f}   MAE = {disease_mae:.2f}")
    print(f"  Model 3 (Irrigation): F1 = {irr_f1:.4f}   Acc = {irr_accuracy:.4f}")
    print(f"\n  Total time: {elapsed:.1f}s")
    print(f"  All models saved to: {MODELS_DIR}/")


if __name__ == "__main__":
    main()
