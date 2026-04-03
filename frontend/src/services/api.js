import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getAirQuality = async (lat, lon) => {
  const response = await api.get('/air-quality', { params: { lat, lon } });
  return response.data;
};

export const getPredictions = async (lat, lon, hours = 24) => {
  const response = await api.get('/predict', { params: { lat, lon, hours } });
  return response.data;
};

export const calculateHealthRisk = async (aqi, healthProfile) => {
  const response = await api.post('/health-risk', { aqi, health_profile: healthProfile });
  return response.data;
};

export const searchLocations = async (query) => {
  const response = await api.get('/locations/search', { params: { q: query } });
  return response.data;
};

export const checkApiHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;