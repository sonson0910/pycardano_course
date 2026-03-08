# 🎬 SCRIPT BÀI GIẢNG — Lesson 9: Backend API (FastAPI + Service Layer)
# Thời lượng: ~18 phút
# Công cụ: Screen recording + VS Code + Terminal + Browser (Swagger UI + CardanoScan)

---

## [00:00 – 01:30] 🎯 Giới thiệu & Mục tiêu

**Nói:**

> Xin chào! **Lesson 9** — bài thứ tư trong chapter.
>
> Ba bài trước, chúng ta đã có:
> - Smart contract (Lesson 6)
> - AI model + IPFS (Lesson 7)
> - Off-chain Python scripts (Lesson 8)
>
> Nhưng tất cả đều chạy bằng **CLI** — command line. User bình thường không xài được! Bài hôm nay, chúng ta sẽ wrap tất cả thành **REST API** bằng **FastAPI** — để frontend (Lesson 10) có thể gọi.
>
> Sau bài này các bạn sẽ:
> - Xây dựng **FastAPI backend** với kiến trúc **service layer**
> - Design **7 REST API endpoints** cho face detection + DID lifecycle
> - Implement **face-based verify** — feature quan trọng: upload ảnh mặt → so sánh với IPFS → on-chain
> - Cấu hình CORS, singleton services, và error handling
>
> Let's build!

---

## [01:30 – 04:30] 📚 Kiến trúc Backend

*(Hiện diagram)*

**Nói:**

> Trước khi code, hãy nhìn kiến trúc tổng thể:

```
FastAPI (:8000)
├── Routers (API endpoints)         ← Tiếp nhận HTTP requests
│   ├── face.py    → /api/v1/face/detect
│   └── did.py     → /api/v1/did/create, /register, /verify, /revoke
│
├── Services (Business logic)       ← Logic xử lý chính
│   ├── FaceTrackerService          → MediaPipe Tasks API
│   ├── IPFSService                 → Pinata upload/fetch
│   └── CardanoService              → PyCardano + Blockfrost + DID state
│
└── Models (Schemas)                ← Validate input/output
    └── schemas.py                  → Pydantic BaseModel
```

> Architecture này theo pattern **layered architecture**:
> - **Router** chỉ biết nhận request, gọi service, trả response
> - **Service** chứa toàn bộ business logic — không biết HTTP
> - **Model** validate data — type-safe
>
> Mỗi service là **singleton** — tạo 1 lần, dùng cả đời ứng dụng:

```python
_instance = None

def get_cardano_service():
    global _instance
    if _instance is None:
        _instance = CardanoService()  # Heavy init: load wallet, script, connect Blockfrost
    return _instance
```

> Tại sao singleton? Vì khởi tạo wallet, load script, kết nối Blockfrost **tốn thời gian**. Init 1 lần rồi reuse là tối ưu nhất.

---

## [04:30 – 07:30] 🛠️ REST API Design

