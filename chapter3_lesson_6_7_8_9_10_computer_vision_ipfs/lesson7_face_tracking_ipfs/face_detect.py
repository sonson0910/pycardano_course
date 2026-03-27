"""
Lesson 7 — Face Detection & Embedding Extraction
Sử dụng MediaPipe Tasks API (v0.10+) để phát hiện khuôn mặt và trích xuất embedding

Usage:
    python face_detect.py --image path/to/face.jpg
    python face_detect.py --webcam  # Sử dụng webcam
"""

import argparse
import json
import sys
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

import cv2
import mediapipe as mp
import numpy as np

# ═══════════════════════════════════════════════
# MODEL PATHS — tự động download nếu chưa có
# ═══════════════════════════════════════════════

MODELS_DIR = Path(__file__).parent / "models"

FACE_DETECTOR_MODEL = MODELS_DIR / "blaze_face_short_range.tflite"
FACE_DETECTOR_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "face_detector/blaze_face_short_range/float16/latest/blaze_face_short_range.tflite"
)

FACE_LANDMARKER_MODEL = MODELS_DIR / "face_landmarker.task"
FACE_LANDMARKER_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "face_landmarker/face_landmarker/float16/latest/face_landmarker.task"
)


def _ensure_model(path: Path, url: str):
    """Download model nếu chưa có"""
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    print(f"📥 Downloading model: {path.name} ...")
    urllib.request.urlretrieve(url, str(path))
    print(f"   ✅ Saved to {path}")


# ═══════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════


@dataclass
class FaceResult:
    """Kết quả phát hiện khuôn mặt"""

    face_id: int
    bbox: Tuple[int, int, int, int]  # x, y, w, h
    confidence: float
    landmarks: List[dict] = field(default_factory=list)
    embedding: Optional[List[float]] = None


# ═══════════════════════════════════════════════
# FACE DETECTOR — MediaPipe Tasks API
# ═══════════════════════════════════════════════


class FaceDetector:
    """
    Face Detection sử dụng MediaPipe Tasks API (v0.10+)

    MediaPipe Face Detection:
    - Ultra-fast inference (< 50ms per frame)
    - 95%+ accuracy
    - 6 keypoints: mắt, mũi, tai, miệng

    MediaPipe Face Landmarker:
    - 478 facial landmarks với depth estimation
    - Dùng để tạo face embedding
    """

    def __init__(self, min_confidence: float = 0.5):
        # Download models nếu chưa có
        _ensure_model(FACE_DETECTOR_MODEL, FACE_DETECTOR_URL)
        _ensure_model(FACE_LANDMARKER_MODEL, FACE_LANDMARKER_URL)

        # FaceDetector — phát hiện vị trí mặt
        detector_options = mp.tasks.vision.FaceDetectorOptions(
            base_options=mp.tasks.BaseOptions(
                model_asset_path=str(FACE_DETECTOR_MODEL)
            ),
            min_detection_confidence=min_confidence,
        )
        self.detector = mp.tasks.vision.FaceDetector.create_from_options(
            detector_options
        )

        # FaceLandmarker — 478 landmarks 3D
        landmarker_options = mp.tasks.vision.FaceLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(
                model_asset_path=str(FACE_LANDMARKER_MODEL)
            ),
            num_faces=5,
            min_face_detection_confidence=min_confidence,
            min_face_presence_confidence=min_confidence,
            min_tracking_confidence=0.5,
        )
        self.landmarker = mp.tasks.vision.FaceLandmarker.create_from_options(
            landmarker_options
        )

        self.min_confidence = min_confidence
        print(f"✅ FaceDetector initialized (MediaPipe Tasks API v{mp.__version__})")

    def detect(self, frame: np.ndarray) -> List[FaceResult]:
        """
        Phát hiện khuôn mặt trong frame

        Args:
            frame: Ảnh BGR từ OpenCV

        Returns:
            Danh sách FaceResult
        """
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, _ = frame.shape

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        result = self.detector.detect(mp_image)
        faces: List[FaceResult] = []

        if not result.detections:
            return faces

        for idx, detection in enumerate(result.detections):
            score = detection.categories[0].score
            if score < self.min_confidence:
                continue

            bbox = detection.bounding_box
            x = max(0, bbox.origin_x)
            y = max(0, bbox.origin_y)
            bw = min(bbox.width, w - x)
            bh = min(bbox.height, h - y)

            faces.append(
                FaceResult(
                    face_id=idx,
                    bbox=(x, y, bw, bh),
                    confidence=float(score),
                )
            )

        return faces

    def extract_landmarks(self, frame: np.ndarray) -> List[List[dict]]:
        """
        Trích xuất 478 facial landmarks bằng FaceLandmarker

        Returns:
            Danh sách landmarks cho mỗi khuôn mặt
        """
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, _ = frame.shape

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        result = self.landmarker.detect(mp_image)
        all_landmarks = []

        if result.face_landmarks:
            for face_lm in result.face_landmarks:
                landmarks = []
                for i, lm in enumerate(face_lm):
                    landmarks.append(
                        {
                            "idx": i,
                            "x": int(lm.x * w),
                            "y": int(lm.y * h),
                            "z": round(lm.z, 6),
                        }
                    )
                all_landmarks.append(landmarks)

        return all_landmarks

    def extract_embedding(
        self, frame: np.ndarray, bbox: Tuple[int, int, int, int]
    ) -> Optional[List[float]]:
        """
        Trích xuất face embedding (512D vector) từ vùng khuôn mặt

        Pipeline:
            1. Crop vùng mặt theo bbox
            2. Resize về 128x128
            3. Chuyển sang RGB + normalize [0, 1]
            4. Flatten → normalize thành unit vector
            5. Pad/truncate về 512 chiều

        Args:
            frame: Ảnh BGR
            bbox: (x, y, w, h)

        Returns:
            Vector 512 chiều (unit vector)
        """
        x, y, w, h = bbox
        if w <= 0 or h <= 0:
            return None

        face_roi = frame[y : y + h, x : x + w]
        if face_roi.size == 0:
            return None

        # Resize → RGB → normalize
        face_resized = cv2.resize(face_roi, (128, 128))
        face_rgb = cv2.cvtColor(face_resized, cv2.COLOR_BGR2RGB)
        flat = face_rgb.flatten().astype(np.float32) / 255.0

        # Normalize thành unit vector
        norm = np.linalg.norm(flat)
        if norm > 0:
            flat = flat / norm

        # Đảm bảo 512 chiều
        if len(flat) < 512:
            flat = np.pad(flat, (0, 512 - len(flat)))
        else:
            flat = flat[:512]

        return flat.tolist()

    def process_image(self, frame: np.ndarray) -> List[FaceResult]:
        """
        Pipeline đầy đủ: detect → landmarks → embedding

        Args:
            frame: Ảnh BGR

        Returns:
            Danh sách FaceResult đầy đủ
        """
        faces = self.detect(frame)
        all_landmarks = self.extract_landmarks(frame)

        for i, face in enumerate(faces):
            # Gán landmarks nếu có
            if i < len(all_landmarks):
                face.landmarks = all_landmarks[i]

            # Trích xuất embedding
            face.embedding = self.extract_embedding(frame, face.bbox)

        return faces

    def draw_results(self, frame: np.ndarray, faces: List[FaceResult]) -> np.ndarray:
        """Vẽ bounding box và thông tin lên ảnh"""
        output = frame.copy()

        for face in faces:
            x, y, w, h = face.bbox
            cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 2)

            label = f"Face {face.face_id} ({face.confidence:.0%})"
            cv2.putText(
                output,
                label,
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
            )

        return output

    def release(self):
        """Giải phóng tài nguyên MediaPipe"""
        self.detector.close()
        self.landmarker.close()


