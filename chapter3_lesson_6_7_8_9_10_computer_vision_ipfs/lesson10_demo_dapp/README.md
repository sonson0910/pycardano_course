# Lesson 10 — Demo DApp

## Mục tiêu bài học

- Xây dựng **giao diện React** cho DApp hoàn chỉnh
- **Demo end-to-end**: Upload ảnh → Face Detection → IPFS → Create DID → Manage lifecycle
- Hiểu cách **frontend giao tiếp** với backend API
- Thấy **toàn bộ pipeline** hoạt động: CV + IPFS + Smart Contract + UI

## Demo Flow

```
┌──────────────────────────────────────────────┐
│              DID Face DApp                    │
│  ┌────────────────┐  ┌────────────────────┐  │
│  │ 📸 Detect Face  │  │ 🆔 Manage DIDs     │  │
│  └────────────────┘  └────────────────────┘  │
│                                               │
│  1. Upload ảnh khuôn mặt                      │
│  2. Face Detection → 512D Embedding           │
│  3. Upload embedding → IPFS CID               │
│  4. Create DID → Lock 2 ADA to contract       │
│  5. Register / Verify / Revoke DID            │
│  6. View TX history on Cardano Explorer       │
│                                               │
└──────────────────────────────────────────────┘
```

## Cấu trúc thư mục

```
lesson10_demo_dapp/
├── README.md
├── package.json
├── vite.config.ts             # Dev server + API proxy
├── tsconfig.json
├── index.html
└── src/
    ├── main.tsx               # Entry point
    ├── App.tsx                # Tab navigation + health check
    ├── index.css              # Dark theme design system
    ├── api/
    │   └── client.ts          # Typed API client (Axios)
    └── components/
        ├── FaceDetector.tsx    # Upload + detect + IPFS result
        └── DIDManager.tsx     # Full CRUD lifecycle
```

## Yêu cầu

- **Backend đang chạy** (Lesson 9) tại http://localhost:8000
- Node.js 18+

## Cài đặt & Chạy

```bash
cd lesson10_demo_dapp
npm install
npm run dev
```

Mở browser: http://localhost:5173

## Tính năng

### Tab 1: 📸 Detect Face
- Kéo thả / click upload ảnh khuôn mặt
- Hiển thị kết quả: bounding box, confidence score
- Tự động upload embedding lên IPFS → hiển thị CID
- Nút **"Create DID"** để chuyển sang Tab 2

### Tab 2: 🆔 Manage DIDs
- Danh sách tất cả DIDs đã tạo
- Status indicator theo lifecycle:
  - 🟡 **Locked** → 🟣 **Registered** → 🟢 **Verified** → 🔴 **Revoked**
- Nút actions: Register, Verify, Revoke
- TX History với link tới [Preprod CardanoScan](https://preprod.cardanoscan.io)

### Dark Theme UI
- Gradient header, glassmorphism cards
- Smooth hover effects & loading spinners
- Responsive layout (mobile-friendly)

## Demo Steps

1. Mở http://localhost:5173
2. Tab **Detect Face** → upload ảnh có khuôn mặt
3. Xem kết quả detection → nhấn **"Create DID from this face"**
4. Tab **Manage DIDs** → thấy DID mới với status **Locked**
5. Nhấn **Register** → TX gửi lên Preprod → status → **Registered**
6. Nhấn **Verify** → status → **Verified** ✅
7. Click TX hash → xem trên CardanoScan

## Kết quả mong đợi

Giao diện hoạt động end-to-end:
- Face detection hiển thị confidence + embedding dimension
- IPFS CID được tạo và hiển thị
- DID lifecycle hoàn chỉnh trên Cardano Preprod
- Tất cả giao dịch có thể verify trên block explorer
