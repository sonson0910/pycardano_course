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

interface VerifyResult {
  verified: boolean;
  confidence: number;
  message: string;
  txHash?: string;
}

export const DIDAManagement: React.FC<{
  preFilledDID?: {
    did: string;
    ipfs_hash: string;
  };
}> = ({ preFilledDID }) => {
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
  const [verifyResult, setVerifyResult] = useState<VerifyResult | null>(null);
  const [verifyLoading, setVerifyLoading] = useState(false);
  const [uploadingFace, setUploadingFace] = useState(false);

  const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api/v1';

  // Auto-fill form when DID data received from FaceDetector
  useEffect(() => {
    if (preFilledDID) {
      setFormData({
        didId: preFilledDID.did,
        faceEmbedding: preFilledDID.ipfs_hash,
        action: 'create',
      });
      // ✅ Auto-select the newly created DID
      const newDID: DID = {
        id: preFilledDID.did,
        did: preFilledDID.did,
        status: 'created',
        faceHash: preFilledDID.ipfs_hash,
        createdAt: new Date().toISOString(),
        lastUpdated: new Date().toISOString(),
        txHistory: [{
          action: 'create',
          txHash: '', // Will be updated after registration
          timestamp: new Date().toISOString(),
          confirmed: false,
        }],
      };
      setSelectedDID(newDID);

      // ✅ Tự động fetch DID list để cập nhật
      setTimeout(fetchDIDs, 1000);
    }
  }, [preFilledDID]);

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

      // Convert API response to DID format
      const didData = data.data;
      const selectedDIDData: DID = {
        id: did,
        did: did,
        status: didData.status || 'created',
        faceHash: didData.face_hash || '',
        createdAt: didData.created_at || new Date().toISOString(),
        lastUpdated: new Date().toISOString(),
        txHistory: [] // TODO: Add tx history from API
      };

      setSelectedDID(selectedDIDData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch DID status');
    }
  };

  // Detect faces and upload to IPFS
  const detectFaces = async (file: File) => {
    setUploadingFace(true);
    setError(null);
    try {
      const formDataObj = new FormData();
      formDataObj.append('file', file);

      const response = await fetch(`${API_BASE}/detect-faces`, {
        method: 'POST',
        body: formDataObj,
      });

      if (!response.ok) throw new Error('Failed to detect faces');
      const data = await response.json();

      if (data.embedding_ipfs_hash) {
        setFormData({
          ...formData,
          faceEmbedding: data.embedding_ipfs_hash,
        });
        setSuccess(`✅ Ảnh đã được upload! IPFS: ${data.embedding_ipfs_hash.substring(0, 20)}...`);
      } else {
        setError('No faces detected in image');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload image');
    } finally {
      setUploadingFace(false);
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
      // Create abort controller with 120 second timeout (backend waits up to 60s)
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 120000);

      const response = await fetch(`${API_BASE}/did/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          did_id: formData.didId,
          face_embedding: formData.faceEmbedding,
        }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) throw new Error('Failed to create DID');
      const data = await response.json();
      setSuccess(`DID created! TX: ${data.tx_hash}`);
      setFormData({ didId: '', faceEmbedding: '', action: 'create' });
      setTimeout(fetchDIDs, 2000);
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        setError('Request timeout - please try again');
      } else {
        setError(err instanceof Error ? err.message : 'Failed to create DID');
      }
    } finally {
      setLoading(false);
    }
  };

  // Register DID
  const registerDID = async (did: string) => {
    setLoading(true);
    setError(null);
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 120000);

      const response = await fetch(`${API_BASE}/did/${did}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) throw new Error('Failed to register DID');
      const data = await response.json();
      setSuccess(`DID registered! TX: ${data.tx_hash}`);
      setTimeout(() => fetchDIDStatus(did), 2000);
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        setError('Request timeout - please try again');
      } else {
        setError(err instanceof Error ? err.message : 'Failed to register DID');
      }
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
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 120000);

      const response = await fetch(`${API_BASE}/did/${did}/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          new_face_embedding: formData.faceEmbedding,
        }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) throw new Error('Failed to update DID');
      const data = await response.json();
      setSuccess(`DID updated! TX: ${data.tx_hash}`);
      setTimeout(() => fetchDIDStatus(did), 2000);
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        setError('Request timeout - please try again');
      } else {
        setError(err instanceof Error ? err.message : 'Failed to update DID');
      }
    } finally {
      setLoading(false);
    }
  };

  // Verify DID
  const verifyDID = async (did: string) => {
    setLoading(true);
    setError(null);
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 120000);

      // Send face_embedding if available, otherwise verify stored hash
      const body = formData.faceEmbedding ?
        { face_embedding: formData.faceEmbedding } :
        {};

      const response = await fetch(`${API_BASE}/did/${did}/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: Object.keys(body).length > 0 ? JSON.stringify(body) : undefined,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) throw new Error('Failed to verify DID');
      const data = await response.json();

      // Set verify result with confidence
      setVerifyResult({
        verified: data.verified || false,
        confidence: data.confidence || 0,
        message: data.verified ?
          `✅ Xác thực thành công! ${((data.confidence || 0) * 100).toFixed(2)}% giống` :
          `❌ Xác thực thất bại`,
        txHash: data.tx_hash,
      });

      setSuccess(data.verified ? 'DID verified successfully!' : 'DID verification failed');
      setTimeout(() => fetchDIDStatus(did), 2000);
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        setError('Request timeout - please try again');
      } else {
        setError(err instanceof Error ? err.message : 'Failed to verify DID');
      }
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
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 120000);

      const response = await fetch(`${API_BASE}/did/${did}/revoke`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) throw new Error('Failed to revoke DID');
      const data = await response.json();
      setSuccess(`DID revoked! TX: ${data.tx_hash}`);
      setTimeout(() => fetchDIDStatus(did), 2000);
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        setError('Request timeout - please try again');
      } else {
        setError(err instanceof Error ? err.message : 'Failed to revoke DID');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDIDs();
  }, []);

  // Get status color emoji
  const getStatusEmoji = (status: string) => {
    switch (status) {
      case 'created': return '🟡'; // Yellow
      case 'registered': return '🟠'; // Orange
      case 'updated': return '🔵'; // Blue
      case 'verified': return '🟢'; // Green
      case 'revoked': return '⛔'; // Red
      default: return '⚪'; // Gray
    }
  };

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
    if (!status || typeof status !== 'string') {
      return 'Unknown';
    }
    return status.charAt(0).toUpperCase() + status.slice(1);
  };

  // Render step progress
  const renderStepProgress = (status: string) => {
    const steps = [
      { name: 'Created', status: 'created', emoji: '✅' },
      { name: 'Registered', status: 'registered', emoji: '📝' },
      { name: 'Updated', status: 'updated', emoji: '🔄' },
      { name: 'Verified', status: 'verified', emoji: '✔️' },
    ];

    const currentIndex = steps.findIndex(s => s.status === status);

    return (
      <div className="step-progress">
        {steps.map((step, idx) => (
          <div key={step.status} className={`step ${idx <= currentIndex ? 'completed' : ''}`}>
            <div className="step-marker">{idx <= currentIndex ? step.emoji : '○'}</div>
            <div className="step-label">{step.name}</div>
            {idx < steps.length - 1 && <div className={`step-connector ${idx < currentIndex ? 'completed' : ''}`} />}
          </div>
        ))}
      </div>
    );
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
            <label>Upload Face Image</label>
            <input
              type="file"
              accept="image/*"
              onChange={(e) => {
                if (e.target.files?.[0]) {
                  detectFaces(e.target.files[0]);
                }
              }}
              disabled={uploadingFace || loading}
            />
            {uploadingFace && <p className="loading-text">Uploading and detecting faces...</p>}
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
                      {getStatusEmoji(did.status)} {getStatusLabel(did.status)}
                    </span>
                  </div>
                  <p className="did-hash">{did.faceHash ? did.faceHash.substring(0, 40) + '...' : 'No hash'}</p>
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
          <h2>🆔 Quản Lý DID: {selectedDID.did}</h2>

          {/* Step Progress */}
          {renderStepProgress(selectedDID.status)}

          <div className="status-info">
            <p>
              <strong>Trạng thái:</strong>{' '}
              <span className={`status-value status-${getStatusColor(selectedDID.status)}`}>
                {getStatusEmoji(selectedDID.status)} {getStatusLabel(selectedDID.status)}
              </span>
            </p>
            <p>
              <strong>📅 Ngày tạo:</strong> {new Date(selectedDID.createdAt).toLocaleString()}
            </p>
            <p>
              <strong>⏰ Cập nhật lần cuối:</strong> {new Date(selectedDID.lastUpdated).toLocaleString()}
            </p>
            <p>
              <strong>🔗 IPFS:</strong> <code>{selectedDID.faceHash}</code>
            </p>
          </div>

          {/* Upload Image for Update/Verify */}
          {(selectedDID.status === 'registered' || selectedDID.status === 'updated' || selectedDID.status === 'verified') && (
            <div className="form-group upload-section">
              <label>📷 Upload New Face Image for Update/Verify</label>
              <input
                type="file"
                accept="image/*"
                onChange={(e) => {
                  if (e.target.files?.[0]) {
                    detectFaces(e.target.files[0]);
                  }
                }}
                disabled={uploadingFace || loading}
                title="Upload a new face image"
              />
              {uploadingFace && <p className="loading-text">Uploading and detecting faces...</p>}
              {formData.faceEmbedding && (
                <p className="success-text">✅ Ready: {formData.faceEmbedding.substring(0, 30)}...</p>
              )}
            </div>
          )}

          {/* Action Buttons */}
          <div className="actions-grid">
            {selectedDID.status === 'created' && (
              <button
                className="btn btn-register"
                onClick={() => registerDID(selectedDID.did)}
                disabled={loading}
              >
                {loading ? '⏳ Đang xử lý...' : '📝 Register'}
              </button>
            )}

            {selectedDID.status === 'registered' && (
              <>
                <button
                  className="btn btn-update"
                  onClick={() => selectedDID && updateDID(selectedDID.did)}
                  disabled={loading || !formData.faceEmbedding || !selectedDID}
                >
                  {loading ? '⏳ Đang xử lý...' : '🔄 Cập Nhật Ảnh'}
                </button>
              </>
            )}

            {(selectedDID.status === 'updated' || selectedDID.status === 'registered') && (
              <button
                className="btn btn-verify"
                onClick={() => selectedDID && verifyDID(selectedDID.did)}
                disabled={verifyLoading || !selectedDID}
              >
                {verifyLoading ? '⏳ Đang xác thực...' : '✅ Xác Thực'}
              </button>
            )}

            {selectedDID.status !== 'revoked' && (
              <button
                className="btn btn-revoke"
                onClick={() => selectedDID && revokeDID(selectedDID.did)}
                disabled={loading || !selectedDID}
              >
                {loading ? '⏳ Đang xử lý...' : '❌ Huỷ Bỏ (Không Thể Hoàn Tác!)'}
              </button>
            )}

            {selectedDID.status === 'verified' && (
              <div className="verified-badge">
                <span>🟢 ĐÃ XÁC THỰC</span>
              </div>
            )}

            {selectedDID.status === 'revoked' && (
              <div className="revoked-badge">
                <span>⛔ ĐÃ HUỶBỎ</span>
              </div>
            )}
          </div>

          {/* Verify Result Display */}
          {verifyResult && (
            <div className={`verify-result ${verifyResult.verified ? 'success' : 'error'}`}>
              <div className="verify-header">
                <span className="verify-status">
                  {verifyResult.verified ? '🟢' : '🔴'} {verifyResult.message}
                </span>
              </div>
              {verifyResult.verified && (
                <>
                  <div className="confidence-display">
                    <p>🎯 Mức độ giống nhau:</p>
                    <div className="confidence-bar">
                      {/* Dynamic width percentage - cannot be moved to CSS file */}
                      {/* eslint-disable-next-line react/style-prop-object */}
                      <div
                        className="confidence-fill"
                        style={{width: `${(verifyResult.confidence * 100).toFixed(2)}%`}}
                      >
                        {(verifyResult.confidence * 100).toFixed(2)}%
                      </div>
                    </div>
                  </div>
                  {verifyResult.txHash && (
                    <p className="verify-tx">
                      <strong>TX Hash:</strong> {verifyResult.txHash}
                    </p>
                  )}
                </>
              )}
            </div>
          )}

          <div className="tx-history">
            <h3>Transaction History</h3>
            {!selectedDID || !selectedDID.txHistory || selectedDID.txHistory.length === 0 ? (
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
