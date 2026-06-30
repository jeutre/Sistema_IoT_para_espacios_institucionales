import React, { useEffect } from 'react';
import useIotStore from '../store/iotStore';
import './Dispositivos.css';

const Dispositivos = () => {
  const { dispositivos, fetchDispositivos, loading } = useIotStore();

  useEffect(() => {
    fetchDispositivos();
  }, [fetchDispositivos]);

  return (
    <div className="dispositivos-container">
      <header className="dashboard-header">
        <h1>Gestión de Dispositivos ESP32</h1>
        <p>Monitoreo y administración de microcontroladores IoT.</p>
      </header>

      <div className="glass-container dispositivos-wrapper">
        <div className="toolbar">
          <button className="btn-primary" onClick={fetchDispositivos} disabled={loading}>
            {loading ? 'Sincronizando...' : '↻ Actualizar Lista'}
          </button>
          <input type="text" placeholder="Buscar por identificador o IP..." className="search-input" />
        </div>

        <table className="dispositivos-table">
          <thead>
            <tr>
              <th>ID Sistema</th>
              <th>Identificador</th>
              <th>Dirección IP</th>
              <th>Laboratorio / Ubicación</th>
              <th>Estado de Red</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {loading && dispositivos.length === 0 ? (
              <>
                {[...Array(5)].map((_, i) => (
                  <tr key={`skeleton-${i}`} className="skeleton-row">
                    <td><div className="skeleton skeleton-id"></div></td>
                    <td><div className="skeleton skeleton-text"></div></td>
                    <td><div className="skeleton skeleton-ip"></div></td>
                    <td><div className="skeleton skeleton-text"></div></td>
                    <td><div className="skeleton skeleton-badge"></div></td>
                    <td><div className="skeleton skeleton-button"></div></td>
                  </tr>
                ))}
              </>
            ) : dispositivos.map(disp => (
              <tr key={disp.id}>
                <td className="log-id">#{disp.id}</td>
                <td className="disp-identificador"><strong>{disp.identificador}</strong></td>
                <td className="disp-ip">{disp.ip}</td>
                <td>{disp.laboratorio?.nombre || 'Sin asignar'}</td>
                <td>
                  <span className={`estado-badge ${disp.estado === 'conectado' ? 'conectado' : 'desconectado'}`}>
                    {disp.estado === 'conectado' ? '● En línea' : '○ Fuera de línea'}
                  </span>
                </td>
                <td>
                  <button className="btn-secondary btn-sm" disabled={disp.estado !== 'conectado'}>Ping</button>
                  <button className="btn-secondary btn-sm ml-2">Configurar</button>
                </td>
              </tr>
            ))}
            {!loading && dispositivos.length === 0 && (
              <tr><td colSpan="6" style={{textAlign:'center', padding:'2rem'}}>No hay dispositivos registrados.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Dispositivos;
