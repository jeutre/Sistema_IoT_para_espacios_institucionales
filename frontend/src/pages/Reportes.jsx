import React, { useState, useEffect } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, ArcElement, Title, Tooltip, Legend } from 'chart.js';
import { Bar, Pie } from 'react-chartjs-2';
import api from '../axiosConfig';
import './Reportes.css';

ChartJS.register(
  CategoryScale, LinearScale, BarElement, ArcElement, Title, Tooltip, Legend
);

const Reportes = () => {
  // Aquí podrías cargar datos reales en el futuro
  // const [chartData, setChartData] = useState(null);

  const handleExportPDF = () => {
    alert("La exportación a PDF requiere una librería adicional (ej. ReportLab o jsPDF). ¡Esta función estará disponible en la próxima actualización!");
  };

  const handleExportCSV = async (modelo) => {
    try {
      // El backend soporta: 'conexion', 'ocupacion', 'historial'
      const response = await api.get(`/reportes/exportar/${modelo}/`, {
        responseType: 'blob',
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `reporte_${modelo}_${new Date().getTime()}.csv`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
    } catch (error) {
      console.error("Error exportando el reporte:", error);
      alert(`Hubo un problema al exportar. Verifica que tienes conexión al servidor.`);
    }
  };

  // Datos de ejemplo para los gráficos
  const barChartData = {
    labels: ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4', 'Sem 5'],
    datasets: [{
      label: 'Rendimiento General',
      data: [65, 59, 80, 81, 56],
      backgroundColor: 'rgba(59, 130, 246, 0.5)',
      borderColor: 'rgba(59, 130, 246, 1)',
      borderWidth: 1,
    }],
  };

  const pieChartData = {
    labels: ['Laboratorios', 'Aulas', 'Talleres', 'Auditorios'],
    datasets: [{
      label: 'Ocupación de Espacios',
      data: [45, 30, 15, 10],
      backgroundColor: [
        'rgba(59, 130, 246, 0.7)',
        'rgba(16, 185, 129, 0.7)',
        'rgba(139, 92, 246, 0.7)',
        'rgba(239, 68, 68, 0.7)',
      ],
      borderColor: [
        '#3b82f6',
        '#10b981',
        '#8b5cf6',
        '#ef4444',
      ],
      borderWidth: 1,
    }],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { position: 'top' } }
  };

  return (
    <div className="reportes-container">
      <header className="dashboard-header">
        <h1>Panel de Reportes</h1>
        <p>Estadísticas de rendimiento y exportación de datos (Vista Administrativa).</p>
      </header>

      <div className="reportes-actions">
        <button className="btn-secondary" onClick={handleExportPDF} title="Función en desarrollo">Exportar Resumen (PDF)</button>
        <div className="export-group">
          <span>Exportar datos (CSV):</span>
          <button className="btn-secondary" onClick={() => handleExportCSV('historial')}>Historial de Uso</button>
          <button className="btn-secondary" onClick={() => handleExportCSV('ocupacion')}>Ocupación Actual</button>
          <button className="btn-secondary" onClick={() => handleExportCSV('conexion')}>Estado de Conexión</button>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-card glass-container">
          <h3>Rendimiento General por Semestre</h3>
          <div className="chart-wrapper"><Bar data={barChartData} options={chartOptions} /></div>
        </div>

        <div className="chart-card glass-container">
          <h3>Ocupación de Aulas</h3>
          <div className="chart-wrapper"><Pie data={pieChartData} options={chartOptions} /></div>
        </div>
      </div>
    </div>
  );
};

export default Reportes;
