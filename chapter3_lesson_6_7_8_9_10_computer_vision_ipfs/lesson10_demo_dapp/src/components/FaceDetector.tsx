import { useState, useRef } from 'react';
import { detectFaces, FaceDetectResponse } from '../api/client';

interface Props {
  onDetected: (ipfsCid: string) => void;
}

export default function FaceDetector({ onDetected }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [result, setResult] = useState<FaceDetectResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = (f: File) => {
    setFile(f);
    setPreview(URL.createObjectURL(f));
    setResult(null);
    setError(null);
  };

  const handleDetect = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const res = await detectFaces(file);
      setResult(res);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Face detection failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="card">
        <h3>📸 Upload Face Image</h3>

        <div
          className={`upload-zone ${file ? 'has-file' : ''}`}
          onClick={() => inputRef.current?.click()}
        >
          <input
            ref={inputRef}
            type="file"
            accept="image/*"
            onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
          />
          {preview ? (
            <img
              src={preview}
              alt="Preview"
              style={{ maxWidth: '100%', maxHeight: 300, borderRadius: 8 }}
            />
          ) : (
            <>
              <span className="icon">📷</span>
              <p>Click to upload face image</p>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', marginTop: 8 }}>
                Supports JPG, PNG, WebP
              </p>
            </>
          )}
        </div>

        {file && (
          <div style={{ marginTop: 16, textAlign: 'center' }}>
            <button className="btn btn-primary" onClick={handleDetect} disabled={loading}>
              {loading ? <><span className="spinner" /> Detecting...</> : '🔍 Detect Faces'}
            </button>
          </div>
        )}
      </div>

      {error && <div className="message error">❌ {error}</div>}

      {result && (
        <div className="card face-results">
          <h3>🎯 Detection Results</h3>

          {result.faces_detected === 0 ? (
            <div className="message info">No faces detected. Try a different image.</div>
          ) : (
            <>
              <div className="message success">
                ✅ Detected {result.faces_detected} face(s)
              </div>

              {result.faces.map((face) => (
                <div key={face.face_id} className="face-card">
                  <div className="face-info">
                    <strong>Face {face.face_id}</strong>
                    <span className="confidence">{(face.confidence * 100).toFixed(1)}% confidence</span>
                    <span style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
                      {face.landmark_count} landmarks · {face.embedding_dim}D embedding
                    </span>
                  </div>
                </div>
              ))}

              {result.ipfs_cid && (
                <div className="ipfs-cid">
                  <strong>📦 IPFS CID:</strong> {result.ipfs_cid}
                </div>
              )}

              {result.ipfs_cid && (
                <div style={{ marginTop: 16, textAlign: 'center' }}>
                  <button
                    className="btn btn-success"
                    onClick={() => onDetected(result.ipfs_cid!)}
                  >
                    🆔 Create DID from this face →
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}
