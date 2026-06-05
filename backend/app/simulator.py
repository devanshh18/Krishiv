"""
IoT Simulator — generates realistic greenhouse sensor readings every 60 seconds.
Runs as a background task inside the FastAPI server.
"""

import asyncio
import logging
import random
import math
from datetime import datetime

from app.database import SessionLocal
from app.models.reading import SensorReading
from app.ml.engine import ml_engine

logger = logging.getLogger(__name__)


class GreenhouseSimulator:
    """Generates realistic sensor readings that change smoothly over time."""

    def __init__(self):
        # Current sensor values — each reading drifts from these
        self.state = {
            'air_temperature': 24.0,
            'humidity': 62.0,
            'co2_level': 950.0,
            'light_intensity': 22000.0,
            'soil_moisture': 48.0,
            'soil_ph': 6.4,
            'soil_temperature': 21.0,
            'ec_conductivity': 2.0,
            'nitrogen': 195.0,
            'phosphorus': 42.0,
            'potassium': 190.0,
            'ventilation_rate': 45.0,
            'outside_temperature': 30.0,
            'outside_humidity': 50.0,
            'wind_speed': 8.0,
            'leaf_wetness_hours': 1.5,
            'previous_irrigation_mm': 55.0,
        }
        self.crop_type = 'Tomato'
        self.growth_stage = 'Flowering'
        self.tick_count = 0

    def drift(self, current, target, speed=0.1, noise=0.5):
        """
        Move a value slowly toward a target with some randomness.
        Speed controls how fast it moves (0.1 = 10% of the gap per tick).
        Noise adds random variation.
        """
        step = (target - current) * speed
        return current + step + random.gauss(0, noise)

    def clamp(self, value, low, high):
        """Keep a value within bounds."""
        return max(low, min(high, value))

    def generate_reading(self):
        """Generate the next sensor reading based on current time of day."""
        self.tick_count += 1
        now = datetime.now()
        hour = now.hour + now.minute / 60.0

        # Day/night factor: -1 at 5am (coldest), +1 around 5pm (hottest)
        day_factor = math.sin((hour - 5) * math.pi / 12)
        day_factor = self.clamp(day_factor, -1, 1)

        # Outside temperature follows day/night cycle (20-38°C range)
        outside_target = 29 + 9 * day_factor
        self.state['outside_temperature'] = self.clamp(
            self.drift(self.state['outside_temperature'], outside_target, 0.15, 0.3),
            15, 45
        )

        # Air temperature: greenhouse is warmer during the day
        air_target = self.state['outside_temperature'] - 2 + 3 * max(0, day_factor)
        self.state['air_temperature'] = self.clamp(
            self.drift(self.state['air_temperature'], air_target, 0.12, 0.2),
            12, 42
        )

        # Soil temperature: changes slower than air, always a bit cooler
        soil_target = self.state['air_temperature'] - 3
        self.state['soil_temperature'] = self.clamp(
            self.drift(self.state['soil_temperature'], soil_target, 0.05, 0.1),
            10, 35
        )

        # Humidity: higher at night, lower during hot day
        humidity_target = 65 - 15 * day_factor
        self.state['humidity'] = self.clamp(
            self.drift(self.state['humidity'], humidity_target, 0.1, 1.0),
            25, 95
        )

        # Outside humidity: opposite of temperature
        outside_hum_target = 55 - 10 * day_factor
        self.state['outside_humidity'] = self.clamp(
            self.drift(self.state['outside_humidity'], outside_hum_target, 0.1, 1.5),
            20, 90
        )

        # Light: bright during day, zero at night
        if 6 <= hour <= 19:
            light_target = 25000 * max(0, math.sin((hour - 6) * math.pi / 13))
        else:
            light_target = 0
        self.state['light_intensity'] = self.clamp(
            self.drift(self.state['light_intensity'], light_target, 0.2, 500),
            0, 50000
        )

        # CO2: higher at night (respiration), lower during day (photosynthesis)
        co2_target = 900 - 200 * day_factor
        self.state['co2_level'] = self.clamp(
            self.drift(self.state['co2_level'], co2_target, 0.08, 15),
            300, 1800
        )

        # Soil moisture: slowly decreases, jumps up after irrigation
        moisture = self.state['soil_moisture'] - random.uniform(0.05, 0.2)
        if moisture < 30:
            # Auto-irrigate when soil gets too dry
            moisture += random.uniform(15, 25)
            self.state['previous_irrigation_mm'] = random.uniform(40, 80)
        else:
            # Previous irrigation amount slowly decays
            self.state['previous_irrigation_mm'] = self.clamp(
                self.state['previous_irrigation_mm'] * 0.95, 0, 200
            )
        self.state['soil_moisture'] = self.clamp(moisture, 15, 85)

        # EC conductivity: slight random drift around 2.0
        self.state['ec_conductivity'] = self.clamp(
            self.drift(self.state['ec_conductivity'], 2.0, 0.05, 0.03),
            0.5, 5.0
        )

        # Soil pH: very stable, barely changes
        self.state['soil_ph'] = self.clamp(
            self.drift(self.state['soil_ph'], 6.4, 0.02, 0.01),
            5.0, 8.0
        )

        # NPK nutrients: slow drift toward typical values
        self.state['nitrogen'] = self.clamp(
            self.drift(self.state['nitrogen'], 200, 0.03, 2), 50, 400)
        self.state['phosphorus'] = self.clamp(
            self.drift(self.state['phosphorus'], 45, 0.03, 1), 10, 120)
        self.state['potassium'] = self.clamp(
            self.drift(self.state['potassium'], 200, 0.03, 2), 50, 400)

        # Ventilation: fans run more during hot parts of the day
        vent_target = 30 + 25 * max(0, day_factor)
        self.state['ventilation_rate'] = self.clamp(
            self.drift(self.state['ventilation_rate'], vent_target, 0.15, 1),
            5, 95
        )

        # Wind speed: random variation
        self.state['wind_speed'] = self.clamp(
            self.drift(self.state['wind_speed'], 8, 0.1, 0.8),
            0, 35
        )

        # Leaf wetness: more when humidity is high
        wetness_target = max(0, (self.state['humidity'] - 60) / 10)
        self.state['leaf_wetness_hours'] = self.clamp(
            self.drift(self.state['leaf_wetness_hours'], wetness_target, 0.1, 0.3),
            0, 20
        )

        # Build the reading dictionary
        reading = {}
        for key, value in self.state.items():
            reading[key] = round(value, 2)

        reading['crop_type'] = self.crop_type
        reading['growth_stage'] = self.growth_stage

        # Light hours (day length) varies by time of year
        day_of_year = now.timetuple().tm_yday
        reading['light_hours'] = round(
            12 + 2 * math.sin((day_of_year - 80) * 2 * math.pi / 365), 1
        )

        return reading


