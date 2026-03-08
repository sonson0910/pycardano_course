# 🎬 SCRIPT BÀI GIẢNG — Lesson 7: Face Detection + IPFS (MediaPipe + Pinata)
# Thời lượng: ~17 phút
# Công cụ: Screen recording + Terminal + VS Code + Browser (IPFS Gateway)

---

## [00:00 – 01:30] 🎯 Giới thiệu & Mục tiêu

**Nói:**

> Xin chào! Chào mừng đến **Lesson 7** — bài thứ hai trong Chapter 3.
>
> Bài trước, chúng ta đã viết smart contract bằng Aiken — phần **on-chain**. Hôm nay, chúng ta sẽ xử lý phần **AI** và **off-chain storage** — hai thành phần quan trọng còn lại.
>
> Cụ thể, sau bài này các bạn sẽ:
> - Sử dụng **MediaPipe** — AI framework của Google — để **phát hiện khuôn mặt**
> - Trích xuất **face embedding** — vector 512 chiều — "dấu vân tay số" của khuôn mặt
> - Upload embedding lên **IPFS** qua **Pinata** và nhận về **CID**
> - Hiểu tại sao dùng IPFS và cách nó liên kết với DIDDatum on-chain
>
> Lesson này là cầu nối giữa thế giới **AI** và **Blockchain**. Let's go!

---

## [01:30 – 04:30] 📚 Lý thuyết: MediaPipe là gì?

**Nói:**

> **MediaPipe** là framework AI của Google, chuyên về xử lý **vision** — tức các bài toán liên quan đến hình ảnh và video. Nó cung cấp các model pre-trained chạy rất nhanh trên CPU — không cần GPU.
>
> Trong project này, chúng ta sử dụng 2 components:

*(Hiện slide)*

> **1. FaceDetector** — Phát hiện khuôn mặt:
> - Input: ảnh hoặc frame video
> - Output: bounding box (vị trí mặt), confidence score (độ tin cậy), 6 keypoints (mắt, mũi, tai, miệng)
> - Tốc độ: < 50ms trên CPU
> - Dùng model `blaze_face_short_range.tflite` (chỉ 300KB!)
>
> **2. FaceLandmarker** — 478 điểm landmark 3D:
> - Từ mỗi khuôn mặt detected, extract 478 điểm (x, y, z)
> - Bao gồm: đường viền mặt, lông mày, mắt, mũi, miệng... chi tiết cực kỳ
> - Dùng model `face_landmarker.task`

> ⚠️ **Lưu ý quan trọng** cho các bạn nào đã từng dùng MediaPipe:
>
> Từ phiên bản **0.10.x** trở đi, Google đã **deprecated** API cũ `mp.solutions`. Giờ phải dùng **Tasks API** mới:

```python
# ❌ CŨ — sẽ báo lỗi: module 'mediapipe' has no attribute 'solutions'
import mediapipe as mp
mp_face = mp.solutions.face_detection
detector = mp_face.FaceDetection()

# ✅ MỚI — Tasks API
import mediapipe as mp
base_options = mp.tasks.BaseOptions(model_asset_path="blaze_face_short_range.tflite")
options = mp.tasks.vision.FaceDetectorOptions(base_options=base_options)
detector = mp.tasks.vision.FaceDetector.create_from_options(options)
```

> Nếu bạn tìm tutorial cũ trên mạng, hầu hết đều dùng API cũ. Nhớ cập nhật sang Tasks API nhé!

---

## [04:30 – 07:30] 🧬 Face Embedding — "Dấu vân tay số"

**Nói:**

> Bây giờ, câu hỏi quan trọng: **Face embedding là gì?**
>
> Hãy tưởng tượng mỗi khuôn mặt là 1 điểm trong không gian 512 chiều. Hai khuôn mặt của **cùng 1 người** sẽ nằm **gần nhau** trong không gian này. Hai khuôn mặt **khác người** sẽ nằm **xa nhau**.

*(Vẽ diagram)*

