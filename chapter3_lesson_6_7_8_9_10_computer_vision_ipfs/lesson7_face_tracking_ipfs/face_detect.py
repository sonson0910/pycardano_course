"""
Lesson 6 — Face Detection & Embedding Extraction
Sử dụng MediaPipe để phát hiện khuôn mặt và trích xuất embedding

Usage:
    python face_detect.py --image path/to/face.jpg
    python face_detect.py --webcam  # Sử dụng webcam
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

import cv2
import mediapipe as mp
import numpy as np


@dataclass
class FaceResult:
    """Kết quả phát hiện khuôn mặt"""

    face_id: int
    bbox: Tuple[int, int, int, int]  # x, y, w, h
    confidence: float
    landmarks: List[dict] = field(default_factory=list)
    embedding: Optional[List[float]] = None


class FaceDetector:
    """
    Face Detection sử dụng MediaPipe

    MediaPipe Face Detection:
    - Ultra-fast inference (< 50ms per frame)
    - 95%+ accuracy
    - 6 keypoints: mắt, mũi, tai, miệng

    MediaPipe Face Mesh:
    - 468 facial landmarks với depth estimation
    - Dùng để tạo face embedding
    """

    def __init__(self, min_confidence: float = 0.5):
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_face_mesh = mp.solutions.face_mesh

        self.detector = self.mp_face_detection.FaceDetection(
            model_selection=1,  # 1 = full-range, 0 = short-range
            min_detection_confidence=min_confidence,
        )

        self.mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=5,
            min_detection_confidence=min_confidence,
            min_tracking_confidence=0.5,
        )

        self.min_confidence = min_confidence
        print("✅ FaceDetector initialized (MediaPipe)")

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

        results = self.detector.process(frame_rgb)
        faces: List[FaceResult] = []

        if not results.detections:
            return faces

        for idx, detection in enumerate(results.detections):
            score = detection.score[0]
            if score < self.min_confidence:
                continue

            bbox_data = detection.location_data.relative_bounding_box
            x = max(0, int(bbox_data.xmin * w))
            y = max(0, int(bbox_data.ymin * h))
            bw = min(int(bbox_data.width * w), w - x)
            bh = min(int(bbox_data.height * h), h - y)

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
        Trích xuất 468 facial landmarks bằng FaceMesh

        Returns:
            Danh sách landmarks cho mỗi khuôn mặt
        """
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, _ = frame.shape

        results = self.mesh.process(frame_rgb)
        all_landmarks = []

        if results.multi_face_landmarks:
            for face_lm in results.multi_face_landmarks:
                landmarks = []
                for i, lm in enumerate(face_lm.landmark):
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
                output, label, (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2,
            )

        return output

    def release(self):
        """Giải phóng tài nguyên MediaPipe"""
        self.detector.close()
        self.mesh.close()


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
    parser.add_argument("--output", type=str, default="face_embedding.json", help="File output")
    parser.add_argument("--confidence", type=float, default=0.5, help="Ngưỡng confidence")
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
            print(f"   Face {face.face_id}: confidence={face.confidence:.2f}, bbox={face.bbox}")
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
                output_frame, f"Faces: {len(faces)}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2,
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
