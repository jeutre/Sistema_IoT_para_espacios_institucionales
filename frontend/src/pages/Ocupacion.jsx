import React, { useEffect, useState } from 'react';
import useIotStore from '../store/iotStore';
import './Ocupacion.css';

const Ocupacion = () => {
  const {
    ocupacion, fetchOcupacion,
    historialOcupacion, fetchHistorialOcupacion,
    dispositivos, fetchDispositivos,
    loading,
  } = useIotStore();

  const [filtros, setFiltros] = useState({ dispositivo: '', desde: '', hasta: '' });
  const [buscado, setBuscado] = useState(false);

  // Tiempo real: se refresca cada 6 segundos (ocupación + dispositivos).
  useEffect(() => {
    const cargar = () => { fetchOcupacion(); fetchDispositivos(); };
    cargar();
    const interval = setInterval(cargar, 6000);
    return () => clearInterval(interval);
  }, [fetchOcupacion, fetchDispositivos]);

  const handleBuscarHistorial = (e) => {
    e.preventDefault();
    setBuscado(true);
    fetchHistorialOcupacion(filtros);
  };

  const handleLimpiarFiltros = () => {
    setFiltros({ dispositivo: '', desde: '', hasta: '' });
    setBuscado(false);
  };

  const nombreDispositivo = (id) => {
    const disp = dispositivos.find((d) => d.id === Number(id));
    return disp ? disp.identificador : `#${id}`;
  };

  const ocupados = ocupacion.filter(o => o.estado === 'ocupado').length;
  const libres = ocupacion.filter(o => o.estado === 'vacio').length;

  return (
    <div className="page-container">
      <style>{`
        @keyframes ocPulseRing { 0%{transform:scale(0.9);opacity:0.7} 70%{transform:scale(1.3);opacity:0} 100%{opacity:0} }
        @keyframes ocBlink { 0%,100%{opacity:1} 50%{opacity:0.3} }
        @keyframes ocGlowGreen { 0%,100%{box-shadow:0 0 18px rgba(0,255,102,0.2)} 50%{box-shadow:0 0 32px rgba(0,255,102,0.45)} }
        @keyframes ocGlowRed { 0%,100%{box-shadow:0 0 20px rgba(255,0,60,0.3)} 50%{box-shadow:0 0 40px rgba(255,0,60,0.6)} }
        .oc-card{transition:all .4s ease;}
      `}</style>

      <div className="toolbar-row">
        <div className="toolbar-left">
          <h2 className="ocupacion-page-title">Monitoreo de Ocupación</h2>
        </div>
        <div className="toolbar-right">
          <span style={{ display:'inline-flex', alignItems:'center', gap:6, color:'#00ff66', fontSize:12, border:'1px solid rgba(0,255,102,0.35)', borderRadius:20, padding:'3px 12px' }}>
            <span style={{ width:7, height:7, borderRadius:'50%', background:'#00ff66', animation:'ocBlink 1.4s infinite' }}></span>
            EN VIVO
          </span>
        </div>
      </div>

      {/* KPIs */}
      <div style={{ display:'grid', gridTemplateColumns:'repeat(3,1fr)', gap:14, marginBottom:18 }}>
        <div style={{ background:'rgba(255,0,60,0.06)', border:'1px solid rgba(255,0,60,0.25)', borderRadius:12, padding:'0.9rem', textAlign:'center' }}>
          <div style={{ color:'#ff003c', fontSize:30, fontWeight:600 }}>{ocupados}</div>
          <div style={{ color:'#8aa0b8', fontSize:11, letterSpacing:'0.05em' }}>OCUPADOS</div>
        </div>
        <div style={{ background:'rgba(0,255,102,0.06)', border:'1px solid rgba(0,255,102,0.25)', borderRadius:12, padding:'0.9rem', textAlign:'center' }}>
          <div style={{ color:'#00ff66', fontSize:30, fontWeight:600 }}>{libres}</div>
          <div style={{ color:'#8aa0b8', fontSize:11, letterSpacing:'0.05em' }}>DISPONIBLES</div>
        </div>
        <div style={{ background:'rgba(0,240,255,0.06)', border:'1px solid rgba(0,240,255,0.22)', borderRadius:12, padding:'0.9rem', textAlign:'center' }}>
          <div style={{ color:'#00f0ff', fontSize:30, fontWeight:600 }}>{ocupacion.length}</div>
          <div style={{ color:'#8aa0b8', fontSize:11, letterSpacing:'0.05em' }}>SENSORES</div>
        </div>
      </div>

      {/* Tarjetas de ocupación animadas */}
      <div style={{ display:'flex', flexDirection:'column', gap:14 }}>
        {loading && ocupacion.length === 0 ? (
          <div className="page-card" style={{ textAlign:'center', padding:'2rem', color:'rgba(255,255,255,0.4)' }}>Cargando...</div>
        ) : ocupacion.length === 0 ? (
          <div className="page-card" style={{ textAlign:'center', padding:'2.5rem', color:'rgba(255,255,255,0.4)' }}>
            No hay datos de ocupación disponibles todavía.
          </div>
        ) : (
          ocupacion.map((ev, idx) => {
            const ocupado = ev.estado === 'ocupado';
            const color = ocupado ? '#ff003c' : '#00ff66';
            const rgba = ocupado ? '255,0,60' : '0,255,102';
            const anim = ocupado ? 'ocGlowRed 1.6s infinite' : 'ocGlowGreen 3s infinite';
            const ringSpeed = ocupado ? '1.4s' : '2.2s';
            return (
              <div key={idx} className="oc-card" style={{
                background:`rgba(${rgba},0.04)`, border:`1px solid rgba(${rgba},0.25)`,
                borderRadius:16, padding:'1.4rem', display:'flex', alignItems:'center', gap:'1.5rem',
                animation:anim
              }}>
                <div style={{ position:'relative', width:96, height:96, flexShrink:0, display:'flex', alignItems:'center', justifyContent:'center' }}>
                  <span style={{ position:'absolute', width:96, height:96, borderRadius:'50%', background:`rgba(${rgba},0.4)`, animation:`ocPulseRing ${ringSpeed} infinite` }}></span>
                  <span style={{ position:'absolute', width:96, height:96, borderRadius:'50%', background:`rgba(${rgba},0.3)`, animation:`ocPulseRing ${ringSpeed} infinite ${parseFloat(ringSpeed)/2}s` }}></span>
                  <div style={{ position:'relative', width:70, height:70, borderRadius:'50%', background:`rgba(${rgba},0.12)`, border:`2px solid ${color}`, display:'flex', alignItems:'center', justifyContent:'center' }}>
                    <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2">
                      {ocupado
                        ? (<><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/></>)
                        : (<><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></>)}
                    </svg>
                  </div>
                </div>

                <div style={{ flex:1 }}>
                  <div style={{ color:'#e8eef7', fontSize:18, fontWeight:600 }}>{ev.laboratorio || 'Laboratorio'}</div>
                  <div style={{ color:'#5f7185', fontSize:12, fontFamily:'monospace', marginBottom:6 }}>{ev.dispositivo || 'Sensor'}</div>
                  <div style={{ color, fontSize:22, fontWeight:600 }}>{ocupado ? 'Espacio Ocupado' : 'Espacio Disponible'}</div>
                  <div style={{ color:'#5f7185', fontSize:11, marginTop:8 }}>
                    Última actualización · <span style={{ color:'#00f0ff', fontFamily:'monospace' }}>
                      {ev.ultima_vez ? new Date(ev.ultima_vez).toLocaleTimeString('es-EC', { hour:'2-digit', minute:'2-digit' }) : '—'}
                    </span>
                  </div>
                </div>

                <div style={{ textAlign:'right' }}>
                  <div style={{ display:'flex', gap:3, alignItems:'flex-end', justifyContent:'flex-end', height:26 }}>
                    <span style={{ width:5, height:'40%', background:color, borderRadius:2 }}></span>
                    <span style={{ width:5, height:'65%', background:color, borderRadius:2 }}></span>
                    <span style={{ width:5, height:'90%', background:color, borderRadius:2 }}></span>
                    <span style={{ width:5, height:'100%', background:color, borderRadius:2 }}></span>
                  </div>
                  <div style={{ color:'#5f7185', fontSize:10, marginTop:6 }}>señal</div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Historial (sin cambios) */}
      <div className="glass-container historial-wrapper" style={{ marginTop:18 }}>
        <h3 className="form-title">Historial de ocupación</h3>
        <form onSubmit={handleBuscarHistorial} className="historial-filtros">
          <select value={filtros.dispositivo} onChange={(e) => setFiltros({ ...filtros, dispositivo: e.target.value })}>
            <option value="">Todos los dispositivos</option>
            {dispositivos.map((d) => (<option key={d.id} value={d.id}>{d.identificador}</option>))}
          </select>
          <input type="date" value={filtros.desde} onChange={(e) => setFiltros({ ...filtros, desde: e.target.value })} />
          <input type="date" value={filtros.hasta} onChange={(e) => setFiltros({ ...filtros, hasta: e.target.value })} />
          <button className="btn-primary" type="submit" disabled={loading}>
            {loading ? 'Buscando...' : 'Buscar historial'}
          </button>
          <button type="button" className="btn-secondary" onClick={handleLimpiarFiltros}>Limpiar</button>
        </form>

        <table className="historial-table">
          <thead>
            <tr><th>Dispositivo</th><th>Estado</th><th>Fecha y hora</th></tr>
          </thead>
          <tbody>
            {historialOcupacion.map((evento) => (
              <tr key={evento.id}>
                <td>{nombreDispositivo(evento.dispositivo)}</td>
                <td>
                  <span className={`estado-badge ${evento.estado === 'ocupado' ? 'desconectado' : 'conectado'}`}>
                    {evento.estado === 'ocupado' ? '● Ocupado' : '○ Vacío'}
                  </span>
                </td>
                <td>{new Date(evento.registrado_en).toLocaleString()}</td>
              </tr>
            ))}
            {buscado && !loading && historialOcupacion.length === 0 && (
              <tr><td colSpan="3" style={{ textAlign:'center', padding:'2rem' }}>No hay eventos para los filtros seleccionados.</td></tr>
            )}
            {!buscado && (
              <tr><td colSpan="3" style={{ textAlign:'center', padding:'2rem' }}>Selecciona un rango de fechas y presiona "Buscar historial".</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Ocupacion;