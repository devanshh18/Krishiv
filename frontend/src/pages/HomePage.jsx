import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowRight, Activity, ShieldAlert, Droplets } from 'lucide-react';
import Logo from '../components/Logo';
import Footer from '../components/Footer';

const fade = { hidden: { opacity: 0, y: 16 }, show: { opacity: 1, y: 0 } };
const stagger = { show: { transition: { staggerChildren: 0.1 } } };

export default function HomePage() {
  const navigate = useNavigate();

  return (
    <div className="home-page">
      <section className="hero-section">
        <motion.div className="hero-badge" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }}>
          <span className="dot" /> Greenhouse Intelligence Platform
        </motion.div>

        <motion.h1 className="hero-title" variants={fade} initial="hidden" animate="show" transition={{ delay: 0.2 }}>
          Welcome{" "}to{" "}<Logo height={55} useGradient={true} style={{ display: 'inline-block', verticalAlign: 'baseline' }} />
        </motion.h1>

        <motion.p className="hero-subtitle" variants={fade} initial="hidden" animate="show" transition={{ delay: 0.3 }}>
          An intelligent monitoring platform that uses machine learning to optimize
          your greenhouse environment - from health scoring to disease prediction
          and smart irrigation advisory.
        </motion.p>

        <motion.div className="hero-actions" variants={fade} initial="hidden" animate="show" transition={{ delay: 0.4 }}>
          <button className="btn btn-primary" onClick={() => navigate('/dashboard')}>
            Go to Dashboard <ArrowRight size={16} />
          </button>
          <button className="btn btn-secondary" onClick={() => navigate('/about')}>
            Learn More
          </button>
        </motion.div>
      </section>

      <section className="features-section">
        <div className="section-header">
          <div className="section-label">Capabilities</div>
          <h2 className="section-title">What Krishiv Offers</h2>
        </div>

        <motion.div className="features-grid" variants={stagger} initial="hidden" whileInView="show" viewport={{ once: true }}>
          <motion.div className="feature-card" variants={fade}>
            <div className="feature-icon health"><Activity size={22} /></div>
            <h3>Environmental Health Scoring</h3>
            <p>
              Real-time health score (0–100) calculated from 19 sensor parameters using
              a Gradient Boosting model. Get per-parameter breakdowns and
              actionable insights every 60 seconds.
            </p>
          </motion.div>

          <motion.div className="feature-card" variants={fade}>
            <div className="feature-icon disease"><ShieldAlert size={22} /></div>
            <h3>Disease Risk Prediction</h3>
            <p>
              Predict disease risk percentage using climate and moisture data.
              Identify threats like powdery mildew, botrytis, and root rot before
              visible symptoms appear, with specific warnings.
            </p>
          </motion.div>

          <motion.div className="feature-card" variants={fade}>
            <div className="feature-icon irrigation"><Droplets size={22} /></div>
            <h3>Irrigation Advisory</h3>
            <p>
              Smart irrigation recommendations powered by soil analysis,
              climate data, and crop-specific classification. Know exactly
              when and how much to irrigate.
            </p>
          </motion.div>
        </motion.div>

        <motion.div className="metrics-bar" variants={stagger} initial="hidden" whileInView="show" viewport={{ once: true }}>
          {[
            ['3', 'ML Models'],
            ['19+', 'Sensor Parameters'],
            ['60s', 'Update Interval'],
            ['6', 'Crop Types'],
          ].map(([value, label]) => (
            <motion.div className="metric-item" key={label} variants={fade}>
              <div className="metric-value">{value}</div>
              <div className="metric-label">{label}</div>
            </motion.div>
          ))}
        </motion.div>
      </section>

      <Footer />
    </div>
  );
}
