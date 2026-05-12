/// <reference types="vite/client" />
import axios from 'axios';

// Khi deploy: VITE_API_URL = "https://did-face-dapp-api.onrender.com"
// Khi local: rỗng → dùng Vite proxy (vite.config.ts)
const API_BASE = import.meta.env.VITE_API_URL || '';

const api = axios.create({ baseURL: API_BASE });

// ═══════════════════════════════════════
// Types
// ═══════════════════════════════════════

export interface FaceInfo {
  face_id: number;
  confidence: number;
  bbox: [number, number, number, number];
  landmark_count: number;
  embedding_dim: number;
}

export interface FaceDetectResponse {
  faces_detected: number;
  faces: FaceInfo[];
  ipfs_cid: string | null;
}

export interface DIDInfo {
  did_id: string;
  ipfs_hash: string;
  owner: string;
  created_at: number;
  verified: boolean;
  status: string;
  tx_history: { action: string; tx_hash: string }[];
}

export interface DIDCreateResponse {
  did_id: string;
  tx_hash: string;
  ipfs_hash: string;
  status: string;
  explorer_url: string;
}

export interface DIDActionResponse {
  did_id: string;
  action: string;
  tx_hash: string;
  status: string;
  explorer_url: string;
}

export interface FaceVerifyResponse {
  did_id: string;
  match: boolean;
  similarity: number;
  threshold: number;
  message: string;
  tx_hash: string | null;
  explorer_url: string | null;
}

// ═══════════════════════════════════════
// API Functions
// ═══════════════════════════════════════

export async function healthCheck(): Promise<{ status: string }> {
  const { data } = await api.get('/health');
  return data;
}

export async function detectFaces(file: File): Promise<FaceDetectResponse> {
  const form = new FormData();
  form.append('file', file);
  const { data } = await api.post('/api/v1/face/detect', form);
  return data;
}

export async function createDID(ipfsHash: string, didId?: string): Promise<DIDCreateResponse> {
  const { data } = await api.post('/api/v1/did/create', {
    ipfs_hash: ipfsHash,
    did_id: didId,
  });
  return data;
}

export async function registerDID(didId: string): Promise<DIDActionResponse> {
  const { data } = await api.post(`/api/v1/did/${encodeURIComponent(didId)}/register`);
  return data;
}

export async function verifyDID(didId: string, faceFile: File): Promise<FaceVerifyResponse> {
  const form = new FormData();
  form.append('file', faceFile);
  const { data } = await api.post(`/api/v1/did/${encodeURIComponent(didId)}/verify`, form);
  return data;
}

export async function revokeDID(didId: string): Promise<DIDActionResponse> {
  const { data } = await api.post(`/api/v1/did/${encodeURIComponent(didId)}/revoke`);
  return data;
}

export async function getDID(didId: string): Promise<DIDInfo> {
  const { data } = await api.get(`/api/v1/did/${encodeURIComponent(didId)}`);
  return data;
}

export async function listDIDs(): Promise<{ total: number; dids: DIDInfo[] }> {
  const { data } = await api.get('/api/v1/did/list/all');
  return data;
}
