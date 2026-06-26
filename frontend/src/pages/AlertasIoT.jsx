import React, { useEffect } from 'react';
import useIotStore from '../store/iotStore';
import './AlertasIoT.css';

const AlertasIoT = () => {
  const { alertas, fetchAlertas, loading } = useIotStore();

  useEffect(() => {
    fetchAlertas();
  }, [fetchAlertas]);

  return (
    <div className="alertas-container">
      <header className="dashboard-header">
        <h1>Centro de Alertas IoT</h1>
        <p>Notificaciones críticas, errores de conexión y advertencias de sensores físicos.</p>
      </header>

      <div className="glass-container alertas-wrapper">
        <div className="alertas-list">
          {alertas.length === 0 ? (
            <p className="no-alertas">No hay alertas activas en el sistema.</p>
          ) : (
            alertas.map(alerta => (
              <div key={alerta.id} className={`alerta-item nivel-${alerta.nivel}`}>
                <div className="alerta-icon">
                  {alerta.nivel === 'critico' && '🔥'}
                  {alerta.nivel === 'alto' && '⚠️'}
                  {alerta.nivel === 'medio' && 'ℹ️'}
                </div>
                <div className="alerta-content">
                  <div className="alerta-header">
                    <h4>{alerta.dispositivo} <span className="alerta-tipo">({alerta.tipo})</span></h4>
                    <span className="alerta-tiempo">{alerta.tiempo}</span>
                  </div>
                  <p className="alerta-mensaje">{alerta.mensaje}</p>
                </div>
                <button className="btn-secondary btn-sm alerta-action">Atender</button>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default AlertasIoT;
