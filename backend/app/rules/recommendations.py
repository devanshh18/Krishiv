"""Rule engine: generates alerts and recommendations from ML outputs + sensor data."""


def generate_alerts_and_recommendations(
    sensor_data: dict,
    health_result,
    disease_result,
    irrigation_result,
) -> tuple[list[dict], list[str]]:
    """
    Generate human-readable alerts and action suggestions.

    Args:
        sensor_data: Raw sensor reading dict
        health_result: HealthResult from ML engine
        disease_result: DiseaseResult from ML engine
        irrigation_result: IrrigationResult from ML engine

    Returns:
        (alerts, recommendations) — list of alert dicts and list of recommendation strings
    """
    alerts = []
    recommendations = []

    # ── Humidity alerts ─────────────────────────────────────────────
    humidity = sensor_data['humidity']
    if humidity > 85:
        alerts.append({
            "type": "danger",
            "message": f"Humidity critically high ({humidity:.0f}%) — severe fungal risk"
        })
        recommendations.append("Increase ventilation immediately to bring humidity below 70%")
    elif humidity > 80:
        alerts.append({
            "type": "warning",
            "message": f"Humidity high ({humidity:.0f}%) — fungal risk elevated"
        })
        recommendations.append("Increase ventilation to bring humidity below 70%")
    elif humidity < 35:
        alerts.append({
            "type": "warning",
            "message": f"Humidity too low ({humidity:.0f}%) — leaf desiccation risk"
        })
        recommendations.append("Enable misting or reduce ventilation to raise humidity")

    # ── Temperature alerts ──────────────────────────────────────────
    temp = sensor_data['air_temperature']
    if temp > 35:
        alerts.append({
            "type": "danger",
            "message": f"Temperature too high ({temp:.1f}°C) — heat stress likely"
        })
        recommendations.append("Activate cooling system or increase shade screen")
    elif temp > 32:
        alerts.append({
            "type": "warning",
            "message": f"Temperature elevated ({temp:.1f}°C) — approaching stress zone"
        })
        recommendations.append("Monitor temperature — consider activating cooling if it rises further")
    elif temp < 15:
        alerts.append({
            "type": "warning",
            "message": f"Temperature too low ({temp:.1f}°C) — growth will slow significantly"
        })
        recommendations.append("Activate heating system to maintain minimum 18°C")

    # ── CO₂ alerts ──────────────────────────────────────────────────
    co2 = sensor_data['co2_level']
    if co2 < 600:
        alerts.append({
            "type": "info",
            "message": f"CO₂ below optimal ({co2:.0f} ppm) — consider CO₂ enrichment"
        })
        recommendations.append("Enable CO₂ supplementation to reach 800-1200 ppm range")
    elif co2 > 1500:
        alerts.append({
            "type": "warning",
            "message": f"CO₂ too high ({co2:.0f} ppm) — diminishing returns above 1500 ppm"
        })
        recommendations.append("Reduce CO₂ injection — current levels waste resources")

    # ── VPD alerts ──────────────────────────────────────────────────
    vpd = sensor_data.get('vpd', 1.0)
    if vpd < 0.4:
        alerts.append({
            "type": "warning",
            "message": f"VPD critically low ({vpd:.2f} kPa) — stomata closed, disease risk high"
        })
    elif vpd > 1.5:
        alerts.append({
            "type": "warning",
            "message": f"VPD too high ({vpd:.2f} kPa) — plants losing water too fast"
        })
        recommendations.append("Increase humidity or lower temperature to reduce VPD")

    # ── Disease-based recommendations ───────────────────────────────
    if disease_result.risk_score > 75:
        recommendations.append("CRITICAL: Inspect all plants for disease symptoms immediately")
        recommendations.append("Apply preventive fungicide if no symptoms yet")
        recommendations.append("Avoid overhead watering to reduce leaf wetness")
    elif disease_result.risk_score > 60:
        recommendations.append("Monitor leaves for white powdery spots or gray mold")
        recommendations.append("Avoid overhead watering to reduce leaf wetness")
    elif disease_result.risk_score > 40:
        recommendations.append("Keep monitoring — moderate disease risk detected")

    # ── Irrigation-based recommendations ────────────────────────────
    if irrigation_result.need == 'High':
        recommendations.append(
            f"Irrigate immediately — soil moisture at {sensor_data['soil_moisture']:.0f}%"
        )
    elif irrigation_result.need == 'Medium':
        recommendations.append(
            f"Plan irrigation within 2-3 hours — soil moisture at {sensor_data['soil_moisture']:.0f}%"
        )
    elif irrigation_result.need == 'Low':
        recommendations.append("Avoid irrigation for next few hours — soil moisture sufficient")

    # ── Soil pH alerts ──────────────────────────────────────────────
    ph = sensor_data['soil_ph']
    if ph < 5.5:
        alerts.append({
            "type": "warning",
            "message": f"Soil pH too acidic ({ph:.1f}) — nutrient lockout risk"
        })
        recommendations.append("Add agricultural lime to raise pH to 6.0-6.8 range")
    elif ph > 7.5:
        alerts.append({
            "type": "warning",
            "message": f"Soil pH too alkaline ({ph:.1f}) — iron/zinc deficiency risk"
        })
        recommendations.append("Add sulfur or acidic fertilizer to lower pH")

    # ── EC alerts ───────────────────────────────────────────────────
    ec = sensor_data['ec_conductivity']
    if ec > 3.5:
        alerts.append({
            "type": "warning",
            "message": f"EC too high ({ec:.1f} mS/cm) — salt burn risk"
        })
        recommendations.append("Flush soil with clean water to reduce salt buildup")
    elif ec < 1.0:
        alerts.append({
            "type": "info",
            "message": f"EC low ({ec:.1f} mS/cm) — nutrients may be insufficient"
        })
        recommendations.append("Consider increasing fertilizer concentration")

    # ── Soil moisture extremes ──────────────────────────────────────
    sm = sensor_data['soil_moisture']
    if sm > 75:
        alerts.append({
            "type": "danger",
            "message": f"Soil moisture critically high ({sm:.0f}%) — root rot risk"
        })
        recommendations.append("Stop irrigation and improve drainage immediately")
    elif sm < 20:
        alerts.append({
            "type": "danger",
            "message": f"Soil moisture critically low ({sm:.0f}%) — severe drought stress"
        })

    # ── Health-based recommendations ────────────────────────────────
    if health_result.score < 50:
        alerts.append({
            "type": "danger",
            "message": f"Overall health score poor ({health_result.score:.0f}/100) — multiple parameters need attention"
        })

    # Deduplicate recommendations while preserving order
    seen = set()
    unique_recs = []
    for r in recommendations:
        if r not in seen:
            seen.add(r)
            unique_recs.append(r)

    return alerts, unique_recs


