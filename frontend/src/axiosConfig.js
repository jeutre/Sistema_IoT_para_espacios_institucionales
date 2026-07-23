import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/v1',
  timeout: 10000,
});

// Interceptor de peticiones
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor de respuestas con manejo de refresh token
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // Si el error es 401 y no es una solicitud de refresh token
    if (error.response && error.response.status === 401 && !originalRequest._retry && !originalRequest.url.includes('/auth/token/refresh/')) {
      originalRequest._retry = true;
      
      try {
        // Intentar refrescar el token
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
          throw new Error('No hay refresh token disponible');
        }
        
        const refreshResponse = await axios.post(
          'http://127.0.0.1:8000/api/v1/auth/token/refresh/',
          { refresh: refreshToken },
          { baseURL: '' }
        );
        
        const { access } = refreshResponse.data;
        localStorage.setItem('access_token', access);
        
        // Reintentar la solicitud original con el nuevo token
        originalRequest.headers.Authorization = `Bearer ${access}`;
        return api(originalRequest);
        
      } catch (refreshError) {
        // Si el refresh falla, limpiar tokens y redirigir al login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        
        // Solo redirigir si estamos en el navegador
        if (typeof window !== 'undefined') {
          window.location.href = '/login';
        }
        
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;
