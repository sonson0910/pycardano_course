import React, { useState } from 'react';
import { detectFaces } from '../api';

export const FaceDetector: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFile(e.target.files?.[0] || null);
    setError(null);
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

  return (
    <div className="face-detector">
      <h2>Face Detection</h2>

      <div className="upload-section">
        <input
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          disabled={loading}
        />
        <button onClick={handleDetect} disabled={loading || !file}>
          {loading ? 'Processing...' : 'Detect Faces'}
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      {result && (
        <div className="results">
          <h3>Results</h3>
          <p>Faces detected: {result.faces_detected}</p>
          {result.faces && result.faces.length > 0 && (
            <ul>
              {result.faces.map((face: any, idx: number) => (
                <li key={idx}>
                  Face {idx + 1}: Confidence {(face.confidence * 100).toFixed(2)}%
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
};

export default FaceDetector;
