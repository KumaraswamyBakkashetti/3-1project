import axios from 'axios';

const API_URL = 'http://localhost:8080/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const login = async (username, password) => {
  const response = await api.post('/login', { username, password });
  return response.data;
};

export const runMAS = async (task, code = '') => {
  const response = await api.post('/run_mas', { task, code });
  return response.data;
};

export const getUserRuns = async () => {
  const response = await api.get('/runs/user');
  return response.data;
};

export const getAllRuns = async () => {
  const response = await api.get('/runs/all');
  return response.data;
};

export const getRun = async (runId) => {
  const response = await api.get(`/run/${runId}`);
  return response.data;
};

export const exportCSV = async () => {
  const response = await api.get('/export_csv');
  return response.data;
};

export default api;
