import { create } from 'zustand';
import api from '../axiosConfig';

const useAuthStore = create((set, get) => ({
  user: null,
  isAuthenticated: false,
  error: null,
  loading: false,
  refreshingToken: false,
  
  login: async (username, password) => {
    set({ loading: true, error: null });
    try {
      // Llamada real al endpoint JWT de Django
      const response = await api.post('/auth/token/', { username, password });
      
      const { access, refresh } = response.data;
      
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      
      set({ user: { username }, isAuthenticated: true, loading: false });
      return true;
    } catch (err) {
      set({ 
        error: err.response?.data?.detail || 'Credenciales inválidas', 
        loading: false 
      });
      return false;
    }
  },
  
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    set({ user: null, isAuthenticated: false, error: null });
  },
  
  checkAuth: () => {
    const token = localStorage.getItem('access_token');
    if (token) {
      set({ isAuthenticated: true });
    } else {
      set({ isAuthenticated: false, user: null });
    }
  },
  
  refreshToken: async () => {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      get().logout();
      return false;
    }
    
    set({ refreshingToken: true });
    
    try {
      const response = await api.post('/auth/token/refresh/', { 
        refresh: refreshToken 
      });
      
      const { access } = response.data;
      localStorage.setItem('access_token', access);
      
      set({ refreshingToken: false, isAuthenticated: true });
      return true;
    } catch (err) {
      console.error('Error al refrescar token:', err);
      get().logout();
      set({ refreshingToken: false });
      return false;
    }
  },
  
  getUserProfile: async () => {
    try {
      const response = await api.get('/auth/perfil/');
      set({ user: response.data });
      return response.data;
    } catch (err) {
      console.error('Error al obtener perfil:', err);
      return null;
    }
  }
}));

export default useAuthStore;
