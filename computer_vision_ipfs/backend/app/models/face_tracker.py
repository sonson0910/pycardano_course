"""
Face Detection and Tracking Model using MTCNN
Integrates real-time face detection with embedding extraction
MTCNN is more compatible with Windows/Anaconda than MediaPipe
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from mtcnn import MTCNN
import logging

logger = logging.getLogger(__name__)


@dataclass
class FaceData:
    """Data structure for detected face"""

    face_id: int
    bbox: Tuple[int, int, int, int]  # x, y, w, h
    embedding: Optional[np.ndarray] = None
    confidence: float = 0.0
    landmarks: Optional[List] = None


class FaceTracker:
    """
    Real-time face tracking using MTCNN
    Detects faces, extracts embeddings, and tracks them across frames

    MTCNN (Multi-task Cascaded Convolutional Networks):
    - More reliable on Windows
    - Works with Anaconda
    - Better for production use
    """

    def __init__(self, min_detection_confidence: float = 0.5):
        """
        Initialize FaceTracker

        Args:
            min_detection_confidence: Minimum confidence threshold for detection
        """
        try:
            self.detector = MTCNN()
            self.min_confidence = min_detection_confidence
            self.tracked_faces: Dict[int, FaceData] = {}
            self.next_face_id = 0
            logger.info("✓ FaceTracker initialized with MTCNN")
        except Exception as e:
            logger.error(f"Failed to initialize MTCNN: {e}")
            raise

    def detect_faces(self, frame: np.ndarray) -> List[FaceData]:
        """
        Detect faces in the given frame using MTCNN

        Args:
            frame: Input image frame (BGR format from OpenCV)

        Returns:
            List of detected faces with bounding boxes and confidence
        """
        try:
            # MTCNN expects RGB format
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Detect faces
            results = self.detector.detect_faces(frame_rgb)

            detected_faces = []
            h, w, _ = frame.shape

            for detection in results:
                # Extract bounding box
                box = detection["box"]
                x, y, width, height = box

                # Ensure coordinates are within bounds
                x = max(0, x)
                y = max(0, y)
                width = min(width, w - x)
                height = min(height, h - y)

                # Extract confidence
                confidence = detection["confidence"]

                # Extract landmarks (5 points: eyes, nose, mouth)
                landmarks = detection.get("keypoints", {})

                if confidence >= self.min_confidence:
                    face = FaceData(
                        face_id=self.next_face_id,
                        bbox=(x, y, width, height),
                        confidence=confidence,
                        landmarks=landmarks,
                    )

                    detected_faces.append(face)
                    self.next_face_id += 1

            logger.debug(f"Detected {len(detected_faces)} faces")
            return detected_faces

        except Exception as e:
            logger.error(f"Error detecting faces: {e}")
            return []

    def extract_landmarks(self, frame: np.ndarray) -> List[Dict]:
        """
        Extract facial landmarks using FaceMesh

        Args:
            frame: Input image frame (BGR format)

        Returns:
            List of landmarks for each detected face
        """
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(frame_rgb)

        landmarks_list = []

        if results.multi_face_landmarks:
            h, w, _ = frame.shape

            for face_landmarks in results.multi_face_landmarks:
                landmarks = []
                for landmark in face_landmarks.landmark:
                    x = int(landmark.x * w)
                    y = int(landmark.y * h)
                    z = landmark.z
                    landmarks.append({"x": x, "y": y, "z": z})

                landmarks_list.append(landmarks)

        return landmarks_list

    def extract_embedding(
        self, frame: np.ndarray, bbox: Tuple[int, int, int, int]
    ) -> Optional[np.ndarray]:
        """
        Extract face embedding from the given bounding box
        Uses normalized pixel values as embedding (can be enhanced with deep learning models)

        Args:
            frame: Input image frame
            bbox: Bounding box (x, y, w, h)

        Returns:
            Face embedding as numpy array (512 dimensions) or None if extraction fails
        """
        try:
            x, y, w, h = bbox

            # Validate bounding box
            if w <= 0 or h <= 0 or x < 0 or y < 0:
                logger.warning(f"Invalid bounding box: {bbox}")
                return None

            # Extract face ROI
            face_roi = frame[y : y + h, x : x + w]

            if face_roi.size == 0:
                logger.warning("Empty face ROI")
                return None

            # Resize to fixed size for consistent embedding
            face_resized = cv2.resize(face_roi, (128, 128))

            # Convert to RGB
            face_rgb = cv2.cvtColor(face_resized, cv2.COLOR_BGR2RGB)

            # Extract features
            # Method 1: Simple normalized pixel values
            embedding = face_rgb.flatten().astype(np.float32) / 255.0

            # Method 2: Enhanced with local binary patterns (optional)
            # Can be enhanced later with deep learning models

            # Normalize to unit vector for cosine similarity
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm

            # Ensure 512-dim for consistency
            if len(embedding) < 512:
                embedding = np.pad(
                    embedding, (0, 512 - len(embedding)), mode="constant"
                )
            else:
                embedding = embedding[:512]

            return embedding

        except Exception as e:
            logger.error(f"Error extracting embedding: {e}")
            return None

    def track_faces(self, frame: np.ndarray) -> List[FaceData]:
        """
        Detect and track faces in the current frame

        Args:
            frame: Input image frame

        Returns:
            List of tracked faces with IDs and embeddings
        """
        detected_faces = self.detect_faces(frame)

        # Extract embeddings for each detected face
        for face in detected_faces:
            x, y, w, h = face.bbox
            face.embedding = self.extract_embedding(frame, (x, y, w, h))

        return detected_faces

    def draw_faces(self, frame: np.ndarray, faces: List[FaceData]) -> np.ndarray:
        """
        Draw detected faces with bounding boxes and IDs on the frame

        Args:
            frame: Input image frame
            faces: List of detected faces

        Returns:
            Frame with drawn faces
        """
        output_frame = frame.copy()

        for face in faces:
            x, y, w, h = face.bbox

            # Draw bounding box
            cv2.rectangle(output_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Draw face ID and confidence
            label = f"ID: {face.face_id} ({face.confidence:.2f})"
            cv2.putText(
                output_frame,
                label,
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2,
            )

        return output_frame

    def release(self):
        """Release resources"""
        self.face_detection.close()
        self.face_mesh.close()
