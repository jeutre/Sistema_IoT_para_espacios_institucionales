import React, { useEffect, useState } from 'react';
import useIotStore from '../store/iotStore';
import './Equipos.css';

const Equipos = () => {
  const { equipos, laboratorios, fetchEquipos, fetchLaboratorios, pingTodos, createEquipo, updateEquipo, equiposActivos, equiposInactivos } = useIotStore();
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({ id: null, nombre: '', ip: '', mac: '', laboratorio: '', activo: true });
  const [isPinging, setIsPinging] = useState(false);
  const [filter, setFilter] = useState('all'); // all, activo, inactivo

  useEffect(() => {
    fetchEquipos();
    fetchLaboratorios();
  }, [fetchEquipos, fetchLaboratorios]);

  const handlePing = async () => {
    setIsPinging(true);
    await pingTodos();
    setIsPinging(false);
  };

  const handleOpenModal = (equipo = null) => {
    if (equipo) {
      setFormData({
        id: equipo.id,
        nombre: equipo.nombre,
        ip: equipo.ip,
        mac: equipo.mac,
        laboratorio: equipo.laboratorio,
        activo: equipo.activo
      });
    } else {
      setFormData({ id: null, nombre: '', ip: '', mac: '', laboratorio: laboratorios[0]?.id || '', activo: true });
    }
    setShowModal(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (formData.id) {
        await updateEquipo(formData.id, formData);
      } else {
        await createEquipo(formData);
      }
      setShowModal(false);
    } catch (error) {
      alert("Error al guardar equipo. Revisa que la IP o MAC no estén duplicadas.");
    }
  };

  const filteredEquipos = equipos.filter(eq => {
    if (filter === 'activo') return eq.estado_conexion === 'activo';
    if (filter === 'inactivo') return eq.estado_conexion === 'inactivo';
    return true;
  });

  return (
    <div className="page-container">
      <div className="toolbar-row">
        <div className="toolbar-left" style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <button className="btn-primary" onClick={() => handleOpenModal()}>
            + Nuevo Equipo
          </button>
          <button className="btn-secondary" onClick={handlePing} disabled={isPinging}>
            {isPinging ? 'Ejecutando Ping...' : 'Ping Automático a Todos'}
          </button>
        </div>
        
        <div className="toolbar-right">
          <div className="tabs">
            <button className={`tab-btn ${filter === 'all' ? 'active' : ''}`} onClick={() => setFilter('all')}>
              Todos
            </button>
            <button className={`tab-btn ${filter === 'activo' ? 'active' : ''}`} onClick={() => setFilter('activo')}>
              Activos ({equiposActivos || equipos.filter(e => e.estado_conexion === 'activo').length})
            </button>
            <button className={`tab-btn ${filter === 'inactivo' ? 'active' : ''}`} onClick={() => setFilter('inactivo')}>
              Inactivos ({equiposInactivos || equipos.filter(e => e.estado_conexion === 'inactivo').length})
            </button>
          </div>
        </div>
      </div>

      <div className="page-card card-table-wrapper">
        <table className="data-table">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>IP IPv4</th>
              <th>MAC</th>
              <th>Estado Conexión</th>
              <th>Último Ping</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {filteredEquipos.map(eq => (
              <tr key={eq.id}>
                <td className="cell-highlight">{eq.nombre}</td>
                <td className="cell-mono">{eq.ip}</td>
                <td className="cell-mono">{eq.mac}</td>
                <td>
                  <span className={`status-badge ${eq.estado_conexion === 'activo' ? 'online' : 'offline'}`}>
                    <span className="status-dot"></span>
                    {eq.estado_conexion === 'activo' ? 'Responde' : 'No Responde'}
                  </span>
                </td>
                <td>{eq.ultimo_ping ? new Date(eq.ultimo_ping).toLocaleString('es-EC') : 'Nunca'}</td>
                <td className="cell-actions">
                  <button className="btn-secondary btn-sm" onClick={() => handleOpenModal(eq)}>Editar</button>
                </td>
              </tr>
            ))}
            {filteredEquipos.length === 0 && (
              <tr>
                <td colSpan="6" className="empty-state">No hay equipos registrados</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{formData.id ? 'Editar Equipo' : 'Nuevo Equipo'}</h3>
              <button className="btn-close" onClick={() => setShowModal(false)}>&times;</button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Nombre del Equipo</label>
                <input required type="text" className="form-control" value={formData.nombre} onChange={e => setFormData({...formData, nombre: e.target.value})} placeholder="Ej. PC-01 Laboratorio Redes" />
              </div>
              <div className="form-group">
                <label>Dirección IPv4</label>
                <input required type="text" className="form-control cell-mono" value={formData.ip} onChange={e => setFormData({...formData, ip: e.target.value})} placeholder="192.168.1.50" />
              </div>
              <div className="form-group">
                <label>Dirección MAC</label>
                <input required type="text" className="form-control cell-mono" value={formData.mac} onChange={e => setFormData({...formData, mac: e.target.value})} placeholder="00:1A:2B:3C:4D:5E" />
              </div>
              <div className="form-group">
                <label>Laboratorio Asignado</label>
                <select required className="form-control" value={formData.laboratorio} onChange={e => setFormData({...formData, laboratorio: e.target.value})}>
                  <option value="">Seleccione un laboratorio</option>
                  {laboratorios.map(lab => (
                    <option key={lab.id} value={lab.id}>{lab.nombre}</option>
                  ))}
                </select>
              </div>
              <label className="checkbox-label" style={{marginTop: '1rem'}}>
                <input type="checkbox" checked={formData.activo} onChange={e => setFormData({...formData, activo: e.target.checked})} />
                Monitorear este equipo (Activo)
              </label>
              <div className="modal-actions">
                <button type="button" className="btn-secondary" onClick={() => setShowModal(false)}>Cancelar</button>
                <button type="submit" className="btn-primary">Guardar Equipo</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Equipos;
