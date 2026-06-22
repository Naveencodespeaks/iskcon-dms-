import axios from 'axios';

// Create an axios instance configured with the API base URL.  The
// base URL can be set via NEXT_PUBLIC_API_URL environment variable,
// which is injected at build time by Next.js.  If not provided,
// default to the local backend.  All requests automatically include
// the Authorization header if a token exists in localStorage.

const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: apiBaseUrl,
});

// Request interceptor to attach Bearer token
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers = config.headers || {};
      config.headers['Authorization'] = `Bearer ${token}`;
    }
  }
  return config;
});

export default api;