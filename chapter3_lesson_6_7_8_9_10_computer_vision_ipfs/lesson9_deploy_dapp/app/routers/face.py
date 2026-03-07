"""Face Detection Router"""

import logging

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.models.schemas import FaceDetectResponse, FaceInfo
from app.services.face_tracker import get_face_tracker
from app.services.ipfs_service import get_ipfs_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/face")


@router.post("/detect", response_model=FaceDetectResponse)
async def detect_faces(file: UploadFile = File(...)):
    """
    Upload ảnh → phát hiện khuôn mặt → upload embedding lên IPFS

    Returns:
        Danh sách faces + IPFS CID
    """
    try:
        image_bytes = await file.read()
        logger.info(f"📸 Received image: {file.filename} ({len(image_bytes)} bytes)")

        # Face detection
        tracker = get_face_tracker()
        faces = tracker.detect_and_embed(image_bytes)

        if not faces:
            return FaceDetectResponse(faces_detected=0, faces=[])

        # Upload embedding lên IPFS
        ipfs_cid = None
        try:
            ipfs = get_ipfs_service()
            embedding_data = {
                "faces": [
                    {
                        "face_id": f["face_id"],
                        "confidence": f["confidence"],
                        "embedding": f["embedding"],
                    }
                    for f in faces
                ]
            }
            ipfs_cid = ipfs.upload_json(embedding_data, name=file.filename or "face")
        except Exception as e:
            logger.warning(f"⚠️ IPFS upload failed: {e}")

        face_infos = [
            FaceInfo(
                face_id=f["face_id"],
                confidence=f["confidence"],
                bbox=f["bbox"],
                landmark_count=f["landmark_count"],
                embedding_dim=f["embedding_dim"],
            )
            for f in faces
        ]

        return FaceDetectResponse(
            faces_detected=len(faces),
            faces=face_infos,
            ipfs_cid=ipfs_cid,
        )

    except Exception as e:
        logger.error(f"❌ Face detection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
