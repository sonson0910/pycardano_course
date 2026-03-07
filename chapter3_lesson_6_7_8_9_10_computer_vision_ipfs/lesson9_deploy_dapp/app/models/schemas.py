"""Pydantic schemas cho API request/response"""

from typing import List, Optional, Tuple

from pydantic import BaseModel


# ═══════════════════════════════════════════════
# Face Detection
# ═══════════════════════════════════════════════

class FaceInfo(BaseModel):
    face_id: int
    confidence: float
    bbox: Tuple[int, int, int, int]
    landmark_count: int
    embedding_dim: int


class FaceDetectResponse(BaseModel):
    faces_detected: int
    faces: List[FaceInfo]
    ipfs_cid: Optional[str] = None


# ═══════════════════════════════════════════════
# DID Management
# ═══════════════════════════════════════════════

class DIDCreateRequest(BaseModel):
    ipfs_hash: str
    did_id: Optional[str] = None
    amount: int = 2_000_000  # 2 ADA


class DIDCreateResponse(BaseModel):
    did_id: str
    tx_hash: str
    ipfs_hash: str
    status: str = "locked"
    explorer_url: str


class DIDActionResponse(BaseModel):
    did_id: str
    action: str
    tx_hash: str
    status: str
    explorer_url: str


class DIDInfo(BaseModel):
    did_id: str
    ipfs_hash: str
    owner: str
    created_at: int
    verified: bool
    status: str
    tx_history: List[dict] = []


class DIDListResponse(BaseModel):
    total: int
    dids: List[DIDInfo]


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None


class FaceVerifyResponse(BaseModel):
    did_id: str
    match: bool
    similarity: float
    threshold: float
    message: str
    tx_hash: Optional[str] = None
    explorer_url: Optional[str] = None
