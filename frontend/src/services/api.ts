import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with default config
export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('[API Request Error]', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`[API Response] ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('[API Response Error]', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Portfolio API
export const portfolioApi = {
  getAll: async () => {
    const response = await api.get('/api/v1/portfolios');
    return response.data;
  },
  
  getById: async (id: string) => {
    const response = await api.get(`/api/v1/portfolios/${id}`);
    return response.data;
  },
};

// Stock API
export const stockApi = {
  getBySymbol: async (symbol: string) => {
    const response = await api.get(`/api/v1/stocks/${symbol}`);
    return response.data;
  },
  
  search: async (query: string) => {
    const response = await api.get(`/api/v1/stocks/search`, {
      params: { q: query },
    });
    return response.data;
  },
};

// Health check
export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};
