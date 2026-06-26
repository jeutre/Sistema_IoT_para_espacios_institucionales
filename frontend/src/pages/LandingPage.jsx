import React from 'react';
import { Link } from 'react-router-dom';
import './LandingPage.css';

const LandingPage = () => {
  return (
    <div className="landing-container">
      <div className="glass-container hero-section">
        <h1 className="hero-title">Sistema IoT</h1>
        <h2 className="hero-subtitle">Para Espacios Institucionales Inteligentes</h2>
        <p className="hero-description">
          Conecta, monitorea y administra de manera eficiente los recursos, laboratorios,
          aulas y dispositivos de nuestra institución, todo en tiempo real.
        </p>
        <div className="action-buttons">
          <Link to="/login" className="btn-primary">
            Iniciar Sesión
          </Link>
          <a href="#about" className="btn-secondary">
            Conocer más
          </a>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;
