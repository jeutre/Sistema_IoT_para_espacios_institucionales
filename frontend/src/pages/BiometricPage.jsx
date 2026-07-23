import React, { useRef, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import './BiometricPage.css';

const BiometricPage = () => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [stream, setStream] = useState(null);
  const [error, setError] = useState('');
  const [isVerifying, setIsVerifying] = useState(false);
  const [verified, setVerified] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
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

  const captureAndVerify = () => {
    if (!videoRef.current || !canvasRef.current) return;

    setIsVerifying(true);
    setError('');

    const context = canvasRef.current.getContext('2d');
    context.drawImage(videoRef.current, 0, 0, 300, 225);

    // Simular verificación biométrica local
    setTimeout(() => {
      setIsVerifying(false);
      setVerified(true);
      stopCamera();

      // Redirigir al dashboard después de 1.5 segundos
      setTimeout(() => {
        navigate('/dashboard');
      }, 1500);
    }, 2000);
  };

  return (
    <div className="biometric-wrapper">
      <div className="glass-container biometric-container">
        <h2>Verificación Biométrica</h2>
        <p>Por favor, mira a la cámara para validar tu identidad.</p>

        {error && <div className="error-message">{error}</div>}
        {verified && <div className="success-message">✅ Identidad verificada exitosamente</div>}

        <div className="camera-box">
          {!stream && !verified && (
            <div className="camera-placeholder">
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" />
                <circle cx="12" cy="13" r="4" />
              </svg>
              <p>Iniciando cámara...</p>
            </div>
          )}
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className={`video-feed ${!stream || verified ? 'hidden' : ''}`}
          />
          <canvas ref={canvasRef} width="300" height="225" style={{ display: 'none' }} />

          {isVerifying && (
            <div className="scanning-overlay">
              <div className="scanner-line"></div>
              <p className="scanning-text">Escaneando...</p>
            </div>
          )}

          {verified && (
            <div className="verified-overlay">
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#22c55e" strokeWidth="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                <polyline points="22 4 12 14.01 9 11.01" />
              </svg>
            </div>
          )}
        </div>

        <button
          className="btn-primary auth-submit"
          onClick={captureAndVerify}
          disabled={!stream || isVerifying || verified}
        >
          {isVerifying ? 'Verificando...' : verified ? '✓ Verificado' : 'Capturar y Verificar'}
        </button>

        {!stream && !verified && (
          <button className="btn-secondary auth-submit" onClick={startCamera}>
            Reintentar cámara
          </button>
        )}
      </div>
    </div>
  );
};

export default BiometricPage;