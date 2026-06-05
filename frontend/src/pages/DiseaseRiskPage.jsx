import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ShieldAlert, Search, ArrowRight, Loader2, AlertTriangle } from 'lucide-react';
import { predictDisease } from '../api/client';
import ScoreGauge from '../components/ScoreGauge';
import Footer from '../components/Footer';

const PRESETS = {
  'High Risk': {
    air_temperature: 28, humidity: 90, co2_level: 600,
    ventilation_rate: 5, soil_moisture: 75,
    leaf_wetness_hours: 10, outside_temperature: 32,
    outside_humidity: 85, wind_speed: 2,
    crop_type: 'Tomato', growth_stage: 'Flowering',
  },
  'Low Risk': {
    air_temperature: 24, humidity: 55, co2_level: 1000,
    ventilation_rate: 50, soil_moisture: 45,
    leaf_wetness_hours: 0.5, outside_temperature: 28,
    outside_humidity: 40, wind_speed: 10,
    crop_type: 'Tomato', growth_stage: 'Vegetative',
  },
  'Moderate': {
    air_temperature: 26, humidity: 72, co2_level: 800,
    ventilation_rate: 25, soil_moisture: 58,
    leaf_wetness_hours: 4, outside_temperature: 30,
    outside_humidity: 65, wind_speed: 6,
    crop_type: 'Cucumber', growth_stage: 'Fruiting',
  },
};

const FIELDS = [
  { title: 'Climate Conditions', fields: [
    { key: 'air_temperature', label: 'Air Temperature (°C)', step: 0.1, min: 0, max: 50 },
    { key: 'humidity', label: 'Humidity (%)', step: 0.1, min: 0, max: 100 },
    { key: 'co2_level', label: 'CO\u2082 Level (ppm)', step: 1, min: 200, max: 2000 },
    { key: 'ventilation_rate', label: 'Ventilation (%)', step: 1, min: 0, max: 100 },
  ]},
  { title: 'Moisture', fields: [
    { key: 'soil_moisture', label: 'Soil Moisture (%)', step: 0.1, min: 0, max: 100 },
    { key: 'leaf_wetness_hours', label: 'Leaf Wetness (hrs)', step: 0.5, min: 0, max: 24 },
  ]},
  { title: 'External', fields: [
    { key: 'outside_temperature', label: 'Outside Temp (°C)', step: 0.1, min: -10, max: 55 },
    { key: 'outside_humidity', label: 'Outside Humidity (%)', step: 0.1, min: 0, max: 100 },
    { key: 'wind_speed', label: 'Wind Speed (km/h)', step: 0.1, min: 0, max: 50 },
  ]},
  { title: 'Crop', fields: [
    { key: 'crop_type', label: 'Crop Type', type: 'select', options: ['Tomato', 'Cucumber', 'Capsicum', 'Lettuce', 'Chili', 'Herbs'] },
    { key: 'growth_stage', label: 'Growth Stage', type: 'select', options: ['Seedling', 'Vegetative', 'Flowering', 'Fruiting', 'Harvest'] },
  ]},
];

const INIT = {
  air_temperature: '', humidity: '', co2_level: '',
  ventilation_rate: '', soil_moisture: '',
  leaf_wetness_hours: '', outside_temperature: '',
  outside_humidity: '', wind_speed: '',
  crop_type: 'Tomato', growth_stage: 'Flowering',
};

export default function DiseaseRiskPage() {
  const [form, setForm] = useState(INIT);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const set = (k, v) => setForm(p => ({ ...p, [k]: v }));
  const loadPreset = (n) => { setForm(PRESETS[n]); setResult(null); setError(''); };

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true); setError('');
    try {
      const payload = { ...form };
      for (const k of Object.keys(payload)) {
        if (k !== 'crop_type' && k !== 'growth_stage') {
          payload[k] = parseFloat(payload[k]);
          if (isNaN(payload[k])) { setError(`Invalid value for ${k}`); setLoading(false); return; }
        }
      }
      const res = await predictDisease(payload);
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail?.[0]?.msg || err.message || 'Prediction failed');
    } finally { setLoading(false); }
  };

  const riskColor = result?.disease?.risk_score >= 60 ? '#C53030'
    : result?.disease?.risk_score >= 40 ? '#B45309' : '#1B7A4E';

  return (
    <div className="predict-page">
      <div className="page-header">
        <h1><ShieldAlert size={24} /> Disease Risk Predictor</h1>
        <p>Analyze environmental conditions to predict disease risk and get prevention recommendations.</p>
      </div>

      <div className="predict-layout">
        <form className="form-panel" onSubmit={submit}>
          <div className="form-panel-header">
            <h2>Input Parameters</h2>
            <div className="preset-buttons">
              {Object.keys(PRESETS).map(n => (
                <button key={n} type="button" className="preset-btn" onClick={() => loadPreset(n)}>{n}</button>
              ))}
            </div>
          </div>

          {FIELDS.map(g => (
            <div key={g.title}>
              <div className="form-group-title">{g.title}</div>
              <div className="form-fields">
                {g.fields.map(f => (
                  <div className="form-field" key={f.key}>
                    <label htmlFor={`d-${f.key}`}>{f.label}</label>
                    {f.type === 'select' ? (
                      <select id={`d-${f.key}`} value={form[f.key]} onChange={e => set(f.key, e.target.value)}>
                        {f.options.map(o => <option key={o} value={o}>{o}</option>)}
                      </select>
                    ) : (
                      <input id={`d-${f.key}`} type="number" step={f.step} min={f.min} max={f.max}
                        value={form[f.key]} onChange={e => set(f.key, e.target.value)}
                        placeholder={f.label.split('(')[0].trim()} required />
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}

          {error && <div className="alert-item danger" style={{ marginTop: 16 }}><AlertTriangle size={14} className="alert-icon" /> {error}</div>}

          <div className="submit-row">
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? <><Loader2 size={16} className="spinning" /> Analyzing...</> : <><Search size={16} /> Predict Disease Risk</>}
            </button>
          </div>
        </form>

        <div className="results-panel">
          <AnimatePresence mode="wait">
            {!result ? (
              <div className="results-empty">
                <ShieldAlert size={40} className="empty-icon" />
                <p>Enter sensor data and click predict<br />to see disease risk analysis</p>
              </div>
            ) : (
              <motion.div key="result" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
                <div className="result-hero">
                  <ScoreGauge value={100 - result.disease.risk_score} label="Safety" size="large" color={riskColor} />
                  <div className="result-hero-info">
                    <h3>Disease Risk Score</h3>
                    <div className="result-number" style={{ color: riskColor }}>{result.disease.risk_score.toFixed(1)}%</div>
                    <span className={`level-badge ${result.disease.risk_level.toLowerCase()}`}>{result.disease.risk_level} Risk</span>
                  </div>
                </div>

                {result.disease.warnings?.length > 0 && (
                  <div className="result-summary">
                    <strong>Key concern: </strong>{result.disease.warnings[0]}
                  </div>
                )}

                {result.recommendations?.length > 0 && (
                  <div className="result-recs-section">
                    <div className="result-recs-title">Recommendations</div>
                    {result.recommendations.map((r, i) => (
                      <div key={i} className="result-rec-item">
                        <ArrowRight size={13} className="rec-bullet" /> {r}
                      </div>
                    ))}
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      <Footer />
    </div>
  );
}
