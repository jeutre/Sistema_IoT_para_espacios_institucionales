import React, { useState, useEffect, useCallback } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, ArcElement, Title, Tooltip, Legend } from 'chart.js';
import { Bar, Pie } from 'react-chartjs-2';
import api from '../axiosConfig';
import './Reportes.css';

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Title, Tooltip, Legend);

const Reportes = () => {
  const [exporting, setExporting] = useState(null);
  const [success, setSuccess] = useState('');
  const [desde, setDesde] = useState('');
  const [hasta, setHasta] = useState('');

  const [barData, setBarData] = useState({ labels: [], datasets: [] });
  const [pieData, setPieData] = useState({ labels: [], datasets: [] });
  const [cargando, setCargando] = useState(false);
  const [sinDatos, setSinDatos] = useState(false);

  // Trae datos REALES del backend (respeta el filtro de fechas)
  const cargarGraficos = useCallback(async () => {
    setCargando(true);
    setSinDatos(false);
    try {
      const params = {};
      if (desde) params.desde = desde;
      if (hasta) params.hasta = hasta;

      // Gráfico de barras: ocupación por hora (dato real de /ocupacion/horas-pico/)
      const hp = await api.get('/ocupacion/horas-pico/', { params });
      const detalle = hp.data?.detalle_por_hora ?? [];
      setBarData({
        labels: detalle.map(d => `${String(d.hora).padStart(2, '0')}:00`),
        datasets: [{
          label: 'Eventos "ocupado"',
          data: detalle.map(d => d.total_eventos_ocupado),
          backgroundColor: 'rgba(0, 240, 255, 0.4)',
          borderColor: '#00f0ff',
          borderWidth: 1,
          borderRadius: 4,
        }],
      });

      // Gráfico circular: ocupado vs disponible (dato real de /dashboard/kpis/)
      const kpis = await api.get('/dashboard/kpis/', { params });
      const ocupado = kpis.data?.porcentaje_ocupacion ?? 0;
      const disponible = Math.max(100 - ocupado, 0);
      setPieData({
        labels: ['Ocupado (%)', 'Disponible (%)'],
        datasets: [{
          data: [ocupado, disponible],
          backgroundColor: ['#00f0ff', '#00ff66'],
          borderColor: ['rgba(10,20,40,0.8)'],
          borderWidth: 2,
        }],
      });

      setSinDatos(detalle.length === 0);
    } catch (error) {
      console.error('Error cargando gráficos:', error);
      setSinDatos(true);
    } finally {
      setCargando(false);
    }
  }, [desde, hasta]);

  useEffect(() => { cargarGraficos(); }, [cargarGraficos]);

  const handleExportPDF = () => {
    alert('Exportación a PDF disponible próximamente.');
  };

  const handleExportCSV = async (modelo) => {
    setExporting(modelo);
    setSuccess('');
    try {
      const params = {};
      if (desde) params.desde = desde;
      if (hasta) params.hasta = hasta;
      const response = await api.get(`/reportes/exportar/${modelo}/`, {
        params,
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `reporte_${modelo}_${Date.now()}.csv`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
      setSuccess(`Reporte ${modelo} exportado correctamente`);
      setTimeout(() => setSuccess(''), 3000);
    } catch (error) {
      console.error('Error exportando:', error);
      alert('Error al exportar. Verifica conexión al servidor.');
    } finally {
      setExporting(null);
    }
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: { color: 'rgba(255,255,255,0.5)', font: { size: 11 } }
      }
    },
    scales: {
      x: { ticks: { color: 'rgba(255,255,255,0.3)' }, grid: { color: 'rgba(255,255,255,0.03)' } },
      y: { ticks: { color: 'rgba(255,255,255,0.3)' }, grid: { color: 'rgba(255,255,255,0.05)' } },
    }
  };

  return (
    <div className="page-container">
      <div className="report-stats">
        <div className="stat-chip">
          <span className="chip-dot cyan"></span>
          Período: {desde || 'inicio'} a {hasta || 'hoy'}
        </div>
      </div>

      {/* Filtro de fechas (HU-33) */}
      <div className="page-card">
        <h3 className="section-title">Período del reporte</h3>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-end', flexWrap: 'wrap' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', opacity: 0.6 }}>Desde</label>
            <input type="date" value={desde} onChange={e => setDesde(e.target.value)} />
          </div>
          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', opacity: 0.6 }}>Hasta</label>
            <input type="date" value={hasta} onChange={e => setHasta(e.target.value)} />
          </div>
          <button className="btn-secondary" onClick={cargarGraficos}>Aplicar</button>
          <button className="btn-secondary" onClick={() => { setDesde(''); setHasta(''); }}>Limpiar</button>
        </div>
      </div>

      <div className="page-card">
        <div className="export-section">
          <h3 className="section-title">Exportar Datos</h3>
          <div className="export-buttons">
            <button className="btn-secondary" onClick={handleExportPDF}>Exportar PDF</button>
            {[
              { key: 'historial', label: 'Historial de Uso' },
              { key: 'ocupacion', label: 'Ocupación' },
              { key: 'conexion', label: 'Conexiones' },
            ].map(item => (
              <button
                key={item.key}
                className="btn-primary"
                onClick={() => handleExportCSV(item.key)}
                disabled={exporting === item.key}
              >
                {exporting === item.key ? '↻ Exportando...' : `CSV: ${item.label}`}
              </button>
            ))}
          </div>
          {success && <div className="export-success">{success}</div>}
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-card page-card">
          <h3 className="section-title">Ocupación por hora {cargando && '(cargando...)'}</h3>
          <div className="chart-wrapper">
            {sinDatos
              ? <p style={{ opacity: 0.5, textAlign: 'center' }}>Sin datos de ocupación en el período.</p>
              : <Bar data={barData} options={chartOptions} />}
          </div>
        </div>
        <div className="chart-card page-card">
          <h3 className="section-title">Ocupado vs Disponible</h3>
          <div className="chart-wrapper"><Pie data={pieData} options={chartOptions} /></div>
        </div>
      </div>
    </div>
  );
};

export default Reportes;