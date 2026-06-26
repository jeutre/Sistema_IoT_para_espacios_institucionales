import axios from 'axios';

// Instancia de Axios
const api = axios.create({
  baseURL: 'http://localhost:8081/api/',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Interceptor para inyectar el token JWT en las peticiones
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

// Interceptor para manejar respuestas (opcionalmente renovar tokens aquí si es necesario)
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Si la autenticación falla globalmente, podemos redirigir al login
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('access_token');
      // window.location.href = '/login'; // Descomentar según flujo final
    }
    return Promise.reject(error);
  }
);

export default api;
