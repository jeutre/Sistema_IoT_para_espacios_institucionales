import React from 'react';
import './SimpleChart.css';

const SimpleChart = ({ title, data, type = 'bar', height = 200 }) => {
  const maxValue = Math.max(...data.map(item => item.value));
  
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
    const points = data.map((item, index) => {
      const x = (index / (data.length - 1)) * 100;
      const y = 100 - (item.value / maxValue) * 100;
      return `${x}% ${y}%`;
    }).join(', ');
    
    return (
      <div className="chart-line-container">
        <svg className="chart-line-svg" viewBox="0 0 100 100" preserveAspectRatio="none">
          <polyline
            points={points}
            fill="none"
            stroke="var(--accent-primary)"
            strokeWidth="2"
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