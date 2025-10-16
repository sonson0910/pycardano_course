import React, { useState, useEffect } from 'react';
import './DIDAManagement.css';

interface DID {
  id: string;
  did: string;
  status: 'created' | 'registered' | 'updated' | 'verified' | 'revoked';
  faceHash: string;
  createdAt: string;
  lastUpdated: string;
  txHistory: Transaction[];
}

interface Transaction {
  action: 'create' | 'register' | 'update' | 'verify' | 'revoke';
  txHash: string;
  timestamp: string;
  confirmed: boolean;
}

interface FormData {
  didId: string;
  faceEmbedding: string;
  action: 'create' | 'register' | 'update' | 'verify' | 'revoke';
}

export const DIDAManagement: React.FC = () => {
  const [dids, setDids] = useState<DID[]>([]);
  const [formData, setFormData] = useState<FormData>({
    didId: '',
    faceEmbedding: '',
    action: 'create',
  });
  const [loading, setLoading] = useState(false);
  const [selectedDID, setSelectedDID] = useState<DID | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api/v1';

  // Fetch all DIDs
  const fetchDIDs = async () => {
    try {
      const response = await fetch(`${API_BASE}/dids`);
      if (!response.ok) throw new Error('Failed to fetch DIDs');
      const data = await response.json();
      setDids(data.dids || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch DIDs');
    }
  };

  // Fetch DID status
  const fetchDIDStatus = async (did: string) => {
    try {
      const response = await fetch(`${API_BASE}/did/${did}/status`);
      if (!response.ok) throw new Error('Failed to fetch DID status');
      const data = await response.json();
      setSelectedDID(data.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch DID status');
    }
  };

  // Create DID
  const createDID = async () => {
    if (!formData.didId || !formData.faceEmbedding) {
      setError('Please fill in all fields');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/did/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          did_id: formData.didId,
          face_embedding: formData.faceEmbedding,
        }),
      });

      if (!response.ok) throw new Error('Failed to create DID');
      const data = await response.json();
      setSuccess(`DID created! TX: ${data.tx_hash}`);
      setFormData({ didId: '', faceEmbedding: '', action: 'create' });
      setTimeout(fetchDIDs, 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create DID');
    } finally {
      setLoading(false);
    }
  };

  // Register DID
  const registerDID = async (did: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/did/${did}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });

      if (!response.ok) throw new Error('Failed to register DID');
      const data = await response.json();
      setSuccess(`DID registered! TX: ${data.tx_hash}`);
      setTimeout(() => fetchDIDStatus(did), 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to register DID');
    } finally {
      setLoading(false);
    }
  };

  // Update DID
  const updateDID = async (did: string) => {
    if (!formData.faceEmbedding) {
      setError('Please provide new face embedding');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/did/${did}/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          new_face_embedding: formData.faceEmbedding,
        }),
      });

      if (!response.ok) throw new Error('Failed to update DID');
      const data = await response.json();
      setSuccess(`DID updated! TX: ${data.tx_hash}`);
      setTimeout(() => fetchDIDStatus(did), 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update DID');
    } finally {
      setLoading(false);
    }
  };

  // Verify DID
  const verifyDID = async (did: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/did/${did}/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });

      if (!response.ok) throw new Error('Failed to verify DID');
      const data = await response.json();
      setSuccess(data.verified ? 'DID verified successfully!' : 'DID verification failed');
      setTimeout(() => fetchDIDStatus(did), 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to verify DID');
    } finally {
      setLoading(false);
    }
  };

  // Revoke DID
  const revokeDID = async (did: string) => {
    if (!confirm('Are you sure? This action is permanent and cannot be reversed.')) {
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/did/${did}/revoke`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });

      if (!response.ok) throw new Error('Failed to revoke DID');
      const data = await response.json();
      setSuccess(`DID revoked! TX: ${data.tx_hash}`);
      setTimeout(() => fetchDIDStatus(did), 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to revoke DID');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDIDs();
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'created': return 'created';
      case 'registered': return 'registered';
      case 'updated': return 'updated';
      case 'verified': return 'verified';
      case 'revoked': return 'revoked';
      default: return 'unknown';
    }
  };

  const getStatusLabel = (status: string) => {
    return status.charAt(0).toUpperCase() + status.slice(1);
  };

  return (
    <div className="did-management-container">
      <header className="did-header">
        <h1>🆔 DID Management</h1>
        <p>Decentralized Identity with Face Recognition on Cardano</p>
      </header>

      {error && (
        <div className="alert alert-error">
          <span>❌ {error}</span>
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      {success && (
        <div className="alert alert-success">
          <span>✅ {success}</span>
          <button onClick={() => setSuccess(null)}>×</button>
        </div>
      )}

      <div className="content-grid">
        {/* Create DID Section */}
        <section className="card create-section">
          <h2>Create New DID</h2>
          <div className="form-group">
            <label>DID ID</label>
            <input
              type="text"
              placeholder="did:cardano:your_id"
              value={formData.didId}
              onChange={(e) => setFormData({ ...formData, didId: e.target.value })}
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label>Face Embedding Hash</label>
            <textarea
              placeholder="QmYourIPFSHash..."
              value={formData.faceEmbedding}
              onChange={(e) => setFormData({ ...formData, faceEmbedding: e.target.value })}
              disabled={loading}
              rows={3}
            />
          </div>

          <button
            className="btn btn-primary"
            onClick={createDID}
            disabled={loading || !formData.didId || !formData.faceEmbedding}
          >
            {loading ? 'Creating...' : 'Create DID'}
          </button>
        </section>

        {/* DID List Section */}
        <section className="card list-section">
          <h2>Your DIDs ({dids.length})</h2>
          <div className="did-list">
            {dids.length === 0 ? (
              <p className="empty-message">No DIDs created yet</p>
            ) : (
              dids.map((did) => (
                <div
                  key={did.id}
                  className={`did-item did-item-${getStatusColor(did.status)}`}
                  onClick={() => fetchDIDStatus(did.did)}
                >
                  <div className="did-header-info">
                    <span className="did-name">{did.did}</span>
                    <span className={`did-status did-status-${getStatusColor(did.status)}`}>
                      {getStatusLabel(did.status)}
                    </span>
                  </div>
                  <p className="did-hash">{did.faceHash.substring(0, 40)}...</p>
                  <p className="did-timestamp">Created: {new Date(did.createdAt).toLocaleString()}</p>
                </div>
              ))
            )}
          </div>
        </section>
      </div>

      {/* Selected DID Actions */}
      {selectedDID && (
        <section className="card actions-section">
          <h2>DID Actions: {selectedDID.did}</h2>

          <div className="status-info">
            <p>
              <strong>Status:</strong>{' '}
              <span className={`status-value status-${getStatusColor(selectedDID.status)}`}>
                {getStatusLabel(selectedDID.status)}
              </span>
            </p>
            <p>
              <strong>Created:</strong> {new Date(selectedDID.createdAt).toLocaleString()}
            </p>
            <p>
              <strong>Last Updated:</strong> {new Date(selectedDID.lastUpdated).toLocaleString()}
            </p>
          </div>

          <div className="actions-grid">
            {selectedDID.status === 'created' && (
              <button
                className="btn btn-register"
                onClick={() => registerDID(selectedDID.did)}
                disabled={loading}
              >
                {loading ? 'Registering...' : 'Register'}
              </button>
            )}

            {selectedDID.status === 'registered' && (
              <>
                <button
                  className="btn btn-update"
                  onClick={() => updateDID(selectedDID.did)}
                  disabled={loading || !formData.faceEmbedding}
                >
                  {loading ? 'Updating...' : 'Update Face Hash'}
                </button>
                <button
                  className="btn btn-verify"
                  onClick={() => verifyDID(selectedDID.did)}
                  disabled={loading}
                >
                  {loading ? 'Verifying...' : 'Verify'}
                </button>
              </>
            )}

            {selectedDID.status !== 'revoked' && (
              <button
                className="btn btn-revoke"
                onClick={() => revokeDID(selectedDID.did)}
                disabled={loading}
              >
                {loading ? 'Revoking...' : 'Revoke'}
              </button>
            )}
          </div>

          <div className="tx-history">
            <h3>Transaction History</h3>
            {selectedDID.txHistory.length === 0 ? (
              <p>No transactions yet</p>
            ) : (
              <ul>
                {selectedDID.txHistory.map((tx, idx) => (
                  <li key={idx} className={tx.confirmed ? 'confirmed' : 'pending'}>
                    <strong>{tx.action.toUpperCase()}</strong>
                    <span className="tx-status">{tx.confirmed ? '✓ Confirmed' : '⏳ Pending'}</span>
                    <a
                      href={`https://preprod.cardanoscan.io/transaction/${tx.txHash}`}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {tx.txHash.substring(0, 16)}...
                    </a>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <button className="btn btn-secondary" onClick={() => setSelectedDID(null)}>
            Close
          </button>
        </section>
      )}
    </div>
  );
};

export default DIDAManagement;
