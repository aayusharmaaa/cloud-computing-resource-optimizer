import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Cloud, Download, Wifi, Server, Settings, Cpu as IconCpu, ShieldAlert, ArrowUpCircle, ArrowDownCircle, FileWarning } from 'lucide-react';
import { useTheme } from '../ThemeContext';
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
  const [loading, setLoading] = useState(false);
  const wsRef = useRef(null);
  
  const [cluster, setCluster] = useState('us-east-1a-prod-01');
  const { theme } = useTheme();
  
  // HITL State
  const [aiEnabled, setAiEnabled] = useState(true);
  const [forceLoad, setForceLoad] = useState(null);
  const [maxNodes, setMaxNodes] = useState(10);

  const fetchDashboardStats = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/api/dashboard/stats`);
      setDashboardStats(res.data);
    } catch (err) {
      console.error('Error fetching dashboard stats:', err);
    }
  };

  const fetchPrediction = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE_URL}/api/predict/`);
      setPrediction(res.data);

      const formattedHistory = res.data.cpu_history.map((val, i) => ({
        time: `T-${res.data.cpu_history.length - i}`,
        cpu: val,
        memory: res.data.memory_history[i] || 0
      }));
      setHistory(formattedHistory);
    } catch (err) {
      console.error('Error fetching prediction:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws');
    wsRef.current = ws;

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      let iso = data.timestamp;
      if (typeof iso === 'string' && !iso.endsWith('Z')) iso = `${iso}Z`;
      let dateObj = new Date(iso);
      if (Number.isNaN(dateObj.getTime())) dateObj = new Date();
      const formatted = new Intl.DateTimeFormat(undefined, {
        hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false
      }).format(dateObj);
      
      setRealtimeData(prev => [...prev, { ...data, time: formatted }].slice(-50));
    };
    return () => ws.close();
  }, []);

  useEffect(() => {
    fetchDashboardStats();
    fetchPrediction();
    const interval = setInterval(() => {
      fetchDashboardStats();
    }, 30000);
    return () => clearInterval(interval);
  }, []);

  const exportReport = () => {
    const reportData = {
      generatedAt: new Date().toISOString(),
      clusterID: cluster,
      supervisorConfig: {
        aiAutoscaling: aiEnabled,
        maxNodesLimit: maxNodes
      },
      telemetrySnapshot: dashboardStats,
      predictiveModel: prediction,
      recentNodesState: activeNodes
    };
    
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(reportData, null, 2));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", `cloud-audit-${cluster}-${Date.now()}.json`);
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
  };

  const handleManualAction = (actionType) => {
    setForceLoad(actionType);
    setTimeout(() => {
      setForceLoad(null);
      alert(`System executed manual architectural override [${actionType}] across ${cluster}.`);
    }, 1500);
  };

  const activeNodes = [
    { id: 'node-alpha', status: 'optimal', lag: '12ms', ip: '192.168.1.101' },
    { id: 'node-beta', status: 'optimal', lag: '14ms', ip: '192.168.1.102' },
    { id: 'node-gamma', status: 'warning', lag: '45ms', ip: '192.168.1.103' },
    { id: 'node-delta', status: 'optimal', lag: '11ms', ip: '192.168.1.104' },
  ];

  return (
    <div className={`dashboard-container ${theme}`}>
      <div className="dashboard-header">
        
        <div className="toolbar-title" style={{ fontSize: '1.1rem', fontWeight: '600', color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
           Operations Dashboard
        </div>
        
        <div className="header-tools">
          <div className="live-status-indicator">
            <span className="live-dot"></span>
            <span>Live Stream</span>
          </div>
          
          <select 
            className="tool-select"
            value={cluster}
            onChange={(e) => setCluster(e.target.value)}
          >
            <option value="us-east-1a-prod-01">us-east-1a-prod</option>
            <option value="eu-west-1-prod-02">eu-west-1-prod</option>
            <option value="ap-south-1-prod-03">ap-south-1-prod</option>
          </select>

          <button className="btn-secondary" onClick={fetchPrediction} disabled={loading}>
            <Wifi size={16} /> Sync Metrics
          </button>
          <button className="btn-primary" onClick={exportReport}>
            <Download size={16} /> Export JSON
          </button>
        </div>
      </div>

      {dashboardStats && (
        <div className="metrics-row">
          <MetricCard title="Compute Load" type="cpu" current={dashboardStats.current_cpu} predicted={dashboardStats.predicted_cpu} unit="%" />
          <MetricCard title="Memory Usage" type="memory" current={dashboardStats.current_memory} predicted={dashboardStats.predicted_memory} unit="%" />
          <CostCard hourly={dashboardStats.current_cost_per_hour} monthly={dashboardStats.monthly_cost} savings={dashboardStats.potential_savings} savingsPercent={dashboardStats.savings_percentage} />
          <ActionCard action={dashboardStats.recommended_action} urgency={prediction?.action_details?.urgency || 'medium'} reason={prediction?.action_details?.reason || 'Optimal routing in effect.'} confidence={prediction?.confidence ?? 0.6} />
        </div>
      )}

      <div className="main-content-row">
        <div className="dashboard-card chart-glow-bg">
          <div className="card-header">
            <div className="card-title">
              <IconCpu size={18} /> Telemetry Core
            </div>
            <div className={`ai-guardrail ${aiEnabled ? 'active' : 'bypassed'}`}>
               <ShieldAlert size={14} /> {aiEnabled ? 'AI Protection Active' : 'AI Protection Bypassed'}
            </div>
          </div>
          <div style={{ height: '400px', position: 'relative', zIndex: 1 }}>
            {history.length > 0 ? (
              <Chart data={history} realtimeData={realtimeData.slice(-20)} />
            ) : (
              <div className="loading-state">Initializing Prediction Matrices...</div>
            )}
          </div>
        </div>

        <div className="terminal-window">
          <div className="terminal-header">
            <div className="term-cmds">
              <div className="term-dot r"></div><div className="term-dot y"></div><div className="term-dot g"></div>
            </div>
            <span className="ssh-title">SSH supervisor@{cluster}</span>
          </div>
          <div className="terminal-body" id="term-body">
            {realtimeData.length === 0 && <div className="log-entry"><span className="log-time">System</span><span>Awaiting telemetry stream...</span></div>}
            
            {realtimeData.slice(-50).map((item, idx) => {
              const cpuVal = item.cpu;
              const warnCPU = cpuVal > 75;
              const warnMem = item.memory > 80;
              return (
                <div key={idx} className="log-entry">
                  <span className="log-time">[{item.time}]</span><span className="log-key">RAW</span>
                  <span className="log-val">
                    CPU: <span className={warnCPU ? 'warn' : 'ok'}>{cpuVal.toFixed(1)}%</span> | 
                    MEM: <span className={warnMem ? 'warn' : 'ok'}>{item.memory.toFixed(1)}%</span> | 
                    NET: <span className="ok">{item.network.toFixed(1)}MB/s</span>
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
      
      <div className="enterprise-features-row">
        <div className="dashboard-card">
          <div className="card-header">
            <div className="card-title">
              <Server size={18} /> Active Node Health
            </div>
          </div>
          <div className="nodes-grid">
            {activeNodes.map(node => (
              <div key={node.id} className={`node-card ${node.status}`}>
                <div className="node-icon"><Server size={20} /></div>
                <div className="node-info">
                  <div className="node-id">{node.id}</div>
                  <div className="node-ip">{node.ip}</div>
                </div>
                <div className="node-meta">
                  <span className="node-lag">{node.lag}</span>
                  <span className={`status-dot ${node.status}`}></span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="dashboard-card hitl-card">
          <div className="hitl-header-box">
            <div className="card-title" style={{ color: 'var(--accent)' }}>
              <Settings size={18} /> Control Override (HITL)
            </div>
            
            <div className="ai-status-toggle">
              <span className="toggle-label" style={{ color: aiEnabled ? 'var(--success)' : 'var(--text-muted)'}}>
                {aiEnabled ? 'AI Auto: ON' : 'AI Auto: OFF'}
              </span>
              <div className={`toggle-track ${!aiEnabled ? 'disabled' : ''}`} onClick={() => setAiEnabled(!aiEnabled)}>
                <div className="toggle-thumb"></div>
              </div>
            </div>
          </div>

          <div className="hitl-panel">
            <div className="node-limiter">
              <div style={{ display:'flex', justifyContent:'space-between', marginBottom:'0.5rem' }}>
                <span className="subtext" style={{color: 'var(--text-main)', fontWeight:600}}>Hard Node Limit Constraint</span>
                <span className="subtext" style={{fontWeight:700, color: 'var(--accent)'}}>{maxNodes} Instances</span>
              </div>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: '0 0 1rem 0', lineHeight: 1.4 }}>
                This constraint enforces an absolute maximum physical quota on server allocations. It acts as a mandatory billing fail-safe, ensuring the AI model cannot exceed your defined scaling budget during traffic spikes.
              </p>
              <input 
                type="range" 
                min="1" max="50" 
                value={maxNodes}
                onChange={(e) => setMaxNodes(Number(e.target.value))}
                className="pro-slider"
              />
            </div>

            <div className="hitl-actions" style={{ gridTemplateColumns: '1fr 1fr' }}>
              <button 
                className={`hitl-btn primary ${forceLoad === 'provision' ? 'loading' : ''}`}
                onClick={() => handleManualAction('provision')}
              >
                {forceLoad === 'provision' ? <div className="spinner"></div> : <><ArrowUpCircle size={20} /> Force Provision (Upscale)</>}
              </button>
              
              <button 
                className={`hitl-btn danger ${forceLoad === 'deprovision' ? 'loading' : ''}`}
                onClick={() => handleManualAction('deprovision')}
              >
                {forceLoad === 'deprovision' ? <div className="spinner"></div> : <><ArrowDownCircle size={20} /> Force Deprovision (Downscale)</>}
              </button>
              
              <button className="hitl-btn warn" onClick={() => alert("Submitting anomaly report to On-Call PagerDuty...")} style={{ gridColumn: 'span 2' }}>
                <FileWarning size={16} /> Submit Error Logs & Halt
              </button>
            </div>
          </div>
        </div>
      </div>

    </div>
  );
}

export default Dashboard;
