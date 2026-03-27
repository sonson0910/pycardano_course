# 🎬 SCRIPT BÀI GIẢNG — Lesson 7: Face Detection + IPFS (MediaPipe + Pinata)
# Thời lượng: ~18 phút
# Công cụ: Screen recording + Terminal + VS Code (mở lesson7 folder) + Browser (Pinata IPFS gateway)

---

## [00:00 – 01:30] 🎯 Giới thiệu & Mục tiêu

**Nói:**

> Xin chào các bạn! Chào mừng đến **Lesson 7** — bài thứ hai trong Chapter 3.
>
> Bài trước, chúng ta đã viết smart contract — phần **on-chain**. Hôm nay, chúng ta xử lý phần **AI** và **off-chain storage** — hai thành phần quan trọng còn lại trong pipeline.
>
> Cụ thể, bài này các bạn sẽ:
> - Sử dụng **MediaPipe Tasks API** (v0.10+) — framework AI của Google — để **phát hiện khuôn mặt** với 2 module: **FaceDetector** và **FaceLandmarker**
> - Trích xuất **face embedding** — vector **512 chiều** — "dấu vân tay số" của khuôn mặt bạn
> - Upload embedding lên **IPFS** qua **Pinata** và nhận về **CID**
> - Hiểu tại sao dùng IPFS và cách nó liên kết với DIDDatum on-chain (Lesson 6)
>
> Đây là bài nối giữa thế giới **AI** và **Blockchain**. Bắt đầu thôi!

---

## [01:30 – 04:00] 📚 Lý thuyết: MediaPipe Tasks API — 2 module chính

**Nói:**

> **MediaPipe** là framework AI open-source của Google dành cho các bài toán vision. Đặc điểm: chạy cực nhanh trên CPU, không cần GPU.
>
> Từ phiên bản **0.10.14** trở đi, Google đã **xóa hoàn toàn** API cũ `mp.solutions`. Bạn bắt buộc phải dùng **Tasks API** mới — `mp.tasks.vision`. Nếu tìm tutorial trên mạng mà thấy `mp.solutions.face_detection` thì đó là code cũ, sẽ crash ngay.
>
> Trong project này, chúng ta dùng **2 module** kết hợp:

*(Hiện slide)*

> **Module 1: FaceDetector** — phát hiện vị trí mặt:
> - Model: `blaze_face_short_range.tflite` (chỉ ~200KB!)
> - Output: **bounding box** (vị trí mặt), **confidence score** (độ tin cậy), **keypoints**
> - Tốc độ: < 50ms trên CPU
>
> **Module 2: FaceLandmarker** — 478 facial landmarks 3D:
> - Model: `face_landmarker.task`
> - Output: **478 điểm** `(x, y, z)` cho mỗi khuôn mặt — đường viền mặt, lông mày, mắt, mũi, miệng
> - Support tối đa **5 khuôn mặt** cùng lúc
>
> **Tại sao cần cả hai?**
> - FaceDetector cho ta **vị trí** (bounding box) — biết mặt ở đâu → dùng để crop
> - FaceLandmarker cho ta **hình dạng chi tiết** (478 landmarks 3D)
> - Kết hợp: detect vị trí → crop vùng mặt → tạo embedding

> Cả hai module đều cần file model `.tflite` / `.task`. Script của chúng ta sẽ **tự download** model lần đầu chạy, lưu vào thư mục `models/`.

---

## [04:00 – 07:30] 🧬 Face Embedding — Pipeline 5 bước

*(Mở file `face_detect.py`, scroll tới method `extract_embedding`)*

**Nói:**

> Bây giờ hãy tìm hiểu cách tạo **face embedding**. Đây là phần cốt lõi.
>
> Face embedding là **vector 512 chiều** — giống "dấu vân tay số" của khuôn mặt. Hai ảnh cùng 1 người → vector gần giống nhau. Khác người → vector khác biệt lớn.
>
> Pipeline trích xuất embedding gồm **5 bước**:

*(Hiện code trên màn hình)*

