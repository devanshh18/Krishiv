# 🌿 Krishiv — Greenhouse Intelligence System

![Krishiv Banner](logo.png)

## About the Project

Greenhouse farming is growing rapidly in India, but most farmers still rely on manual observation and guesswork to manage their crops. Problems like overwatering, undetected disease outbreaks, and poor environmental control lead to significant crop losses every season.

**Krishiv** solves this by bringing machine learning into the greenhouse. It continuously monitors sensor data — temperature, humidity, soil moisture, nutrients, and more — and uses three trained ML models to provide:

- **Health Score (0–100)** — Is the greenhouse environment good for the crops right now?
- **Disease Risk (0–100)** — Are conditions favorable for fungal or bacterial infections?
- **Irrigation Need (Low / Medium / High)** — Does the soil need watering?

Instead of checking dozens of sensor readings manually, farmers and agronomists get a single dashboard with clear scores, alerts, and actionable recommendations — helping them make better decisions faster and reduce crop loss.

## Features

- **Health Score Prediction** — Scores greenhouse environment health (0–100) based on 10 sensor parameters
- **Disease Risk Assessment** — Predicts disease risk (0–100) by analyzing humidity, ventilation, leaf wetness, and other factors
- **Irrigation Recommendation** — Classifies irrigation need as Low, Medium, or High based on soil conditions
- **Live Dashboard** — Auto-refreshing dashboard with real-time sensor data, trend charts, and alerts
- **IoT Simulator** — Built-in sensor simulator that generates realistic readings every 60 seconds
- **Rule-Based Alerts** — Smart alerts and actionable recommendations based on sensor thresholds

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **ML Models** | scikit-learn (GradientBoosting) |
| **Backend** | FastAPI, SQLAlchemy, PostgreSQL |
| **Frontend** | React, Vite, Recharts |
| **Data** | pandas, NumPy |

## Project Structure

```
├── data/
│   ├── greenhouse_scoring.py    # Scoring formulas (labels the training data)
│   └── greenhouse_data.csv      # Curated dataset (~900 rows)
│
├── ml/
│   └── train_models.py          # Training pipeline for all 3 models
│
├── models/
│   ├── health_model.pkl          # Trained health score model
│   ├── disease_model.pkl         # Trained disease risk model
│   ├── irrigation_model.pkl      # Trained irrigation classifier
│   └── preprocessor.pkl          # Feature engineering metadata
│
├── backend/
│   ├── .env.example              # Environment variables template
│   └── app/
│       ├── main.py               # FastAPI app entry point
│       ├── config.py             # Settings (reads .env)
│       ├── database.py           # PostgreSQL connection
│       ├── simulator.py          # IoT sensor simulator
│       ├── ml/
│       │   ├── engine.py         # Loads models, runs predictions
│       │   └── feature_eng.py    # Feature engineering for inference
│       ├── models/
│       │   └── reading.py        # Database table definition (ORM)
│       ├── routers/              # API route handlers
│       ├── rules/
│       │   └── recommendations.py  # Alert & recommendation logic
│       └── schemas/              # Request/response validation
│
├── frontend/
│   └── src/
│       ├── App.jsx               # Root component + routing
│       ├── api/client.js         # API client (Axios)
│       ├── pages/                # Dashboard, Disease, Irrigation, About
│       └── components/           # Navbar, ScoreGauge, etc.
│
└── requirements.txt
```

## ML Pipeline

### Dataset
- ~900 rows curated from multiple public greenhouse sensor datasets, agricultural research papers, and open IoT monitoring sources
- Covers 6 crop types (Tomato, Cucumber, Capsicum, Lettuce, Chili, Herbs) with realistic Indian greenhouse conditions
- 21 sensor features + 5 target labels
- Contains real-world noise, missing values (~5%), and seasonal weather variations

### Models

| Model | Type | Target | Key Metrics |
|-------|------|--------|-------------|
| Health Score | GradientBoostingRegressor | 0–100 score | R² ≈ 0.79, MAE ≈ 3.5 |
| Disease Risk | GradientBoostingRegressor | 0–100 score | R² ≈ 0.74, MAE ≈ 5.2 |
| Irrigation Need | GradientBoostingClassifier | Low/Medium/High | F1 ≈ 0.76, Acc ≈ 0.77 |

### Feature Engineering
7 derived features are created from raw sensors:
- Temperature differential, Heat stress index, NPK balance
- Moisture-EC ratio, Light efficiency, Drought index
- Humidity-CO2 interaction

## Setup & Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL

### 1. Clone the repository
```bash
git clone https://github.com/devanshh18/Krishiv.git
cd Krishiv
```

### 2. Set up Python environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

### 3. Set up the database
Create a PostgreSQL database named `greenhouse_intelligence`, then configure the connection:
```bash
cd backend
cp .env.example .env
# Edit .env and set your DATABASE_URL with the correct password
```

### 4. Train the models (optional — pre-trained models are included)
```bash
python ml/train_models.py
```

### 5. Start the backend
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 6. Start the frontend
```bash
cd frontend
npm install
npm run dev
```

The app will be available at:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/latest-dashboard` | Latest reading + predictions + alerts |
| POST | `/api/predict` | Run all 3 models on custom sensor data |
| POST | `/api/predict/disease` | Disease risk prediction only |
| POST | `/api/predict/irrigation` | Irrigation need prediction only |
| POST | `/api/readings` | Store a sensor reading |
| GET | `/api/trends?range=hours` | Historical data for charts |
| GET | `/api/latest` | Most recent sensor reading |
