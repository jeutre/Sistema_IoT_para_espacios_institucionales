import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import useIotStore from '../store/iotStore';
import SimpleChart from '../components/SimpleChart';
import './Dashboard.css';

const Dashboard = () => {
  const navigate = useNavigate();
  const { 
    dispositivos, 
    ocupacion, 
    alertas, 
    loading, 
    fetchDispositivos, 
    fetchOcupacion, 
    fetchAlertas 
  } = useIotStore();
  
  const [metrics, setMetrics] = useState({
    dispositivosActivos: 0,
    totalDispositivos: 0,
    alertasCriticas: 0,
    ocupacionActual: 0,
    eficienciaEnergetica: 0
  });

  useEffect(() => {
    fetchDispositivos();
    fetchOcupacion();
    fetchAlertas();
  }, [fetchDispositivos, fetchOcupacion, fetchAlertas]);

  useEffect(() => {
    if (dispositivos.length > 0 || ocupacion.length > 0 || alertas.length > 0) {
      const dispositivosActivos = dispositivos.filter(d => d.estado === 'conectado').length;
      const totalDispositivos = dispositivos.length;
      const alertasCriticas = alertas.filter(a => a.nivel === 'critico').length;
      
      // Calcular ocupación actual (dispositivos con estado 'ocupado' en los últimos 30 minutos)
      const ahora = new Date();
      const ocupacionReciente = ocupacion.filter(o => {
        const fechaEvento = new Date(o.registrado_en);
        const diferenciaMinutos = (ahora - fechaEvento) / (1000 * 60);
        return diferenciaMinutos <= 30 && o.estado === 'ocupado';
      });
      
      // Calcular eficiencia energética (ejemplo: porcentaje de dispositivos en modo bajo consumo)
      const dispositivosBajoConsumo = dispositivos.filter(d => 
        d.estado === 'conectado' && d.modo_consumo === 'bajo'
      ).length;
      const eficienciaEnergetica = totalDispositivos > 0 
        ? Math.round((dispositivosBajoConsumo / totalDispositivos) * 100)
        : 0;

      setMetrics({
        dispositivosActivos,
        totalDispositivos,
        alertasCriticas,
        ocupacionActual: ocupacionReciente.length,
        eficienciaEnergetica
      });
    }
  }, [dispositivos, ocupacion, alertas]);

  if (loading && dispositivos.length === 0) {
    return (
      <div className="dashboard-container">
        <header className="dashboard-header">
          <h1>Centro de Comando IoT</h1>
          <p>Cargando métricas del campus inteligente...</p>
        </header>
        <div className="widgets-grid">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="glass-container widget skeleton">
              <div className="skeleton-title"></div>
              <div className="skeleton-value"></div>
              <div className="skeleton-text"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>Centro de Comando IoT</h1>
        <p>Estado global del campus inteligente y telemetría de sensores.</p>
      </header>

      <div className="widgets-grid">
        <div className="glass-container widget" onClick={() => navigate('/dashboard/dispositivos')} style={{cursor: 'pointer'}}>
          <h3>Dispositivos Activos</h3>
          <div className="widget-value text-cyan">
            {metrics.dispositivosActivos} / {metrics.totalDispositivos}
          </div>
          <p className="mt-2 text-sm text-muted">Módulos ESP32 en línea</p>
        </div>
        
        <div className="glass-container widget" onClick={() => navigate('/dashboard/alertas')} style={{cursor: 'pointer'}}>
          <h3>Alertas Críticas</h3>
          <div className="widget-value text-red">{metrics.alertasCriticas}</div>
          <p className="mt-2 text-sm text-muted">Requieren atención inmediata</p>
        </div>
        
        <div className="glass-container widget" onClick={() => navigate('/dashboard/ocupacion')} style={{cursor: 'pointer'}}>
          <h3>Eficiencia Energética</h3>
          <div className="widget-value text-green">{metrics.eficienciaEnergetica}%</div>
          <p className="mt-2 text-sm text-muted">Consumo dentro de lo esperado</p>
        </div>
        
        <div className="glass-container widget" onClick={() => navigate('/dashboard/ocupacion')} style={{cursor: 'pointer'}}>
          <h3>Ocupación Actual</h3>
          <div className="widget-value text-yellow">{metrics.ocupacionActual}</div>
          <p className="mt-2 text-sm text-muted">Aulas y laboratorios en uso</p>
        </div>
        
        {/* Charts Section */}
        <div className="charts-grid">
          <SimpleChart 
            title="Actividad de Dispositivos (Últimas 24h)"
            data={[
              { label: '00:00', value: 8 },
              { label: '04:00', value: 6 },
              { label: '08:00', value: 12 },
              { label: '12:00', value: 15 },
              { label: '16:00', value: 18 },
              { label: '20:00', value: 14 },
              { label: '23:59', value: 9 }
            ]}
            type="line"
            height={250}
          />
          
          <SimpleChart 
            title="Ocupación por Laboratorio"
            data={[
              { label: 'Lab 1', value: 85 },
              { label: 'Lab 2', value: 60 },
              { label: 'Lab 3', value: 45 },
              { label: 'Lab 4', value: 90 },
              { label: 'Lab 5', value: 30 }
            ]}
            type="bar"
            height={250}
          />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
