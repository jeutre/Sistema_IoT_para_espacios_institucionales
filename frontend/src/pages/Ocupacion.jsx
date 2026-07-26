import React, { useEffect, useState } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';
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
    ocupacion, 
    ocupacionTiempoReal, 
    horasPico, 
    fetchOcupacion, 
    fetchOcupacionTiempoReal, 
    fetchHorasPico, 
    loading 
  } = useIotStore();

  const [activeTab, setActiveTab] = useState('realtime'); // 'realtime' or 'history'
  const [dateRange, setDateRange] = useState({ desde: '', hasta: '' });

  useEffect(() => {
    fetchOcupacionTiempoReal();
    const interval = setInterval(() => fetchOcupacionTiempoReal(), 30000);
    return () => clearInterval(interval);
  }, [fetchOcupacionTiempoReal]);

  useEffect(() => {
    if (activeTab === 'history') {
      fetchOcupacion(dateRange.desde, dateRange.hasta);
      fetchHorasPico(dateRange.desde, dateRange.hasta);
    }
  }, [activeTab, dateRange, fetchOcupacion, fetchHorasPico]);

  const handleFilter = (e) => {
    e.preventDefault();
    fetchOcupacion(dateRange.desde, dateRange.hasta);
    fetchHorasPico(dateRange.desde, dateRange.hasta);
  };

  const chartData = {
    labels: horasPico?.detalle_por_hora?.map(h => `${h.hora}:00`) || [],
    datasets: [
      {
        label: 'Eventos de Ocupación',
        data: horasPico?.detalle_por_hora?.map(h => h.total_eventos_ocupado) || [],
        backgroundColor: 'rgba(54, 162, 235, 0.5)',
        borderColor: 'rgb(54, 162, 235)',
        borderWidth: 1,
      },
    ],
  };

  return (
    <div className="page-container">
      <div className="toolbar-row">
        <div className="toolbar-left">
          <div className="tabs">
            <button 
              className={`tab-btn ${activeTab === 'realtime' ? 'active' : ''}`}
              onClick={() => setActiveTab('realtime')}
            >
              Tiempo Real
            </button>
            <button 
              className={`tab-btn ${activeTab === 'history' ? 'active' : ''}`}
              onClick={() => setActiveTab('history')}
            >
              Historial y Estadísticas
            </button>
          </div>
        </div>
        {activeTab === 'realtime' && (
          <div className="toolbar-right">
            <span className="live-badge">
              <span className="live-dot"></span>
              EN VIVO
            </span>
          </div>
        )}
      </div>

      {activeTab === 'realtime' && (
        <div className="ocupacion-grid">
          {loading && ocupacionTiempoReal.length === 0 ? (
            [...Array(6)].map((_, i) => (
              <div key={`sk-${i}`} className="page-card ocupacion-card skeleton">
                <div className="skeleton-title" style={{width: '60%'}}></div>
                <div className="skeleton-value" style={{width: '40%', height: '60px', margin: '1rem auto'}}></div>
                <div className="skeleton-text" style={{width: '80%'}}></div>
              </div>
            ))
          ) : ocupacionTiempoReal.length === 0 ? (
            <div className="page-card empty-card" style={{gridColumn: '1 / -1'}}>
              <p>No hay datos de ocupación disponibles</p>
            </div>
          ) : (
            ocupacionTiempoReal.map((evento, i) => (
              <div key={i} className={`page-card ocupacion-card ${evento.estado}`}>
                <div className="ocupacion-card-header">
                  <div className="ocupacion-card-info">
                    <span className="ocupacion-lab">{evento.laboratorio || 'Sensor'}</span>
                    <span className="ocupacion-device">{evento.dispositivo || '?'}</span>
                  </div>
                  <div className={`ocupacion-indicator ${evento.estado}`}>
                    <span className="indicator-pulse"></span>
                    {evento.estado === 'ocupado' ? 'OCUPADO' : 'LIBRE'}
                  </div>
                </div>
                <div className="ocupacion-card-body">
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
              </div>
            ))
          )}
        </div>
      )}

      {activeTab === 'history' && (
        <div className="history-container">
          <div className="filter-bar page-card" style={{padding: '1rem', marginBottom: '1.5rem', display: 'flex', gap: '1rem', alignItems: 'flex-end'}}>
            <div className="form-group" style={{marginBottom: 0}}>
              <label>Desde:</label>
              <input type="date" className="form-control" value={dateRange.desde} onChange={e => setDateRange({...dateRange, desde: e.target.value})} />
            </div>
            <div className="form-group" style={{marginBottom: 0}}>
              <label>Hasta:</label>
              <input type="date" className="form-control" value={dateRange.hasta} onChange={e => setDateRange({...dateRange, hasta: e.target.value})} />
            </div>
            <button className="btn-primary" onClick={handleFilter}>Filtrar</button>
          </div>

          <div className="dashboard-grid" style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem'}}>
            <div className="page-card" style={{padding: '1.5rem'}}>
              <h3>Horas Pico de Ocupación</h3>
              {horasPico?.detalle_por_hora?.length > 0 ? (
                <Bar 
                  data={chartData} 
                  options={{ responsive: true, plugins: { legend: { position: 'top' } } }} 
                />
              ) : (
                <p className="empty-state">No hay suficientes datos</p>
              )}
            </div>

            <div className="page-card card-table-wrapper" style={{maxHeight: '400px', overflowY: 'auto'}}>
              <table className="data-table">
                <thead style={{position: 'sticky', top: 0, zIndex: 1}}>
                  <tr>
                    <th>Fecha y Hora</th>
                    <th>Estado</th>
                  </tr>
                </thead>
                <tbody>
                  {ocupacion.map(evt => (
                    <tr key={evt.id}>
                      <td>{new Date(evt.registrado_en).toLocaleString('es-EC')}</td>
                      <td>
                        <span className={`status-badge ${evt.estado === 'ocupado' ? 'offline' : 'online'}`}>
                          {evt.estado === 'ocupado' ? 'Ocupado' : 'Vacío'}
                        </span>
                      </td>
                    </tr>
                  ))}
                  {ocupacion.length === 0 && (
                    <tr><td colSpan="2" className="empty-state">No hay eventos en este rango</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Ocupacion;