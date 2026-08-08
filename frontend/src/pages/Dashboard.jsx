import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import useIotStore from '../store/iotStore';
import SimpleChart from '../components/SimpleChart';
import api from '../axiosConfig';
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

  const [time, setTime] = useState(new Date());
  const [labChartData, setLabChartData] = useState([]);
  const [activityChartData, setActivityChartData] = useState([]);
  const [networkNodes, setNetworkNodes] = useState([]);
  const [kpis, setKpis] = useState(null);

  // KPIs reales del backend (HU-23) + actividad real por hora
  useEffect(() => {
    const cargar = () => {
      api.get('/dashboard/kpis/').then(r => setKpis(r.data)).catch(() => {});
      api.get('/ocupacion/horas-pico/').then(r => {
        const det = r.data?.detalle_por_hora ?? [];
        setActivityChartData(det.map(d => ({
          label: `${String(d.hora).padStart(2, '0')}:00`,
          value: d.total_eventos_ocupado
        })));
      }).catch(() => {});
    };
    cargar();
    const id = setInterval(cargar, 15000);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    const interval = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    // Todo el dashboard en tiempo real: se recargan los datos cada 10 segundos.
    const cargarStore = () => {
      fetchDispositivos();
      fetchOcupacion();
      fetchAlertas();
    };
    cargarStore();
    const id = setInterval(cargarStore, 10000);
    return () => clearInterval(id);
  }, [fetchDispositivos, fetchOcupacion, fetchAlertas]);

  useEffect(() => {
    const safeDispositivos = Array.isArray(dispositivos) ? dispositivos : [];
    const safeOcupacion = Array.isArray(ocupacion) ? ocupacion : [];
    const safeAlertas = Array.isArray(alertas) ? alertas : [];

    if (safeDispositivos.length > 0 || safeOcupacion.length > 0 || safeAlertas.length > 0) {
      const dispositivosActivos = safeDispositivos.filter(d => d.estado === 'conectado').length;
      const totalDispositivos = safeDispositivos.length;
      const alertasCriticas = safeAlertas.filter(a => a.nivel === 'critico').length;
      
      const ahora = new Date();
      const ocupacionReciente = safeOcupacion.filter(o => {
        const fechaEvento = new Date(o.registrado_en);
        const diferenciaMinutos = (ahora - fechaEvento) / (1000 * 60);
        return diferenciaMinutos <= 30 && o.estado === 'ocupado';
      });
      
      const dispositivosBajoConsumo = safeDispositivos.filter(d => 
        d.estado === 'conectado' && d.modo_consumo === 'bajo'
      ).length;
      const eficienciaEnergetica = totalDispositivos > 0 
        ? Math.round((dispositivosBajoConsumo / totalDispositivos) * 100)
        : 85; // Default if no data

      setMetrics({
        dispositivosActivos,
        totalDispositivos,
        alertasCriticas,
        ocupacionActual: ocupacionReciente.length,
        eficienciaEnergetica
      });

      // --- Generar datos para Gráfico de Ocupación por Lab ---
      const labCounts = {};
      safeOcupacion.forEach(o => {
        if (o.estado === 'ocupado') {
          const device = safeDispositivos.find(d => d.id === o.dispositivo);
          if (device && device.laboratorio) {
            const labName = device.laboratorio.nombre || `Lab ${device.laboratorio}`;
            labCounts[labName] = (labCounts[labName] || 0) + 1;
          }
        }
      });
      
      let labData = Object.keys(labCounts).map(lab => ({
        label: lab.replace('Laboratorio', 'Lab'),
        value: labCounts[lab]
      }));
      if (labData.length === 0) {
        labData = [{label: 'Sin eventos recientes', value: 0}];
      }
      setLabChartData(labData);

      // La actividad por hora ahora viene de datos REALES (ver efecto de KPIs arriba).

      // --- Topología Dinámica ---
      const nodes = safeDispositivos.map((d, index) => {
        const positions = [
          {x: 20, y: 30}, {x: 50, y: 15}, {x: 75, y: 40}, 
          {x: 35, y: 70}, {x: 65, y: 80}, {x: 25, y: 55}, {x: 55, y: 50}
        ];
        const pos = positions[index % positions.length];
        return {
          id: d.id,
          x: pos.x,
          y: pos.y,
          label: d.identificador,
          active: d.estado === 'conectado',
          isGateway: false
        };
      });
      // Nodo Gateway
      nodes.push({ id: 'gw', x: 85, y: 65, label: 'Gateway Central', active: true, isGateway: true });
      setNetworkNodes(nodes);
    }
  }, [dispositivos, ocupacion, alertas]);

  const formatDate = (date) => {
    return date.toLocaleDateString('es-EC', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString('es-EC', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    });
  };

  if (loading && dispositivos.length === 0) {
    return (
      <div className="dashboard-container">
        <header className="dashboard-header">
          <div className="header-top">
            <div className="header-brand">
              <div className="logo-icon">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="2" y="2" width="20" height="8" rx="2" ry="2" />
                  <rect x="2" y="14" width="20" height="8" rx="2" ry="2" />
                  <line x1="6" y1="6" x2="6.01" y2="6" />
                  <line x1="6" y1="18" x2="6.01" y2="18" />
                </svg>
              </div>
              <div>
                <h1>Centro de Comando IoT</h1>
                <p className="subtitle">Sistema de Monitoreo Inteligente</p>
              </div>
            </div>
            <div className="header-status">
              <div className="status-indicator loading-pulse">
                <span className="status-dot"></span>
                Inicializando sistemas...
              </div>
            </div>
          </div>
        </header>
        <div className="widgets-grid">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="glass-container widget skeleton">
              <div className="skeleton-icon"></div>
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
      <div className="dashboard-bg-grid"></div>
      <div className="dashboard-bg-circles">
        <div className="bg-circle c1"></div>
        <div className="bg-circle c2"></div>
        <div className="bg-circle c3"></div>
      </div>

      <header className="dashboard-header">
        <div className="header-top">
          <div className="header-brand">
            <div className="logo-icon">
              <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="2" y="2" width="20" height="8" rx="2" ry="2" />
                <rect x="2" y="14" width="20" height="8" rx="2" ry="2" />
                <line x1="6" y1="6" x2="6.01" y2="6" />
                <line x1="6" y1="18" x2="6.01" y2="18" />
              </svg>
            </div>
            <div>
              <h1>Centro de Comando IoT</h1>
              <p className="subtitle">Sistema de Monitoreo Inteligente v2.0</p>
            </div>
          </div>
          <div className="header-right">
            <div className="header-time">
              <div className="time-digital">{formatTime(time)}</div>
              <div className="date-text">{formatDate(time)}</div>
            </div>
            <div className="header-status">
              <div className="status-indicator online">
                <span className="status-dot"></span>
                Sistema Operativo
              </div>
            </div>
          </div>
        </div>
        <div className="header-stats-bar">
          <div className="stat-chip">
            <span className="chip-dot cyan"></span>
            Uptime: 99.8%
          </div>
          <div className="stat-chip">
            <span className="chip-dot green"></span>
            Red: Estable
          </div>
          <div className="stat-chip">
            <span className="chip-dot yellow"></span>
            Latencia: 12ms
          </div>
          <div className="stat-chip">
            <span className="chip-dot purple"></span>
            Señal WiFi: -45dBm
          </div>
        </div>
      </header>

      {/* ── KPIs Institucionales (HU-23) ── */}
      <div className="glass-container" style={{ padding: '1.2rem', marginBottom: '1rem' }}>
        <div style={{ display:'flex', alignItems:'center', gap:8, marginBottom:'1rem' }}>
          <span style={{ color:'#00f0ff', fontWeight:600 }}>KPIs Institucionales</span>
          <span style={{ marginLeft:'auto', color:'#00ff66', fontSize:12, border:'1px solid rgba(0,255,102,0.35)', borderRadius:20, padding:'2px 10px' }}>en vivo</span>
        </div>
        <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit,minmax(155px,1fr))', gap:14 }}>

          <div style={{ background:'rgba(0,240,255,0.06)', border:'1px solid rgba(0,240,255,0.2)', borderRadius:12, padding:'1rem' }}>
            <div style={{ color:'#8aa0b8', fontSize:11, letterSpacing:'0.04em' }}>OCUPACIÓN</div>
            <div style={{ color:'#00f0ff', fontSize:30, fontWeight:500 }}>{kpis?.porcentaje_ocupacion ?? 0}<span style={{fontSize:15}}>%</span></div>
            <div style={{ display:'flex', alignItems:'flex-end', gap:3, height:32, marginTop:8 }}>
              {activityChartData.slice(-8).map((d,i)=>{const mx=Math.max(...activityChartData.map(x=>x.value),1);return <div key={i} style={{ flex:1, height:`${Math.max((d.value/mx)*100,6)}%`, background:'#00f0ff', opacity:0.35+0.65*(d.value/mx), borderRadius:'2px 2px 0 0' }}></div>;})}
            </div>
            <div style={{ color:'#5f7185', fontSize:10, marginTop:6 }}>por hora (real)</div>
          </div>

          <div style={{ background:'rgba(168,85,247,0.06)', border:'1px solid rgba(168,85,247,0.22)', borderRadius:12, padding:'1rem' }}>
            <div style={{ color:'#8aa0b8', fontSize:11, letterSpacing:'0.04em' }}>DISPONIBILIDAD</div>
            <div style={{ color:'#a855f7', fontSize:30, fontWeight:500 }}>{kpis?.disponibilidad_equipos ?? 0}<span style={{fontSize:15}}>%</span></div>
            <div style={{ height:6, background:'rgba(255,255,255,0.08)', borderRadius:4, marginTop:14 }}><div style={{ height:'100%', width:`${kpis?.disponibilidad_equipos ?? 0}%`, background:'#a855f7', borderRadius:4 }}></div></div>
            <div style={{ color:'#5f7185', fontSize:10, marginTop:10 }}>equipos operativos</div>
          </div>

          <div style={{ background:'rgba(255,221,0,0.06)', border:'1px solid rgba(255,221,0,0.22)', borderRadius:12, padding:'1rem' }}>
            <div style={{ color:'#8aa0b8', fontSize:11, letterSpacing:'0.04em' }}>INACTIVIDAD</div>
            <div style={{ color:'#ffdd00', fontSize:30, fontWeight:500 }}>{kpis?.tiempo_promedio_inactividad_min ?? 0}<span style={{fontSize:15}}> min</span></div>
            <div style={{ height:6, background:'rgba(255,255,255,0.08)', borderRadius:4, marginTop:14 }}><div style={{ height:'100%', width:`${Math.min((kpis?.tiempo_promedio_inactividad_min ?? 0),100)}%`, background:'#ffdd00', borderRadius:4 }}></div></div>
            <div style={{ color:'#5f7185', fontSize:10, marginTop:10 }}>promedio equipos</div>
          </div>

          <div style={{ background:'rgba(0,255,102,0.06)', border:'1px solid rgba(0,255,102,0.22)', borderRadius:12, padding:'1rem' }}>
            <div style={{ color:'#8aa0b8', fontSize:11, letterSpacing:'0.04em' }}>AHORRO ENERG.</div>
            <div style={{ color:'#00ff66', fontSize:30, fontWeight:500 }}>{(((kpis?.ahorro_energetico?.ahorro_potencial_wh) ?? 0)/1000).toFixed(1)}<span style={{fontSize:15}}> kWh</span></div>
            <div style={{ height:6, background:'rgba(255,255,255,0.08)', borderRadius:4, marginTop:14 }}><div style={{ height:'100%', width:`${Math.min((((kpis?.ahorro_energetico?.ahorro_potencial_wh)??0)/1000),100)}%`, background:'#00ff66', borderRadius:4 }}></div></div>
            <div style={{ color:'#5f7185', fontSize:10, marginTop:10 }}>{kpis?.ahorro_energetico?.horas_inactividad_total ?? 0} h inactivas</div>
          </div>

          <div style={{ background:'rgba(255,102,0,0.06)', border:'1px solid rgba(255,102,0,0.22)', borderRadius:12, padding:'1rem' }}>
            <div style={{ color:'#8aa0b8', fontSize:11, letterSpacing:'0.04em' }}>EFICIENCIA</div>
            <div style={{ color:'#ff6600', fontSize:30, fontWeight:500 }}>{kpis?.eficiencia_operativa ?? 0}<span style={{fontSize:15}}>%</span></div>
            <div style={{ display:'flex', alignItems:'flex-end', gap:3, height:32, marginTop:8 }}>
              {activityChartData.slice(-8).map((d,i)=>{const mx=Math.max(...activityChartData.map(x=>x.value),1);return <div key={i} style={{ flex:1, height:`${Math.max((d.value/mx)*100,6)}%`, background:'#ff6600', opacity:0.35+0.65*(d.value/mx), borderRadius:'2px 2px 0 0' }}></div>;})}
            </div>
            <div style={{ color:'#5f7185', fontSize:10, marginTop:6 }}>uso real del espacio</div>
          </div>

        </div>
      </div>

      {/* Top Metrics Row */}
      <div className="widgets-grid">
        <div className="glass-container widget metric-card" onClick={() => navigate('/dashboard/dispositivos')} style={{cursor: 'pointer'}}>
          <div className="metric-icon cyan-glow">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="2" y="2" width="20" height="8" rx="2" ry="2" />
              <rect x="2" y="14" width="20" height="8" rx="2" ry="2" />
              <line x1="6" y1="6" x2="6.01" y2="6" />
              <line x1="6" y1="18" x2="6.01" y2="18" />
            </svg>
          </div>
          <div className="metric-content">
            <h3>Dispositivos Activos</h3>
            <div className="widget-value text-cyan">
              {metrics.dispositivosActivos}
              <span className="value-suffix">/{metrics.totalDispositivos}</span>
            </div>
            <div className="metric-bar">
              <div className="metric-bar-fill cyan" style={{width: `${metrics.totalDispositivos > 0 ? (metrics.dispositivosActivos/metrics.totalDispositivos)*100 : 0}%`}}></div>
            </div>
            <p className="metric-label">Módulos ESP32 en línea</p>
          </div>
        </div>

        <div className="glass-container widget metric-card" onClick={() => navigate('/dashboard/alertas')} style={{cursor: 'pointer'}}>
          <div className="metric-icon red-glow">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
              <line x1="12" y1="9" x2="12" y2="13" />
              <line x1="12" y1="17" x2="12.01" y2="17" />
            </svg>
          </div>
          <div className="metric-content">
            <h3>Alertas Críticas</h3>
            <div className="widget-value text-red">{metrics.alertasCriticas}</div>
            <div className="metric-bar">
              <div className="metric-bar-fill red" style={{width: `${Math.min(metrics.alertasCriticas * 20, 100)}%`}}></div>
            </div>
            <p className="metric-label">Requieren atención inmediata</p>
          </div>
        </div>

        <div className="glass-container widget metric-card">
          <div className="metric-icon green-glow">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 20V10" />
              <path d="M18 20V4" />
              <path d="M6 20v-4" />
            </svg>
          </div>
          <div className="metric-content">
            <h3>Eficiencia Operativa</h3>
            <div className="widget-value text-green">{kpis?.eficiencia_operativa ?? 0}<span className="value-suffix">%</span></div>
            <div className="metric-bar">
              <div className="metric-bar-fill green" style={{width: `${kpis?.eficiencia_operativa ?? 0}%`}}></div>
            </div>
            <p className="metric-label">% de ocupación real del espacio</p>
          </div>
        </div>

        <div className="glass-container widget metric-card" onClick={() => navigate('/dashboard/ocupacion')} style={{cursor: 'pointer'}}>
          <div className="metric-icon yellow-glow">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
              <circle cx="9" cy="7" r="4" />
              <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
              <path d="M16 3.13a4 4 0 0 1 0 7.75" />
            </svg>
          </div>
          <div className="metric-content">
            <h3>Ocupación Actual</h3>
            <div className="widget-value text-yellow">{metrics.ocupacionActual}<span className="value-suffix"> espacios</span></div>
            <div className="metric-bar">
              <div className="metric-bar-fill yellow" style={{width: `${Math.min(metrics.ocupacionActual * 20, 100)}%`}}></div>
            </div>
            <p className="metric-label">Aulas y laboratorios en uso</p>
          </div>
        </div>
      </div>

      {/* Middle Section: Network Topology + Quick Alerts */}
      <div className="dashboard-mid-section">
        <div className="glass-container network-panel">
          <div className="panel-header">
            <h3>
              <span className="panel-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
                </svg>
              </span>
              Topología de Red IoT
            </h3>
            <span className="panel-badge live">
              <span className="live-dot"></span>
              EN VIVO
            </span>
          </div>
          <div className="network-topology">
            <svg viewBox="0 0 100 100" className="network-svg">
              {/* Líneas de conexión */}
              {networkNodes.map(node => {
                if(node.isGateway) return null;
                return (
                  <line 
                    key={`line-${node.id}`}
                    x1={node.x} y1={node.y} 
                    x2="85" y2="65" 
                    stroke="rgba(0,240,255,0.3)" 
                    strokeWidth="0.8" 
                    strokeDasharray={node.active ? "none" : "3,3"}
                  />
                );
              })}
              {/* Nodos */}
              {networkNodes.map(node => (
                <g key={node.id}>
                  <circle cx={node.x} cy={node.y} r={node.isGateway ? 4 : 3} 
                    fill={node.active ? (node.isGateway ? '#00f0ff' : '#00ff66') : '#ff003c'}
                    opacity={node.active ? 1 : 0.4}
                  />
                  <circle cx={node.x} cy={node.y} r={node.isGateway ? 7 : 5}
                    fill="none"
                    stroke={node.active ? (node.isGateway ? '#00f0ff' : '#00ff66') : '#ff003c'}
                    strokeWidth="0.5"
                    opacity={0.5 + (node.active ? 0.5 : 0)}
                    className="pulse-ring"
                  />
                  <text x={node.x} y={node.y + (node.isGateway ? 8 : 7)} textAnchor="middle" 
                    fill={node.active ? 'rgba(255,255,255,0.7)' : 'rgba(255,255,255,0.3)'}
                    fontSize="2.5"
                  >
                    {node.label}
                  </text>
                </g>
              ))}
              {/* Datos de tráfico animados (fijos como efecto visual) */}
              <circle cx="35" cy="21" r="1.5" fill="#00f0ff" opacity="0.8" className="data-packet p1" />
              <circle cx="55" cy="78" r="1.5" fill="#00ff66" opacity="0.8" className="data-packet p2" />
            </svg>
          </div>
          <div className="network-stats">
            <div className="net-stat">
              <span className="net-stat-value">{metrics.totalDispositivos}</span>
              <span className="net-stat-label">Nodos</span>
            </div>
            <div className="net-stat">
              <span className="net-stat-value">{metrics.dispositivosActivos}</span>
              <span className="net-stat-label">Conectados</span>
            </div>
            <div className="net-stat">
              <span className="net-stat-value">1</span>
              <span className="net-stat-label">Gateway</span>
            </div>
            <div className="net-stat">
              <span className="net-stat-value">2.4</span>
              <span className="net-stat-label">Ghz</span>
            </div>
          </div>
        </div>

        <div className="glass-container alerts-panel">
          <div className="panel-header">
            <h3>
              <span className="panel-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
                </svg>
              </span>
              Alertas Recientes
            </h3>
            <span className="panel-badge count">{alertas.length}</span>
          </div>
          <div className="alerts-list">
            {alertas.length === 0 ? (
              <div className="alerts-empty">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="rgba(0,255,102,0.3)" strokeWidth="1.5">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                  <polyline points="22 4 12 14.01 9 11.01" />
                </svg>
                <p>Todos los sistemas operando con normalidad</p>
              </div>
            ) : (
              alertas.slice(0, 4).map((alerta) => (
                <div key={alerta.id} className={`alerta-item ${alerta.nivel}`}>
                  <div className="alerta-dot"></div>
                  <div className="alerta-info">
                    <span className="alerta-title">{alerta.descripcion}</span>
                    <span className="alerta-time">{alerta.tiempo_relativo}</span>
                  </div>
                  <span className={`alerta-level ${alerta.nivel}`}>{alerta.nivel}</span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="charts-grid">
        <SimpleChart 
          title="Actividad de Dispositivos (Últimas 24h)"
          data={activityChartData}
          type="line"
          height={250}
        />
        
        <SimpleChart 
          title="Ocupación por Laboratorio"
          data={labChartData}
          type="bar"
          height={250}
        />
      </div>

      {/* Footer Status Bar */}
      <div className="dashboard-footer">
        <div className="footer-left">
          <span className="footer-dot"></span>
          <span>Última actualización: {formatTime(time)}</span>
        </div>
        <div className="footer-right">
          <span>API v1.0</span>
          <span className="footer-sep">|</span>
          <span>Uptime: 99.8%</span>
          <span className="footer-sep">|</span>
          <span>Dispositivos: {metrics.dispositivosActivos}/{metrics.totalDispositivos}</span>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;