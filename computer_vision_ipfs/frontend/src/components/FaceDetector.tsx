import React, { useState } from 'react';
import { detectFaces, createDID } from '../api';
import './FaceDetector.css';

interface DetectionResult {
  faces_detected: number;
  faces: Array<{
    confidence: number;
    embedding?: number[];
  }>;
  embedding_ipfs_hash?: string;
}

export const FaceDetector: React.FC<{
  onDIDCreated?: (didData: any) => void;
}> = ({ onDIDCreated }) => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<DetectionResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [creatingDID, setCreatingDID] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFile(e.target.files?.[0] || null);
    setError(null);
    setResult(null);
  };

  const handleDetect = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await detectFaces(file);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Detection failed');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateDID = async () => {
    if (!result?.embedding_ipfs_hash) {
      setError('Please detect face first');
      return;
    }

    try {
      setCreatingDID(true);
      setError(null);

      const didResponse = await createDID(result.embedding_ipfs_hash, {
        face_image_ipfs: result.embedding_ipfs_hash,
      });

      if (didResponse.did && didResponse.ipfs_hash) {
        onDIDCreated?.(didResponse);
        alert(`✅ DID Created!\n\nDID: ${didResponse.did}\nIPFS: ${didResponse.ipfs_hash}\n\nTX: ${didResponse.tx_hash}`);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'DID creation failed');
    } finally {
      setCreatingDID(false);
    }
  };

  return (
    <div className="face-detector">
      <h2>Face Detection & DID Creation</h2>

      <div className="upload-section">
        <input
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          disabled={loading || creatingDID}
          title="Select image file for face detection"
        />
        <button onClick={handleDetect} disabled={loading || !file || creatingDID}>
          {loading ? 'Processing...' : 'Detect Faces'}
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      {result && (
        <div className="results">
          <h3>✅ Detection Results</h3>
          <p><strong>Faces detected:</strong> {result.faces_detected}</p>
          {result.faces && result.faces.length > 0 && (
            <>
              <p><strong>Face Confidence Scores:</strong></p>
              <ul>
                {result.faces.map((face, idx) => (
                  <li key={idx}>
                    Face {idx + 1}: {(face.confidence * 100).toFixed(2)}%
                  </li>
                ))}
              </ul>
            </>
          )}
          {result.embedding_ipfs_hash && (
            <>
              <p><strong>📤 Embedding uploaded to IPFS</strong></p>
              <div className="ipfs-hash-display">
                {result.embedding_ipfs_hash}
              </div>
              <button
                onClick={handleCreateDID}
                disabled={creatingDID}
                className="create-did-button"
              >
                {creatingDID ? '⏳ Creating DID...' : '🔗 Create DID'}
              </button>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default FaceDetector;