*(Mở Swagger UI — http://localhost:8000/docs)*

**Nói:**

> Hãy nhìn vào 7 endpoints:

| Endpoint | Method | Input | Output | Mô tả |
|----------|--------|-------|--------|--------|
| `/face/detect` | POST | `file: image` | Faces + IPFS CID | AI detect + IPFS upload |
| `/did/create` | POST | `{ ipfs_hash }` | TX hash + DID ID | Lock 2 ADA to script |
| `/did/{id}/register` | POST | — | TX hash | CKV continuing output |
| `/did/{id}/verify` | POST | `file: face_image` | Similarity + TX | **So sánh mặt!** |
| `/did/{id}/revoke` | POST | — | TX hash | Burn DID |
| `/did/{id}` | GET | — | DID info | Chi tiết 1 DID |
| `/did/list/all` | GET | — | All DIDs | Danh sách |

> Hầu hết endpoints khá standard — nhận input, gọi service, trả output. Nhưng có 1 endpoint đặc biệt: **Verify**.

---

## [07:30 – 12:30] 🎯 Face-based Verify — Điểm nhấn

**Nói:**

> Đây là feature quan trọng nhất bài này. Verify **không chỉ là bấm nút** — nó phải **chứng minh danh tính bằng khuôn mặt**.
>
> Flow:

```
1. User upload ảnh mặt mới
      ↓
2. Backend detect face → extract embedding (vector 512D)
      ↓
3. Lấy CID từ DIDDatum → fetch embedding gốc từ IPFS
      ↓
4. Cosine similarity giữa 2 embeddings
      ↓
5. ≥ 70%? → ✅ Match → Submit Verify TX (verified 0→1)
   < 70%? → ❌ Mismatch → Từ chối verify
```

> Hãy xem code:

*(Mở `did.py` — router)*

```python
@router.post("/{did_id}/verify", response_model=FaceVerifyResponse)
async def verify_did(did_id: str, file: UploadFile = File(...)):
    """Verify DID bằng face image"""
    import numpy as np
    
    svc = get_cardano_service()
    did_info = svc.get_did(did_id)
    
    # Bước 1: Detect face từ ảnh upload
    image_bytes = await file.read()
    tracker = get_face_tracker()
    faces = tracker.detect_and_embed(image_bytes)
    new_embedding = faces[0]["embedding"]

    # Bước 2: Fetch embedding gốc từ IPFS
    ipfs = get_ipfs_service()
    original_data = ipfs.get_json(did_info["ipfs_hash"])
    original_embedding = original_data["faces"][0]["embedding"]

    # Bước 3: Cosine similarity
    vec_new = np.array(new_embedding, dtype=np.float32)
    vec_orig = np.array(original_embedding, dtype=np.float32)
    dot = np.dot(vec_new, vec_orig)
    similarity = float(dot / (np.linalg.norm(vec_new) * np.linalg.norm(vec_orig)))

    # Bước 4: Match → submit TX
    threshold = 0.7
    if similarity >= threshold:
        result = svc.perform_action(did_id, "verify")
        return FaceVerifyResponse(
            match=True,
            similarity=similarity,
            tx_hash=result["tx_hash"],
            message="Face matched! DID verified on-chain."
        )
    else:
        return FaceVerifyResponse(
            match=False,
            similarity=similarity,
            message=f"Face mismatch ({similarity:.0%} < {threshold:.0%})"
        )
```

> Đây là nơi **AI** gặp **Blockchain**:
> - AI (MediaPipe) detect face từ ảnh user upload
> - IPFS fetch embedding gốc lưu khi tạo DID
> - Toán học (cosine similarity) quyết định match hay không
> - Blockchain (PyCardano) submit transaction nếu match
>
> Response trả về có trường `similarity` — frontend sẽ hiển thị **similarity bar** rất trực quan.

---

## [12:30 – 14:30] ⚠️ Cardano Service — CKV Logic

**Nói:**

> Bên trong `CardanoService`, method `perform_action()` xử lý CKV logic — giống Lesson 8 nhưng được organize gọn hơn:

```python
def perform_action(self, did_id, action_name):
    # Tìm UTxO
    utxos = self.context.utxos(self.script_address)
    target = find_by_last_tx(utxos, did_info)

    builder = TransactionBuilder(self.context)
    builder.add_input_address(self.address)    # ← Wallet UTxOs cho fees!
    builder.add_script_input(utxo=target, script=self.script, redeemer=Redeemer(Action()))
    
    # CKV logic
    if action == "revoke":
        pass  # Không output = burn
    elif action == "verify":
        raw_datum = target.output.datum
        input_datum = DIDDatum.from_cbor(raw_datum.cbor)  # ← Deserialize!
        out_datum = DIDDatum(..., verified=1)              # 0 → 1
        builder.add_output(TransactionOutput(script_address, coin, datum=out_datum))
    else:  # register
        builder.add_output(TransactionOutput(script_address, coin, datum=target.output.datum))
```

> Mấy cái trap từ Lesson 8 đều áp dụng ở đây:
> 1. `add_input_address()` — wallet cho fees
> 2. `DIDDatum.from_cbor()` — RawCBOR cần deserialize
> 3. `verified: int` — không dùng bool

---

## [14:30 – 16:30] 🖥️ Live Demo: Swagger UI

*(Chạy terminal + browser)*

**Nói:**

> Chạy backend:

```bash
cd lesson9_deploy_dapp
python -m uvicorn app.main:app --reload --port 8000
```

```
INFO | 🚀 Starting DApp Backend...
INFO | ✅ CardanoService initialized
INFO |    Wallet: addr_test1qz...
INFO |    Script: addr_test1wz...
INFO | Uvicorn running on http://0.0.0.0:8000
```

*(Mở http://localhost:8000/docs)*

> FastAPI tự động tạo **Swagger UI** — interactive API docs. Tại đây bạn có thể test mọi endpoint trực tiếp từ browser, không cần Postman.
>
> Test health check: `GET /health` → `{"status":"ok","service":"did-face-dapp"}`
>
> Test face detect: `POST /api/v1/face/detect` → upload ảnh → thấy confidence score, embedding dimension, IPFS CID.
>
> Swagger UI rất hữu ích khi debug — bạn thấy chính xác request/response body và status codes.

---

## [16:30 – 18:00] 🔑 Tổng kết & Preview

**Nói:**

> Tổng kết Lesson 9:
>
> 1. **Layered Architecture**: Router → Service → Model — tách biệt concerns
> 2. **Singleton Services**: Init nặng 1 lần, reuse suốt đời app
> 3. **Face-based Verify**: Upload ảnh → cosine similarity → on-chain TX (nếu match)
> 4. **CKV Logic trong service**: Tất cả trap (RawCBOR, add_input_address, Int) được xử lý
> 5. **Swagger UI**: Auto-generated API docs cho debug
>
> Backend sẵn sàng! Bài cuối — **Lesson 10** — chúng ta sẽ xây dựng **React frontend** để user tương tác trực quan. Đó mới là thứ user thực sự nhìn thấy!
>
> Hẹn gặp ở Lesson 10!

---

*Kết thúc Lesson 9 — ~18 phút*
