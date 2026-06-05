import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

// Full prediction (all 3 models)
export const predict = (sensorData) => api.post('/predict', sensorData);

// Store a reading
export const storeReading = (sensorData) => api.post('/readings', sensorData);

// Dashboard composite endpoint
export const getLatestDashboard = () => api.get('/latest-dashboard');

// Original latest reading
export const getLatest = () => api.get('/latest');

// Trends
export const getTrends = (range = 'hours') => api.get(`/trends?range=${range}`);

// Disease-only prediction
export const predictDisease = (data) => api.post('/predict/disease', data);

// Irrigation-only prediction
export const predictIrrigation = (data) => api.post('/predict/irrigation', data);

export default api;
