import React, { useState, useEffect } from 'react';
import { healthCheck } from './api';
import FaceDetector from './components/FaceDetector';

const App: React.FC = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        await healthCheck();
        setIsConnected(true);
      } catch (err) {
        setError('Failed to connect to backend');
        setIsConnected(false);
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Check every 30s

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="app">
      <header className="header">
        <h1>🎯 Computer Vision + Blockchain DApp</h1>
        <p>Face Tracking with DIDs on Cardano</p>
      </header>

      <main className="main">
        {error && <div className="error-banner">{error}</div>}

        <div className="status">
          {isConnected ? (
            <span className="status-badge status-connected">✅ Connected</span>
          ) : (
            <span className="status-badge status-disconnected">❌ Disconnected</span>
          )}
        </div>

        {isConnected && (
          <div className="content">
            <FaceDetector />
          </div>
        )}
      </main>

      <footer className="footer">
        <p>Made for PyCardano Course | Powered by Cardano Blockchain</p>
      </footer>
    </div>
  );
};

export default App;
