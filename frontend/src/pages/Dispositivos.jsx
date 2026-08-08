import React, { useEffect, useState } from 'react';
import useIotStore from '../store/iotStore';
import api from '../axiosConfig';
import './Dispositivos.css';

const Dispositivos = () => {
  const { dispositivos, fetchDispositivos, laboratorios, fetchLaboratorios, loading } = useIotStore();
  const [search, setSearch] = useState('');
  const [filterStatus, setFilterStatus] = useState('todos');
  const [mensaje, setMensaje] = useState('');
  const [accionando, setAccionando] = useState(null);

  // Edición (Config): asociar laboratorio + editar IP
  const [editando, setEditando] = useState(null);
  const [editIp, setEditIp] = useState('');
  const [editLab, setEditLab] = useState('');

  // HU-07: el estado se actualiza SOLO cada 10 segundos.
  useEffect(() => {
    fetchDispositivos();
    fetchLaboratorios();
    const interval = setInterval(() => fetchDispositivos(), 10000);
    return () => clearInterval(interval);
  }, [fetchDispositivos, fetchLaboratorios]);

  const aviso = (txt) => { setMensaje(txt); setTimeout(() => setMensaje(''), 4000); };

  // Abrir el editor (Config)
  const abrirConfig = (disp) => {
    setEditando(disp);
    setEditIp(disp.ip || '');
    setEditLab(disp.laboratorio || '');
  };

  // Guardar cambios: laboratorio (HU-06) + IP
  const guardarConfig = async () => {
    setAccionando(editando.id);
    try {
      await api.patch(`/dispositivos/esp32/${editando.id}/`, {
        ip: editIp.trim(),
        laboratorio: editLab || null,
      });
      aviso(`ESP32 ${editando.identificador} actualizado.`);
      setEditando(null);
      fetchDispositivos();
    } catch (e) {
      console.error(e);
      aviso('No se pudo guardar (revisa la IP o el laboratorio).');
    } finally {
      setAccionando(null);
    }
  };

  const handleEliminar = async (disp) => {
    if (!window.confirm(`¿Eliminar el ESP32 "${disp.identificador}"? Esta acción no se puede deshacer.`)) return;
    setAccionando(disp.id);
    try {
      await api.delete(`/dispositivos/esp32/${disp.id}/`);
      aviso(`ESP32 ${disp.identificador} eliminado.`);
      fetchDispositivos();
    } catch (e) {
      console.error(e);
      aviso('No se pudo eliminar el dispositivo.');
    } finally {
      setAccionando(null);
    }
  };

  const filtered = dispositivos.filter(d => {
    const matchesSearch = d.identificador?.toLowerCase().includes(search.toLowerCase()) || d.ip?.includes(search);
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
            <input type="text" placeholder="Buscar por ID o IP..." className="search-input"
                   value={search} onChange={(e) => setSearch(e.target.value)} />
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

      {mensaje && (
        <div style={{ margin:'0 0 1rem', padding:'0.6rem 1rem', borderRadius:8,
                      background:'rgba(0,240,255,0.1)', color:'#00f0ff', fontSize:'0.9rem' }}>
          {mensaje}
        </div>
      )}

      <div className="page-card">
        <div className="card-table-wrapper">
          <table className="data-table">
            <thead>
              <tr><th>ID</th><th>Identificador</th><th>IP</th><th>Laboratorio</th><th>Estado</th><th>Última Conexión</th><th>Acciones</th></tr>
            </thead>
            <tbody>
              {loading && dispositivos.length === 0 ? (
                [...Array(4)].map((_, i) => (
                  <tr key={`sk-${i}`}>{[...Array(7)].map((_, j) => (<td key={j}><div className="skeleton-cell" style={{width: `${60 + j*10}%`}}></div></td>))}</tr>
                ))
              ) : filtered.length === 0 ? (
                <tr><td colSpan="7" className="empty-state">No se encontraron dispositivos</td></tr>
              ) : (
                filtered.map(disp => (
                  <tr key={disp.id}>
                    <td className="cell-mono">#{disp.id}</td>
                    <td className="cell-highlight">{disp.identificador}</td>
                    <td className="cell-mono">{disp.ip}</td>
                    <td>{disp.laboratorio_nombre || <span style={{color:'#ffb020'}}>Sin asignar</span>}</td>
                    <td>
                      <span className={`status-badge ${disp.estado === 'conectado' ? 'online' : 'offline'}`}>
                        <span className="status-dot"></span>
                        {disp.estado === 'conectado' ? 'En línea' : 'Fuera de línea'}
                      </span>
                    </td>
                    <td className="cell-muted">{disp.ultima_conexion ? new Date(disp.ultima_conexion).toLocaleString() : '—'}</td>
                    <td>
                      <div className="cell-actions">
                        <button className="btn-secondary btn-sm" onClick={() => abrirConfig(disp)} disabled={accionando === disp.id}>Config</button>
                        <button className="btn-secondary btn-sm btn-delete" onClick={() => handleEliminar(disp)}
                                disabled={accionando === disp.id} title="Eliminar dispositivo">✕</button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal de configuración: asociar laboratorio (HU-06) + IP */}
      {editando && (
        <div onClick={() => setEditando(null)} style={{
          position:'fixed', inset:0, background:'rgba(0,0,0,0.6)', display:'flex',
          alignItems:'center', justifyContent:'center', zIndex:1000 }}>
          <div onClick={(e) => e.stopPropagation()} style={{
            background:'#0f1d33', border:'1px solid rgba(0,240,255,0.25)', borderRadius:14,
            padding:'1.5rem', width:'min(420px,90vw)' }}>
            <h3 style={{ color:'#e8eef7', margin:'0 0 1rem' }}>Configurar {editando.identificador}</h3>

            <label style={{ display:'block', color:'#8aa0b8', fontSize:12, marginBottom:4 }}>Laboratorio asignado</label>
            <select value={editLab} onChange={(e) => setEditLab(e.target.value)}
                    style={{ width:'100%', padding:'0.6rem', borderRadius:8, background:'#0a1526',
                             color:'#e8eef7', border:'1px solid rgba(255,255,255,0.15)', marginBottom:'1rem' }}>
              <option value="">— Sin asignar —</option>
              {laboratorios.map((l) => (<option key={l.id} value={l.id}>{l.nombre}</option>))}
            </select>

            <label style={{ display:'block', color:'#8aa0b8', fontSize:12, marginBottom:4 }}>Dirección IP</label>
            <input value={editIp} onChange={(e) => setEditIp(e.target.value)} placeholder="192.168.1.60"
                   style={{ width:'100%', padding:'0.6rem', borderRadius:8, background:'#0a1526',
                            color:'#e8eef7', border:'1px solid rgba(255,255,255,0.15)', marginBottom:'1.4rem' }} />

            <div style={{ display:'flex', gap:10, justifyContent:'flex-end' }}>
              <button className="btn-secondary" onClick={() => setEditando(null)}>Cancelar</button>
              <button className="btn-primary" onClick={guardarConfig} disabled={accionando === editando.id}>
                {accionando === editando.id ? 'Guardando...' : 'Guardar'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dispositivos;