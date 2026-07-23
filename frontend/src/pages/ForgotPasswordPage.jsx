import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import loginBgEs from '../assets/imagen01.png';
import logo from '../assets/logo.png';
import './LoginPage.css';
import './RegisterPage.css';

const ForgotPasswordPage = () => {
  const [email, setEmail] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isEmailSent, setIsEmailSent] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    // Aquí puedes agregar la lógica para enviar el correo de recuperación
    // Por ahora, simulamos un envío exitoso después de 1.5 segundos
    await new Promise(resolve => setTimeout(resolve, 1500));
    setIsEmailSent(true);
    setIsSubmitting(false);
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
            <p>{isEmailSent ? 'Correo Enviado' : 'Recuperar Contraseña'}</p>
          </div>

          {isEmailSent ? (
            <div style={{ textAlign: 'center', color: 'rgba(255,255,255,0.9)' }}>
              <p style={{ marginBottom: '1.5rem' }}>
                Hemos enviado un correo electrónico a <strong>{email}</strong> con instrucciones para restablecer tu contraseña.
              </p>
              <button
                type="button"
                className="btn-primary cyber-btn"
                onClick={() => navigate('/login')}
              >
                Volver al Login
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="auth-form cyber-form">
              <div className="input-group cyber-input">
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  placeholder="CORREO ELECTRÓNICO"
                />
                <div className="input-glow"></div>
              </div>

              <button
                type="submit"
                className="btn-primary cyber-btn"
                disabled={isSubmitting}
              >
                {isSubmitting ? 'ENVIANDO...' : 'ENVIAR ENLACE DE RECUPERACIÓN'}
              </button>

              <button
                type="button"
                className="btn-secondary cyber-btn outline-btn"
                onClick={() => navigate('/login')}
              >
                Volver al Login
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default ForgotPasswordPage;