def generate_disease_recommendations(
    sensor_data: dict,
    disease_result,
) -> tuple[list[dict], list[str]]:
    """
    Generate alerts and recommendations focused on disease risk only.
    Used by the standalone disease prediction endpoint.
    """
    alerts = []
    recommendations = []

    # Humidity alerts (disease-relevant)
    humidity = sensor_data['humidity']
    if humidity > 85:
        alerts.append({
            "type": "danger",
            "message": f"Humidity critically high ({humidity:.0f}%) — severe fungal risk"
        })
        recommendations.append("Increase ventilation immediately to bring humidity below 70%")
    elif humidity > 80:
        alerts.append({
            "type": "warning",
            "message": f"Humidity high ({humidity:.0f}%) — fungal risk elevated"
        })
        recommendations.append("Increase ventilation to bring humidity below 70%")

    # VPD alerts
    vpd = sensor_data.get('vpd', 1.0)
    if vpd < 0.4:
        alerts.append({
            "type": "warning",
            "message": f"VPD critically low ({vpd:.2f} kPa) — stomata closed, disease risk high"
        })
        recommendations.append("Increase air circulation and reduce humidity")
    elif vpd > 1.5:
        alerts.append({
            "type": "warning",
            "message": f"VPD too high ({vpd:.2f} kPa) — plant stress may weaken disease resistance"
        })

    # Ventilation alert
    ventilation = sensor_data.get('ventilation_rate', 40)
    if ventilation < 10 and humidity > 75:
        alerts.append({
            "type": "warning",
            "message": "Poor ventilation with high humidity — fungal spread likely"
        })
        recommendations.append("Open vents to at least 30% to improve air circulation")

    # Leaf wetness alert
    leaf_wetness = sensor_data.get('leaf_wetness_hours', 0)
    if leaf_wetness > 6:
        alerts.append({
            "type": "warning",
            "message": f"Extended leaf wetness ({leaf_wetness:.0f}h) — foliar disease risk elevated"
        })
        recommendations.append("Reduce overhead watering and improve air circulation to dry foliage")

    # Soil moisture (root rot risk)
    sm = sensor_data.get('soil_moisture', 50)
    if sm > 70:
        alerts.append({
            "type": "warning",
            "message": f"High soil moisture ({sm:.0f}%) — root rot risk"
        })

    # Disease-level recommendations
    if disease_result.risk_score >= 75:
        recommendations.append("CRITICAL: Inspect all plants for disease symptoms immediately")
        recommendations.append("Apply preventive fungicide if no symptoms yet")
        recommendations.append("Avoid overhead watering to reduce leaf wetness")
    elif disease_result.risk_score >= 60:
        recommendations.append("Monitor leaves for white powdery spots or gray mold")
        recommendations.append("Avoid overhead watering to reduce leaf wetness")
    elif disease_result.risk_score >= 40:
        recommendations.append("Keep monitoring — moderate disease risk detected")
    else:
        recommendations.append("Disease risk is low — continue routine monitoring")

    # Deduplicate
    seen = set()
    unique_recs = []
    for r in recommendations:
        if r not in seen:
            seen.add(r)
            unique_recs.append(r)

    return alerts, unique_recs


