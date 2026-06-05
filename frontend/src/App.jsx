import { useState, useEffect, useCallback } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import DashboardPage from './pages/DashboardPage';
import DiseaseRiskPage from './pages/DiseaseRiskPage';
import IrrigationPage from './pages/IrrigationPage';
import AboutPage from './pages/AboutPage';
import { getLatestDashboard, getTrends } from './api/client';
import './App.css';

const POLL = 60000;

function App() {
  const [dashboardData, setDashboardData] = useState(null);
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastFetch, setLastFetch] = useState(null);
  const [countdown, setCountdown] = useState(60);
  const [trendRange, setTrendRange] = useState('hours');

  const fetchData = useCallback(async () => {
    try {
      const [d, t] = await Promise.all([getLatestDashboard(), getTrends(trendRange)]);
      if (d.data) setDashboardData(d.data);
      if (t.data) setTrends(t.data);
      setLastFetch(new Date());
      setCountdown(60);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, [trendRange]);

  useEffect(() => {
    fetchData();
    const iv = setInterval(fetchData, POLL);
    return () => clearInterval(iv);
  }, [fetchData]);

  useEffect(() => {
    const t = setInterval(() => setCountdown(p => p > 0 ? p - 1 : 60), 1000);
    return () => clearInterval(t);
  }, []);

  return (
    <BrowserRouter>
      <div className="app">
        <Navbar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route
              path="/dashboard"
              element={
                <DashboardPage
                  data={dashboardData}
                  trends={trends}
                  loading={loading}
                  lastFetch={lastFetch}
                  countdown={countdown}
                  trendRange={trendRange}
                  setTrendRange={setTrendRange}
                  refetch={fetchData}
                />
              }
            />
            <Route path="/disease" element={<DiseaseRiskPage />} />
            <Route path="/irrigation" element={<IrrigationPage />} />
            <Route path="/about" element={<AboutPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
