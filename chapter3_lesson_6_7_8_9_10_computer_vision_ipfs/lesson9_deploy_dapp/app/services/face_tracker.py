"""
Face Detection Service — MediaPipe Tasks API (v0.10.32+)

Dùng mp.tasks.vision.FaceDetector thay vì mp.solutions (deprecated).
Singleton service cho face detection trong API router.
"""

import logging
from pathlib import Path
from typing import List, Optional, Tuple

import cv2
import mediapipe as mp
import numpy as np

logger = logging.getLogger(__name__)

# Singleton
_instance: Optional["FaceTrackerService"] = None


def get_face_tracker() -> "FaceTrackerService":
    """Lazy singleton — khởi tạo lần đầu khi cần"""
    global _instance
    if _instance is None:
        _instance = FaceTrackerService()
    return _instance


class FaceTrackerService:
    """MediaPipe Face Detection (Tasks API v0.10.32+) + Embedding"""

    def __init__(self, min_confidence: float = 0.3):
        # Model path
        model_path = Path(__file__).parent.parent.parent / "models" / "blaze_face_short_range.tflite"
        if not model_path.exists():
            raise FileNotFoundError(
                f"Model not found: {model_path}\n"
                "Download: curl -sL -o models/blaze_face_short_range.tflite "
                "https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite"
            )

        # New Tasks API
        base_options = mp.tasks.BaseOptions(model_asset_path=str(model_path))
        options = mp.tasks.vision.FaceDetectorOptions(
            base_options=base_options,
            min_detection_confidence=min_confidence,
        )
        self.detector = mp.tasks.vision.FaceDetector.create_from_options(options)
        logger.info("✅ FaceTrackerService initialized (Tasks API v0.10.32)")

    def detect_and_embed(self, image_bytes: bytes) -> List[dict]:
        """
        Detect faces + extract embeddings from image bytes

        Returns:
            List of {"face_id", "confidence", "bbox", "landmark_count", "embedding", "embedding_dim"}
        """
        # Decode image
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is None:
            raise ValueError("Cannot decode image")

        h, w, _ = frame.shape

        # Convert BGR→RGB for mediapipe
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        # Detect faces using Tasks API
        result = self.detector.detect(mp_image)

        faces = []
        for idx, detection in enumerate(result.detections):
            bbox = detection.bounding_box
            x = max(0, bbox.origin_x)
            y = max(0, bbox.origin_y)
            bw = min(bbox.width, w - x)
            bh = min(bbox.height, h - y)

            score = detection.categories[0].score if detection.categories else 0.0

            # Extract embedding from face ROI
            embedding = self._extract_embedding(frame, (x, y, bw, bh))

            faces.append({
                "face_id": idx,
                "confidence": round(float(score), 4),
                "bbox": (x, y, bw, bh),
                "landmark_count": len(detection.keypoints) if detection.keypoints else 0,
                "embedding": embedding,
                "embedding_dim": len(embedding) if embedding else 0,
            })

        logger.info(f"Detected {len(faces)} face(s)")
        return faces

    def _extract_embedding(
        self, frame: np.ndarray, bbox: Tuple[int, int, int, int]
    ) -> Optional[List[float]]:
        """512D unit vector from face ROI"""
        x, y, w, h = bbox
        if w <= 0 or h <= 0:
            return None

        roi = frame[y : y + h, x : x + w]
        if roi.size == 0:
            return None

        resized = cv2.resize(roi, (128, 128))
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        flat = rgb.flatten().astype(np.float32) / 255.0

        norm = np.linalg.norm(flat)
        if norm > 0:
            flat = flat / norm

        if len(flat) < 512:
            flat = np.pad(flat, (0, 512 - len(flat)))
        else:
            flat = flat[:512]

        return flat.tolist()
