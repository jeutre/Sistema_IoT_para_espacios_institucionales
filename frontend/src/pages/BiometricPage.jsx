import React, { useRef, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import './BiometricPage.css';
import api from '../axiosConfig';

const BiometricPage = () => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [stream, setStream] = useState(null);
  const [error, setError] = useState('');
  const [isVerifying, setIsVerifying] = useState(false);
  const navigate = useNavigate();
  const isAuthenticated = useAuthStore(state => state.isAuthenticated);

  useEffect(() => {
    // Si no está autenticado, no debería estar en biometría en el flujo real,
    // pero por ahora lo permitimos para prueba, o puedes redirigir.
    startCamera();
    return () => {
      stopCamera();
    };
  }, []);

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({ video: true });
      setStream(mediaStream);
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
    } catch (err) {
      setError('No se pudo acceder a la cámara. Por favor, concede los permisos.');
      console.error(err);
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
    }
  };

  const captureAndVerify = async () => {
    if (!videoRef.current || !canvasRef.current) return;
    
    setIsVerifying(true);
    setError('');
    
    const context = canvasRef.current.getContext('2d');
    context.drawImage(videoRef.current, 0, 0, 300, 225);
    
    const imageData = canvasRef.current.toDataURL('image/jpeg');
    
    try {
      // Llamada real al backend para la validación biométrica.
      // El endpoint '/auth/verify-biometric/' es un ejemplo.
      await api.post('/auth/verify-biometric/', { image: imageData });

      alert("¡Identidad verificada exitosamente!");
      stopCamera();
      navigate('/dashboard');
    } catch (err) {
      setError('Verificación fallida. Inténtalo de nuevo.');
      console.error("Error en la verificación biométrica:", err);
    } finally {
      setIsVerifying(false);
    }
  };

  return (
    <div className="biometric-wrapper">
      <div className="glass-container biometric-container">
        <h2>Verificación Biométrica</h2>
        <p>Por favor, mira a la cámara para validar tu identidad.</p>
        
        {error && <div className="error-message">{error}</div>}
        
        <div className="camera-box">
          <video ref={videoRef} autoPlay playsInline muted className="video-feed" />
          <canvas ref={canvasRef} width="300" height="225" style={{ display: 'none' }} />
          
          {isVerifying && (
            <div className="scanning-overlay">
              <div className="scanner-line"></div>
            </div>
          )}
        </div>

        <button 
          className="btn-primary auth-submit" 
          onClick={captureAndVerify}
          disabled={!stream || isVerifying}
        >
          {isVerifying ? 'Verificando...' : 'Capturar y Verificar'}
        </button>
      </div>
    </div>
  );
};

export default BiometricPage;
