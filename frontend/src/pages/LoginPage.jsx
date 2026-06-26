import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import loginBgEs from '../assets/login-bg-es.png';
import logo from '../assets/logo.png';
import './LoginPage.css';

const LoginPage = () => {
  const [formData, setFormData] = useState({ username: '', password: '' });
  const navigate = useNavigate();
  const loginAction = useAuthStore((state) => state.login);
  const storeError = useAuthStore((state) => state.error);
  const storeLoading = useAuthStore((state) => state.loading);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    const success = await loginAction(formData.username, formData.password);
    if (success) {
      navigate('/biometria');
    }
  };

  const handleRegister = () => {
    alert("El registro está temporalmente deshabilitado.");
  };

  const handleForgotPassword = () => {
    alert("Función de recuperación de contraseña en desarrollo.");
  };

  return (
    <div 
      className="login-fullscreen-layout" 
      style={{ backgroundImage: `url(${loginBgEs})` }}
    >
      <div className="login-overlay">
        <div className="login-glass-card">
          <div className="login-brand">
            <img src={logo} alt="Tecnoecuatoriano Logo" className="login-logo" />
            <p>Sistema IoT Institucional</p>
          </div>

          {storeError && <div className="error-message">{storeError}</div>}
          
          <form onSubmit={handleLogin} className="auth-form cyber-form">
            <div className="input-group cyber-input">
              <label htmlFor="username">Usuario</label>
              <input 
                type="text" 
                id="username"
                name="username" 
                value={formData.username}
                onChange={handleChange}
                required 
                placeholder="Ingresa tu usuario"
                autoComplete="username"
              />
              <div className="input-glow"></div>
            </div>

            <div className="input-group cyber-input">
              <label htmlFor="password">Contraseña</label>
              <input 
                type="password" 
                id="password"
                name="password" 
                value={formData.password}
                onChange={handleChange}
                required 
                placeholder="••••••••"
                autoComplete="current-password"
              />
              <div className="input-glow"></div>
            </div>

            <div className="forgot-password-link">
              <button type="button" className="text-btn cyber-link" onClick={handleForgotPassword}>
                ¿Olvidaste tu contraseña?
              </button>
            </div>

            <button type="submit" className="btn-primary cyber-btn" disabled={storeLoading}>
              {storeLoading ? <span className="scanning">AUTENTICANDO...</span> : 'INICIAR SESIÓN'}
            </button>
            
            <button type="button" className="btn-secondary cyber-btn outline-btn" onClick={handleRegister}>
              REGISTRARSE
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
