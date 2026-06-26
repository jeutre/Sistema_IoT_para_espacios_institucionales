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

// Interceptor de respuestas (Para manejar expiración de token en el futuro)
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response && error.response.status === 401) {
      // Si el backend dice que no estamos autorizados (token expirado)
      // Se podría intentar un refresh, o simplemente desloguear:
      localStorage.removeItem('access_token');
      // window.location.href = '/login'; // Opcional: forzar redirección
    }
    return Promise.reject(error);
  }
);

export default api;
