import { motion } from 'framer-motion';
import { RefreshCw, Thermometer, Droplets, Wind, Sprout, AlertTriangle, CheckCircle2, ArrowRight, TrendingUp } from 'lucide-react';
import Chart from 'react-apexcharts';
import ScoreGauge from '../components/ScoreGauge';
import LoadingSpinner from '../components/LoadingSpinner';
import Footer from '../components/Footer';

const fade = { hidden: { opacity: 0, y: 12 }, show: { opacity: 1, y: 0 } };

const SENSORS = [
  { key: 'air_temperature', label: 'Temperature', unit: '\u00B0C', icon: Thermometer, ranges: [[20, 28], [16, 32]] },
  { key: 'humidity', label: 'Humidity', unit: '%', icon: Droplets, ranges: [[50, 70], [40, 80]] },
  { key: 'co2_level', label: 'CO\u2082 Level', unit: 'ppm', icon: Wind, ranges: [[800, 1200], [400, 1500]] },
  { key: 'soil_moisture', label: 'Soil Moisture', unit: '%', icon: Sprout, ranges: [[40, 60], [30, 70]] },
];

function getStatus(ranges, val) {
  if (!ranges || val == null) return null;
  if (val >= ranges[0][0] && val <= ranges[0][1]) return 'optimal';
  if (val >= ranges[1][0] && val <= ranges[1][1]) return 'suboptimal';
  return 'poor';
}

function fmtTime(ts) {
  if (!ts) return '';
  return new Date(ts).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
}

function fmtTimestamp(ts, range) {
  if (!ts) return '';
  const date = new Date(ts);
  if (range === 'days') {
    return date.toLocaleDateString('en-IN', { day: '2-digit', month: 'short' });
  }
  return date.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
}

