import React, { useState } from 'react';
<<<<<<< Updated upstream
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import useToastStore from '../store/toastStore';
import loginBgEs from '../assets/login-bg-es.png';
=======
import { Link } from 'react-router-dom';
import loginBg from '../assets/imagen01.png';
>>>>>>> Stashed changes
import logo from '../assets/logo.png';
import './LoginPage.css';

const RegisterPage = () => {
<<<<<<< Updated upstream
  const [formData, setFormData] = useState({ 
    firstName: '',
    lastName: '',
    username: '', 
    email: '', 
    password: '', 
    confirmPassword: '' 
  });
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const navigate = useNavigate();
  const registerAction = useAuthStore((state) => state.register);
  const storeError = useAuthStore((state) => state.error);
  const storeLoading = useAuthStore((state) => state.loading);
  const successToast = useToastStore((state) => state.success);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
    
    if (touched[name]) {
      validateField(name, value);
    }
  };

  const handleBlur = (e) => {
    const { name, value } = e.target;
    setTouched({ ...touched, [name]: true });
    validateField(name, value);
  };

  const validateField = (fieldName, value) => {
    const newErrors = { ...errors };
    
    switch (fieldName) {
      case 'firstName':
        if (!value.trim()) newErrors.firstName = 'Requerido';
        else delete newErrors.firstName;
        break;
      case 'lastName':
        if (!value.trim()) newErrors.lastName = 'Requerido';
        else delete newErrors.lastName;
        break;
      case 'username':
        if (!value.trim()) {
          newErrors.username = 'El usuario es requerido';
        } else if (value.length < 3) {
          newErrors.username = 'Mínimo 3 caracteres';
        } else {
          delete newErrors.username;
        }
        break;
      
      case 'email':
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!value.trim()) {
          newErrors.email = 'El correo es requerido';
        } else if (!emailRegex.test(value)) {
          newErrors.email = 'Correo electrónico inválido';
        } else {
          delete newErrors.email;
        }
        break;
        
      case 'password':
        if (!value) {
          newErrors.password = 'La contraseña es requerida';
        } else if (value.length < 6) {
          newErrors.password = 'Mínimo 6 caracteres';
        } else {
          delete newErrors.password;
        }
        // También validar confirmPassword si ya fue tocada
        if (touched.confirmPassword && formData.confirmPassword !== value) {
          newErrors.confirmPassword = 'Las contraseñas no coinciden';
        } else if (touched.confirmPassword) {
          delete newErrors.confirmPassword;
        }
        break;
        
      case 'confirmPassword':
        if (!value) {
          newErrors.confirmPassword = 'Confirma tu contraseña';
        } else if (value !== formData.password) {
          newErrors.confirmPassword = 'Las contraseñas no coinciden';
        } else {
          delete newErrors.confirmPassword;
        }
        break;
        
      default:
        break;
    }
    
    setErrors(newErrors);
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.firstName.trim()) newErrors.firstName = 'Requerido';
    if (!formData.lastName.trim()) newErrors.lastName = 'Requerido';

    if (!formData.username.trim()) newErrors.username = 'Requerido';
    else if (formData.username.length < 3) newErrors.username = 'Mínimo 3 caracteres';
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!formData.email.trim()) newErrors.email = 'Requerido';
    else if (!emailRegex.test(formData.email)) newErrors.email = 'Correo inválido';
    
    if (!formData.password) newErrors.password = 'Requerida';
    else if (formData.password.length < 6) newErrors.password = 'Mínimo 6 caracteres';
    
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'No coinciden';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    
    setTouched({
      firstName: true,
      lastName: true,
      username: true,
      email: true,
      password: true,
      confirmPassword: true
    });
    
    if (!validateForm()) return;
    
    const isSuccess = await registerAction({
      first_name: formData.firstName,
      last_name: formData.lastName,
      username: formData.username,
      email: formData.email,
      password: formData.password
    });
    
    if (isSuccess) {
      successToast('Registro exitoso y sesión iniciada. Bienvenido.');
      navigate('/biometria');
    }
  };

  return (
    <div 
      className="login-fullscreen-layout" 
      style={{ backgroundImage: `url(${loginBgEs})` }}
    >
      <div className="login-overlay">
        <div className="login-glass-card">
          <div className="login-brand">
            <img src={logo} alt="Tecnoecuatoriano Logo" className="login-logo" />
            <p>Registro IoT Institucional</p>
          </div>

          {storeError && <div className="error-message">{storeError}</div>}
          
          <form onSubmit={handleRegister} className="auth-form cyber-form">
            <div className="input-group cyber-input">
              <label htmlFor="firstName">Nombres</label>
              <input 
                type="text" 
                id="firstName"
                name="firstName" 
                value={formData.firstName}
                onChange={handleChange}
                onBlur={handleBlur}
                required 
                placeholder="Tus Nombres"
                className={errors.firstName ? 'input-error' : ''}
              />
              {errors.firstName && <div className="validation-error">{errors.firstName}</div>}
            </div>

            <div className="input-group cyber-input">
              <label htmlFor="lastName">Apellidos</label>
              <input 
                type="text" 
                id="lastName"
                name="lastName" 
                value={formData.lastName}
                onChange={handleChange}
                onBlur={handleBlur}
                required 
                placeholder="Tus Apellidos"
                className={errors.lastName ? 'input-error' : ''}
              />
              {errors.lastName && <div className="validation-error">{errors.lastName}</div>}
            </div>

            <div className="input-group cyber-input">
              <label htmlFor="username">Usuario</label>
              <input 
                type="text" 
                id="username"
                name="username" 
                value={formData.username}
                onChange={handleChange}
                onBlur={handleBlur}
                required 
                placeholder="Elige un usuario"
                className={errors.username ? 'input-error' : ''}
              />
              {errors.username && <div className="validation-error">{errors.username}</div>}
            </div>

            <div className="input-group cyber-input">
              <label htmlFor="email">Correo Electrónico</label>
              <input 
                type="email" 
                id="email"
                name="email" 
                value={formData.email}
                onChange={handleChange}
                onBlur={handleBlur}
                required 
                placeholder="tucorreo@ejemplo.com"
                className={errors.email ? 'input-error' : ''}
              />
              {errors.email && <div className="validation-error">{errors.email}</div>}
            </div>

            <div className="input-group cyber-input">
              <label htmlFor="password">Contraseña</label>
              <div className="password-input-wrapper" style={{ position: 'relative' }}>
                <input 
                  type={showPassword ? 'text' : 'password'}
                  id="password"
                  name="password" 
                  value={formData.password}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  required 
                  placeholder="••••••••"
                  className={errors.password ? 'input-error' : ''}
                  style={{ width: '100%' }}
                />
                <button 
                  type="button" 
                  className="password-toggle-btn"
                  onClick={() => setShowPassword(!showPassword)}
                  style={{ position: 'absolute', right: '10px', top: '50%', transform: 'translateY(-50%)', background: 'transparent', border: 'none', cursor: 'pointer', color: 'rgba(255, 255, 255, 0.6)' }}
                >
                  {showPassword ? '👁️' : '🙈'}
                </button>
              </div>
              {errors.password && <div className="validation-error">{errors.password}</div>}
            </div>
            
            <div className="input-group cyber-input">
              <label htmlFor="confirmPassword">Confirmar Contraseña</label>
              <div className="password-input-wrapper" style={{ position: 'relative' }}>
                <input 
                  type={showConfirmPassword ? 'text' : 'password'}
                  id="confirmPassword"
                  name="confirmPassword" 
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  required 
                  placeholder="••••••••"
                  className={errors.confirmPassword ? 'input-error' : ''}
                  style={{ width: '100%' }}
                />
                <button 
                  type="button" 
                  className="password-toggle-btn"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  style={{ position: 'absolute', right: '10px', top: '50%', transform: 'translateY(-50%)', background: 'transparent', border: 'none', cursor: 'pointer', color: 'rgba(255, 255, 255, 0.6)' }}
                >
                  {showConfirmPassword ? '👁️' : '🙈'}
                </button>
              </div>
              {errors.confirmPassword && <div className="validation-error">{errors.confirmPassword}</div>}
            </div>

            <button type="submit" className="btn-primary cyber-btn" disabled={storeLoading}>
              {storeLoading ? <span className="scanning">REGISTRANDO...</span> : 'CREAR CUENTA'}
            </button>
            
            <button type="button" className="btn-secondary cyber-btn outline-btn" onClick={() => navigate('/login')} style={{ marginTop: '10px' }}>
              VOLVER AL LOGIN
            </button>
          </form>
=======
  const [regData, setRegData] = useState({ username: '', email: '', password: '', confirmPassword: '' });
  const [regStep, setRegStep] = useState(1);
  const [passwordStrength, setPasswordStrength] = useState(0);
  const [showPassword, setShowPassword] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setRegData({ ...regData, [name]: value });
    if (name === 'password') {
      let strength = 0;
      if (value.length >= 6) strength += 25;
      if (value.length >= 10) strength += 25;
      if (/[A-Z]/.test(value)) strength += 15;
      if (/[0-9]/.test(value)) strength += 15;
      if (/[^A-Za-z0-9]/.test(value)) strength += 20;
      setPasswordStrength(strength);
    }
  };

  const handleRegister = (e) => {
    e.preventDefault();
    if (regData.password !== regData.confirmPassword) {
      alert('Las contraseñas no coinciden');
      return;
    }
    setRegStep(2);
    setTimeout(() => setRegStep(3), 2000);
  };

  const getStrengthLabel = () => {
    if (passwordStrength <= 25) return { label: 'Débil', color: '#ff4444' };
    if (passwordStrength <= 50) return { label: 'Regular', color: '#ffaa00' };
    if (passwordStrength <= 75) return { label: 'Buena', color: '#00d4ff' };
    return { label: 'Fuerte', color: '#00ff88' };
  };

  return (
    <div className="login-fullscreen-layout" style={{ backgroundImage: `url(${loginBg})` }}>
      <div className="login-circuit-grid" />
      
      <div className="login-overlay">
        <div className="login-glass-card">
          <div className="card-corner top-left" />
          <div className="card-corner top-right" />
          <div className="card-corner bottom-left" />
          <div className="card-corner bottom-right" />

          <div className="login-brand">
            <img src={logo} alt="Tecnoecuatoriano Logo" className="login-logo" />
            <p className="brand-title">Crear Nueva Cuenta</p>
          </div>

          {regStep === 1 && (
            <form onSubmit={handleRegister} className="auth-form">
              <div className="reg-steps">
                <div className="step active">1</div>
                <div className="step-line" />
                <div className="step">2</div>
                <div className="step-line" />
                <div className="step">3</div>
              </div>

              <div className="input-group">
                <label><span className="input-icon">👤</span> Nombre de usuario</label>
                <input type="text" name="username" value={regData.username} onChange={handleChange}
                  required placeholder="Ej: juan.perez" />
                <div className="input-glow" />
              </div>

              <div className="input-group">
                <label><span className="input-icon">📧</span> Correo electrónico</label>
                <input type="email" name="email" value={regData.email} onChange={handleChange}
                  required placeholder="correo@institucion.edu.ec" />
                <div className="input-glow" />
              </div>

              <div className="input-group">
                <label><span className="input-icon">🔒</span> Contraseña</label>
                <div className="password-wrapper">
                  <input type={showPassword ? 'text' : 'password'} name="password" value={regData.password}
                    onChange={handleChange} required placeholder="Mínimo 6 caracteres" />
                  <button type="button" className="toggle-password" onClick={() => setShowPassword(!showPassword)}>
                    {showPassword ? '🙈' : '👁️'}
                  </button>
                </div>
                <div className="password-strength-bar">
                  <div className="strength-fill" style={{ width: `${passwordStrength}%`, backgroundColor: getStrengthLabel().color }} />
                </div>
                <span className="strength-label" style={{ color: getStrengthLabel().color }}>
                  {passwordStrength > 0 ? getStrengthLabel().label : ''}
                </span>
                <div className="input-glow" />
              </div>

              <div className="input-group">
                <label><span className="input-icon">🔐</span> Confirmar contraseña</label>
                <input type={showPassword ? 'text' : 'password'} name="confirmPassword" value={regData.confirmPassword}
                  onChange={handleChange} required placeholder="Repite la contraseña"
                  style={regData.confirmPassword && regData.password !== regData.confirmPassword ? { borderColor: '#ff4444' } : {}} />
                {regData.confirmPassword && regData.password !== regData.confirmPassword && (
                  <span className="field-error">Las contraseñas no coinciden</span>
                )}
                <div className="input-glow" />
              </div>

              <div className="terms-check">
                <input type="checkbox" id="terms" required />
                <label htmlFor="terms">Acepto los <a href="#terms">términos y condiciones</a></label>
              </div>

              <button type="submit" className="btn-primary cyber-btn">CREAR CUENTA</button>

              <div className="auth-switch">
                <span>¿Ya tienes cuenta?</span>
                <Link to="/login" className="text-btn highlight">Iniciar sesión</Link>
              </div>
            </form>
          )}

          {regStep === 2 && (
            <div className="verification-panel">
              <div className="verif-icon">📧</div>
              <h3>Verifica tu correo</h3>
              <p className="verif-text">Hemos enviado un código de verificación a <strong>{regData.email}</strong></p>
              <div className="code-inputs">
                {[1,2,3,4].map(i => (
                  <input key={i} type="text" maxLength="1" className="code-digit"
                    onKeyUp={(e) => {
                      if (e.target.value && e.target.nextSibling) e.target.nextSibling.focus();
                    }} />
                ))}
              </div>
              <p className="verif-resend">¿No recibiste el código? <button type="button" className="text-btn">Reenviar</button></p>
            </div>
          )}

          {regStep === 3 && (
            <div className="success-panel">
              <div className="success-icon">
                <svg viewBox="0 0 50 50">
                  <circle cx="25" cy="25" r="23" fill="none" stroke="#00ff88" strokeWidth="3" />
                  <path d="M15 25 L22 32 L35 18" fill="none" stroke="#00ff88" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </div>
              <h3>¡Registro Exitoso!</h3>
              <p>Tu cuenta ha sido creada correctamente. Ahora puedes iniciar sesión.</p>
              <Link to="/login" className="btn-primary cyber-btn" style={{ textDecoration: 'none', display: 'inline-block', maxWidth: '280px' }}>
                IR A INICIAR SESIÓN
              </Link>
            </div>
          )}
>>>>>>> Stashed changes
        </div>
      </div>
    </div>
  );
};

<<<<<<< Updated upstream
export default RegisterPage;
=======
export default RegisterPage;
>>>>>>> Stashed changes
