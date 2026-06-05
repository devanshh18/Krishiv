"""
Scoring formulas used to label the greenhouse training data.

Three models:
  1. Health Score      — 0-100, regression
  2. Disease Risk      — 0-100, regression
  3. Irrigation Need   — Low/Medium/High, classification
"""

import math
import random


def calculate_health_score(row):
    """Score how healthy the greenhouse environment is (0-100)."""
    score = 0

    # Air temperature (max 15)
    t = row['air_temperature']
    if 20 <= t <= 28:
        score += 15
    elif 16 <= t < 20 or 28 < t <= 32:
        score += 10
    else:
        score += 5

    # Humidity (max 12)
    h = row['humidity']
    if 50 <= h <= 70:
        score += 12
    elif 40 <= h < 50 or 70 < h <= 80:
        score += 8
    else:
        score += 4

    # CO2 (max 12)
    c = row['co2_level']
    if 800 <= c <= 1200:
        score += 12
    elif 400 <= c < 800 or 1200 < c <= 1500:
        score += 8
    else:
        score += 4

    # Light (max 10)
    l = row['light_intensity']
    if 15000 <= l <= 30000:
        score += 10
    elif 10000 <= l < 15000 or 30000 < l <= 45000:
        score += 7
    else:
        score += 3

    # Soil moisture (max 10)
    sm = row['soil_moisture']
    if 40 <= sm <= 60:
        score += 10
    elif 30 <= sm < 40 or 60 < sm <= 70:
        score += 7
    else:
        score += 3

    # Soil pH (max 10)
    ph = row['soil_ph']
    if 6.0 <= ph <= 6.8:
        score += 10
    elif 5.5 <= ph < 6.0 or 6.8 < ph <= 7.5:
        score += 7
    else:
        score += 3

    # Soil temperature (max 8)
    st = row['soil_temperature']
    if 18 <= st <= 24:
        score += 8
    elif 15 <= st < 18 or 24 < st <= 28:
        score += 5
    else:
        score += 2

    # EC (max 8)
    ec = row['ec_conductivity']
    if 1.5 <= ec <= 2.5:
        score += 8
    elif 1.0 <= ec < 1.5 or 2.5 < ec <= 3.5:
        score += 5
    else:
        score += 2

    # VPD (max 8)
    vpd = row['vpd']
    if 0.8 <= vpd <= 1.2:
        score += 8
    elif 0.5 <= vpd < 0.8 or 1.2 < vpd <= 1.5:
        score += 5
    else:
        score += 2

    # NPK balance (max 7)
    n, p, k = row['nitrogen'], row['phosphorus'], row['potassium']
    npk_score = 0
    if 150 <= n <= 250:
        npk_score += 1
    if 30 <= p <= 60:
        npk_score += 1
    if 150 <= k <= 250:
        npk_score += 1
    score += {3: 7, 2: 5, 1: 3, 0: 1}[npk_score]

    return min(score, 100)


def get_health_category(score):
    if score >= 80: return 'Excellent'
    elif score >= 70: return 'Good'
    elif score >= 60: return 'Moderate'
    elif score >= 50: return 'Fair'
    else: return 'Poor'


def calculate_disease_risk(row):
    """Score how favourable conditions are for plant diseases (0-100)."""
    risk = 0

    # Humidity — fungal risk (max 25)
    h = row['humidity']
    if h > 85:
        risk += 25
    elif h > 75:
        risk += 18
    elif h > 70:
        risk += 10
    else:
        risk += 3

    # Temperature in fungal sweet spot 15-25C (max 20)
    t = row['air_temperature']
    if 18 <= t <= 25:
        risk += 20
    elif 15 <= t < 18 or 25 < t <= 30:
        risk += 12
    else:
        risk += 4

    # Low VPD = wet leaves (max 15)
    vpd = row['vpd']
    if vpd < 0.4:
        risk += 15
    elif vpd < 0.8:
        risk += 10
    elif vpd < 1.2:
        risk += 5
    else:
        risk += 2

    # Poor ventilation (max 15)
    vent = row['ventilation_rate']
    if vent < 10:
        risk += 15
    elif vent < 30:
        risk += 8
    else:
        risk += 3

    # Leaf wetness (max 15)
    lw = row['leaf_wetness_hours']
    if lw > 6:
        risk += 15
    elif lw > 3:
        risk += 10
    elif lw > 1:
        risk += 5
    else:
        risk += 1

    # Waterlogged soil = root disease (max 10)
    sm = row['soil_moisture']
    if sm > 75:
        risk += 10
    elif sm > 60:
        risk += 6
    else:
        risk += 2

    return min(risk, 100)


def get_disease_risk_level(score):
    if score >= 75: return 'Critical'
    elif score >= 60: return 'High'
    elif score >= 40: return 'Medium'
    else: return 'Low'


def calculate_irrigation_need(row, noise=False):
    """Compute irrigation urgency and return Low/Medium/High."""
    urgency = 0

    # Soil moisture (max 30)
    sm = row['soil_moisture']
    if sm < 25:
        urgency += 30
    elif sm < 35:
        urgency += 20
    elif sm < 45:
        urgency += 10
    else:
        urgency += 2

    # Temperature (max 20)
    t = row['air_temperature']
    if t > 35:
        urgency += 20
    elif t > 28:
        urgency += 12
    else:
        urgency += 4

    # Humidity (max 15)
    h = row['humidity']
    if h < 40:
        urgency += 15
    elif h < 55:
        urgency += 10
    else:
        urgency += 3

    # Growth stage (max 15)
    stage = row['growth_stage']
    stage_scores = {
        'Flowering': 15, 'Fruiting': 13, 'Vegetative': 10,
        'Seedling': 7, 'Harvest': 5,
    }
    urgency += stage_scores.get(stage, 8)

    # EC — salt buildup (max 10)
    ec = row['ec_conductivity']
    if ec > 3.0:
        urgency += 10
    elif ec > 2.5:
        urgency += 6
    else:
        urgency += 2

    # Recent irrigation reduces need
    prev = row['previous_irrigation_mm']
    if prev > 80:
        urgency -= 8
    elif prev > 40:
        urgency -= 4

    # Add noise during data generation for label uncertainty
    if noise:
        urgency += random.gauss(0, 5)

    urgency = max(0, min(urgency, 100))

    if urgency >= 60: return 'High'
    elif urgency >= 35: return 'Medium'
    else: return 'Low'


def calculate_vpd(air_temperature, humidity):
    """VPD in kPa using the Tetens formula."""
    svp = 0.6108 * math.exp((17.27 * air_temperature) / (air_temperature + 237.3))
    vpd = svp * (1 - humidity / 100.0)
    return round(vpd, 4)


def label_row(row):
    """Apply all three scoring functions to a single row."""
    health = calculate_health_score(row)
    disease = calculate_disease_risk(row)
    irrigation = calculate_irrigation_need(row)
    return {
        'health_score': health,
        'health_category': get_health_category(health),
        'disease_risk_score': disease,
        'disease_risk_level': get_disease_risk_level(disease),
        'irrigation_need': irrigation,
    }
