import React, { useEffect } from 'react';
import useIotStore from '../store/iotStore';
import './Ocupacion.css';

const Ocupacion = () => {
  const { ocupacion, fetchOcupacion, loading } = useIotStore();

  useEffect(() => {
    fetchOcupacion();
    const interval = setInterval(() => fetchOcupacion(), 30000);
    return () => clearInterval(interval);
  }, [fetchOcupacion]);

  return (
    <div className="page-container">
      <div className="toolbar-row">
        <div className="toolbar-left">
          <div className="ocupacion-stats">
            <div className="stat-chip">
              <span className="chip-dot green"></span>
              Ocupados: {ocupacion.filter(o => o.estado === 'ocupado').length}
            </div>
            <div className="stat-chip">
              <span className="chip-dot cyan"></span>
              Libres: {ocupacion.filter(o => o.estado === 'vacio').length}
            </div>
            <div className="stat-chip">
              <span className="chip-dot yellow"></span>
              Total: {ocupacion.length}
            </div>
          </div>
        </div>
        <div className="toolbar-right">
          <span className="live-badge">
            <span className="live-dot"></span>
            EN VIVO
          </span>
        </div>
      </div>

      <div className="ocupacion-grid">
        {loading && ocupacion.length === 0 ? (
          [...Array(6)].map((_, i) => (
            <div key={`sk-${i}`} className="page-card ocupacion-card skeleton">
              <div className="skeleton-title" style={{width: '60%'}}></div>
              <div className="skeleton-value" style={{width: '40%', height: '60px', margin: '1rem auto'}}></div>
              <div className="skeleton-text" style={{width: '80%'}}></div>
            </div>
          ))
        ) : ocupacion.length === 0 ? (
          <div className="page-card empty-card">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.2)" strokeWidth="1.5">
              <rect x="3" y="3" width="18" height="18" rx="2"/>
              <line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/>
            </svg>
            <p>No hay datos de ocupación disponibles</p>
          </div>
        ) : (
          ocupacion.map(evento => (
            <div key={evento.id} className={`page-card ocupacion-card ${evento.estado}`}>
              <div className="ocupacion-card-header">
                <div className="ocupacion-card-info">
                  <span className="ocupacion-lab">{evento.dispositivo?.identificador || 'Sensor'}</span>
                  <span className="ocupacion-device">ESP32-{evento.dispositivo?.id || '?'}</span>
                </div>
                <div className={`ocupacion-indicator ${evento.estado}`}>
                  <span className="indicator-pulse"></span>
                  {evento.estado === 'ocupado' ? 'OCUPADO' : 'LIBRE'}
                </div>
              </div>
              <div className="ocupacion-card-body">
                <div className="ocupacion-icon">
                  {evento.estado === 'ocupado' ? (
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#ff6b6b" strokeWidth="1.5">
                      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                      <circle cx="9" cy="7" r="4"/>
                    </svg>
                  ) : (
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#00ff66" strokeWidth="1.5">
                      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                      <polyline points="22 4 12 14.01 9 11.01"/>
                    </svg>
                  )}
                </div>
                <h3 className={`ocupacion-status ${evento.estado}`}>
                  {evento.estado === 'ocupado' ? 'Espacio Ocupado' : 'Espacio Disponible'}
                </h3>
                <div className="ocupacion-meta">
                  <span>Última actualización</span>
                  <span className="ocupacion-time">
                    {evento.registrado_en ? new Date(evento.registrado_en).toLocaleTimeString('es-EC', { hour: '2-digit', minute: '2-digit' }) : '—'}
                  </span>
                </div>
              </div>
              <div className="ocupacion-card-footer">
                <div className="ocupacion-signal">
                  <span className="signal-bar active"></span>
                  <span className="signal-bar active"></span>
                  <span className="signal-bar active"></span>
                  <span className="signal-bar"></span>
                </div>
                <span className="ocupacion-sensor-id">ID: {evento.id}</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Ocupacion;