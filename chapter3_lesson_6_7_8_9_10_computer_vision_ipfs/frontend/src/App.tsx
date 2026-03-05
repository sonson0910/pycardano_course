import React, { useState, useEffect } from 'react';
import { healthCheck } from './api';
import FaceDetector from './components/FaceDetector';
import { DIDAManagement } from './components/DIDAManagement';
import './App.css';

const App: React.FC = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [preFilledDID, setPreFilledDID] = useState<{
    did: string;
    ipfs_hash: string;
  } | null>(null);
  const [activeTab, setActiveTab] = useState<'detect' | 'manage'>('detect');

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

  const handleDIDCreated = (didData: any) => {
    setPreFilledDID({
      did: didData.did,
      ipfs_hash: didData.ipfs_hash,
    });
    // Auto-switch to manage tab after DID created
    setTimeout(() => setActiveTab('manage'), 1000);
  };

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
            {/* Tab Navigation */}
            <div className="tabs">
              <button
                className={`tab-button ${activeTab === 'detect' ? 'active' : ''}`}
                onClick={() => setActiveTab('detect')}
              >
                📸 1. Detect Face
              </button>
              <button
                className={`tab-button ${activeTab === 'manage' ? 'active' : ''}`}
                onClick={() => setActiveTab('manage')}
              >
                🆔 2. Manage DIDs
              </button>
            </div>

            {/* Tab Content */}
            <div className="tab-content">
              {activeTab === 'detect' && (
                <div className="tab-pane active">
                  <FaceDetector onDIDCreated={handleDIDCreated} />
                </div>
              )}

              {activeTab === 'manage' && (
                <div className="tab-pane active">
                  <DIDAManagement preFilledDID={preFilledDID} />
                </div>
              )}
            </div>
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
