"""DID Management Router"""

import logging

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.models.schemas import (
    DIDActionResponse,
    DIDCreateRequest,
    DIDCreateResponse,
    DIDInfo,
    DIDListResponse,
    FaceVerifyResponse,
)
from app.services.cardano_service import get_cardano_service
from app.services.face_tracker import get_face_tracker
from app.services.ipfs_service import get_ipfs_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/did")


@router.post("/create", response_model=DIDCreateResponse)
async def create_did(req: DIDCreateRequest):
    """Tạo DID mới + Lock vào smart contract"""
    try:
        svc = get_cardano_service()
        result = svc.create_did(
            ipfs_hash=req.ipfs_hash,
            did_id=req.did_id,
            amount=req.amount,
        )
        return DIDCreateResponse(**result)
    except Exception as e:
        logger.error(f"❌ Create DID failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{did_id}/register", response_model=DIDActionResponse)
async def register_did(did_id: str):
    """Register DID (CKV continuing output)"""
    try:
        svc = get_cardano_service()
        result = svc.perform_action(did_id, "register")
        return DIDActionResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Register DID failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{did_id}/verify", response_model=FaceVerifyResponse)
async def verify_did(did_id: str, file: UploadFile = File(...)):
    """
    Verify DID bằng face image:
    1. Upload ảnh mới → detect face → extract embedding
    2. Fetch embedding gốc từ IPFS (CID lưu on-chain)
    3. Cosine similarity ≥ 0.7 → submit Verify TX on-chain
    """
    import numpy as np

    svc = get_cardano_service()
    did_info = svc.get_did(did_id)
    if not did_info:
        raise HTTPException(status_code=404, detail=f"DID not found: {did_id}")

    try:
        # Step 1: Detect face + extract embedding from uploaded image
        image_bytes = await file.read()
        logger.info(f"🔍 Verify: received image ({len(image_bytes)} bytes)")

        tracker = get_face_tracker()
        faces = tracker.detect_and_embed(image_bytes)

        if not faces:
            return FaceVerifyResponse(
                did_id=did_id,
                match=False,
                similarity=0.0,
                threshold=0.7,
                message="No face detected in uploaded image",
            )

        new_embedding = faces[0]["embedding"]
        if not new_embedding:
            return FaceVerifyResponse(
                did_id=did_id,
                match=False,
                similarity=0.0,
                threshold=0.7,
                message="Could not extract embedding from face",
            )

        # Step 2: Fetch original embedding from IPFS
        ipfs = get_ipfs_service()
        ipfs_cid = did_info["ipfs_hash"]
        logger.info(f"📦 Fetching original embedding from IPFS: {ipfs_cid}")

        original_data = ipfs.get_json(ipfs_cid)
        original_embedding = original_data["faces"][0]["embedding"]

        # Step 3: Cosine similarity
        vec_new = np.array(new_embedding, dtype=np.float32)
        vec_orig = np.array(original_embedding, dtype=np.float32)

        dot = np.dot(vec_new, vec_orig)
        norm_new = np.linalg.norm(vec_new)
        norm_orig = np.linalg.norm(vec_orig)
        similarity = float(dot / (norm_new * norm_orig + 1e-8))

        threshold = 0.7
        match = similarity >= threshold

        logger.info(f"🎯 Cosine similarity: {similarity:.4f} | Match: {match}")

        # Step 4: If match → submit Verify TX on-chain
        tx_hash = None
        explorer_url = None
        if match:
            result = svc.perform_action(did_id, "verify")
            tx_hash = result["tx_hash"]
            explorer_url = result["explorer_url"]
            logger.info(f"✅ Verify TX submitted: {tx_hash}")

        return FaceVerifyResponse(
            did_id=did_id,
            match=match,
            similarity=round(similarity, 4),
            threshold=threshold,
            message="Face matched! DID verified on-chain." if match else f"Face mismatch (similarity: {similarity:.2%} < {threshold:.0%})",
            tx_hash=tx_hash,
            explorer_url=explorer_url,
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Verify DID failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{did_id}/revoke", response_model=DIDActionResponse)
async def revoke_did(did_id: str):
    """Thu hồi DID vĩnh viễn"""
    try:
        svc = get_cardano_service()
        result = svc.perform_action(did_id, "revoke")
        return DIDActionResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Revoke DID failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{did_id}", response_model=DIDInfo)
async def get_did(did_id: str):
    """Lấy thông tin DID"""
    svc = get_cardano_service()
    did = svc.get_did(did_id)
    if not did:
        raise HTTPException(status_code=404, detail=f"DID not found: {did_id}")
    return DIDInfo(**did)


@router.get("/list/all", response_model=DIDListResponse)
async def list_dids():
    """Liệt kê tất cả DIDs"""
    svc = get_cardano_service()
    dids = svc.list_dids()
    return DIDListResponse(
        total=len(dids),
        dids=[DIDInfo(**d) for d in dids],
    )
