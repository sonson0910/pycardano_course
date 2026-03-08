# 🎬 SCRIPT BÀI GIẢNG — Lesson 10: Frontend Demo (React + Vite)
# Thời lượng: ~17 phút
# Công cụ: Screen recording + VS Code + Browser (DApp frontend) + Terminal

---

## [00:00 – 01:30] 🎯 Giới thiệu & Mục tiêu

**Nói:**

> Xin chào! **Lesson 10** — bài cuối cùng trong Chapter 3!
>
> Đây là lúc mọi thứ **kết hợp lại** thành một sản phẩm thực sự. Chúng ta sẽ xây dựng **giao diện React** cho DApp — nơi user có thể:
> - Upload ảnh khuôn mặt → AI detect
> - Tạo DID trên blockchain
> - Quản lý vòng đời: Register → Verify (bằng mặt!) → Revoke
> - Xem toàn bộ lịch sử giao dịch
>
> Sau bài này các bạn sẽ:
> - Hiểu cách xây dựng frontend cho DApp blockchain
> - Sử dụng **Vite proxy** để kết nối frontend ↔ backend
> - Thấy toàn bộ pipeline hoạt động **end-to-end** thực tế
>
> This is the grand finale! Let's go!

---

## [01:30 – 04:00] 📚 Kiến trúc Frontend

*(Hiện diagram)*

**Nói:**

> Kiến trúc đơn giản nhưng hiệu quả:

```
React App (Vite :5173)
├── App.tsx              → Main layout + tabs + health check
├── FaceDetector.tsx     → Tab 1: Upload ảnh + detect + IPFS
├── DIDManager.tsx       → Tab 2: DID lifecycle UI
├── api/client.ts        → API client (Axios) — typed!
└── index.css            → Dark theme design system
```

> Chúng ta dùng:
> - **Vite** — build tool siêu nhanh cho React
> - **TypeScript** — type-safe, ít bugs
> - **Axios** — HTTP client cho API calls
> - **CSS thuần** — dark theme, glassmorphism, gradient
>
> **Vite proxy** là trick quan trọng:

```typescript
// vite.config.ts
server: {
  proxy: {
    '/api': 'http://localhost:8000',
    '/health': 'http://localhost:8000',
  }
}
```

> Frontend chạy ở port 5173, backend ở port 8000. Bình thường sẽ bị **CORS** block. Nhưng với proxy, khi frontend gọi `/api/v1/...`, Vite sẽ **forward** request tới `localhost:8000/api/v1/...`. Browser không biết — nghĩ là cùng origin!

---

## [04:00 – 07:00] 📝 API Client — Typed

*(Mở `client.ts`)*

**Nói:**

> File `client.ts` chứa tất cả API functions — fully typed:

```typescript
export interface FaceVerifyResponse {
  did_id: string;
  match: boolean;
  similarity: number;
  threshold: number;
  message: string;
  tx_hash: string | null;
}

// Face detect — gửi ảnh qua FormData
export async function detectFaces(file: File): Promise<FaceDetectResponse> {
  const form = new FormData();
  form.append('file', file);
  const { data } = await api.post('/api/v1/face/detect', form);
  return data;
}

// Verify — cũng gửi ảnh
export async function verifyDID(didId: string, faceFile: File): Promise<FaceVerifyResponse> {
  const form = new FormData();
  form.append('file', faceFile);
  const { data } = await api.post(`/api/v1/did/${didId}/verify`, form);
  return data;
}
```

> Chú ý: `verifyDID` nhận **File** làm parameter — vì backend cần ảnh mặt để so sánh. Đây không phải API call thông thường mà là **multipart form upload**.
>
> TypeScript types đảm bảo: nếu backend thay đổi response format, TypeScript sẽ báo lỗi ngay lập tức. Rất hữu ích khi refactor!

---

## [07:00 – 10:00] 🎨 Tab 1: Face Detection

*(Mở `FaceDetector.tsx`)*

**Nói:**

> Tab đầu tiên — **Detect Face**:

```typescript
// Upload zone — drag & drop hoặc click
<div className="upload-zone" onClick={() => inputRef.current?.click()}>
  <span className="icon">📸</span>
  <p>Click or drag an image to upload</p>
  <input type="file" accept="image/*" onChange={handleUpload} />
</div>

// Khi user chọn ảnh → gọi API
const handleDetect = async () => {
  setLoading(true);
  const result = await detectFaces(selectedFile);
  setFaces(result.faces);
  setIpfsCid(result.ipfs_cid);
};
```

> Kết quả hiển thị:
> - **Faces detected**: số lượng mặt phát hiện
> - **Confidence**: độ tin cậy (ví dụ: 98.5%)
> - **Embedding dimension**: 512
> - **IPFS CID**: hash để truy cập embedding trên IPFS
>
> Sau khi detect, hiện nút **"Create DID from this face"** → lock DID lên blockchain.

---

## [10:00 – 14:00] 🆔 Tab 2: DID Lifecycle Manager

*(Mở `DIDManager.tsx`)*

**Nói:**

> Tab thứ hai — **Manage DIDs** — đây là nơi quản lý toàn bộ vòng đời DID.
>
> Mỗi DID hiển thị dạng **card** với:
> - DID ID (ví dụ: `did:cardano:8090aa0a2a983078`)
> - Status badge: 🟡 LOCKED → 🟣 REGISTERED → 🟢 VERIFIED → 🔴 REVOKED
> - IPFS Hash, Owner, Created date
> - Trường **Verified**: ❌ No hoặc ✅ Yes
> - **Action buttons** — thay đổi theo status
> - **Transaction history** — link tới CardanoScan