```python
def extract_embedding(self, frame, bbox):
    x, y, w, h = bbox
    if w <= 0 or h <= 0:
        return None

    # Bước 1: Crop vùng mặt theo bounding box
    face_roi = frame[y:y+h, x:x+w]
    if face_roi.size == 0:
        return None

    # Bước 2: Resize về kích thước chuẩn 128x128
    face_resized = cv2.resize(face_roi, (128, 128))

    # Bước 3: Chuyển BGR → RGB và normalize pixel về [0, 1]
    face_rgb = cv2.cvtColor(face_resized, cv2.COLOR_BGR2RGB)
    flat = face_rgb.flatten().astype(np.float32) / 255.0

    # Bước 4: Normalize thành unit vector (độ dài = 1)
    norm = np.linalg.norm(flat)
    if norm > 0:
        flat = flat / norm

    # Bước 5: Pad hoặc truncate về đúng 512 chiều
    if len(flat) < 512:
        flat = np.pad(flat, (0, 512 - len(flat)))
    else:
        flat = flat[:512]

    return flat.tolist()
```

> Giải thích từng bước:
>
> **Bước 1 — Crop**: Dùng bounding box từ FaceDetector để cắt vùng mặt ra khỏi ảnh gốc. Bỏ background, chỉ giữ khuôn mặt.
>
> **Bước 2 — Resize 128×128**: Ảnh mặt crop có kích thước tùy ý (tùy khoảng cách camera). Resize về 128×128 để **chuẩn hóa** — mọi khuôn mặt cùng kích thước.
>
> **Bước 3 — RGB + Normalize [0,1]**: OpenCV đọc ảnh dạng BGR, chuyển sang RGB. Rồi chia 255 để đưa giá trị pixel về khoảng [0, 1]. Ảnh 128×128×3 channels = **49,152 giá trị** → flatten thành mảng 1 chiều.
>
> **Bước 4 — Unit vector**: Normalize thành vector có **độ dài = 1** (unit vector). Rất quan trọng cho cosine similarity sau này — chỉ cần tính dot product thay vì chia norms.
>
> **Bước 5 — Truncate 512D**: 49,152 giá trị quá nhiều. Lấy **512 giá trị đầu tiên** (truncate). Nếu ít hơn thì pad thêm 0. Kết quả: **vector 512 chiều**, nhất quán, gọn, đủ thông tin.

> Con số **512** là quy ước phổ biến trong face recognition — đủ lớn để phân biệt, đủ nhỏ để lưu trữ.

---

## [07:30 – 10:00] 🏗️ Class FaceDetector — Khởi tạo & Detect

*(Scroll lên `__init__` trong `face_detect.py`)*

**Nói:**

> Hãy nhìn tổng thể class `FaceDetector`.
>
> Đầu tiên là `__init__` — khởi tạo 2 module MediaPipe:

```python
class FaceDetector:
    def __init__(self, min_confidence: float = 0.5):
        # Download models nếu chưa có — tự động!
        _ensure_model(FACE_DETECTOR_MODEL, FACE_DETECTOR_URL)
        _ensure_model(FACE_LANDMARKER_MODEL, FACE_LANDMARKER_URL)

        # FaceDetector — phát hiện vị trí mặt
        detector_options = mp.tasks.vision.FaceDetectorOptions(
            base_options=mp.tasks.BaseOptions(
                model_asset_path=str(FACE_DETECTOR_MODEL)
            ),
            min_detection_confidence=min_confidence,
        )
        self.detector = mp.tasks.vision.FaceDetector.create_from_options(detector_options)

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
        self.landmarker = mp.tasks.vision.FaceLandmarker.create_from_options(landmarker_options)
```

> Chú ý hàm `_ensure_model()` — nó kiểm tra file model có tồn tại không, nếu chưa thì **tự download** từ Google Storage. Lần đầu chạy sẽ tải ~5MB, lần sau chạy tức thì.
>
> Cách khởi tạo Tasks API khác hẳn API cũ:
> - API cũ: `mp.solutions.face_detection.FaceDetection()` — đơn giản nhưng đã bị xóa
> - Tasks API: cần tạo **Options** object → truyền vào `create_from_options()` → nhận instance
> - Phải chỉ đường dẫn **model file** (`.tflite` / `.task`)
>
> Method `detect()` — phát hiện mặt:

```python
def detect(self, frame):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
    result = self.detector.detect(mp_image)

    for detection in result.detections:
        score = detection.categories[0].score
        bbox = detection.bounding_box
        # bbox.origin_x, bbox.origin_y, bbox.width, bbox.height
```

