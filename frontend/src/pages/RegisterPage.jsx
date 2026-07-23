import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import useToastStore from '../store/toastStore';
import loginBg from '../assets/imagen01.png';
import logo from '../assets/logo.png';
import './LoginPage.css';
import './RegisterPage.css';

const RegisterPage = () => {
  const navigate = useNavigate();
  const register = useAuthStore((state) => state.register);
  const storeLoading = useAuthStore((state) => state.loading);
  const storeError = useAuthStore((state) => state.error);
  const successToast = useToastStore((state) => state.success);
  const errorToast = useToastStore((state) => state.error);

  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState(0);
  const [touched, setTouched] = useState({});
  const [errors, setErrors] = useState({});

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
    if (name === 'password') {
      let strength = 0;
      if (value.length >= 6) strength += 25;
      if (value.length >= 10) strength += 25;
      if (/[A-Z]/.test(value)) strength += 15;
      if (/[0-9]/.test(value)) strength += 15;
      if (/[^A-Za-z0-9]/.test(value)) strength += 20;
      setPasswordStrength(strength);
    }
    if (touched[name]) {
      validateField(name, value);
    }
  };

  const handleBlur = (e) => {
    const { name, value } = e.target;
    setTouched({ ...touched, [name]: true });
    validateField(name, value);
  };

  const validateField = (name, value) => {
    const newErrors = { ...errors };
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    switch (name) {
      case 'firstName':
        if (!value.trim()) newErrors.firstName = 'El nombre es requerido';
        else delete newErrors.firstName;
        break;
      case 'lastName':
        if (!value.trim()) newErrors.lastName = 'El apellido es requerido';
        else delete newErrors.lastName;
        break;
      case 'username':
        if (!value.trim()) newErrors.username = 'El usuario es requerido';
        else if (value.length < 3) newErrors.username = 'Mínimo 3 caracteres';
        else delete newErrors.username;
        break;
      case 'email':
        if (!value.trim()) newErrors.email = 'El correo es requerido';
        else if (!emailRegex.test(value)) newErrors.email = 'Correo electrónico inválido';
        else delete newErrors.email;
        break;
      case 'password':
        if (!value) newErrors.password = 'La contraseña es requerida';
        else if (value.length < 6) newErrors.password = 'Mínimo 6 caracteres';
        else delete newErrors.password;
        if (touched.confirmPassword && formData.confirmPassword !== value) {
          newErrors.confirmPassword = 'Las contraseñas no coinciden';
        } else if (touched.confirmPassword) {
          delete newErrors.confirmPassword;
        }
        break;
      case 'confirmPassword':
        if (!value) newErrors.confirmPassword = 'Confirma tu contraseña';
        else if (value !== formData.password) newErrors.confirmPassword = 'Las contraseñas no coinciden';
        else delete newErrors.confirmPassword;
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
    if (!formData.password) newErrors.password = 'Requerido';
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
    const isSuccess = await register({
      first_name: formData.firstName,
      last_name: formData.lastName,
      username: formData.username,
      email: formData.email,
      password: formData.password
    });
    if (isSuccess) {
      successToast('Registro exitoso y sesión iniciada. Bienvenido.');
      navigate('/biometria');
    } else if (storeError) {
      errorToast(storeError);
    }
  };

  const getStrengthLabel = () => {
    if (passwordStrength <= 25) return { label: 'Débil', color: '#ff4444' };
    if (passwordStrength <= 50) return { label: 'Regular', color: '#ffaa00' };
    if (passwordStrength <= 75) return { label: 'Buena', color: '#00d4ff' };
    return { label: 'Fuerte', color: '#00ff88' };
  };

  return (
    <div
      className="login-fullscreen-layout"
      style={{ backgroundImage: `url(${loginBg})` }}
    >
      <div className="login-overlay">
        <div className="login-glass-card">
          <div className="login-brand">
            <img src={logo} alt="Tecnoecuatoriano Logo" className="login-logo" />
            <p>Crear Nueva Cuenta</p>
          </div>

          {storeError && <div className="error-message">{storeError}</div>}

          <form onSubmit={handleRegister} className="auth-form cyber-form">
            <div className="input-group cyber-input">
              <input
                type="text"
                id="firstName"
                name="firstName"
                value={formData.firstName}
                onChange={handleChange}
                onBlur={handleBlur}
                required
                placeholder="NOMBRES"
                className={errors.firstName ? 'input-error' : ''}
              />
              <div className="input-glow"></div>
              {errors.firstName && (
                <div className="validation-error">{errors.firstName}</div>
              )}
            </div>

            <div className="input-group cyber-input">
              <input
                type="text"
                id="lastName"
                name="lastName"
                value={formData.lastName}
                onChange={handleChange}
                onBlur={handleBlur}
                required
                placeholder="APELLIDOS"
                className={errors.lastName ? 'input-error' : ''}
              />
              <div className="input-glow"></div>
              {errors.lastName && (
                <div className="validation-error">{errors.lastName}</div>
              )}
            </div>

            <div className="input-group cyber-input">
              <input
                type="text"
                id="username"
                name="username"
                value={formData.username}
                onChange={handleChange}
                onBlur={handleBlur}
                required
                placeholder="USUARIO"
                className={errors.username ? 'input-error' : ''}
              />
              <div className="input-glow"></div>
              {errors.username && (
                <div className="validation-error">{errors.username}</div>
              )}
            </div>

            <div className="input-group cyber-input">
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                onBlur={handleBlur}
                required
                placeholder="CORREO ELECTRÓNICO"
                className={errors.email ? 'input-error' : ''}
              />
              <div className="input-glow"></div>
              {errors.email && (
                <div className="validation-error">{errors.email}</div>
              )}
            </div>

            <div className="input-group cyber-input">
              <div className="password-wrapper">
                <input
                  type={showPassword ? 'text' : 'password'}
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  required
                  placeholder="CONTRASEÑA"
                  className={errors.password ? 'input-error' : ''}
                />
                <button
                  type="button"
                  className="toggle-password"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? '🙈' : '👁️'}
                </button>
              </div>
              <div className="input-glow"></div>
              {passwordStrength > 0 && (
                <div className="password-strength-bar">
                  <div
                    className="strength-fill"
                    style={{
                      width: `${passwordStrength}%`,
                      backgroundColor: getStrengthLabel().color
                    }}
                  />
                </div>
              )}
              {passwordStrength > 0 && (
                <span
                  className="strength-label"
                  style={{ color: getStrengthLabel().color }}
                >
                  {getStrengthLabel().label}
                </span>
              )}
              {errors.password && (
                <div className="validation-error">{errors.password}</div>
              )}
            </div>

            <div className="input-group cyber-input">
              <div className="password-wrapper">
                <input
                  type={showConfirmPassword ? 'text' : 'password'}
                  id="confirmPassword"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  required
                  placeholder="CONFIRMAR CONTRASEÑA"
                  className={errors.confirmPassword ? 'input-error' : ''}
                />
                <button
                  type="button"
                  className="toggle-password"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                >
                  {showConfirmPassword ? '🙈' : '👁️'}
                </button>
              </div>
              <div className="input-glow"></div>
              {errors.confirmPassword && (
                <div className="validation-error">{errors.confirmPassword}</div>
              )}
            </div>

            <div className="terms-check">
              <input type="checkbox" id="terms" required />
              <label htmlFor="terms">
                Acepto los <a href="#terms">términos y condiciones</a>
              </label>
            </div>

            <button
              type="submit"
              className="btn-primary cyber-btn"
              disabled={storeLoading}
            >
              {storeLoading ? <span className="scanning">CREANDO...</span> : 'CREAR CUENTA'}
            </button>

            <button
              type="button"
              className="btn-secondary cyber-btn outline-btn"
              onClick={() => navigate('/login')}
            >
              VOLVER AL LOGIN
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
