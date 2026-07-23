import React, { useEffect, useState } from 'react';
import useIotStore from '../store/iotStore';
import './AlertasIoT.css';

const AlertasIoT = () => {
  const { alertas, fetchAlertas, loading } = useIotStore();
  const [filter, setFilter] = useState('todas');

  useEffect(() => {
    fetchAlertas();
  }, [fetchAlertas]);

  const filtered = filter === 'todas' ? alertas : alertas.filter(a => a.nivel === filter);

  const getNivelIcon = (nivel) => {
    const icons = {
      critico: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ff003c" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>,
      alto: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ff6600" strokeWidth="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>,
      medio: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ffdd00" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>,
      bajo: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#00f0ff" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/></svg>,
    };
    return icons[nivel] || null;
  };

  const levelCounts = {
    critico: alertas.filter(a => a.nivel === 'critico').length,
    alto: alertas.filter(a => a.nivel === 'alto').length,
    medio: alertas.filter(a => a.nivel === 'medio').length,
    bajo: alertas.filter(a => a.nivel === 'bajo').length,
  };

  return (
    <div className="page-container">
      <div className="toolbar-row">
        <div className="toolbar-left">
          <div className="alert-filters">
            {['todas', 'critico', 'alto', 'medio', 'bajo'].map(nivel => (
              <button
                key={nivel}
                className={`filter-chip ${filter === nivel ? 'active' : ''} ${nivel}`}
                onClick={() => setFilter(nivel)}
              >
                {nivel !== 'todas' && <span className={`chip-indicator ${nivel}`}></span>}
                {nivel === 'todas' ? 'Todas' : nivel.charAt(0).toUpperCase() + nivel.slice(1)}
                {nivel !== 'todas' && <span className="chip-count">{levelCounts[nivel]}</span>}
              </button>
            ))}
          </div>
        </div>
        <button className="btn-primary" onClick={fetchAlertas} disabled={loading}>
          ↻ Actualizar
        </button>
      </div>

      <div className="page-card">
        {loading && alertas.length === 0 ? (
          <div className="alert-list">
            {[...Array(4)].map((_, i) => (
              <div key={`sk-${i}`} className="alert-item skeleton" style={{display: 'flex', gap: '1rem', padding: '1rem'}}>
                <div className="skeleton-cell" style={{width: '24px', height: '24px', borderRadius: '50%'}}></div>
                <div style={{flex: 1}}>
                  <div className="skeleton-cell" style={{width: '40%', marginBottom: '0.5rem'}}></div>
                  <div className="skeleton-cell" style={{width: '70%'}}></div>
                </div>
              </div>
            ))}
          </div>
        ) : filtered.length === 0 ? (
          <div className="alert-empty">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="rgba(0,255,102,0.3)" strokeWidth="1.5">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
              <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
            <p>No hay alertas {filter !== 'todas' ? `de nivel ${filter}` : ''}</p>
          </div>
        ) : (
          <div className="alert-list">
            {filtered.map(alerta => (
              <div key={alerta.id} className={`alert-item nivel-${alerta.nivel}`}>
                <div className="alert-icon">
                  {getNivelIcon(alerta.nivel)}
                </div>
                <div className="alert-content">
                  <div className="alert-header">
                    <div className="alert-device">
                      <span className="alert-device-name">{alerta.dispositivo}</span>
                      <span className="alert-type">{alerta.tipo}</span>
                    </div>
                    <span className="alert-time">{alerta.tiempo}</span>
                  </div>
                  <p className="alert-message">{alerta.mensaje}</p>
                </div>
                <div className="alert-actions">
                  <span className={`alert-level-badge ${alerta.nivel}`}>{alerta.nivel}</span>
                  <button className="btn-secondary btn-sm">Atender</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default AlertasIoT;