```
Khuôn mặt A (ảnh 1) → [0.12, -0.45, 0.87, ..., 0.33]  ← 512 số
Khuôn mặt A (ảnh 2) → [0.13, -0.44, 0.86, ..., 0.34]  ← rất giống!
Khuôn mặt B          → [0.95, 0.21, -0.63, ..., -0.78] ← rất khác!
```

> Cách tạo embedding từ MediaPipe:
> 1. FaceLandmarker trả về **478 điểm** (x, y, z) — tức 478 × 3 = 1434 giá trị
> 2. Ta **normalize** và **flatten** thành vector 512 chiều
> 3. Vector này chính là "dấu vân tay số" — unique cho mỗi khuôn mặt

> Để so sánh hai embedding, ta dùng **cosine similarity**:

```python
import numpy as np

similarity = np.dot(vec_a, vec_b) / (np.linalg.norm(vec_a) * np.linalg.norm(vec_b))
# 1.0 = giống hệt, 0.0 = khác hoàn toàn
# Threshold ≥ 0.7 → coi là MATCH (cùng 1 người)
```

> Cosine similarity đo **góc giữa 2 vector**, bất kể độ dài. Rất phù hợp cho so sánh embedding!
>
> Bài 9 sau này, khi user bấm **"Verify with Face"**, backend sẽ:
> 1. Detect face từ ảnh upload → extract embedding
> 2. Fetch embedding gốc từ IPFS
> 3. Tính cosine similarity
> 4. ≥ 0.7 → match → submit Verify TX on-chain

---

## [07:30 – 10:30] ☁️ IPFS & Pinata

**Nói:**

> Tiếp theo — **IPFS**. Tại sao không lưu embedding trực tiếp trên blockchain?
>
> Đơn giản: **quá đắt**! Trên Cardano, mỗi byte lưu on-chain đều tốn ADA. Một face embedding 512 floats chiếm khoảng 4KB — lưu on-chain sẽ rất tốn phí.
>
> Giải pháp: Lưu embedding trên **IPFS** — hệ thống file phi tập trung — và chỉ lưu **CID** (content hash, ~46 bytes) on-chain.

*(Hiện slide)*

> **IPFS** — InterPlanetary File System:
> - Hệ thống lưu trữ phi tập trung
> - **Content-addressed**: mỗi file được định danh bằng hash nội dung (CID)
> - Nếu nội dung thay đổi → CID thay đổi → đảm bảo tính toàn vẹn
> - Ai có CID đều có thể truy xuất dữ liệu
>
> **Pinata** — IPFS cloud dễ dùng:
> - Miễn phí tới 500 files
> - API đơn giản: POST JSON → nhận CID
> - Có gateway: truy cập qua `https://gateway.pinata.cloud/ipfs/{CID}`

*(Live demo — browser)*

> Để dùng Pinata, bạn cần:
> 1. Tạo tài khoản tại **pinata.cloud** (miễn phí)
> 2. Vào **API Keys** → tạo JWT token
> 3. Lưu vào file `.env`: `PINATA_JWT=your_token_here`

---

## [10:30 – 13:30] 💻 Code Walkthrough

*(Mở `face_detect.py` trong VS Code)*

**Nói:**

> OK, hãy xem code thực tế.
>
> File `face_detect.py` — script phát hiện khuôn mặt:

```python
import mediapipe as mp
import cv2
import numpy as np

# Bước 1: Khởi tạo FaceDetector (Tasks API mới)
base_options = mp.tasks.BaseOptions(
    model_asset_path="blaze_face_short_range.tflite"
)
options = mp.tasks.vision.FaceDetectorOptions(
    base_options=base_options,
    min_detection_confidence=0.5
)
detector = mp.tasks.vision.FaceDetector.create_from_options(options)

# Bước 2: Đọc ảnh
image = cv2.imread("face.jpg")
rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

# Bước 3: Detect
result = detector.detect(mp_image)
for detection in result.detections:
    print(f"Confidence: {detection.categories[0].score:.2%}")
    bbox = detection.bounding_box
    print(f"BBox: x={bbox.origin_x}, y={bbox.origin_y}, w={bbox.width}, h={bbox.height}")
```

> Tiếp theo là trích xuất embedding. Mình dùng FaceLandmarker:

