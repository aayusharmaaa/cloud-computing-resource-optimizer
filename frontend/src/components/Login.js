import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Lock, Mail, Server, ArrowRight, Zap, Sun, Moon, Cloud, Infinity } from 'lucide-react';
import { useTheme } from '../ThemeContext';
import './Auth.css';

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    
    setTimeout(() => {
      if (email === 'admin@enterprise.com' && password === 'admin123') {
        setIsLoading(false);
        navigate('/cloud-setup');
      } else {
        setError('Invalid credentials. Please use demo account.');
        setIsLoading(false);
      }
    }, 1200);
  };

  const handleDemoFill = () => {
    setEmail('admin@enterprise.com');
    setPassword('admin123');
  };

  return (
    <div className={`auth-container eye-catching-theme ${theme}`}>
      {/* Dynamic Animated Background */}
      <div className="dynamic-bg">
        <div className="blob blob-1"></div>
        <div className="blob blob-2"></div>
        <div className="blob blob-3"></div>
      </div>
      
      {/* Theme Toggle Button */}
      <button className="theme-toggle-btn" onClick={toggleTheme}>
        {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
      </button>

      <div className="auth-wrapper glass-panel">
        <div className="brand-section">
          <div className="minimal-logo-auth">
            <Cloud className="cloud-layer-main" size={40} />
            <Infinity className="infinity-layer-main" size={22} />
          </div>
          <h1 className="gradient-text">Cloud Resource Optimizer</h1>
          <p className="subtitle">Infrastructure Intelligence</p>
        </div>

        <div className="auth-card">
          <form onSubmit={handleLogin} className="auth-form">
            <div className="form-header">
              <h2>Architect Portal</h2>
              <span className="secure-badge"><Lock size={12} /> Encrypted Session</span>
            </div>
            
            <div className="input-group">
              <input 
                type="email" 
                id="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className={email ? 'has-value' : ''}
              />
              <label htmlFor="email"><Mail size={16} /> Work Email</label>
              <div className="input-highlight"></div>
            </div>

            <div className="input-group">
              <input 
                type="password" 
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className={password ? 'has-value' : ''}
              />
              <label htmlFor="password"><Lock size={16} /> Password</label>
              <div className="input-highlight"></div>
            </div>

            {error && <div className="error-message">{error}</div>}

            <button type="submit" className={`auth-button ${isLoading ? 'loading' : ''}`} disabled={isLoading}>
              {isLoading ? (
                <div className="spinner"></div>
              ) : (
                <>
                  Authenticate Identity <ArrowRight size={18} />
                </>
              )}
              <div className="button-glare"></div>
            </button>
          </form>
          
          <div className="demo-credentials">
            <div className="demo-hint-title">
              <Zap size={14} className="accent-icon" /> Testing Environment
            </div>
            <p>Access the simulation sandbox using our demo credentials.</p>
            <button type="button" className="demo-fill-btn" onClick={handleDemoFill}>
              Load Demo Configuration
            </button>
          </div>
        </div>
      </div>

      {/* Futuristic decorative lines */}
      <div className="deco-line line-1"></div>
      <div className="deco-line line-2"></div>
    </div>
  );
}

export default Login;