> Tasks API yêu cầu wrap ảnh trong `mp.Image` trước khi detect. Bounding box trả về qua `detection.bounding_box` với 4 thuộc tính: `origin_x`, `origin_y`, `width`, `height`.
>
> Class có **4 methods chính** theo pipeline:
> - `detect(frame)` → bounding box + confidence
> - `extract_landmarks(frame)` → 478 landmarks (x, y, z)
> - `extract_embedding(frame, bbox)` → vector 512D
> - `process_image(frame)` → gọi cả 3 ở trên = **facade method**

---

## [10:00 – 12:30] ☁️ IPFS & Pinata — Class PinataIPFS

*(Mở file `ipfs_upload.py`)*

**Nói:**

> Tiếp theo — phần **IPFS**. Embedding 512 floats khá lớn, không thể lưu trực tiếp on-chain vì tốn ADA. Giải pháp: lưu trên **IPFS** — hệ thống file phi tập trung — chỉ lưu **CID** (content hash, ~46 bytes) on-chain.

> **IPFS** — InterPlanetary File System:
> - Hệ thống lưu trữ phi tập trung, **content-addressed**
> - Mỗi file được định danh bằng hash nội dung (**CID**)
> - Nội dung thay đổi → CID thay đổi → đảm bảo **tính toàn vẹn**
>
> **Pinata** — IPFS cloud miễn phí:
> - API đơn giản: POST JSON → nhận CID
> - Gateway: `https://gateway.pinata.cloud/ipfs/{CID}`

> Hãy xem class `PinataIPFS`:

```python
class PinataIPFS:
    def __init__(self, jwt_token: str):
        self.jwt = jwt_token
        self.headers = {"Authorization": f"Bearer {jwt_token}"}
        self._verify_auth()    # Xác thực JWT ngay khi khởi tạo

    def _verify_auth(self):
        resp = requests.get(
            f"{PINATA_API_URL}/data/testAuthentication",
            headers=self.headers, timeout=10,
        )
        if resp.status_code != 200:
            raise ValueError(f"❌ Pinata JWT không hợp lệ")
        print("✅ Pinata authentication OK")
```

> Ngay trong `__init__`, `_verify_auth()` gọi API Pinata để **kiểm tra JWT** — nếu sai thì crash ngay, không đợi tới lúc upload.
>
> Method `upload_json()` — upload embedding:

```python
def upload_json(self, data: dict, name: str = "face_embedding") -> dict:
    payload = {
        "pinataContent": data,
        "pinataMetadata": {"name": name},
        "pinataOptions": {"cidVersion": 0},     # CIDv0 bắt đầu "Qm..."
    }
    resp = requests.post(
        f"{PINATA_API_URL}/pinning/pinJSONToIPFS",
        json=payload,
        headers={**self.headers, "Content-Type": "application/json"},
        timeout=30,
    )
    cid = resp.json()["IpfsHash"]
    return {"cid": cid, "url": f"https://gateway.pinata.cloud/ipfs/{cid}"}
```

> `cidVersion: 0` → CID ngắn gọn kiểu `Qm...`. Ngoài ra class còn có `upload_file()` (upload binary) và `get_json()` (fetch dữ liệu bằng CID — dùng ở Lesson 9 khi verify).

---

## [12:30 – 14:30] 🔧 Hàm main() & save_embedding()

*(Scroll xuống phần `save_embedding()` và `main()`)*

**Nói:**

> Hàm `save_embedding()` lưu kết quả ra JSON:

```python
def save_embedding(faces, output_path):
    data = []
    for face in faces:
        data.append({
            "face_id": face.face_id,
            "confidence": round(face.confidence, 4),
            "bbox": list(face.bbox),
            "landmark_count": len(face.landmarks),
            "embedding": face.embedding,        # vector 512 floats
            "embedding_dim": len(face.embedding) if face.embedding else 0,
        })

    output = {"faces_detected": len(faces), "faces": data}
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
```

> Cấu trúc JSON output:
> ```json
> {
>   "faces_detected": 1,
>   "faces": [{
>     "face_id": 0,
>     "confidence": 0.91,
>     "bbox": [2197, 1147, 961, 961],
>     "landmark_count": 478,
>     "embedding": [0.012, -0.045, ...],
>     "embedding_dim": 512
>   }]
> }
> ```
>
> File này sẽ upload lên IPFS ở bước tiếp theo.
>
> Hàm `main()` hỗ trợ **2 mode**:
> - `--image face.jpg` — xử lý ảnh tĩnh, detect → embedding → lưu JSON → hiển thị kết quả
> - `--webcam` — mở webcam realtime, nhấn `s` lưu embedding, `q` thoát