```python
# Khởi tạo FaceLandmarker
lm_options = mp.tasks.vision.FaceLandmarkerOptions(
    base_options=mp.tasks.BaseOptions(model_asset_path="face_landmarker.task"),
    output_face_blendshapes=False,
    num_faces=1
)
landmarker = mp.tasks.vision.FaceLandmarker.create_from_options(lm_options)

# Extract landmarks
lm_result = landmarker.detect(mp_image)
if lm_result.face_landmarks:
    landmarks = lm_result.face_landmarks[0]
    # 478 điểm, mỗi điểm có x, y, z
    coords = [[lm.x, lm.y, lm.z] for lm in landmarks]
    # Flatten + normalize → vector 512D
    flat = np.array(coords).flatten()[:512]
    embedding = (flat / np.linalg.norm(flat)).tolist()
```

*(Mở `ipfs_upload.py`)*

> File `ipfs_upload.py` — upload lên Pinata:

```python
import requests, json

PINATA_JWT = os.getenv("PINATA_JWT")

embedding_data = {
    "faces": [{
        "face_id": 0,
        "confidence": 0.98,
        "embedding": embedding  # vector 512D
    }]
}

response = requests.post(
    "https://api.pinata.cloud/pinning/pinJSONToIPFS",
    json={"pinataContent": embedding_data, "pinataMetadata": {"name": "face_embedding"}},
    headers={"Authorization": f"Bearer {PINATA_JWT}"}
)
cid = response.json()["IpfsHash"]
print(f"✅ CID: {cid}")
# Ví dụ: QmXLaBYop7bGLQ2uWtDUo5tk7niVDLdKpLTRfULAAwp6gz
```

---

## [13:30 – 15:30] 🖥️ Live Demo

*(Chạy terminal)*

**Nói:**

> Bây giờ chạy thực tế!

```bash
cd lesson7_face_tracking_ipfs
pip install -r requirements.txt
python face_detect.py --image ../test_face.jpg
```

> Kết quả:

```
📸 Loading image: test_face.jpg
✅ Detected 1 face(s)
   Face 0: confidence=98.5%, bbox=(120, 80, 200, 250)
   Landmarks: 478 points extracted
   Embedding: 512-dimensional vector
💾 Saved to: face_embedding.json
```

> Upload IPFS:

```bash
python ipfs_upload.py --file face_embedding.json
```

```
📤 Uploading to Pinata IPFS...
✅ Upload successful!
   CID: QmXLaBYop7bGLQ2uWtDUo5tk7niVDLdKpLTRfULAAwp6gz
   URL: https://gateway.pinata.cloud/ipfs/QmXLaBYop7bGLQ2u...
```

*(Mở browser — truy cập IPFS gateway URL)*

> Các bạn có thể truy cập URL này trên browser để xem JSON embedding đã upload lên IPFS. Đây là dữ liệu **phi tập trung** — bất kỳ ai có CID đều có thể truy xuất.
>
> **Lưu CID lại** — Lesson 8 sẽ cần nó để lock DID vào smart contract!

---

## [15:30 – 17:00] 🔑 Tổng kết & Preview

**Nói:**

> Tổng kết Lesson 7:
>
> 1. **MediaPipe Tasks API** — AI framework mới nhất của Google, detect face < 50ms
> 2. **Face Embedding** — vector 512D, "dấu vân tay số" unique cho mỗi khuôn mặt
> 3. **Cosine Similarity** — thuật toán so sánh khuôn mặt, threshold ≥ 0.7
> 4. **IPFS + Pinata** — lưu embedding off-chain, chỉ lưu CID on-chain
>
> Đến đây, chúng ta đã có:
> - ✅ Smart contract (Lesson 6) → file `plutus.json`
> - ✅ Face embedding (Lesson 7) → IPFS CID
>
> Bài tiếp theo — **Lesson 8** — chúng ta sẽ viết **off-chain code** bằng Python để kết nối hai thứ này lại: tạo transactions, lock DID vào contract, và thực hiện full lifecycle trên Preprod testnet.
>
> Hẹn gặp ở Lesson 8!

---

*Kết thúc Lesson 7 — ~17 phút*
