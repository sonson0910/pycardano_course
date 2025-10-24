/**
 * Frontend utilities for blockchain interactions
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 60000, // Increased to 60 seconds
});

/**
 * Face detection - uploads image and returns face data + IPFS hash
 */
export const detectFaces = async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/api/v1/detect-faces', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });

    return response.data;
};

/**
 * Create DID - auto-generates DID ID and IPFS hash if not provided
 * @param faceEmbedding - IPFS hash or raw embedding data
 * @param metadata - Optional metadata
 * @returns { did, ipfs_hash, tx_hash }
 */
export const createDID = async (
    faceEmbedding: string,
    metadata?: Record<string, any>
) => {
    const response = await api.post('/api/v1/did/create', {
        face_embedding: faceEmbedding,
        ...metadata,
    });

    return response.data;
};

/**
 * Verify face against stored DID
 */
export const verifyFace = async (did: string, faceIPFSHash: string) => {
    const response = await api.get(`/api/v1/verify-face/${did}`, {
        params: {
            face_ipfs_hash: faceIPFSHash,
        },
    });

    return response.data;
};

/**
 * Get DID document
 */
export const getDIDDocument = async (did: string) => {
    const response = await api.get(`/api/v1/did/${did}`);
    return response.data;
};

/**
 * List all DIDs
 */
export const listDIDs = async () => {
    const response = await api.get('/api/v1/dids');
    return response.data;
};

/**
 * Register DID on blockchain
 */
export const registerDID = async (did: string) => {
    const response = await api.post(`/api/v1/did/${did}/register`);
    return response.data;
};

/**
 * Update DID with new face embedding
 */
export const updateDID = async (did: string, newFaceIPFSHash: string) => {
    const response = await api.post(`/api/v1/did/${did}/update`, {
        new_face_ipfs_hash: newFaceIPFSHash,
    });
    return response.data;
};

/**
 * Verify DID integrity
 */
export const verifyDID = async (did: string) => {
    const response = await api.post(`/api/v1/did/${did}/verify`);
    return response.data;
};

/**
 * Revoke DID
 */
export const revokeDID = async (did: string) => {
    const response = await api.post(`/api/v1/did/${did}/revoke`);
    return response.data;
};

/**
 * Health check
 */
export const healthCheck = async () => {
    const response = await api.get('/api/v1/health');
    return response.data;
};
