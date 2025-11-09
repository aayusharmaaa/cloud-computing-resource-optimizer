import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import Chart from './Chart';
import MetricCard from './MetricCard';
import ActionCard from './ActionCard';
import CostCard from './CostCard';
import './Dashboard.css';

const API_BASE_URL = 'http://localhost:8000';

function Dashboard() {
  const [dashboardStats, setDashboardStats] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [history, setHistory] = useState([]);
  const [realtimeData, setRealtimeData] = useState([]);
  const [isRealtime, setIsRealtime] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const wsRef = useRef(null);
  const [theme, setTheme] = useState('light');
  // Theme management
  useEffect(() => {
    const saved = localStorage.getItem('cro_theme');
    const initial = saved === 'dark' ? 'dark' : 'light';
    setTheme(initial);
    document.documentElement.classList.toggle('dark', initial === 'dark');
  }, []);

  const toggleTheme = () => {
    const next = theme === 'light' ? 'dark' : 'light';
    setTheme(next);
    localStorage.setItem('cro_theme', next);
    document.documentElement.classList.toggle('dark', next === 'dark');
  };

  // Fetch dashboard stats
  const fetchDashboardStats = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/api/dashboard/stats`);
      setDashboardStats(res.data);
    } catch (err) {
      console.error('Error fetching dashboard stats:', err);
      setError('Failed to load dashboard data');
    }
  };

  // Fetch prediction
  const fetchPrediction = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE_URL}/api/predict/`);
      setPrediction(res.data);
      
      // Format history for chart
      const formattedHistory = res.data.cpu_history.map((val, i) => ({
        time: `T-${res.data.cpu_history.length - i}`,
        cpu: val,
        memory: res.data.memory_history[i] || 0
      }));
      setHistory(formattedHistory);
      
      setError(null);
    } catch (err) {
      console.error('Error fetching prediction:', err);
      setError('Failed to load predictions');
    } finally {
      setLoading(false);
    }
  };

  // Setup WebSocket for real-time updates
  useEffect(() => {
    if (isRealtime) {
      const ws = new WebSocket('ws://localhost:8000/ws');
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connected');
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        let iso = data.timestamp;
        if (typeof iso === 'string' && !iso.endsWith('Z')) iso = `${iso}Z`;
        let dateObj = new Date(iso);
        if (Number.isNaN(dateObj.getTime())) dateObj = new Date();
        const formatted = new Intl.DateTimeFormat(undefined, {
          hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false
        }).format(dateObj);
        setRealtimeData(prev => {
          const newData = [...prev, {
            ...data,
            time: formatted
          }];
          // Keep only last 20 data points
          return newData.slice(-20);
        });
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
      };

      return () => {
        ws.close();
      };
    } else {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    }
  }, [isRealtime]);

  // Initial data fetch
  useEffect(() => {
    fetchDashboardStats();
    fetchPrediction();
    
    // Refresh stats every 30 seconds
    const interval = setInterval(() => {
      fetchDashboardStats();
      if (!isRealtime) {
        fetchPrediction();
      }
    }, 30000);

    return () => clearInterval(interval);
  }, [isRealtime]);

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1 className="main-title">AI-Driven Cloud Resource Optimizer📈</h1>
        <div className="header-controls">
          <button
            className={`toggle-button ${theme === 'dark' ? 'active' : ''}`}
            onClick={toggleTheme}
            title="Toggle dark mode"
          >
            {theme === 'dark' ? 'Dark' : 'Light'}
          </button>
          <button
            className={`toggle-button ${isRealtime ? 'active' : ''}`}
            onClick={() => setIsRealtime(!isRealtime)}
          >
            {isRealtime ? 'Realtime' : 'Manual'}
          </button>
          <button
            className="refresh-button"
            onClick={fetchPrediction}
            disabled={loading}
          >
            {loading ? 'Loading…' : 'Refresh'}
          </button>
        </div>
      </div>

      {error && (
        <div className="error-banner">{error}</div>
      )}

      {/* Stats Cards */}
      <div className="stats-grid">
        {dashboardStats && (
          <>
            <MetricCard
              title="CPU Utilization"
              current={dashboardStats.current_cpu}
              predicted={dashboardStats.predicted_cpu}
              unit="%"
              color="#dc2626"
              icon={<svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><rect x="7" y="7" width="10" height="10" rx="2" stroke="#111827" strokeWidth="1.5"/><path d="M7 2v4M17 2v4M7 18v4M17 18v4M2 7h4M2 17h4M18 7h4M18 17h4" stroke="#111827" strokeWidth="1.5" strokeLinecap="round"/></svg>}
            />
            <MetricCard
              title="Memory Utilization"
              current={dashboardStats.current_memory}
              predicted={dashboardStats.predicted_memory}
              unit="%"
              color="#2563eb"
              icon={<svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><rect x="3" y="5" width="18" height="10" rx="2" stroke="#111827" strokeWidth="1.5"/><path d="M7 19h10" stroke="#111827" strokeWidth="1.5" strokeLinecap="round"/></svg>}
            />
            <CostCard
              hourly={dashboardStats.current_cost_per_hour}
              monthly={dashboardStats.monthly_cost}
              savings={dashboardStats.potential_savings}
              savingsPercent={dashboardStats.savings_percentage}
            />
            <ActionCard
              action={dashboardStats.recommended_action}
              urgency={prediction?.action_details?.urgency || 'medium'}
              reason={prediction?.action_details?.reason || ''}
              confidence={prediction?.confidence || 0}
            />
          </>
        )}
      </div>

      {/* Charts Section */}
      <div className="charts-section">
        <div className="chart-card">
          <h3 className="card-title">Resource Utilization</h3>
          {history.length > 0 ? (
            <Chart data={history} realtimeData={isRealtime ? realtimeData : []} />
          ) : (
            <div className="loading-placeholder">Loading chart data...</div>
          )}
        </div>

        {prediction && (
          <div className="chart-card">
            <h3 className="card-title">Prediction</h3>
            <div className="prediction-details">
              <div className="prediction-item">
                <span className="label">Predicted CPU:</span>
                <span className="value">{prediction.predicted_cpu}%</span>
              </div>
              <div className="prediction-item">
                <span className="label">Predicted Memory:</span>
                <span className="value">{prediction.predicted_memory}%</span>
              </div>
              <div className="prediction-item">
                <span className="label">Confidence:</span>
                <span className="value">{Math.round(prediction.confidence * 100)}%</span>
              </div>
              <div className="prediction-item">
                <span className="label">Cost Savings Potential:</span>
                <span className="value savings">${prediction.cost_savings.toFixed(4)}/hour</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Real-time Data Stream */}
      {isRealtime && realtimeData.length > 0 && (
        <div className="chart-card">
          <h3 className="card-title">Real-Time Metrics</h3>
          <div className="realtime-stream">
            {realtimeData.slice(-10).reverse().map((item, idx) => (
              <div key={idx} className="realtime-item">
                <span className="time">{item.time}</span>
                <span className="metric cpu">CPU: {item.cpu.toFixed(1)}%</span>
                <span className="metric memory">Mem: {item.memory.toFixed(1)}%</span>
                <span className="metric network">Net: {item.network.toFixed(1)}MB/s</span>
                <span className="metric cost">${item.cost.toFixed(4)}/hr</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Info Section */}
      <div className="info-card">
        <h3 className="card-title">About</h3>
        <p>
          This AI-driven cloud resource optimizer uses advanced LSTM neural networks to predict 
          future resource requirements based on historical patterns. The system analyzes CPU, 
          memory, and network utilization to recommend optimal scaling actions, helping you 
          maintain performance while minimizing costs.
        </p>
        <div className="features-list">
          <div className="feature">Real-time monitoring ✅</div>
          <div className="feature">Predictive analytics ✅</div>
          <div className="feature">Cost optimization ✅</div>
          <div className="feature">Automated recommendations ✅</div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
