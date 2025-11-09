import React from 'react';

function MetricCard({ title, current, predicted, unit, color, icon }) {
  const trend = predicted - current;
  const trendIcon = trend > 5 ? '▲' : trend < -5 ? '▼' : '—';
  const trendClass = trend > 5 ? 'trend-up' : trend < -5 ? 'trend-down' : 'trend-stable';

  return (
    <div className="metric-card" style={{ borderLeftColor: color }}>
      <div className="metric-header">
        <h4>
          {icon && <span style={{ marginRight: 8, display: 'inline-flex', verticalAlign: 'middle' }}>{icon}</span>}
          {title}
        </h4>
        <span className="trend-indicator">{trendIcon}</span>
      </div>
      <div className="metric-values">
        <div className="current-value">
          <span className="label">Current:</span>
          <span className="value" style={{ color }}>{current.toFixed(1)}{unit}</span>
        </div>
        <div className="predicted-value">
          <span className="label">Predicted:</span>
          <span className={`value ${trendClass}`}>
            {predicted.toFixed(1)}{unit}
          </span>
        </div>
      </div>
      <div className="metric-bar">
        <div 
          className="bar-fill current-bar"
          style={{ width: `${Math.min(current, 100)}%`, backgroundColor: color }}
        />
        <div 
          className="bar-fill predicted-bar"
          style={{ 
            width: `${Math.min(predicted, 100)}%`, 
            backgroundColor: color,
            opacity: 0.5
          }}
        />
      </div>
    </div>
  );
}

export default MetricCard;


