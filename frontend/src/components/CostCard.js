import React from 'react';

function CostCard({ hourly, monthly, savings, savingsPercent }) {
  const annual = monthly * 12;
  const potentialAnnualSavings = savings * 24 * 365;

  return (
    <div className="cost-card">
      <div className="cost-header">
        <h4 style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
           <span style={{ fontWeight: '600', color: '#111827', fontSize: '18px' }}>$</span>
          Cost Analysis
        </h4>
      </div>
      <div className="cost-content">
        <div className="cost-item">
          <span className="cost-label">Hourly Cost:</span>
          <span className="cost-value">${hourly.toFixed(4)}</span>
        </div>
        <div className="cost-item">
          <span className="cost-label">Monthly Cost:</span>
          <span className="cost-value">${monthly.toFixed(2)}</span>
        </div>
        <div className="cost-item">
          <span className="cost-label">Annual Cost:</span>
          <span className="cost-value">${annual.toFixed(2)}</span>
        </div>
        <div className="savings-section">
          <div className="savings-header">
            <span className="savings-label">Potential Savings:</span>
            <span className="savings-percentage">{savingsPercent.toFixed(1)}%</span>
          </div>
          <div className="savings-details">
            <div className="savings-item">
              <span>Hourly:</span>
              <span className="savings-value">${savings.toFixed(4)}</span>
            </div>
            <div className="savings-item">
              <span>Annual:</span>
              <span className="savings-value">${potentialAnnualSavings.toFixed(2)}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default CostCard;


