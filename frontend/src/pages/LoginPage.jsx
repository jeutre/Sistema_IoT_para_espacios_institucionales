import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import loginBgEs from '../assets/login-bg-es.png';
import logo from '../assets/logo.png';
import './LoginPage.css';

const LoginPage = () => {
  const [formData, setFormData] = useState({ username: '', password: '' });
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const navigate = useNavigate();
  const loginAction = useAuthStore((state) => state.login);
  const storeError = useAuthStore((state) => state.error);
  const storeLoading = useAuthStore((state) => state.loading);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
    
    // Validar en tiempo real cuando el usuario modifica
    if (touched[name]) {
      validateField(name, value);
    }
  };

  const handleBlur = (e) => {
    const { name, value } = e.target;
    setTouched({ ...touched, [name]: true });
    validateField(name, value);
  };

  const validateField = (fieldName, value) => {
    const newErrors = { ...errors };
    
    switch (fieldName) {
      case 'username':
        if (!value.trim()) {
          newErrors.username = 'El usuario es requerido';
        } else if (value.length < 3) {
          newErrors.username = 'Mínimo 3 caracteres';
        } else {
          delete newErrors.username;
        }
        break;
        
      case 'password':
        if (!value) {
          newErrors.password = 'La contraseña es requerida';
        } else if (value.length < 6) {
          newErrors.password = 'Mínimo 6 caracteres';
        } else {
          delete newErrors.password;
        }
        break;
        
      default:
        break;
    }
    
    setErrors(newErrors);
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.username.trim()) {
      newErrors.username = 'El usuario es requerido';
    } else if (formData.username.length < 3) {
      newErrors.username = 'Mínimo 3 caracteres';
    }
    
    if (!formData.password) {
      newErrors.password = 'La contraseña es requerida';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Mínimo 6 caracteres';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    
    // Marcar todos los campos como tocados
    setTouched({
      username: true,
      password: true
    });
    
    if (!validateForm()) {
      return;
    }
    
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
                onBlur={handleBlur}
                required 
                placeholder="Ingresa tu usuario"
                autoComplete="username"
                className={errors.username ? 'input-error' : ''}
              />
              <div className="input-glow"></div>
              {errors.username && (
                <div className="validation-error">{errors.username}</div>
              )}
            </div>

            <div className="input-group cyber-input">
              <label htmlFor="password">Contraseña</label>
              <input 
                type="password" 
                id="password"
                name="password" 
                value={formData.password}
                onChange={handleChange}
                onBlur={handleBlur}
                required 
                placeholder="••••••••"
                autoComplete="current-password"
                className={errors.password ? 'input-error' : ''}
              />
              <div className="input-glow"></div>
              {errors.password && (
                <div className="validation-error">{errors.password}</div>
              )}
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
