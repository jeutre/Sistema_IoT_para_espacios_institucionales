import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import useAuthStore from './store/authStore';

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

const ProtectedRoute = ({ children }) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  // Temporalmente quitamos la protección estricta para pruebas sin backend
  // return isAuthenticated ? children : <Navigate to="/login" />;
  return children;
};

function App() {
  const checkAuth = useAuthStore((state) => state.checkAuth);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

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
    </Router>
  );
}

export default App;
