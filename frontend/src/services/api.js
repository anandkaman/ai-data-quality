import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth APIs
export const register = async (userData) => {
  const response = await api.post('/auth/register', userData);
  return response.data;
};

export const login = async (credentials) => {
  const response = await api.post('/auth/login', credentials);
  if (response.data.access_token) {
    localStorage.setItem('token', response.data.access_token);
  }
  return response.data;
};

export const logout = () => {
  localStorage.removeItem('token');
};

export const getCurrentUser = async () => {
  const response = await api.get('/auth/me');
  return response.data;
};

// Dataset APIs
export const uploadDataset = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const token = localStorage.getItem('token');
  const response = await axios.post(`${API_BASE_URL}/upload/`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
      'Authorization': `Bearer ${token}`
    },
  });
  
  return response.data;
};

export const assessQuality = async (datasetId) => {
  const response = await api.post(`/assessment/${datasetId}`);
  return response.data;
};

export const getQualityReport = async (datasetId) => {
  const response = await api.get(`/assessment/${datasetId}/report`);
  return response.data;
};

export const detectAnomalies = async (datasetId) => {
  const response = await api.post(`/anomaly/${datasetId}`);
  return response.data;
};

export const getAnomalyDetails = async (datasetId) => {
  const response = await api.get(`/anomaly/${datasetId}/details`);
  return response.data;
};

export const generateRecommendations = async (datasetId) => {
  const response = await api.post(`/recommendations/${datasetId}`);
  return response.data;
};

export const getRecommendations = async (datasetId) => {
  const response = await api.get(`/recommendations/${datasetId}`);
  return response.data;
};

export default api;
