import React, { useRef, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './BiometricPage.css';

const BiometricPage = () => {
  const videoRef = useRef(null);
  const [stream, setStream] = useState(null);
  const [error, setError] = useState('');
  const [scanning, setScanning] = useState(false);
  const [done, setDone] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    startCamera();

    // Escaneo automático después de 1.5 segundos
    const scanTimer = setTimeout(() => {
      setScanning(true);

      // Redirigir al dashboard después del escaneo
      setTimeout(() => {
        setDone(true);
        stopCamera();
        setTimeout(() => {
          navigate('/dashboard');
        }, 500);
      }, 2000);
    }, 1500);

    return () => {
      clearTimeout(scanTimer);
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
      setError('No se pudo acceder a la cámara.');
      // Si no hay cámara, igual redirigir después de un momento
      setTimeout(() => navigate('/dashboard'), 2000);
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
    }
  };

  return (
    <div className="biometric-wrapper">
      <div className="glass-container biometric-container">
        <h2>Verificación Biométrica</h2>
        <p>{scanning ? 'Escaneando...' : 'Preparando cámara...'}</p>

        {error && <div className="error-message">{error}</div>}

        <div className="camera-box">
          {!stream && !error && (
            <div className="camera-placeholder">
              <div className="spinner"></div>
              <p>Iniciando cámara...</p>
            </div>
          )}
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className={`video-feed ${(!stream || done) ? 'hidden' : ''}`}
          />

          {scanning && (
            <div className="scanning-overlay">
              <div className="scanner-line"></div>
            </div>
          )}

          {done && (
            <div className="verified-overlay">
              <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="#22c55e" strokeWidth="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                <polyline points="22 4 12 14.01 9 11.01" />
              </svg>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default BiometricPage;