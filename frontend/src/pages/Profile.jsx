import React, { useState } from 'react';
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

  useEffect(() => {
    const fetchProfile = async () => {
      const data = await getUserProfile();
      if (data) {
        setFormData({
          firstName: data.first_name || '',
          lastName: data.last_name || '',
          email: data.email || '',
          phone: data.phone || '' // si no hay teléfono, se deja en blanco
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
    // Aquí se llamaría a student_service vía Axios para actualizar los datos
    alert("Datos actualizados correctamente.");
  };
  
  // Obtener iniciales reales
  const initials = (formData.firstName?.[0] || '') + (formData.lastName?.[0] || '');
  const displayInitials = initials || user.username?.[0]?.toUpperCase() || '?';

  return (
    <div className="profile-container">
      <header className="dashboard-header">
        <h1>Mi Perfil</h1>
        <p>Gestiona tus datos personales y credenciales.</p>
      </header>

      <div className="profile-content glass-container">
        <div className="profile-header">
          <div className="profile-avatar">
            <span className="avatar-initials">{displayInitials}</span>
            <button className="change-avatar-btn">📷</button>
          </div>
          <div className="profile-title">
            <h2>{formData.firstName || formData.lastName ? `${formData.firstName} ${formData.lastName}` : user.username}</h2>
            <p>@{user.username}</p>
          </div>
        </div>

        {loading ? (
           <p style={{ textAlign: 'center', marginTop: '2rem' }}>Cargando datos del perfil...</p>
        ) : (
        <form className="profile-form" onSubmit={handleSave}>
          <div className="form-grid">
            <div className="input-group">
              <label>Nombres</label>
              <input type="text" name="firstName" value={formData.firstName} onChange={handleChange} disabled={!isEditing} />
            </div>
            <div className="input-group">
              <label>Apellidos</label>
              <input type="text" name="lastName" value={formData.lastName} onChange={handleChange} disabled={!isEditing} />
            </div>
            <div className="input-group">
              <label>Correo Electrónico</label>
              <input type="email" name="email" value={formData.email} onChange={handleChange} disabled={!isEditing} />
            </div>
            <div className="input-group">
              <label>Teléfono</label>
              <input type="text" name="phone" value={formData.phone} onChange={handleChange} disabled={!isEditing} />
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