```python
# Webcam mode — loop detect mỗi frame
while True:
    ret, frame = cap.read()
    faces = detector.process_image(frame)
    output_frame = detector.draw_results(frame, faces)
    cv2.imshow("Face Detection", output_frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    elif key == ord("s") and faces:
        save_embedding(faces, args.output)
```

> Vẽ bounding box xanh + label confidence lên mỗi frame, realtime!

---

## [14:30 – 16:00] 🖥️ Live Demo

*(Chạy terminal)*

**Nói:**

> Demo thực tế! Cài đặt:

```bash
cd lesson7_face_tracking_ipfs
pip install -r requirements.txt
```

> Cần 5 thư viện: `mediapipe>=0.10.0`, `opencv-python>=4.8.0`, `numpy`, `requests`, `python-dotenv`.
>
> **Bước 1 — Detect face & extract embedding:**

```bash
python face_detect.py --image face.jpg
```

> Lần đầu chạy, script tự download 2 models:

```
📥 Downloading model: blaze_face_short_range.tflite ...
   ✅ Saved to models/blaze_face_short_range.tflite
📥 Downloading model: face_landmarker.task ...
   ✅ Saved to models/face_landmarker.task
✅ FaceDetector initialized (MediaPipe Tasks API v0.10.32)
📸 Loading image: face.jpg
✅ Detected 1 face(s)
   Face 0: confidence=0.91, bbox=(2197, 1147, 961, 961)
   Landmarks: 478 points
   Embedding: 512-dimensional vector
💾 Saved to: face_embedding.json
```

> Ảnh hiện lên với bounding box xanh quanh mặt! File `face_embedding.json` đã được tạo.
>
> **Bước 2 — Upload IPFS:**

```bash
python ipfs_upload.py --file face_embedding.json
```

```
✅ Pinata authentication OK
📄 Loaded: face_embedding.json
   Faces: 1
📤 Uploading JSON to Pinata IPFS...
✅ Upload successful!
   CID: QmXLaBYop7bGLQ2uWtDUo5tk7niVDLdKpLTRfULAAwp6gz
   Size: 4523 bytes
   URL: https://gateway.pinata.cloud/ipfs/QmXLaBYop7bGLQ2u...

💡 CID đã lưu vào: face_embedding.cid
   Dùng CID này cho Lesson 8 (off-chain code)
```

*(Mở browser — truy cập IPFS gateway URL)*

> Script tự lưu CID vào file `.cid` — tiện cho Lesson 8!

---

## [16:00 – 18:00] 🔑 Tổng kết

**Nói:**

> Tổng kết Lesson 7:
>
> **1. MediaPipe Tasks API (v0.10+):**
> - `mp.tasks.vision.FaceDetector` → bounding box + confidence
> - `mp.tasks.vision.FaceLandmarker` → 478 landmarks 3D
> - Cần file model `.tflite` / `.task` — script tự download lần đầu
> - API cũ `mp.solutions` đã bị **xóa hoàn toàn** từ v0.10.14
>
> **2. Face Embedding — Pipeline 5 bước:**
> - Crop mặt theo bbox → resize 128×128 → RGB + normalize [0,1] → unit vector → truncate 512D
> - Kết quả: vector 512 chiều — "dấu vân tay số" unique cho mỗi khuôn mặt
>
> **3. IPFS + Pinata:**
> - Upload JSON embedding → CID (content hash)
> - CID sẽ lưu vào `DIDDatum.face_ipfs_hash` trên blockchain (Lesson 6)
>
> **4. Output JSON:** `faces_detected`, mỗi face có `face_id`, `confidence`, `bbox`, `landmark_count`, `embedding` (512D)
>
> Đến đây, chúng ta đã có:
> - ✅ Smart contract (Lesson 6) → file `plutus.json`
> - ✅ Face embedding + IPFS CID (Lesson 7) → file `face_embedding.json` + CID
>
> Bài tiếp — **Lesson 8** — viết **off-chain code**: đưa CID vào DIDDatum, lock lên smart contract, và thực hiện full lifecycle trên Preprod testnet.
>
> Hẹn gặp ở Lesson 8!

---

*Kết thúc Lesson 7 — ~18 phút*
