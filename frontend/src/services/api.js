import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || '/api';

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add JWT token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth-storage');
    if (token) {
      try {
        const authData = JSON.parse(token);
        // Zustand persist middleware stores data in 'state' property
        const accessToken = authData?.state?.accessToken || authData?.accessToken;
        if (accessToken) {
          config.headers.Authorization = `Bearer ${accessToken}`;
        }
      } catch (e) {
        // Ignore parsing errors
        console.warn('Failed to parse auth token:', e);
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const token = localStorage.getItem('auth-storage');
        if (token) {
          const authData = JSON.parse(token);
          // Zustand persist middleware stores data in 'state' property
          const refreshToken = authData?.state?.refreshToken || authData?.refreshToken;
          if (refreshToken) {
            const response = await axios.post(`${API_URL}/auth/refresh`, {}, {
              headers: {
                Authorization: `Bearer ${refreshToken}`,
              },
            });
            
            const newToken = response.data.access_token;
            // Update stored token - preserve Zustand structure
            const updatedAuth = {
              ...authData,
              state: {
                ...authData.state,
                accessToken: newToken,
              },
            };
            localStorage.setItem('auth-storage', JSON.stringify(updatedAuth));
            
            originalRequest.headers.Authorization = `Bearer ${newToken}`;
            return api(originalRequest);
          }
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem('auth-storage');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;

