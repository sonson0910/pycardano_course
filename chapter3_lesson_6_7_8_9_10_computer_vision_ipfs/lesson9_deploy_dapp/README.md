# Lesson 9 — Deploy DApp hoàn chỉnh lên Testnet

## Mục tiêu bài học

- Deploy **smart contract** (Aiken) lên Cardano Preprod testnet
- Xây dựng **backend API** (FastAPI) kết hợp toàn bộ thành phần
- **Tích hợp** Face Detection + IPFS + Blockchain vào REST API
- Cấu hình **CORS**, **environment variables**, và **service architecture**
- Kiểm tra toàn bộ pipeline hoạt động end-to-end

## Lý thuyết

### Kiến trúc Deploy

```
Cardano Preprod Testnet
        ↑
        │ Blockfrost API
        │
FastAPI Backend (:8000)
├─ POST /api/v1/face/detect     ← MediaPipe face detection
├─ POST /api/v1/did/create      ← Lock DID to smart contract
├─ POST /api/v1/did/{id}/register
├─ POST /api/v1/did/{id}/verify
├─ POST /api/v1/did/{id}/revoke
├─ GET  /api/v1/did/{id}
└─ GET  /api/v1/did/list/all
        │
        ├─ FaceTrackerService (MediaPipe)
        ├─ IPFSService (Pinata)
        └─ CardanoService (PyCardano + Blockfrost)
```

### Service Layer Pattern

```python
# Mỗi service là singleton, lazy-initialized
get_face_tracker()    → FaceTrackerService (singleton)
get_ipfs_service()    → IPFSService (singleton)
get_cardano_service() → CardanoService (singleton)
```

## Cấu trúc thư mục

```
lesson9_deploy_dapp/
├── README.md
├── requirements.txt
└── app/
    ├── __init__.py
    ├── main.py                  # FastAPI entry + CORS + lifespan
    ├── routers/
    │   ├── __init__.py
    │   ├── face.py              # POST /face/detect
    │   └── did.py               # DID CRUD endpoints
    ├── services/
    │   ├── __init__.py
    │   ├── face_tracker.py      # MediaPipe singleton
    │   ├── ipfs_service.py      # Pinata IPFS singleton
    │   └── cardano_service.py   # PyCardano + DID operations
    └── models/
        ├── __init__.py
        └── schemas.py           # Pydantic request/response
```

## Yêu cầu trước khi deploy

1. **Smart contract đã build** (Lesson 6): `plutus.json` tồn tại
2. **File `.env`** đã cấu hình:
   ```
   BLOCKFROST_PROJECT_ID=preprod_xxx
   PINATA_JWT=your_jwt
   MNEMONIC=word1 word2 ... word24
   ```
3. **Ví có ≥ 5 tADA** trên Preprod

## Bước 1: Cài đặt dependencies

```bash
cd lesson9_deploy_dapp
pip install -r requirements.txt
```

## Bước 2: Compile smart contract

```bash
cd ../lesson6_cv_did_integration/did_contract
aiken build
# → Tạo plutus.json
```

## Bước 3: Khởi chạy backend

```bash
cd lesson9_deploy_dapp
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Bước 4: Kiểm tra

### Health check

```bash
curl http://localhost:8000/health
# {"status":"ok","service":"did-face-dapp"}
```

### Swagger UI

Mở browser: http://localhost:8000/docs

### Test face detection

```bash
curl -X POST http://localhost:8000/api/v1/face/detect \
  -F "file=@face.jpg"
```

### Test create DID

```bash
curl -X POST http://localhost:8000/api/v1/did/create \
  -H "Content-Type: application/json" \
  -d '{"ipfs_hash": "QmTestHash123"}'
```

## Kết quả mong đợi

```
INFO | 🚀 Starting DApp Backend...
INFO | ✅ CardanoService initialized
INFO |    Wallet: addr_test1qz...
INFO |    Script: addr_test1wz...
INFO | Uvicorn running on http://0.0.0.0:8000
```

> 💡 Backend sẵn sàng → chuyển sang Lesson 10 để chạy full demo!
