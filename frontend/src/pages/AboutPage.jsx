import { motion } from 'framer-motion';
import { Activity, ShieldAlert, Droplets, Database, Cpu, BarChart3, Layers, Zap, Target, Lightbulb } from 'lucide-react';
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

      {/* What & Why */}
      <motion.section className="about-section" variants={stagger} initial="hidden" whileInView="show" viewport={{ once: true }}>
        <h2><Target size={22} /> What is Krishiv?</h2>
        <p>
          Krishiv is a full-stack, ML-powered greenhouse intelligence system designed to help farmers
          and greenhouse operators make smarter decisions. It continuously monitors environmental
          conditions through IoT sensors, processes the data through three specialized machine learning
          models, and delivers actionable insights on a real-time dashboard.
        </p>
        <div className="about-cards" style={{ gridTemplateColumns: 'repeat(2, 1fr)' }}>
          <motion.div className="about-card" variants={fade}>
            <h3><Lightbulb size={16} style={{ color: 'var(--color-warning)' }} /> The Problem</h3>
            <p>
              Traditional greenhouse management relies heavily on manual observation and guesswork.
              Farmers often detect diseases too late, over-irrigate or under-irrigate crops, and struggle
              to maintain optimal growing conditions. This leads to significant crop loss, wasted water,
              and reduced yields.
            </p>
          </motion.div>
          <motion.div className="about-card" variants={fade}>
            <h3><Target size={16} style={{ color: 'var(--color-success)' }} /> Our Solution</h3>
            <p>
              Krishiv solves this by automating environmental monitoring and applying machine learning
              to predict health scores, disease risks, and irrigation needs in real time. Farmers receive
              timely alerts and specific recommendations, allowing them to act before problems escalate
              — saving crops, conserving water, and improving overall yield.
            </p>
          </motion.div>
        </div>
      </motion.section>

      {/* How It Works */}
      <motion.section className="about-section" variants={stagger} initial="hidden" whileInView="show" viewport={{ once: true }}>
        <h2><Layers size={22} /> How It Works</h2>
        <div className="steps-grid">
          {[
            ['1', 'Data Collection', 'IoT sensors collect 19 environmental parameters every 60 seconds from across the greenhouse.'],
            ['2', 'ML Processing', 'Three Gradient Boosting models process the data — analyzing health, disease risk, and irrigation needs.'],
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
          Krishiv uses three specialized machine learning models, each trained on a curated dataset of
          855 greenhouse samples. All three models use scikit-learn's Gradient Boosting algorithm,
          tuned with hyperparameter optimization for best performance.
        </p>
        <div className="about-cards">
          <motion.div className="about-card" variants={fade}>
            <h3><Activity size={16} style={{ color: 'var(--color-success)' }} /> Health Score Model</h3>
            <p>
              Predicts the overall environmental health score (0–100) using all 19 sensor parameters
              plus 7 engineered features. Scores are broken down per-parameter across temperature,
              humidity, CO₂, light, soil conditions, and NPK balance.
            </p>
            <div className="model-metric">Gradient Boosting Regressor &middot; R&sup2; = 0.79 &middot; MAE = 2.96</div>
          </motion.div>
          <motion.div className="about-card" variants={fade}>
            <h3><ShieldAlert size={16} style={{ color: 'var(--color-danger)' }} /> Disease Risk Model</h3>
            <p>
              Predicts disease risk percentage (0–100) using 13 climate and moisture parameters.
              Identifies threats like powdery mildew, botrytis, and root rot based on
              humidity, leaf wetness, and VPD patterns.
            </p>
            <div className="model-metric">Gradient Boosting Regressor &middot; R&sup2; = 0.74 &middot; MAE = 3.52</div>
          </motion.div>
          <motion.div className="about-card" variants={fade}>
            <h3><Droplets size={16} style={{ color: 'var(--color-info)' }} /> Irrigation Model</h3>
            <p>
              Classifies irrigation need (Low / Medium / High) using 12 soil, climate, and weather
              parameters. Considers soil moisture, pH, EC conductivity, temperature differential,
              and recent irrigation history.
            </p>
            <div className="model-metric">Gradient Boosting Classifier &middot; Accuracy = 77% &middot; F1 = 0.76</div>
          </motion.div>
        </div>
      </motion.section>

      {/* Parameters */}
      <motion.section className="about-section" variants={stagger} initial="hidden" whileInView="show" viewport={{ once: true }}>
        <h2><BarChart3 size={22} /> Sensor Parameters</h2>
        <p>
          The platform monitors 19 raw sensor parameters grouped into three categories,
          plus 7 engineered features calculated in real-time.
        </p>
        <div className="about-cards" style={{ gridTemplateColumns: 'repeat(2, 1fr)' }}>
          <motion.div className="about-card" variants={fade}>
            <h3>Climate and Internal</h3>
            <p>Air Temperature, Humidity, CO₂ Level, Light Intensity, Light Hours, Ventilation Rate, VPD (Vapor Pressure Deficit)</p>
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
            <p>Temperature Differential, Heat Stress Index, NPK Balance, Moisture-EC Ratio, Light Efficiency, Drought Index, Humidity-CO₂ Interaction</p>
          </motion.div>
        </div>
      </motion.section>

      {/* Tech Stack */}
      <motion.section className="about-section" variants={stagger} initial="hidden" whileInView="show" viewport={{ once: true }}>
        <h2><Zap size={22} /> Technology Stack</h2>
        <div className="tech-grid">
          {['React + Vite', 'FastAPI', 'scikit-learn', 'Gradient Boosting', 'PostgreSQL', 'ApexCharts', 'SQLAlchemy', 'Framer Motion'].map(t => (
            <motion.div className="tech-item" key={t} variants={fade}>{t}</motion.div>
          ))}
        </div>
      </motion.section>

      <Footer />
    </div>
  );
}
