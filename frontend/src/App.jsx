import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import useAuthStore from './store/authStore';
import useThemeStore from './store/themeStore';

import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import BiometricPage from './pages/BiometricPage';
import PortalLayout from './pages/PortalLayout';
import Dashboard from './pages/Dashboard';
import Profile from './pages/Profile';
import Dispositivos from './pages/Dispositivos';
import Ocupacion from './pages/Ocupacion';
import AlertasIoT from './pages/AlertasIoT';
import Reportes from './pages/Reportes';
import Auditoria from './pages/Auditoria';
import ToastContainer from './components/ToastContainer';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuthStore();
  
  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Verificando autenticación...</p>
      </div>
    );
  }
  
  return isAuthenticated ? children : <Navigate to="/login" />;
};

function App() {
  const checkAuth = useAuthStore((state) => state.checkAuth);
  const applyTheme = useThemeStore((state) => state.applyTheme);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  useEffect(() => {
    // Inicializar el tema cuando la aplicación se carga
    applyTheme();
    
    // Escuchar cambios en las preferencias del sistema
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = () => {
      const theme = useThemeStore.getState().theme;
      if (theme === 'system') {
        applyTheme();
      }
    };
    
    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [applyTheme]);

  return (
    <Router>
      <div className="app-container">
        <Routes>
          {/* Zona Pública */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/biometria" element={<BiometricPage />} />

          {/* Zona Privada (Centro de Comando IoT) */}
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <PortalLayout />
              </ProtectedRoute>
            } 
          >
            {/* Sub-rutas del portal IoT */}
            <Route index element={<Dashboard />} />
            <Route path="perfil" element={<Profile />} />
            <Route path="dispositivos" element={<Dispositivos />} />
            <Route path="ocupacion" element={<Ocupacion />} />
            <Route path="alertas" element={<AlertasIoT />} />
            
            <Route path="reportes" element={<Reportes />} />
            <Route path="auditoria" element={<Auditoria />} />
          </Route>
        </Routes>
      </div>
      <ToastContainer />
    </Router>
  );
}

export default App;
