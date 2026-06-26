import React, { useState } from 'react';
import useAuthStore from '../store/authStore';
import './Profile.css';

const Profile = () => {
  const user = useAuthStore((state) => state.user) || { username: 'estudiante_demo' };

  const [formData, setFormData] = useState({
    firstName: 'Andrea',
    lastName: 'Ortega',
    email: 'andrea.ortega@institucion.edu',
    phone: '+1 234 567 890'
  });

  const [isEditing, setIsEditing] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSave = (e) => {
    e.preventDefault();
    setIsEditing(false);
    // Aquí se llamaría a student_service vía Axios para actualizar los datos
    alert("Datos actualizados correctamente.");
  };

  return (
    <div className="profile-container">
      <header className="dashboard-header">
        <h1>Mi Perfil</h1>
        <p>Gestiona tus datos personales y credenciales.</p>
      </header>

      <div className="profile-content glass-container">
        <div className="profile-header">
          <div className="profile-avatar">
            <span className="avatar-initials">{formData.firstName[0]}{formData.lastName[0]}</span>
            <button className="change-avatar-btn">📷</button>
          </div>
          <div className="profile-title">
            <h2>{formData.firstName} {formData.lastName}</h2>
            <p>@{user.username}</p>
          </div>
        </div>

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
      </div>
    </div>
  );
};

export default Profile;
