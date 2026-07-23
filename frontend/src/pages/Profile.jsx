import React, { useState, useEffect } from 'react';
import useAuthStore from '../store/authStore';
import './Profile.css';

const Profile = () => {
  const user = useAuthStore((state) => state.user) || { username: 'cargando...' };
  const getUserProfile = useAuthStore((state) => state.getUserProfile);

  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: ''
  });
  
  const [loading, setLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const fetchProfile = async () => {
      setLoading(true);
      const data = await getUserProfile();
      if (data) {
        setFormData({
          firstName: data.first_name || '',
          lastName: data.last_name || '',
          email: data.email || '',
          phone: data.phone || ''
        });
      }
      setLoading(false);
    };
    fetchProfile();
  }, [getUserProfile]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSave = (e) => {
    e.preventDefault();
    setIsEditing(false);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };
  
  const initials = (formData.firstName?.[0] || '') + (formData.lastName?.[0] || '');
  const displayInitials = initials || user.username?.[0]?.toUpperCase() || '?';

  if (loading && !user) {
    return (
      <div className="profile-container">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Cargando perfil...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="profile-container">
      <div className="profile-content glass-container">
        <div className="profile-header">
          <div className="profile-avatar">
            <span className="avatar-initials">{displayInitials}</span>
          </div>
          <div className="profile-title">
            <h2>{formData.firstName || formData.lastName ? `${formData.firstName} ${formData.lastName}` : (user?.username || 'Usuario')}</h2>
            <p>@{user?.username || 'usuario'}</p>
          </div>
        </div>

        {saved && <div className="profile-success">✅ Datos actualizados correctamente</div>}

        {loading ? (
           <div className="loading-container">
             <div className="loading-spinner"></div>
             <p>Cargando datos del perfil...</p>
           </div>
        ) : (
        <form className="profile-form" onSubmit={handleSave}>
          <div className="form-grid">
            <div className="input-group">
              <label>Nombres</label>
              <input type="text" name="firstName" value={formData.firstName} onChange={handleChange} disabled={!isEditing} placeholder="Ingresa tus nombres" />
            </div>
            <div className="input-group">
              <label>Apellidos</label>
              <input type="text" name="lastName" value={formData.lastName} onChange={handleChange} disabled={!isEditing} placeholder="Ingresa tus apellidos" />
            </div>
            <div className="input-group">
              <label>Correo Electrónico</label>
              <input type="email" name="email" value={formData.email} onChange={handleChange} disabled={!isEditing} placeholder="correo@ejemplo.com" />
            </div>
            <div className="input-group">
              <label>Teléfono</label>
              <input type="text" name="phone" value={formData.phone} onChange={handleChange} disabled={!isEditing} placeholder="+593 999 999 999" />
            </div>
          </div>

          <div className="form-actions">
            {isEditing ? (
              <>
                <button type="button" className="btn-secondary" onClick={() => setIsEditing(false)}>Cancelar</button>
                <button type="submit" className="btn-primary">Guardar Cambios</button>
              </>
            ) : (
              <button type="button" className="btn-primary" onClick={() => setIsEditing(true)}>Editar Perfil</button>
            )}
          </div>
        </form>
        )}
      </div>
    </div>
  );
};

export default Profile;