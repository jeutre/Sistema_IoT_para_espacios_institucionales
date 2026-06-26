import React from 'react';
import api from '../axiosConfig';
import './Reportes.css';

const Reportes = () => {
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

  return (
    <div className="reportes-container">
      <header className="dashboard-header">
        <h1>Panel de Reportes</h1>
        <p>Estadísticas de rendimiento y exportación de datos (Vista Administrativa).</p>
      </header>

      <div className="reportes-actions">
        <button className="btn-secondary" onClick={handleExportPDF}>Exportar a PDF</button>
        <button className="btn-secondary" onClick={() => handleExportCSV('historial')}>Exportar a Excel (CSV)</button>
      </div>

      <div className="charts-grid">
        <div className="chart-card glass-container">
          <h3>Rendimiento General por Semestre</h3>
          <div className="mock-chart bar-chart">
            {/* Simulación visual de un gráfico de barras */}
            <div className="bar" style={{ height: '60%' }}><span>Sem 1</span></div>
            <div className="bar" style={{ height: '80%' }}><span>Sem 2</span></div>
            <div className="bar" style={{ height: '40%' }}><span>Sem 3</span></div>
            <div className="bar" style={{ height: '70%' }}><span>Sem 4</span></div>
            <div className="bar" style={{ height: '90%' }}><span>Sem 5</span></div>
          </div>
        </div>

        <div className="chart-card glass-container">
          <h3>Ocupación de Aulas</h3>
          <div className="mock-chart pie-chart">
            {/* Simulación visual de un gráfico circular */}
            <div className="pie-slice" style={{ '--deg': '0deg', '--p': 45, '--c': '#3b82f6' }}></div>
            <div className="pie-slice" style={{ '--deg': '162deg', '--p': 30, '--c': '#10b981' }}></div>
            <div className="pie-slice" style={{ '--deg': '270deg', '--p': 25, '--c': '#8b5cf6' }}></div>
            <div className="pie-legend">
              <span style={{color: '#3b82f6'}}>■ Lab (45%)</span>
              <span style={{color: '#10b981'}}>■ Aulas (30%)</span>
              <span style={{color: '#8b5cf6'}}>■ Talleres (25%)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Reportes;
