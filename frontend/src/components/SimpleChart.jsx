import React from 'react';
import './SimpleChart.css';

const SimpleChart = ({ title, data, type = 'bar', height = 200 }) => {
  const maxValue = (data && data.length) ? Math.max(...data.map(item => item.value), 1) : 1;

  const renderBarChart = () => {
    return (
      <div className="chart-bars">
        {data.map((item, index) => {
          const heightPercent = (item.value / maxValue) * 100;
          return (
            <div key={index} className="chart-bar-container">
              <div 
                className="chart-bar" 
                style={{ height: `${heightPercent}%` }}
                title={`${item.label}: ${item.value}`}
              >
                <span className="chart-bar-value">{item.value}</span>
              </div>
              <div className="chart-bar-label">{item.label}</div>
            </div>
          );
        })}
      </div>
    );
  };
  
  const renderLineChart = () => {
    if (!data || data.length === 0) {
      return <div className="chart-line-container"></div>;
    }
    // El viewBox es "0 0 100 100": los puntos van como números (NO porcentajes).
    const points = data.map((item, index) => {
      const x = data.length === 1 ? 50 : (index / (data.length - 1)) * 100;
      const y = 100 - (item.value / maxValue) * 100;
      return `${x},${y}`;
    }).join(' ');
    
    return (
      <div className="chart-line-container">
        <svg className="chart-line-svg" viewBox="0 0 100 100" preserveAspectRatio="none">
          <polyline
            points={points}
            fill="none"
            stroke="#00f0ff"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
        <div className="chart-line-labels">
          {data.map((item, index) => (
            <div key={index} className="chart-line-label">{item.label}</div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="simple-chart glass-container">
      <h3 className="chart-title">{title}</h3>
      <div className="chart-container" style={{ height: `${height}px` }}>
        {type === 'bar' ? renderBarChart() : renderLineChart()}
      </div>
    </div>
  );
};

export default SimpleChart;