def save_embedding(faces: List[FaceResult], output_path: str):
    """Lưu kết quả embedding ra file JSON"""
    data = []
    for face in faces:
        data.append(
            {
                "face_id": face.face_id,
                "confidence": round(face.confidence, 4),
                "bbox": list(face.bbox),
                "landmark_count": len(face.landmarks),
                "embedding": face.embedding,
                "embedding_dim": len(face.embedding) if face.embedding else 0,
            }
        )

    output = {"faces_detected": len(faces), "faces": data}

    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"💾 Saved to: {output_path}")
    return output


def main():
    parser = argparse.ArgumentParser(description="Face Detection & Embedding")
    parser.add_argument("--image", type=str, help="Đường dẫn tới ảnh")
    parser.add_argument("--webcam", action="store_true", help="Sử dụng webcam")
    parser.add_argument(
        "--output", type=str, default="face_embedding.json", help="File output"
    )
    parser.add_argument(
        "--confidence", type=float, default=0.5, help="Ngưỡng confidence"
    )
    args = parser.parse_args()

    if not args.image and not args.webcam:
        print("❌ Cần chỉ định --image <path> hoặc --webcam")
        print("   Ví dụ: python face_detect.py --image face.jpg")
        sys.exit(1)

    detector = FaceDetector(min_confidence=args.confidence)

    if args.image:
        # Mode: Xử lý ảnh
        print(f"📸 Loading image: {args.image}")
        frame = cv2.imread(args.image)
        if frame is None:
            print(f"❌ Không thể đọc ảnh: {args.image}")
            sys.exit(1)

        faces = detector.process_image(frame)
        print(f"✅ Detected {len(faces)} face(s)")

        for face in faces:
            print(
                f"   Face {face.face_id}: confidence={face.confidence:.2f}, bbox={face.bbox}"
            )
            print(f"   Landmarks: {len(face.landmarks)} points")
            if face.embedding:
                print(f"   Embedding: {len(face.embedding)}-dimensional vector")

        # Lưu embedding
        save_embedding(faces, args.output)

        # Hiển thị kết quả
        output_frame = detector.draw_results(frame, faces)
        cv2.imshow("Face Detection", output_frame)
        print("\n⏎ Nhấn phím bất kỳ để đóng...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    elif args.webcam:
        # Mode: Webcam realtime
        print("📹 Opening webcam...")
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Không thể mở webcam")
            sys.exit(1)

        print("⏎ Nhấn 's' để lưu embedding, 'q' để thoát")
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            faces = detector.process_image(frame)
            output_frame = detector.draw_results(frame, faces)

            # Hiển thị số khuôn mặt
            cv2.putText(
                output_frame,
                f"Faces: {len(faces)}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )
            cv2.imshow("Face Detection (Press 'q' to quit)", output_frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            elif key == ord("s") and faces:
                save_embedding(faces, args.output)
                print(f"✅ Saved {len(faces)} face(s) to {args.output}")

        cap.release()
        cv2.destroyAllWindows()

    detector.release()
    print("✅ Done!")


if __name__ == "__main__":
    main()
