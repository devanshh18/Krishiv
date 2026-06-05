import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Droplets, Search, ArrowRight, Loader2, AlertTriangle } from 'lucide-react';
import { predictIrrigation } from '../api/client';
import ScoreGauge from '../components/ScoreGauge';
import Footer from '../components/Footer';

const PRESETS = {
  'Drought Stress': {
    soil_moisture: 18, soil_ph: 6.2, ec_conductivity: 2.5,
    air_temperature: 34, humidity: 35,
    outside_temperature: 38, wind_speed: 15,
    previous_irrigation_mm: 10,
    crop_type: 'Tomato', growth_stage: 'Fruiting',
  },
  'Well Watered': {
    soil_moisture: 55, soil_ph: 6.5, ec_conductivity: 2.0,
    air_temperature: 24, humidity: 62,
    outside_temperature: 28, wind_speed: 6,
    previous_irrigation_mm: 65,
    crop_type: 'Tomato', growth_stage: 'Flowering',
  },
  'Moderate': {
    soil_moisture: 35, soil_ph: 6.8, ec_conductivity: 1.8,
    air_temperature: 28, humidity: 50,
    outside_temperature: 32, wind_speed: 8,
    previous_irrigation_mm: 30,
    crop_type: 'Cucumber', growth_stage: 'Vegetative',
  },
};

const FIELDS = [
  { title: 'Soil Conditions', fields: [
    { key: 'soil_moisture', label: 'Soil Moisture (%)', step: 0.1, min: 0, max: 100 },
    { key: 'soil_ph', label: 'Soil pH', step: 0.1, min: 3, max: 10 },
    { key: 'ec_conductivity', label: 'EC (mS/cm)', step: 0.1, min: 0, max: 10 },
  ]},
  { title: 'Climate', fields: [
    { key: 'air_temperature', label: 'Air Temperature (°C)', step: 0.1, min: 0, max: 50 },
    { key: 'humidity', label: 'Humidity (%)', step: 0.1, min: 0, max: 100 },
  ]},
  { title: 'External', fields: [
    { key: 'outside_temperature', label: 'Outside Temp (°C)', step: 0.1, min: -10, max: 55 },
    { key: 'wind_speed', label: 'Wind Speed (km/h)', step: 0.1, min: 0, max: 50 },
  ]},
  { title: 'History', fields: [
    { key: 'previous_irrigation_mm', label: 'Previous Irrigation (mm)', step: 1, min: 0, max: 200 },
  ]},
  { title: 'Crop', fields: [
    { key: 'crop_type', label: 'Crop Type', type: 'select', options: ['Tomato', 'Cucumber', 'Capsicum', 'Lettuce', 'Chili', 'Herbs'] },
    { key: 'growth_stage', label: 'Growth Stage', type: 'select', options: ['Seedling', 'Vegetative', 'Flowering', 'Fruiting', 'Harvest'] },
  ]},
];

const INIT = {
  soil_moisture: '', soil_ph: '', ec_conductivity: '',
  air_temperature: '', humidity: '',
  outside_temperature: '', wind_speed: '',
  previous_irrigation_mm: '',
  crop_type: 'Tomato', growth_stage: 'Flowering',
};

export default function IrrigationPage() {
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
          if (isNaN(payload[k])) { setError(`Invalid: ${k}`); setLoading(false); return; }
        }
      }
      const res = await predictIrrigation(payload);
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail?.[0]?.msg || err.message || 'Failed');
    } finally { setLoading(false); }
  };

  const needColor = result?.irrigation?.need === 'High' ? '#C53030'
    : result?.irrigation?.need === 'Medium' ? '#B45309' : '#1B7A4E';
  const needVal = result?.irrigation?.need === 'High' ? 90
    : result?.irrigation?.need === 'Medium' ? 55 : 20;

  return (
    <div className="predict-page">
      <div className="page-header">
        <h1><Droplets size={24} /> Irrigation Advisory</h1>
        <p>Analyze soil and climate conditions to get smart irrigation recommendations.</p>
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
                    <label htmlFor={`i-${f.key}`}>{f.label}</label>
                    {f.type === 'select' ? (
                      <select id={`i-${f.key}`} value={form[f.key]} onChange={e => set(f.key, e.target.value)}>
                        {f.options.map(o => <option key={o} value={o}>{o}</option>)}
                      </select>
                    ) : (
                      <input id={`i-${f.key}`} type="number" step={f.step} min={f.min} max={f.max}
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
              {loading ? <><Loader2 size={16} className="spinning" /> Analyzing...</> : <><Search size={16} /> Get Irrigation Advice</>}
            </button>
          </div>
        </form>

        <div className="results-panel">
          <AnimatePresence mode="wait">
            {!result ? (
              <div className="results-empty">
                <Droplets size={40} className="empty-icon" />
                <p>Enter soil and climate data<br />to get irrigation recommendations</p>
              </div>
            ) : (
              <motion.div key="result" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
                <div className="result-hero">
                  <ScoreGauge value={needVal} label="Need" size="large" color={needColor} />
                  <div className="result-hero-info">
                    <h3>Irrigation Need</h3>
                    <div className="result-number" style={{ color: needColor }}>{result.irrigation.need}</div>
                    <span className={`level-badge ${result.irrigation.need.toLowerCase()}`}>{result.irrigation.need} Priority</span>
                  </div>
                </div>

                {/* Soil stats */}
                <div className="stat-cards-row">
                  <div className="stat-card">
                    <div className="stat-val" style={{ color: '#2563EB' }}>{form.soil_moisture}%</div>
                    <div className="stat-label">Soil Moisture</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-val" style={{ color: '#1B7A4E' }}>{form.soil_ph}</div>
                    <div className="stat-label">Soil pH</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-val" style={{ color: '#B45309' }}>{form.ec_conductivity}</div>
                    <div className="stat-label">EC (mS/cm)</div>
                  </div>
                </div>

                {/* One-line recommendation */}
                <div className="result-summary">
                  <strong>{result.irrigation.recommendation}</strong>
                </div>

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
