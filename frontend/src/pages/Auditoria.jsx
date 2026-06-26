import React from 'react';
import './Auditoria.css';

const Auditoria = () => {
  const logs = [
    { id: 1001, usuario: 'admin_master', ip: '192.168.1.10', fecha: '2026-06-25 08:30:12', accion: 'Login Exitoso' },
    { id: 1002, usuario: 'aortega', ip: '200.15.20.5', fecha: '2026-06-25 09:15:00', accion: 'Intento Fallido' },
    { id: 1003, usuario: 'sistema', ip: 'localhost', fecha: '2026-06-25 10:00:00', accion: 'Backup Automático' },
    { id: 1004, usuario: 'mgarcia', ip: '192.168.1.45', fecha: '2026-06-25 10:45:22', accion: 'Login Exitoso' }
  ];

  return (
    <div className="auditoria-container">
      <header className="dashboard-header">
        <h1>Visor de Auditoría</h1>
        <p>Registro de seguridad de accesos y eventos críticos del sistema.</p>
      </header>

      <div className="glass-container logs-wrapper">
        <div className="logs-toolbar">
          <input type="text" placeholder="Buscar por usuario o IP..." className="search-input" />
          <select className="filter-select">
            <option>Todos los eventos</option>
            <option>Login Exitoso</option>
            <option>Intento Fallido</option>
          </select>
        </div>

        <table className="logs-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Usuario</th>
              <th>Dirección IP</th>
              <th>Fecha y Hora</th>
              <th>Acción</th>
            </tr>
          </thead>
          <tbody>
            {logs.map(log => (
              <tr key={log.id}>
                <td className="log-id">#{log.id}</td>
                <td className="log-user">{log.usuario}</td>
                <td className="log-ip">{log.ip}</td>
                <td>{log.fecha}</td>
                <td>
                  <span className={`log-badge ${log.accion === 'Intento Fallido' ? 'danger' : 'info'}`}>
                    {log.accion}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Auditoria;
