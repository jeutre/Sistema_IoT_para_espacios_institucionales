import React, { useEffect, useState } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import useIotStore from '../store/iotStore';
import './Ocupacion.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const Ocupacion = () => {
  const {
    ocupacion, fetchOcupacion,
    historialOcupacion, fetchHistorialOcupacion,
    dispositivos, fetchDispositivos,
    loading,
  } = useIotStore();

  const [filtros, setFiltros] = useState({ dispositivo: '', desde: '', hasta: '' });
  const [buscado, setBuscado] = useState(false);

  useEffect(() => {
    fetchOcupacion();
    fetchDispositivos();
    const interval = setInterval(() => fetchOcupacion(), 30000);
    return () => clearInterval(interval);
  }, [fetchOcupacion, fetchDispositivos]);

  const handleBuscarHistorial = (e) => {
    e.preventDefault();
    setBuscado(true);
    fetchHistorialOcupacion(filtros);
  };

  const handleLimpiarFiltros = () => {
    setFiltros({ dispositivo: '', desde: '', hasta: '' });
    setBuscado(false);
  };

  const nombreDispositivo = (id) => {
    const disp = dispositivos.find((d) => d.id === Number(id));
    return disp ? disp.identificador : `#${id}`;
  };

  return (
    <div className="page-container">
      <div className="toolbar-row">
        <div className="toolbar-left">
          <h2 className="ocupacion-page-title">Monitoreo de Ocupación</h2>
        </div>
        <div className="toolbar-right">
          <span className="live-badge">
            <span className="live-dot"></span>
            EN VIVO
          </span>
        </div>
      </div>

      <div className="kpi-panel">
        <div className="kpi-box ocupado">
          <span className="kpi-number">{ocupacion.filter(o => o.estado === 'ocupado').length}</span>
          <span className="kpi-label">Ocupados</span>
        </div>
        <div className="kpi-box libre">
          <span className="kpi-number">{ocupacion.filter(o => o.estado === 'vacio').length}</span>
          <span className="kpi-label">Disponibles</span>
        </div>
        <div className="kpi-box total">
          <span className="kpi-number">{ocupacion.length}</span>
          <span className="kpi-label">Total sensores</span>
        </div>
      </div>

      <div className="ocupacion-grid">
        {loading && ocupacion.length === 0 ? (
          [...Array(3)].map((_, i) => (
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
          ocupacion.map((evento, idx) => (
            <div key={idx} className={`page-card ocupacion-card ${evento.estado}`}>
              <div className="ocupacion-card-header">
                <div className="ocupacion-card-info">
                  <span className="ocupacion-lab">{evento.laboratorio || 'Laboratorio'}</span>
                  <span className="ocupacion-device">{evento.dispositivo || 'Sensor'}</span>
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
                    {evento.ultima_vez ? new Date(evento.ultima_vez).toLocaleTimeString('es-EC', { hour: '2-digit', minute: '2-digit' }) : '—'}
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
                <span className="ocupacion-sensor-id">{evento.dispositivo || ''}</span>
              </div>
            </div>
          ))
        )}
      </div>

      <div className="glass-container historial-wrapper">
        <h3 className="form-title">Historial de ocupación</h3>
        <form onSubmit={handleBuscarHistorial} className="historial-filtros">
          <select
            value={filtros.dispositivo}
            onChange={(e) => setFiltros({ ...filtros, dispositivo: e.target.value })}
          >
            <option value="">Todos los dispositivos</option>
            {dispositivos.map((d) => (
              <option key={d.id} value={d.id}>{d.identificador}</option>
            ))}
          </select>
          <input
            type="date"
            value={filtros.desde}
            onChange={(e) => setFiltros({ ...filtros, desde: e.target.value })}
          />
          <input
            type="date"
            value={filtros.hasta}
            onChange={(e) => setFiltros({ ...filtros, hasta: e.target.value })}
          />
          <button className="btn-primary" type="submit" disabled={loading}>
            {loading ? 'Buscando...' : 'Buscar historial'}
          </button>
          <button type="button" className="btn-secondary" onClick={handleLimpiarFiltros}>
            Limpiar
          </button>
        </form>

        <table className="historial-table">
          <thead>
            <tr>
              <th>Dispositivo</th>
              <th>Estado</th>
              <th>Fecha y hora</th>
            </tr>
          </thead>
          <tbody>
            {historialOcupacion.map((evento) => (
              <tr key={evento.id}>
                <td>{nombreDispositivo(evento.dispositivo)}</td>
                <td>
                  <span className={`estado-badge ${evento.estado === 'ocupado' ? 'desconectado' : 'conectado'}`}>
                    {evento.estado === 'ocupado' ? '● Ocupado' : '○ Vacío'}
                  </span>
                </td>
                <td>{new Date(evento.registrado_en).toLocaleString()}</td>
              </tr>
            ))}
            {buscado && !loading && historialOcupacion.length === 0 && (
              <tr><td colSpan="3" style={{ textAlign: 'center', padding: '2rem' }}>No hay eventos para los filtros seleccionados.</td></tr>
            )}
            {!buscado && (
              <tr><td colSpan="3" style={{ textAlign: 'center', padding: '2rem' }}>Selecciona un rango de fechas y presiona "Buscar historial".</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Ocupacion;
