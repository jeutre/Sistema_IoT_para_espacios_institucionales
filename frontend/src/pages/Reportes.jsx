import React, { useState } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, ArcElement, Title, Tooltip, Legend } from 'chart.js';
import { Bar, Pie } from 'react-chartjs-2';
import api from '../axiosConfig';
import './Reportes.css';

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Title, Tooltip, Legend);

const Reportes = () => {
  const [exporting, setExporting] = useState(null);
  const [success, setSuccess] = useState('');

  const handleExportPDF = () => {
    alert("Exportación a PDF disponible próximamente.");
  };

  const handleExportCSV = async (modelo) => {
    setExporting(modelo);
    setSuccess('');
    try {
      const response = await api.get(`/reportes/exportar/${modelo}/`, {
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
      console.error("Error exportando:", error);
      alert("Error al exportar. Verifica conexión al servidor.");
    } finally {
      setExporting(null);
    }
  };

  const barData = {
    labels: ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4', 'Sem 5'],
    datasets: [{
      label: 'Rendimiento General',
      data: [65, 59, 80, 81, 56],
      backgroundColor: 'rgba(0, 240, 255, 0.4)',
      borderColor: '#00f0ff',
      borderWidth: 1,
      borderRadius: 4,
    }],
  };

  const pieData = {
    labels: ['Laboratorios', 'Aulas', 'Talleres', 'Auditorios'],
    datasets: [{
      data: [45, 30, 15, 10],
      backgroundColor: ['#00f0ff', '#00ff66', '#a855f7', '#ff6b6b'],
      borderColor: ['rgba(10,20,40,0.8)'],
      borderWidth: 2,
    }],
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
          Exportaciones disponibles: 3
        </div>
        <div className="stat-chip">
          <span className="chip-dot green"></span>
          Última exportación: —
        </div>
      </div>

      <div className="page-card">
        <div className="export-section">
          <h3 className="section-title">Exportar Datos</h3>
          <div className="export-buttons">
            <button className="btn-secondary" onClick={handleExportPDF}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/>
                <line x1="16" y1="17" x2="8" y2="17"/>
              </svg>
              Exportar PDF
            </button>
            {[
              { key: 'historial', label: 'Historial de Uso', icon: 'clock' },
              { key: 'ocupacion', label: 'Ocupación', icon: 'users' },
              { key: 'conexion', label: 'Conexiones', icon: 'wifi' },
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
          <h3 className="section-title">Rendimiento General</h3>
          <div className="chart-wrapper"><Bar data={barData} options={chartOptions} /></div>
        </div>
        <div className="chart-card page-card">
          <h3 className="section-title">Ocupación de Espacios</h3>
          <div className="chart-wrapper"><Pie data={pieData} options={chartOptions} /></div>
        </div>
      </div>
    </div>
  );
};

export default Reportes;