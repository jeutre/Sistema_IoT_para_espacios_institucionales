import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Dashboard.css';

const Dashboard = () => {
  const navigate = useNavigate();

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>Centro de Comando IoT</h1>
        <p>Estado global del campus inteligente y telemetría de sensores.</p>
      </header>

      <div className="widgets-grid">
        <div className="glass-container widget" onClick={() => navigate('/dashboard/dispositivos')} style={{cursor: 'pointer'}}>
          <h3>Dispositivos Activos</h3>
          <div className="widget-value text-cyan">42 / 50</div>
          <p className="mt-2 text-sm text-muted">Módulos ESP32 en línea</p>
        </div>
        
        <div className="glass-container widget" onClick={() => navigate('/dashboard/alertas')} style={{cursor: 'pointer'}}>
          <h3>Alertas Críticas</h3>
          <div className="widget-value text-red">3</div>
          <p className="mt-2 text-sm text-muted">Requieren atención inmediata</p>
        </div>
        
        <div className="glass-container widget" onClick={() => navigate('/dashboard/ocupacion')} style={{cursor: 'pointer'}}>
          <h3>Eficiencia Energética</h3>
          <div className="widget-value text-green">87%</div>
          <p className="mt-2 text-sm text-muted">Consumo dentro de lo esperado</p>
        </div>
        
        <div className="glass-container widget" onClick={() => navigate('/dashboard/ocupacion')} style={{cursor: 'pointer'}}>
          <h3>Ocupación Actual</h3>
          <div className="widget-value text-yellow">12</div>
          <p className="mt-2 text-sm text-muted">Aulas y laboratorios en uso</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
