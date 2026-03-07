import { useState, useEffect } from 'react';
import { healthCheck } from './api/client';
import FaceDetector from './components/FaceDetector';
import DIDManager from './components/DIDManager';

type Tab = 'detect' | 'manage';

export default function App() {
  const [tab, setTab] = useState<Tab>('detect');
  const [connected, setConnected] = useState(false);
  const [lastIpfsCid, setLastIpfsCid] = useState<string | null>(null);

  useEffect(() => {
    const check = async () => {
      try {
        await healthCheck();
        setConnected(true);
      } catch {
        setConnected(false);
      }
    };
    check();
    const interval = setInterval(check, 30_000);
    return () => clearInterval(interval);
  }, []);

  const handleFaceDetected = (ipfsCid: string) => {
    setLastIpfsCid(ipfsCid);
    setTab('manage');
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🎯 DID Face Tracking DApp</h1>
        <p>Computer Vision + Cardano Blockchain</p>
        <div className={`status-badge ${connected ? 'connected' : 'disconnected'}`}>
          <span>{connected ? '●' : '○'}</span>
          {connected ? 'Backend Connected' : 'Backend Disconnected'}
        </div>
      </header>

      <div className="tabs">
        <button
          className={`tab-btn ${tab === 'detect' ? 'active' : ''}`}
          onClick={() => setTab('detect')}
        >
          📸 Detect Face
        </button>
        <button
          className={`tab-btn ${tab === 'manage' ? 'active' : ''}`}
          onClick={() => setTab('manage')}
        >
          🆔 Manage DIDs
        </button>
      </div>

      {tab === 'detect' && (
        <FaceDetector onDetected={handleFaceDetected} />
      )}

      {tab === 'manage' && (
        <DIDManager initialIpfsCid={lastIpfsCid} />
      )}
    </div>
  );
}
