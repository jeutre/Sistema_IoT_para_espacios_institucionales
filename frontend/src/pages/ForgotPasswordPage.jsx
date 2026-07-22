import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import loginBg from '../assets/imagen01.png';
import logo from '../assets/logo.png';
import './LoginPage.css';

const ForgotPasswordPage = () => {
  const [forgotEmail, setForgotEmail] = useState('');
  const [sent, setSent] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!forgotEmail) {
      alert('Ingresa tu correo electrónico');
      return;
    }
    setSent(true);
  };

  return (
    <div className="login-fullscreen-layout" style={{ backgroundImage: `url(${loginBg})` }}>
      <div className="login-circuit-grid" />
      
      <div className="login-overlay">
        <div className="login-glass-card">
          <div className="card-corner top-left" />
          <div className="card-corner top-right" />
          <div className="card-corner bottom-left" />
          <div className="card-corner bottom-right" />

          <div className="login-brand">
            <img src={logo} alt="Tecnoecuatoriano Logo" className="login-logo" />
            <p className="brand-title">Recuperar Contraseña</p>
          </div>

          {!sent ? (
            <form onSubmit={handleSubmit} className="auth-form">
              <div className="forgot-header">
                <div className="forgot-icon">🔑</div>
                <p className="forgot-text">
                  Ingresa tu correo electrónico y te enviaremos instrucciones para restablecer tu contraseña.
                </p>
              </div>

              <div className="input-group">
                <label><span className="input-icon">📧</span> Correo electrónico</label>
                <input type="email" value={forgotEmail} onChange={(e) => setForgotEmail(e.target.value)}
                  required placeholder="correo@institucion.edu.ec" />
                <div className="input-glow" />
              </div>

              <button type="submit" className="btn-primary cyber-btn">
                ENVIAR INSTRUCCIONES
              </button>

              <div className="auth-switch">
                <span>¿Recordaste tu contraseña?</span>
                <Link to="/login" className="text-btn highlight">Iniciar sesión</Link>
              </div>
            </form>
          ) : (
            <div className="success-panel">
              <div className="success-icon">
                <svg viewBox="0 0 50 50">
                  <circle cx="25" cy="25" r="23" fill="none" stroke="#00d4ff" strokeWidth="3" />
                  <path d="M15 25 L22 32 L35 18" fill="none" stroke="#00d4ff" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </div>
              <h3>Correo Enviado</h3>
              <p>Hemos enviado las instrucciones a <strong>{forgotEmail}</strong>. Revisa tu bandeja de entrada.</p>
              <p className="forgot-spam">
                ¿No lo encuentras? Revisa tu carpeta de spam o{' '}
                <button type="button" className="text-btn" onClick={() => setSent(false)}>intenta de nuevo</button>
              </p>
              <Link to="/login" className="btn-primary cyber-btn" style={{ textDecoration: 'none', display: 'inline-block', maxWidth: '280px' }}>
                VOLVER AL INICIO
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ForgotPasswordPage;