> State machine logic trong frontend:

```typescript
const getAvailableActions = (status: string) => {
  switch (status) {
    case 'locked': return ['register'];          // Chỉ có Register
    case 'registered': return ['verify', 'revoke']; // Verify hoặc Revoke
    case 'verified': return ['revoke'];           // Chỉ còn Revoke
    default: return [];                           // Revoked = xong
  }
};
```

> Nút **"📸 Verify with Face"** — đây là điểm đặc biệt:

```typescript
const handleVerifyClick = (didId: string) => {
  setVerifyDIDId(didId);
  verifyInputRef.current?.click();  // Mở file picker!
};

const handleVerifyFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
  const file = e.target.files?.[0];
  if (!file || !verifyDIDId) return;
  
  setLoading(`verify-${verifyDIDId}`);
  const result = await verifyDID(verifyDIDId, file);  // Gửi ảnh lên backend
  setVerifyResult(result);
};
```

> Khi user bấm "Verify" → mở file picker → chọn ảnh mặt → ảnh gửi lên backend → cosine similarity → kết quả trả về:

```
┌───────────────────────────────────────┐
│ ✅ Face Verified!                      │
│ Similarity: 100.0% (threshold: 70%)   │
│ ████████████████████████|██████       │  ← Gradient bar
│ 📝 View TX: 4c21ed16b33ec487...       │
└───────────────────────────────────────┘
```

> Nếu **mismatch** (ví dụ upload ảnh người khác):

```
┌───────────────────────────────────────┐
│ ❌ Face Mismatch                       │
│ Similarity: 23.5% (threshold: 70%)    │
│ ████████|                              │  ← Đỏ
│ Cannot verify — face does not match    │
└───────────────────────────────────────┘
```

> Đây mới là "real verify" — chứng minh danh tính bằng biometric, không chỉ click nút!

---

## [14:00 – 16:00] 🖥️ Full Demo End-to-End

*(Giữ terminal chạy backend, mở browser)*

**Nói:**

> OK, live demo thực tế!
>
> Đầu tiên, chạy cả 2 servers:

```bash
# Terminal 1 — Backend
cd lesson9_deploy_dapp
python -m uvicorn app.main:app --reload --port 8000

# Terminal 2 — Frontend
cd lesson10_demo_dapp
npm install && npm run dev
```

> Mở browser: http://localhost:5173

*(Demo step by step)*

> **Step 1**: Tab Detect Face → upload ảnh → bấm Detect Faces
> → Hiện: 1 face detected, confidence 98.5%, IPFS CID
>
> **Step 2**: Bấm "Create DID from this face" → "Lock DID to Smart Contract"
> → Chờ ~15 giây → DID Created! TX hash hiện lên
>
> **Step 3**: Tab Manage DIDs → thấy DID mới, status LOCKED
> → Bấm "Register" → chờ chút → status → REGISTERED
>
> **Step 4**: ✨ Bấm "📸 Verify with Face" → chọn **cùng ảnh mặt**
> → Backend so sánh → **Similarity: 100.0%** → ✅ VERIFIED!
> → Verified chuyển thành ✅ Yes
>
> **Step 5**: Bấm "Revoke" → DID bị burn → status → REVOKED
> → Transaction History đầy đủ: create → register → verify → revoke

*(Hiện CardanoScan — show TX hashes)*

> Tất cả 4 transactions đều on Cardano Preprod — ai cũng có thể verify trên block explorer!

---

## [16:00 – 17:00] 🎓 Tổng kết Chapter 3

**Nói:**

> Xin chúc mừng! Chúng ta đã hoàn thành **Chapter 3** — 5 bài học xây dựng DApp tích hợp AI + Blockchain!
>
> Hãy nhìn lại toàn bộ pipeline:

```
📸 Camera    → 🤖 MediaPipe   → 📊 Embedding    → ☁️ IPFS (CID)
   (Lesson 7)    (Lesson 7)       (512D vector)     (Lesson 7)
                                                        ↓
🌐 React UI ← 🖥️ FastAPI    ← 🔗 PyCardano    ← ⛓️ Aiken CKV
   (Lesson 10)   (Lesson 9)      (Lesson 8)        (Lesson 6)
```

> **Key takeaways**:
>
> 1. **CKV Pattern** — state machine trên Cardano bằng continuing outputs
> 2. **Face Verify** — biometric verification thực tế, không fake
> 3. **IPFS + Blockchain** — off-chain big data, on-chain reference (CID)
> 4. **Int ≠ Bool** — CBOR encoding phải nhất quán giữa on/off-chain
> 5. **RawCBOR** — datum từ chain cần deserialize
> 6. **add_input_address()** — luôn thêm wallet UTxOs cho transaction fees
>
> Đây không chỉ là demo — đây là **architecture thực tế** cho bất kỳ DApp nào cần:
> - Lưu trữ dữ liệu lớn off-chain (IPFS)
> - Xác minh danh tính bằng AI
> - Quản lý state trên blockchain
>
> Cảm ơn các bạn đã theo dõi Chapter 3! Happy coding! 🚀

---

*Kết thúc Lesson 10 — ~17 phút*
*Tổng thời lượng Chapter 3: ~90 phút (5 bài × ~18 phút)*
