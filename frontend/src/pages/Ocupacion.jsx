import React, { useEffect } from 'react';
import useIotStore from '../store/iotStore';
import './Ocupacion.css';

const Ocupacion = () => {
  const { ocupacion, fetchOcupacion, loading } = useIotStore();

  useEffect(() => {
    fetchOcupacion();
    
    // Simular polling cada 30 segundos
    const interval = setInterval(() => {
      fetchOcupacion();
    }, 30000);
    return () => clearInterval(interval);
  }, [fetchOcupacion]);

  return (
    <div className="ocupacion-container">
      <header className="dashboard-header">
        <h1>Monitoreo de Ocupación</h1>
        <p>Visor en tiempo real de disponibilidad de aulas y laboratorios detectada por sensores.</p>
      </header>

      <div className="ocupacion-grid">
        {loading && ocupacion.length === 0 ? (
          <>
            {[...Array(6)].map((_, i) => (
              <div key={`skeleton-${i}`} className="glass-container ocupacion-card skeleton">
                <div className="card-header">
                  <div className="skeleton skeleton-title"></div>
                  <div className="skeleton skeleton-badge"></div>
                </div>
                
                <div className="card-body">
                  <div className="skeleton skeleton-icon"></div>
                  <div className="skeleton skeleton-status"></div>
                  <div className="skeleton skeleton-time"></div>
                </div>
              </div>
            ))}
          </>
        ) : ocupacion.map(evento => (
          <div key={evento.id} className={`glass-container ocupacion-card ${evento.estado}`}>
            <div className="card-header">
              <h3>{evento.dispositivo?.identificador}</h3>
              <span className="live-indicator">● LIVE</span>
            </div>
            
            <div className="card-body">
              <div className="status-icon">
                {evento.estado === 'ocupado' ? '👥' : '✅'}
              </div>
              <h2 className="status-text">
                {evento.estado === 'ocupado' ? 'Aula Ocupada' : 'Aula Vacía'}
              </h2>
              <p className="time-text">Última actualización: {new Date(evento.registrado_en).toLocaleTimeString()}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Ocupacion;
