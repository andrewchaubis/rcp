import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://work-1-fhzbaswqjorhgjxm.prod-runtime.all-hands.dev';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API service functions
export const apiService = {
  // Get available locations and scenarios
  getLocations: () => api.get('/api/locations'),
  getScenarios: () => api.get('/api/scenarios'),

  // Data management
  uploadData: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/api/upload-data', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  generateData: (data) => api.post('/api/generate-data', data),

  // Analysis endpoints
  analyzeProbabilities: (sessionId, data) => 
    api.post(`/api/analyze-probabilities?session_id=${sessionId}`, data),

  predictTrend: (sessionId, data) => 
    api.post(`/api/predict-trend?session_id=${sessionId}`, data),

  // Time series data
  getRainfallTimeseries: (sessionId) => 
    api.get(`/api/rainfall-timeseries/${sessionId}`),

  getDischargeTimeseries: (sessionId) => 
    api.get(`/api/discharge-timeseries/${sessionId}`),

  // CLIMADA endpoints
  climadaAnalyze: (data) => api.post('/api/climada/analyze', data),
  climadaCompareScenarios: (location, returnPeriod = 100) => 
    api.post(`/api/climada/compare-scenarios?location=${location}&return_period=${returnPeriod}`),
  climadaGenerateReport: (data) => api.post('/api/climada/generate-report', data),

  // Session management
  deleteSession: (sessionId) => api.delete(`/api/session/${sessionId}`),
};

export default api;