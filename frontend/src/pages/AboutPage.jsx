import { motion } from 'framer-motion';
import { Activity, ShieldAlert, Droplets, Database, Cpu, BarChart3, Layers, Zap } from 'lucide-react';
import Logo from '../components/Logo';
import Footer from '../components/Footer';

const fade = { hidden: { opacity: 0, y: 12 }, show: { opacity: 1, y: 0 } };
const stagger = { show: { transition: { staggerChildren: 0.08 } } };

export default function AboutPage() {
  return (
    <div className="about-page">
      <motion.div className="about-hero" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <h1>About{" "}<Logo height={43} useGradient={true} style={{ display: 'inline-block', verticalAlign: 'baseline' }} /></h1>
        <p className="about-intro">
          An intelligent greenhouse monitoring platform that leverages machine learning
          to provide real-time environmental insights, disease risk prediction, and smart irrigation advisory.
        </p>
      </motion.div>

      {/* How It Works */}
      <motion.section className="about-section" variants={stagger} initial="hidden" whileInView="show" viewport={{ once: true }}>
        <h2><Layers size={22} /> How It Works</h2>
        <div className="steps-grid">
          {[
            ['1', 'Data Collection', 'IoT sensors collect 21 environmental parameters every 60 seconds from across the greenhouse.'],
            ['2', 'ML Processing', 'Three specialized ML models process the data \u2014 analyzing health, disease risk, and irrigation needs.'],
            ['3', 'Rule Engine', 'A rule-based engine generates contextual alerts and actionable recommendations from predictions.'],
            ['4', 'Dashboard', 'Results are displayed on a live dashboard with gauges, trend charts, and prioritized alerts.'],
          ].map(([num, title, desc]) => (
            <motion.div className="step-card" key={num} variants={fade}>
              <div className="step-num">{num}</div>
              <h4>{title}</h4>
              <p>{desc}</p>
            </motion.div>
          ))}
        </div>
      </motion.section>

      {/* ML Models */}
      <motion.section className="about-section" variants={stagger} initial="hidden" whileInView="show" viewport={{ once: true }}>
        <h2><Cpu size={22} /> ML Models</h2>
        <p>
          Krishiv uses three specialized machine learning models, each trained on 4,000
          greenhouse samples with 7 algorithms benchmarked and the top 3 tuned via hyperparameter optimization.
        </p>
        <div className="about-cards">
          <motion.div className="about-card" variants={fade}>
            <h3><Activity size={16} style={{ color: 'var(--color-success)' }} /> Health Score Model</h3>
            <p>
              Predicts the overall environmental health score (0-100) using all 21 sensor parameters.
              Uses a 10-parameter weighted scoring system across temperature, humidity, CO2, light,
              soil conditions, and NPK balance.
            </p>
            <div className="model-metric">XGBoost Regressor &middot; R&sup2; = 0.9896</div>
          </motion.div>
          <motion.div className="about-card" variants={fade}>
            <h3><ShieldAlert size={16} style={{ color: 'var(--color-danger)' }} /> Disease Risk Model</h3>
            <p>
              Predicts disease risk percentage (0-100) using 13 climate and moisture parameters.
              Identifies threats like powdery mildew, botrytis, and root rot based on
              humidity, leaf wetness, and VPD patterns.
            </p>
            <div className="model-metric">Gradient Boosting &middot; R&sup2; = 0.9987</div>
          </motion.div>
          <motion.div className="about-card" variants={fade}>
            <h3><Droplets size={16} style={{ color: 'var(--color-info)' }} /> Irrigation Model</h3>
            <p>
              Classifies irrigation need (Low/Medium/High) using 12 soil, climate, and weather
              parameters. Considers soil moisture, pH, EC conductivity, temperature differential,
              and recent irrigation history.
            </p>
            <div className="model-metric">Hist. Gradient Boosting &middot; F1 = 0.9698</div>
          </motion.div>
        </div>
      </motion.section>

      {/* Parameters */}
      <motion.section className="about-section" variants={stagger} initial="hidden" whileInView="show" viewport={{ once: true }}>
        <h2><BarChart3 size={22} /> Sensor Parameters</h2>
        <p>
          The platform monitors 21 raw sensor parameters grouped into three categories,
          plus 7 engineered features calculated in real-time.
        </p>
        <div className="about-cards" style={{ gridTemplateColumns: 'repeat(2, 1fr)' }}>
          <motion.div className="about-card" variants={fade}>
            <h3>Climate and Internal</h3>
            <p>Air Temperature, Humidity, CO2 Level, Light Intensity, Light Hours, Ventilation Rate, VPD (Vapor Pressure Deficit)</p>
          </motion.div>
          <motion.div className="about-card" variants={fade}>
            <h3>Soil and Nutrients</h3>
            <p>Soil Moisture, Soil Temperature, Soil pH, EC Conductivity, Nitrogen, Phosphorus, Potassium, Leaf Wetness Hours</p>
          </motion.div>
          <motion.div className="about-card" variants={fade}>
            <h3>External Weather</h3>
            <p>Outside Temperature, Outside Humidity, Wind Speed</p>
          </motion.div>
          <motion.div className="about-card" variants={fade}>
            <h3>Engineered Features</h3>
            <p>Temperature Differential, Heat Stress Index, NPK Balance, Moisture-EC Ratio, Light Efficiency, Drought Index, Humidity-CO2 Interaction</p>
          </motion.div>
        </div>
      </motion.section>

      {/* Tech Stack */}
      <motion.section className="about-section" variants={stagger} initial="hidden" whileInView="show" viewport={{ once: true }}>
        <h2><Zap size={22} /> Technology Stack</h2>
        <div className="tech-grid">
          {['React + Vite', 'FastAPI', 'scikit-learn', 'XGBoost', 'PostgreSQL', 'ApexCharts', 'SQLAlchemy', 'Framer Motion'].map(t => (
            <motion.div className="tech-item" key={t} variants={fade}>{t}</motion.div>
          ))}
        </div>
      </motion.section>

      <Footer />
    </div>
  );
}