# Create the simulator instance
simulator = GreenhouseSimulator()


async def simulator_loop():
    """Background task: generate a reading every 60 seconds, predict, and store."""
    logger.info("IoT Simulator started — generating readings every 60 seconds")

    # Generate first reading right away (don't wait 60 seconds)
    await generate_and_store()

    while True:
        await asyncio.sleep(60)
        await generate_and_store()


async def generate_and_store():
    """Generate one sensor reading, run ML predictions, and save to database."""
    try:
        # Generate sensor data
        reading_data = simulator.generate_reading()

        # Run all 3 ML models on this reading
        results = ml_engine.predict_all(reading_data)

        # Save to PostgreSQL
        db = SessionLocal()
        try:
            reading = SensorReading(
                air_temperature=reading_data['air_temperature'],
                humidity=reading_data['humidity'],
                co2_level=reading_data['co2_level'],
                light_intensity=reading_data['light_intensity'],
                soil_moisture=reading_data['soil_moisture'],
                soil_ph=reading_data['soil_ph'],
                soil_temperature=reading_data['soil_temperature'],
                ec_conductivity=reading_data['ec_conductivity'],
                nitrogen=reading_data['nitrogen'],
                phosphorus=reading_data['phosphorus'],
                potassium=reading_data['potassium'],
                ventilation_rate=reading_data['ventilation_rate'],
                outside_temperature=reading_data['outside_temperature'],
                outside_humidity=reading_data['outside_humidity'],
                wind_speed=reading_data['wind_speed'],
                crop_type=reading_data['crop_type'],
                growth_stage=reading_data['growth_stage'],
                leaf_wetness_hours=reading_data['leaf_wetness_hours'],
                previous_irrigation_mm=reading_data['previous_irrigation_mm'],
                health_score=results['health'].score,
                health_category=results['health'].category,
                disease_risk_score=results['disease'].risk_score,
                disease_risk_level=results['disease'].risk_level,
                irrigation_need=results['irrigation'].need,
            )
            db.add(reading)
            db.commit()

            logger.info(
                f"Simulator | Health: {results['health'].score:.1f} "
                f"({results['health'].category}) | "
                f"Disease: {results['disease'].risk_score:.1f} | "
                f"Irrigation: {results['irrigation'].need} | "
                f"Temp: {reading_data['air_temperature']:.1f}°C | "
                f"Humidity: {reading_data['humidity']:.0f}%"
            )
        finally:
            db.close()

    except Exception as e:
        logger.error(f"Simulator error: {e}", exc_info=True)
