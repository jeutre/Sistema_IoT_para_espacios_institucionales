import React, { useState } from 'react';
import './Auditoria.css';

const Auditoria = () => {
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('todos');

  const logs = [
    { id: 1001, usuario: 'admin_master', ip: '192.168.1.10', fecha: '2026-06-25 08:30:12', accion: 'Login Exitoso', tipo: 'info' },
    { id: 1002, usuario: 'aortega', ip: '200.15.20.5', fecha: '2026-06-25 09:15:00', accion: 'Intento Fallido', tipo: 'danger' },
    { id: 1003, usuario: 'sistema', ip: 'localhost', fecha: '2026-06-25 10:00:00', accion: 'Backup Automático', tipo: 'info' },
    { id: 1004, usuario: 'mgarcia', ip: '192.168.1.45', fecha: '2026-06-25 10:45:22', accion: 'Login Exitoso', tipo: 'info' },
    { id: 1005, usuario: 'desconocido', ip: '10.0.0.99', fecha: '2026-06-25 11:00:00', accion: 'Acceso Denegado', tipo: 'warning' },
    { id: 1006, usuario: 'jsmith', ip: '192.168.1.100', fecha: '2026-06-25 11:30:00', accion: 'Login Exitoso', tipo: 'info' },
  ];

  const filtered = logs.filter(log => {
    const matchesSearch = log.usuario.toLowerCase().includes(search.toLowerCase()) || log.ip.includes(search);
    const matchesFilter = filter === 'todos' || log.accion.toLowerCase().includes(filter.toLowerCase());
    return matchesSearch && matchesFilter;
  });

  const getTipoIcon = (tipo) => {
    const icons = {
      info: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#00f0ff" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>,
      danger: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ff003c" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>,
      warning: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ffdd00" strokeWidth="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>,
    };
    return icons[tipo] || null;
  };

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
              placeholder="Buscar por usuario o IP..." 
              className="search-input"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <select className="filter-select" value={filter} onChange={(e) => setFilter(e.target.value)}>
            <option value="todos">Todos los eventos</option>
            <option value="exitoso">Login Exitoso</option>
            <option value="fallido">Intento Fallido</option>
            <option value="denegado">Acceso Denegado</option>
            <option value="backup">Backup</option>
          </select>
        </div>
        <div className="toolbar-right">
          <span className="stat-chip">
            <span className="chip-dot green"></span>
            Total: {logs.length} registros
          </span>
        </div>
      </div>

      <div className="page-card">
        <div className="card-table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Usuario</th>
                <th>IP</th>
                <th>Fecha y Hora</th>
                <th>Acción</th>
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr><td colSpan="5" className="empty-state">No se encontraron registros</td></tr>
              ) : (
                filtered.map(log => (
                  <tr key={log.id}>
                    <td className="cell-mono">#{log.id}</td>
                    <td className="cell-highlight">{log.usuario}</td>
                    <td className="cell-mono">{log.ip}</td>
                    <td className="cell-muted">{log.fecha}</td>
                    <td>
                      <div className="action-cell">
                        {getTipoIcon(log.tipo)}
                        <span className={`action-badge ${log.tipo}`}>{log.accion}</span>
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

export default Auditoria;