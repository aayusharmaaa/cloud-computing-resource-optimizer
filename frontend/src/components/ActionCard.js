import React from 'react';

function ActionCard({ action, urgency, reason, confidence }) {
  const getActionConfig = (action) => {
    switch (action) {
      case 'Scale Up':
        return { icon: '⬆️', color: '#e74c3c', bgColor: '#ffeaea' };
      case 'Scale Down':
        return { icon: '⬇️', color: '#2ecc71', bgColor: '#eafaf1' };
      default:
        return { icon: '➡️', color: '#3498db', bgColor: '#eaf5ff' };
    }
  };

  const getUrgencyConfig = (urgency) => {
    switch (urgency) {
      case 'high':
        return { label: 'High Priority', color: '#e74c3c' };
      case 'medium':
        return { label: 'Medium Priority', color: '#f39c12' };
      default:
        return { label: 'Low Priority', color: '#2ecc71' };
    }
  };

  const actionConfig = getActionConfig(action);
  const urgencyConfig = getUrgencyConfig(urgency);

  return (
    <div 
      className="action-card"
      style={{ 
        borderLeftColor: actionConfig.color,
        backgroundColor: actionConfig.bgColor
      }}
    >
      <div className="action-header">
        <h4>
          <span style={{ marginRight: 8, display: 'inline-flex', verticalAlign: 'middle' }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
              <path d="M4 7h16M7 12h10M9 17h6" stroke="#111827" strokeWidth="1.5" strokeLinecap="round"/>
            </svg>
          </span>
          Recommended Action
        </h4>
      </div>
      <div className="action-content">
        <div className="action-name" style={{ color: actionConfig.color }}>
          {action}
        </div>
        <div className="urgency-badge" style={{ backgroundColor: urgencyConfig.color }}>
          {urgencyConfig.label}
        </div>
        {reason && (
          <div className="action-reason">
            {reason}
          </div>
        )}
        <div className="confidence-indicator">
          <span className="label">Confidence:</span>
          <div className="confidence-bar">
            <div 
              className="confidence-fill"
              style={{ 
                width: `${confidence * 100}%`,
                backgroundColor: confidence > 0.7 ? '#2ecc71' : confidence > 0.5 ? '#f39c12' : '#e74c3c'
              }}
            />
            <span className="confidence-value">{Math.round(confidence * 100)}%</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ActionCard;


