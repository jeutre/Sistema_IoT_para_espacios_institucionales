import React, { useEffect, useState } from 'react';
import useIotStore from '../store/iotStore';
import './Laboratorios.css';

const Laboratorios = () => {
  const { laboratorios, fetchLaboratorios, createLaboratorio, updateLaboratorio, loading } = useIotStore();
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState(null);
  
  const [formData, setFormData] = useState({
    nombre: '',
    ubicacion: '',
    capacidad: 10,
    activo: true
  });

  useEffect(() => {
    fetchLaboratorios();
  }, [fetchLaboratorios]);

  const handleOpenModal = (lab = null) => {
    if (lab) {
      setEditingId(lab.id);
      setFormData({
        nombre: lab.nombre,
        ubicacion: lab.ubicacion,
        capacidad: lab.capacidad,
        activo: lab.activo
      });
    } else {
      setEditingId(null);
      setFormData({
        nombre: '',
        ubicacion: '',
        capacidad: 10,
        activo: true
      });
    }
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingId(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    let success = false;
    if (editingId) {
      success = await updateLaboratorio(editingId, formData);
    } else {
      success = await createLaboratorio(formData);
    }
    
    if (success) {
      handleCloseModal();
      fetchLaboratorios();
    }
  };

  return (
    <div className="page-container">
      <div className="toolbar-row">
        <div className="toolbar-left">
          <h2 style={{margin: 0, color: 'var(--text-primary)'}}>Gestión de Laboratorios</h2>
        </div>
        <button className="btn-primary" onClick={() => handleOpenModal()} disabled={loading}>
          + Nuevo Laboratorio
        </button>
      </div>

      <div className="page-card">
        <div className="card-table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Nombre</th>
                <th>Ubicación</th>
                <th>Capacidad</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {loading && laboratorios.length === 0 ? (
                [...Array(3)].map((_, i) => (
                  <tr key={`sk-${i}`}>
                    {[...Array(6)].map((_, j) => (
                      <td key={j}><div className="skeleton-cell" style={{width: `${60 + j*10}%`}}></div></td>
                    ))}
                  </tr>
                ))
              ) : laboratorios.length === 0 ? (
                <tr><td colSpan="6" className="empty-state">No hay laboratorios registrados</td></tr>
              ) : (
                laboratorios.map(lab => (
                  <tr key={lab.id}>
                    <td className="cell-mono">#{lab.id}</td>
                    <td className="cell-highlight">{lab.nombre}</td>
                    <td>{lab.ubicacion}</td>
                    <td>{lab.capacidad}</td>
                    <td>
                      <span className={`status-badge ${lab.activo ? 'online' : 'offline'}`}>
                        <span className="status-dot"></span>
                        {lab.activo ? 'Activo' : 'Inactivo'}
                      </span>
                    </td>
                    <td>
                      <div className="cell-actions">
                        <button className="btn-secondary btn-sm" onClick={() => handleOpenModal(lab)}>Editar</button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {showModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>{editingId ? 'Editar Laboratorio' : 'Nuevo Laboratorio'}</h3>
              <button className="btn-close" onClick={handleCloseModal}>✕</button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Nombre del Laboratorio</label>
                <input 
                  type="text" 
                  required 
                  value={formData.nombre} 
                  onChange={e => setFormData({...formData, nombre: e.target.value})}
                  className="form-control"
                  placeholder="Ej: Lab Redes CISCO"
                />
              </div>
              <div className="form-group">
                <label>Ubicación</label>
                <input 
                  type="text" 
                  required 
                  value={formData.ubicacion} 
                  onChange={e => setFormData({...formData, ubicacion: e.target.value})}
                  className="form-control"
                  placeholder="Ej: Edificio Central, 2do Piso"
                />
              </div>
              <div className="form-group">
                <label>Capacidad (Nro. Equipos)</label>
                <input 
                  type="number" 
                  required 
                  min="1"
                  value={formData.capacidad} 
                  onChange={e => setFormData({...formData, capacidad: parseInt(e.target.value)})}
                  className="form-control"
                />
              </div>
              <div className="form-group checkbox-group">
                <label className="checkbox-label">
                  <input 
                    type="checkbox" 
                    checked={formData.activo} 
                    onChange={e => setFormData({...formData, activo: e.target.checked})}
                  />
                  <span>Laboratorio Activo</span>
                </label>
              </div>
              <div className="modal-actions">
                <button type="button" className="btn-secondary" onClick={handleCloseModal}>Cancelar</button>
                <button type="submit" className="btn-primary" disabled={loading}>
                  {loading ? 'Guardando...' : 'Guardar'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Laboratorios;
