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
      // Llamada real al endpoint JWT de Django
      const response = await api.post('/auth/token/', { username, password });
      
      const { access, refresh } = response.data;
      
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh); // Opcional
      
      // Como el token JWT simple no siempre trae todos los datos del usuario de golpe,
      // seteamos lo básico, en una app real podríamos decodificar el JWT o llamar a /auth/perfil/
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
    // Idealmente verificar si el token está expirado, por ahora con que exista
    if (token) {
      set({ isAuthenticated: true });
    } else {
      set({ isAuthenticated: false, user: null });
    }
  }
}));

export default useAuthStore;
