# Lesson 7 — Setup AI Model (Face Tracking) & Lưu trữ IPFS

## Mục tiêu bài học

- Cài đặt và sử dụng **MediaPipe** — AI model phát hiện khuôn mặt
- Trích xuất **face embedding** (vector 512 chiều) từ ảnh khuôn mặt
- Hiểu cách **face embedding** hoạt động như "dấu vân tay số"
- Upload embedding lên **IPFS** qua **Pinata** và nhận về **CID**
- Hiểu IPFS — hệ thống lưu trữ phi tập trung cho AI model data

## Lý thuyết

### MediaPipe Face Detection — AI Model

MediaPipe là thư viện AI của Google, cung cấp face detection với:
- **Tốc độ nhanh**: < 50ms trên mỗi frame
- **Độ chính xác cao**: > 95%
- **468 facial landmarks** với ước lượng chiều sâu (FaceMesh)
- **6 keypoints** cơ bản: mắt, mũi, tai, miệng

### Face Embedding — Dấu vân tay số

```
Ảnh khuôn mặt → MediaPipe → 468 landmarks → Normalize → Vector 512D
```

Vector 512 chiều này là "dấu vân tay số" của khuôn mặt:
- Mỗi khuôn mặt có vector riêng biệt
- Dùng để so sánh (cosine similarity) và xác minh danh tính
- Là input chính cho DID verification (Lesson 6)

### IPFS & Pinata — Lưu trữ phi tập trung

- **IPFS** (InterPlanetary File System): mỗi file được định danh bằng **CID** (hash nội dung)
- **Pinata**: dịch vụ IPFS cloud miễn phí, API đơn giản để upload/pin
- **Tại sao IPFS?**: Face embedding quá lớn để lưu on-chain → lưu IPFS, chỉ lưu CID on-chain

```
Face Embedding (512D) → Upload Pinata → CID: QmXxx...
                                         ↓
                    Lưu vào DIDDatum.face_ipfs_hash trên blockchain
```

## Cấu trúc thư mục

```
lesson7_face_tracking_ipfs/
├── README.md           # Bài học này
├── face_detect.py      # Script phát hiện khuôn mặt + embedding
├── ipfs_upload.py      # Script upload lên IPFS (Pinata)
└── requirements.txt    # Thư viện Python
```

## Cài đặt

```bash
cd lesson7_face_tracking_ipfs
pip install -r requirements.txt
```

## Chạy script

### 1. Phát hiện khuôn mặt & trích xuất embedding

```bash
python face_detect.py --image path/to/face.jpg
```

Hoặc dùng webcam:

```bash
python face_detect.py --webcam
```

Script sẽ:
- Đọc ảnh / mở webcam
- Phát hiện khuôn mặt bằng MediaPipe
- Trích xuất 468 landmarks + embedding 512D
- Lưu embedding ra file `face_embedding.json`

### 2. Upload embedding lên IPFS

```bash
python ipfs_upload.py --file face_embedding.json
```

Script sẽ:
- Đọc file embedding JSON
- Upload lên Pinata IPFS
- In ra **CID** (IPFS hash)

> 💡 **Lưu lại CID** — bạn sẽ cần nó cho Lesson 8 (off-chain code)!

## Kết quả mong đợi

```
📸 Loading image: face.jpg
✅ Detected 1 face(s)
   Face 0: confidence=0.98, bbox=(120, 80, 200, 250)
   Landmarks: 468 points extracted
   Embedding: 512-dimensional vector
💾 Saved to: face_embedding.json

📤 Uploading to Pinata IPFS...
✅ Upload successful!
   CID: QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG
   URL: https://gateway.pinata.cloud/ipfs/QmYwAPJzv5C...
```

## Lấy tADA testnet

👉 https://docs.cardano.org/cardano-testnets/tools/faucet/
