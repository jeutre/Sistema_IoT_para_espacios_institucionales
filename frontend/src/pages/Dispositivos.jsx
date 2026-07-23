import React, { useEffect, useState } from 'react';
import useIotStore from '../store/iotStore';
import './Dispositivos.css';

const Dispositivos = () => {
  const { dispositivos, fetchDispositivos, loading } = useIotStore();
  const [search, setSearch] = useState('');
  const [filterStatus, setFilterStatus] = useState('todos');

  useEffect(() => {
    fetchDispositivos();
  }, [fetchDispositivos]);

  const filtered = dispositivos.filter(d => {
    const matchesSearch = d.identificador?.toLowerCase().includes(search.toLowerCase()) || 
                          d.ip?.includes(search);
    const matchesFilter = filterStatus === 'todos' || d.estado === filterStatus;
    return matchesSearch && matchesFilter;
  });

  return (
    <div className="page-container">
      <div className="toolbar-row">
        <div className="toolbar-left">
          <div className="toolbar-search">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            <input 
              type="text" 
              placeholder="Buscar por ID o IP..." 
              className="search-input"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <select className="filter-select" value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}>
            <option value="todos">Todos los estados</option>
            <option value="conectado">En línea</option>
            <option value="desconectado">Fuera de línea</option>
          </select>
        </div>
        <button className="btn-primary" onClick={fetchDispositivos} disabled={loading}>
          {loading ? '↻ Sincronizando...' : '↻ Actualizar'}
        </button>
      </div>

      <div className="page-card">
        <div className="card-table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Identificador</th>
                <th>IP</th>
                <th>Ubicación</th>
                <th>Estado</th>
                <th>Última Conexión</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {loading && dispositivos.length === 0 ? (
                [...Array(4)].map((_, i) => (
                  <tr key={`sk-${i}`}>
                    {[...Array(7)].map((_, j) => (
                      <td key={j}><div className="skeleton-cell" style={{width: `${60 + j*10}%`}}></div></td>
                    ))}
                  </tr>
                ))
              ) : filtered.length === 0 ? (
                <tr><td colSpan="7" className="empty-state">No se encontraron dispositivos</td></tr>
              ) : (
                filtered.map(disp => (
                  <tr key={disp.id}>
                    <td className="cell-mono">#{disp.id}</td>
                    <td className="cell-highlight">{disp.identificador}</td>
                    <td className="cell-mono">{disp.ip}</td>
                    <td>{disp.laboratorio?.nombre || '—'}</td>
                    <td>
                      <span className={`status-badge ${disp.estado === 'conectado' ? 'online' : 'offline'}`}>
                        <span className="status-dot"></span>
                        {disp.estado === 'conectado' ? 'En línea' : 'Fuera de línea'}
                      </span>
                    </td>
                    <td className="cell-muted">{disp.ultima_conexion ? new Date(disp.ultima_conexion).toLocaleString() : '—'}</td>
                    <td>
                      <div className="cell-actions">
                        <button className="btn-secondary btn-sm" disabled={disp.estado !== 'conectado'}>Ping</button>
                        <button className="btn-secondary btn-sm">Config</button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Dispositivos;