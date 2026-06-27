import { create } from 'zustand';
import api from '../axiosConfig';

const useAuthStore = create((set) => ({
  user: null,
  isAuthenticated: false,
  error: null,
  loading: false,
  
  login: async (username, password) => {
    set({ loading: true, error: null });
    try {
      // BYPASS TOTAL DE LOGIN PARA PRUEBAS: 
      // Ignoramos el backend y dejamos entrar a todo el mundo
      localStorage.setItem('access_token', 'fake-token-para-pruebas');
      set({ user: { username: username || 'Admin' }, isAuthenticated: true, loading: false });
      return true;
    } catch (err) {
      set({ 
        error: 'Error', 
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
    // Idealmente verificar si el token está expirado, por ahora con que exista
    if (token) {
      set({ isAuthenticated: true });
    } else {
      set({ isAuthenticated: false, user: null });
    }
  }
}));

export default useAuthStore;
