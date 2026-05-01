import { create } from 'zustand';
import { authAPI } from '../services/api';

// FastAPI 422 e detail array hoy - eta theke readable message banai
function extractErrorMessage(error, fallback) {
  const detail = error?.response?.data?.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    return detail.map(e => {
      const field = Array.isArray(e.loc) ? e.loc[e.loc.length - 1] : '';
      return field ? `${field}: ${e.msg}` : e.msg;
    }).join(' | ');
  }
  if (detail && typeof detail === 'object') return JSON.stringify(detail);
  return fallback;
}


export const useAuthStore = create((set, get) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  isInitialized: false, // Useful to prevent flickering on first load
  error: null,

  login: async (phone, password) => {
    set({ isLoading: true, error: null });
    try {
      const response = await authAPI.login({ phone, password });
      const { access_token, refresh_token, user } = response.data;
      
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      
      set({ user, isAuthenticated: true, isLoading: false });
      return true;
    } catch (error) {
      const errorMessage = extractErrorMessage(error, 'Login failed. Please check your credentials.');
      set({ error: errorMessage, isLoading: false });
      return false;
    }
  },

  register: async (userData) => {
    set({ isLoading: true, error: null });
    try {
      const response = await authAPI.register(userData);
      const { access_token, refresh_token, user } = response.data;
      
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      
      set({ user, isAuthenticated: true, isLoading: false });
      return true;
    } catch (error) {
      const errorMessage = extractErrorMessage(error, 'Registration failed');
      set({ error: errorMessage, isLoading: false });
      return false;
    }
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    set({ user: null, isAuthenticated: false, error: null });
  },

  checkAuth: async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      set({ isAuthenticated: false, user: null, isInitialized: true });
      return false;
    }
    
    try {
      set({ isLoading: true });
      const response = await authAPI.me();
      set({ user: response.data, isAuthenticated: true, isLoading: false, isInitialized: true });
      return true;
    } catch (error) {
      // Logic: Only clear tokens if the error is a 401 (Unauthorized)
      if (error.response?.status === 401) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        set({ user: null, isAuthenticated: false });
      }
      set({ isLoading: false, isInitialized: true });
      return false;
    }
  },

  clearError: () => set({ error: null }),
}));

export default useAuthStore;