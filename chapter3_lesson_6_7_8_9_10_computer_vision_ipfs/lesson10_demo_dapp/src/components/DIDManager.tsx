import { useState, useEffect, useCallback, useRef } from 'react';
import {
  createDID,
  listDIDs,
  registerDID,
  verifyDID,
  revokeDID,
  DIDInfo,
  FaceVerifyResponse,
} from '../api/client';

interface Props {
  initialIpfsCid: string | null;
}

export default function DIDManager({ initialIpfsCid }: Props) {
  const [dids, setDids] = useState<DIDInfo[]>([]);
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [verifyResult, setVerifyResult] = useState<FaceVerifyResponse | null>(null);
  const [verifyDIDId, setVerifyDIDId] = useState<string | null>(null);
  const verifyInputRef = useRef<HTMLInputElement>(null);

  const fetchDIDs = useCallback(async () => {
    try {
      const res = await listDIDs();
      setDids(res.dids);
    } catch {
      // Silently fail
    }
  }, []);

  useEffect(() => {
    fetchDIDs();
  }, [fetchDIDs]);

  const handleCreate = async () => {
    if (!initialIpfsCid) return;
    setLoading('create');
    setError(null);
    setVerifyResult(null);
    try {
      const result = await createDID(initialIpfsCid);
      setSuccess(`✅ DID Created! TX: ${result.tx_hash.slice(0, 16)}...`);
      await fetchDIDs();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Create failed');
    } finally {
      setLoading(null);
    }
  };

  const handleRegister = async (didId: string) => {
    setLoading(`register-${didId}`);
    setError(null);
    setSuccess(null);
    setVerifyResult(null);
    try {
      const result = await registerDID(didId);
      setSuccess(`✅ REGISTER: TX ${result.tx_hash.slice(0, 16)}...`);
      await fetchDIDs();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Register failed');
    } finally {
      setLoading(null);
    }
  };

  const handleVerifyClick = (didId: string) => {
    setVerifyDIDId(didId);
    setVerifyResult(null);
    setError(null);
    setSuccess(null);
    // Trigger file input
    verifyInputRef.current?.click();
  };

  const handleVerifyFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !verifyDIDId) return;

    setLoading(`verify-${verifyDIDId}`);
    setError(null);
    try {
      const result = await verifyDID(verifyDIDId, file);
      setVerifyResult(result);
      if (result.match) {
        setSuccess(`✅ VERIFIED! Similarity: ${(result.similarity * 100).toFixed(1)}% | TX: ${result.tx_hash?.slice(0, 16)}...`);
      } else {
        setError(`❌ Face mismatch! Similarity: ${(result.similarity * 100).toFixed(1)}% (need ≥ ${(result.threshold * 100).toFixed(0)}%)`);
      }
      await fetchDIDs();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Verify failed');
    } finally {
      setLoading(null);
      // Reset input
      if (verifyInputRef.current) verifyInputRef.current.value = '';
    }
  };

  const handleRevoke = async (didId: string) => {
    setLoading(`revoke-${didId}`);
    setError(null);
    setSuccess(null);
    setVerifyResult(null);
    try {
      const result = await revokeDID(didId);
      setSuccess(`✅ REVOKE: TX ${result.tx_hash.slice(0, 16)}...`);
      await fetchDIDs();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Revoke failed');
    } finally {
      setLoading(null);
    }
  };

  const getAvailableActions = (status: string) => {
    switch (status) {
      case 'locked': return ['register'];
      case 'registered': return ['verify', 'revoke'];
      case 'verified': return ['revoke'];
      default: return [];
    }
  };

  return (
    <div>
      {/* Hidden file input for verify */}
      <input
        ref={verifyInputRef}
        type="file"
        accept="image/*"
        style={{ display: 'none' }}
        onChange={handleVerifyFile}
      />

      {/* Create DID */}
      {initialIpfsCid && (
        <div className="card">
          <h3>🆕 Create New DID</h3>
          <div className="ipfs-cid" style={{ marginBottom: 16 }}>
            <strong>IPFS CID:</strong> {initialIpfsCid}
          </div>
          <button
            className="btn btn-primary"
            onClick={handleCreate}
            disabled={loading === 'create'}
          >
            {loading === 'create' ? (
              <><span className="spinner" /> Creating DID...</>
            ) : (
              '🔏 Lock DID to Smart Contract'
            )}
          </button>
        </div>
      )}

      {error && <div className="message error">{error}</div>}
      {success && <div className="message success">{success}</div>}

      {/* Verify Result */}
      {verifyResult && (
        <div className={`card ${verifyResult.match ? 'verify-match' : 'verify-mismatch'}`}>
          <h3>{verifyResult.match ? '✅ Face Verified!' : '❌ Face Mismatch'}</h3>
          <div className="verify-details">
            <div className="similarity-bar">
              <div className="similarity-label">
                Similarity: <strong>{(verifyResult.similarity * 100).toFixed(1)}%</strong>
                <span style={{ color: 'var(--text-secondary)', marginLeft: 8 }}>
                  (threshold: {(verifyResult.threshold * 100).toFixed(0)}%)
                </span>
              </div>
              <div className="bar-track">
                <div
                  className={`bar-fill ${verifyResult.match ? 'match' : 'no-match'}`}
                  style={{ width: `${Math.min(verifyResult.similarity * 100, 100)}%` }}
                />
                <div className="threshold-mark" style={{ left: `${verifyResult.threshold * 100}%` }} />
              </div>
            </div>
            {verifyResult.tx_hash && (
              <div style={{ marginTop: 12 }}>
                <a
                  href={verifyResult.explorer_url || '#'}
                  target="_blank"
                  rel="noreferrer"
                  style={{ color: 'var(--primary)' }}
                >
                  📝 View TX: {verifyResult.tx_hash.slice(0, 20)}...
                </a>
              </div>
            )}
          </div>
        </div>
      )}

      {/* DID List */}
      <div className="card">
        <h3>📋 Your DIDs ({dids.length})</h3>

        {dids.length === 0 ? (
          <div className="empty-state">
            <span className="icon">🆔</span>
            <p>No DIDs yet. Detect a face first!</p>
          </div>
        ) : (
          dids.map((did) => (
            <div key={did.did_id} className="did-item">
              <div className="did-item-header">
                <span className="did-id">{did.did_id}</span>
                <span className={`did-status ${did.status}`}>{did.status}</span>
              </div>

              <div className="did-details">
                <div>
                  <label>IPFS Hash</label>
                  <span>{did.ipfs_hash}</span>
                </div>
                <div>
                  <label>Owner</label>
                  <span>{did.owner.slice(0, 16)}...</span>
                </div>
                <div>
                  <label>Created</label>
                  <span>{new Date(did.created_at).toLocaleString()}</span>
                </div>
                <div>
                  <label>Verified</label>
                  <span>{did.verified ? '✅ Yes' : '❌ No'}</span>
                </div>
              </div>

              <div className="did-actions">
                {getAvailableActions(did.status).map((action) => (
                  <button
                    key={action}
                    className={`btn btn-sm ${action === 'revoke' ? 'btn-danger' : action === 'verify' ? 'btn-verify' : 'btn-outline'}`}
                    onClick={() => {
                      if (action === 'register') handleRegister(did.did_id);
                      else if (action === 'verify') handleVerifyClick(did.did_id);
                      else if (action === 'revoke') handleRevoke(did.did_id);
                    }}
                    disabled={loading === `${action}-${did.did_id}`}
                  >
                    {loading === `${action}-${did.did_id}` ? (
                      <span className="spinner" />
                    ) : null}
                    {action === 'register' && '📝 Register'}
                    {action === 'verify' && '📸 Verify with Face'}
                    {action === 'revoke' && '🗑️ Revoke'}
                  </button>
                ))}
              </div>

              {did.tx_history.length > 0 && (
                <div className="tx-history">
                  <h4>Transaction History</h4>
                  {did.tx_history.map((tx, i) => (
                    <div key={i} className="tx-entry">
                      <span>{tx.action}</span>
                      <a
                        href={`https://preprod.cardanoscan.io/transaction/${tx.tx_hash}`}
                        target="_blank"
                        rel="noreferrer"
                      >
                        {tx.tx_hash.slice(0, 16)}...
                      </a>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