def generate_irrigation_recommendations(
    sensor_data: dict,
    irrigation_result,
) -> tuple[list[dict], list[str]]:
    """
    Generate alerts and recommendations focused on irrigation only.
    Used by the standalone irrigation prediction endpoint.
    """
    alerts = []
    recommendations = []

    # Soil moisture
    sm = sensor_data['soil_moisture']
    if sm > 75:
        alerts.append({
            "type": "danger",
            "message": f"Soil moisture critically high ({sm:.0f}%) — root rot risk"
        })
        recommendations.append("Stop irrigation and improve drainage immediately")
    elif sm > 60:
        alerts.append({
            "type": "info",
            "message": f"Soil moisture is adequate ({sm:.0f}%) — no irrigation needed"
        })
    elif sm < 20:
        alerts.append({
            "type": "danger",
            "message": f"Soil moisture critically low ({sm:.0f}%) — severe drought stress"
        })
        recommendations.append("Irrigate immediately with deep watering")
    elif sm < 35:
        alerts.append({
            "type": "warning",
            "message": f"Soil moisture low ({sm:.0f}%) — plants may be stressed"
        })

    # Soil pH
    ph = sensor_data.get('soil_ph', 6.5)
    if ph < 5.5:
        alerts.append({
            "type": "warning",
            "message": f"Soil pH too acidic ({ph:.1f}) — nutrient lockout risk"
        })
        recommendations.append("Add agricultural lime to raise pH to 6.0-6.8 range")
    elif ph > 7.5:
        alerts.append({
            "type": "warning",
            "message": f"Soil pH too alkaline ({ph:.1f}) — iron/zinc deficiency risk"
        })
        recommendations.append("Add sulfur or acidic fertilizer to lower pH")

    # EC
    ec = sensor_data.get('ec_conductivity', 2.0)
    if ec > 3.5:
        alerts.append({
            "type": "warning",
            "message": f"EC too high ({ec:.1f} mS/cm) — salt burn risk"
        })
        recommendations.append("Flush soil with clean water to reduce salt buildup")
    elif ec < 1.0:
        alerts.append({
            "type": "info",
            "message": f"EC low ({ec:.1f} mS/cm) — nutrients may be insufficient"
        })
        recommendations.append("Consider increasing fertilizer concentration")

    # Wind speed (evaporation)
    wind = sensor_data.get('wind_speed', 5)
    if wind > 20 and sm < 40:
        recommendations.append(f"High wind ({wind:.0f} km/h) accelerating evaporation — increase irrigation frequency")

    # Irrigation-level recommendations
    if irrigation_result.need == 'High':
        recommendations.append(f"Irrigate immediately — soil moisture at {sm:.0f}%")
        recommendations.append("Use drip irrigation for efficiency in current conditions")
    elif irrigation_result.need == 'Medium':
        recommendations.append(f"Plan irrigation within 2-3 hours — soil moisture at {sm:.0f}%")
    elif irrigation_result.need == 'Low':
        recommendations.append("No irrigation needed — soil moisture is sufficient")
        recommendations.append("Avoid overwatering to prevent root diseases")

    # Deduplicate
    seen = set()
    unique_recs = []
    for r in recommendations:
        if r not in seen:
            seen.add(r)
            unique_recs.append(r)

    return alerts, unique_recs