export default function DashboardPage({
  data,
  trends,
  loading,
  lastFetch,
  countdown,
  trendRange,
  setTrendRange,
  refetch
}) {
  if (loading) return <LoadingSpinner text="Loading dashboard..." />;
  if (!data) return (
    <div className="dashboard-page">
      <div className="empty-state" style={{ paddingTop: 100, flexDirection: 'column', gap: 12 }}>
        <p>Waiting for first sensor reading from the simulator...</p>
        <button className="btn btn-primary btn-sm" onClick={refetch} style={{ marginTop: 8 }}>Retry</button>
      </div>
    </div>
  );

  const { reading, health, disease, irrigation, alerts, recommendations } = data;

  const chartOpts = {
    chart: { type: 'area', toolbar: { show: false }, zoom: { enabled: false }, fontFamily: "'Plus Jakarta Sans', sans-serif" },
    colors: ['#1B7A4E', '#B45309', '#2563EB', '#7C3AED'],
    stroke: { curve: 'smooth', width: 2.5 },
    fill: { type: 'gradient', gradient: { shadeIntensity: 1, opacityFrom: 0.18, opacityTo: 0.02, stops: [0, 100] } },
    grid: { borderColor: '#E8E4DC', strokeDashArray: 4 },
    xaxis: {
      categories: trends.map(t => fmtTimestamp(t.timestamp, trendRange)),
      labels: { style: { fontSize: '12px', colors: '#7A9485', fontFamily: "'Plus Jakarta Sans'" } },
      axisBorder: { show: false }, axisTicks: { show: false },
    },
    yaxis: { labels: { style: { fontSize: '12px', colors: '#7A9485', fontFamily: "'Plus Jakarta Sans'" } } },
    tooltip: { x: { show: true }, style: { fontSize: '13px' } },
    legend: { position: 'top', horizontalAlign: 'right', fontSize: '13px', fontWeight: 500, markers: { size: 5, offsetX: -3 } },
    dataLabels: { enabled: false },
  };
  const chartSeries = [
    { name: 'Health Score', data: trends.map(t => t.health_score ? +t.health_score.toFixed(1) : null) },
    { name: 'Temperature', data: trends.map(t => t.air_temperature ? +t.air_temperature.toFixed(1) : null) },
    { name: 'Humidity', data: trends.map(t => t.humidity ? +t.humidity.toFixed(1) : null) },
    { name: 'Soil Moisture', data: trends.map(t => t.soil_moisture ? +t.soil_moisture.toFixed(1) : null) },
  ];

  // Semantic colors
  const healthColor = '#1B7A4E';
  const diseaseColor = disease?.risk_score >= 60 ? '#C53030' : disease?.risk_score >= 40 ? '#B45309' : '#1B7A4E';
  const irrColor = irrigation?.need === 'High' ? '#C53030' : irrigation?.need === 'Medium' ? '#B45309' : '#1B7A4E';

  return (
    <div className="dashboard-page">
      <motion.div className="dashboard-header" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <div>
          <h1>Greenhouse Dashboard</h1>
          <div className="header-sub">{reading?.crop_type} &middot; {reading?.growth_stage} Stage</div>
        </div>
        <div className="dashboard-meta">
          <div className="live-indicator"><span className="live-dot" /> Live</div>
          <span className="last-updated">Updated {lastFetch ? fmtTime(lastFetch) : '\u2014'} &middot; Next in {countdown}s</span>
          <button className="refresh-btn" onClick={refetch}><RefreshCw size={13} /> Refresh</button>
        </div>
      </motion.div>

      {/* Score Cards */}
      <motion.div className="scores-row" variants={{ show: { transition: { staggerChildren: 0.08 } } }} initial="hidden" animate="show">
        <motion.div className="score-card" variants={fade}>
          <ScoreGauge value={health?.score || 0} label="Score" size="large" color={healthColor} />
          <div className="score-info">
            <h3>Health Score</h3>
            <div className="score-value" style={{ color: healthColor }}>{health?.score?.toFixed(1)}/100</div>
            <span className={`level-badge ${health?.category?.toLowerCase()}`}>{health?.category}</span>
          </div>
        </motion.div>

        <motion.div className="score-card" variants={fade}>
          <ScoreGauge value={100 - (disease?.risk_score || 0)} label="Safety" size="large" color={diseaseColor} />
          <div className="score-info">
            <h3>Disease Risk</h3>
            <div className="score-value" style={{ color: diseaseColor }}>{disease?.risk_score?.toFixed(1)}%</div>
            <span className={`level-badge ${disease?.risk_level?.toLowerCase()}`}>{disease?.risk_level}</span>
          </div>
        </motion.div>

        <motion.div className="score-card" variants={fade}>
          <ScoreGauge value={irrigation?.need === 'High' ? 90 : irrigation?.need === 'Medium' ? 55 : 20} label="Need" size="large" color={irrColor} />
          <div className="score-info">
            <h3>Irrigation Need</h3>
            <div className="score-value" style={{ color: irrColor }}>{irrigation?.need}</div>
            <span className={`level-badge ${irrigation?.need?.toLowerCase()}`}>{irrigation?.need} Priority</span>
          </div>
        </motion.div>
      </motion.div>

      {/* 4 Key Sensors */}
      <div className="sensor-section-title">Key Readings</div>
      <div className="sensor-grid">
        {SENSORS.map(({ key, label, unit, icon: Icon, ranges }) => {
          const val = reading?.[key];
          const status = getStatus(ranges, val);
          return (
            <motion.div className="sensor-card" key={key} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
              <div className="sensor-card-header">
                <span className="sensor-card-label">{label}</span>
                <Icon size={17} className="sensor-card-icon" />
              </div>
              <div className="sensor-card-value">{val != null ? val.toFixed(1) : '\u2014'}</div>
              <div className="sensor-card-unit">{unit}</div>
              {status && <span className={`sensor-status ${status}`}>{status}</span>}
            </motion.div>
          );
        })}
      </div>

      {/* Alerts & Recommendations */}
      <div className="dashboard-panels">
        <div className="panel">
          <div className="panel-header">
            <AlertTriangle size={16} className="panel-icon" />
            <h3>Alerts</h3>
            <span className="panel-count">{alerts?.length || 0}</span>
          </div>
          {alerts?.length > 0 ? alerts.map((a, i) => (
            <div key={i} className={`alert-item ${a.type}`}>
              <AlertTriangle size={15} className="alert-icon" />
              {a.message}
            </div>
          )) : <div className="empty-state"><CheckCircle2 size={16} style={{ color: '#1B7A4E' }} /> All systems normal</div>}
        </div>

        <div className="panel">
          <div className="panel-header">
            <ArrowRight size={16} className="panel-icon" />
            <h3>Recommendations</h3>
            <span className="panel-count">{recommendations?.length || 0}</span>
          </div>
          {recommendations?.length > 0 ? recommendations.map((r, i) => (
            <div key={i} className="rec-item">
              <ArrowRight size={14} className="rec-icon" /> {r}
            </div>
          )) : <div className="empty-state">No recommendations at this time</div>}
        </div>
      </div>

      {/* Trend Chart */}
      <div className="trend-section">
        <div className="trend-header">
          <h3><TrendingUp size={18} /> Trend History</h3>
          <select
            value={trendRange}
            onChange={(e) => setTrendRange(e.target.value)}
            className="trend-select"
            style={{
              padding: '6px 12px',
              borderRadius: 'var(--r-md)',
              border: '1px solid var(--border-light)',
              background: 'var(--bg-input)',
              color: 'var(--text-primary)',
              fontSize: 'var(--ts-sm)',
              fontWeight: '500',
              cursor: 'pointer',
              outline: 'none',
            }}
          >
            <option value="minutes">Minutes (Last Hour)</option>
            <option value="hours">Hours (Last 24h)</option>
            <option value="days">Days (Last 30d)</option>
          </select>
        </div>
        {trends.length > 0 ? (
          <Chart key={trendRange} options={chartOpts} series={chartSeries} type="area" height={340} />
        ) : (
          <div className="empty-state">Trends will appear as more data accumulates...</div>
        )}
      </div>

      <Footer />
    </div>
  );
}
