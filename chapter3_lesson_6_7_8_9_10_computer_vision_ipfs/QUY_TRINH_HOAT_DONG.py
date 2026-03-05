#!/usr/bin/env python3
"""
Quy trình hoạt động của dự án Computer Vision + Blockchain DApp
"""

print(
    """
╔══════════════════════════════════════════════════════════════════════════════╗
║                 QUY TRÌNH HOẠT ĐỘNG CỦA DỰ ÁN                               ║
║          Computer Vision + Blockchain Decentralized Identity (DID)          ║
╚══════════════════════════════════════════════════════════════════════════════╝

═══════════════════════════════════════════════════════════════════════════════
1️⃣  NGƯỜI DÙNG TRUY CẬP DAPP (Frontend - React)
═══════════════════════════════════════════════════════════════════════════════

Quy trình:
  • Người dùng mở trình duyệt → http://localhost:5173
  • Giao diện React hiển thị:
    - Nút "Chụp ảnh" hoặc "Upload ảnh"
    - Nút "Tạo DID" (Tạo định danh blockchain)
    - Nút "Xác minh khuôn mặt" (Verify face identity)
    - Nút "Xem lịch sử"

Công nghệ:
  - React TypeScript + Vite
  - Gọi API đến Backend FastAPI
  - Lưu trạng thái người dùng (localStorage)


═══════════════════════════════════════════════════════════════════════════════
2️⃣  PHÁT HIỆN KHUÔN MẶT (Face Detection - MediaPipe)
═══════════════════════════════════════════════════════════════════════════════

Quy trình:
  • Người dùng chụp/upload ảnh
  • Frontend gửi HTTP POST tới: /api/v1/detect-faces
  • Backend nhận ảnh:

    a) Xử lý ảnh:
       - Tải ảnh vào bộ nhớ
       - Kiểm tra kích thước (max 10MB)
       - Chuyển sang định dạng RGB

    b) Chạy MediaPipe Face Detection:
       - Phát hiện tất cả khuôn mặt trong ảnh
       - Tính toán tọa độ facial landmarks (468 điểm)
       - Tạo face embedding (vector 512 chiều)

    c) Trả kết quả:
       - Danh sách khuôn mặt phát hiện
       - Tọa độ bounding box
       - Confidence score

Kết quả:
  [{
    "face_id": "face_001",
    "bbox": [x, y, width, height],
    "confidence": 0.98,
    "landmarks": [...]
  }]


═══════════════════════════════════════════════════════════════════════════════
3️⃣  LƯU TRỮ TRÊN IPFS (Off-chain Storage)
═══════════════════════════════════════════════════════════════════════════════

Quy trình:
  • Backend lấy face embedding (vector 512)
  • Chuyển thành JSON:
    {
      "face_embedding": [0.1, 0.2, -0.3, ...],
      "face_id": "face_001",
      "metadata": {"age": 25, "gender": "M"}
    }

  • Gửi lên IPFS:
    - Tạo file temp
    - Upload via Kubo API hoặc Pinata
    - Nhận IPFS hash: QmXxX...

  • IPFS hash là "chứng chỉ" của data:
    - Bất kỳ ai cũng có thể verify data
    - Data không thể bị thay đổi
    - Phân tán trên mạng P2P

Lợi ích:
  - Không lưu dữ liệu trực tiếp trên blockchain (quá đắt tiền)
  - Data được bảo vệ bằng cryptographic hash
  - Có thể truy cập từ bất kỳ node IPFS nào


═══════════════════════════════════════════════════════════════════════════════
4️⃣  TẠO ĐỊNH DANH TRÊN BLOCKCHAIN (DID - Create)
═══════════════════════════════════════════════════════════════════════════════

Quy trình tạo DID:

  a) Chuẩn bị dữ liệu:
     - DID ID: "did:cardano:sonson0910"
     - IPFS hash: "QmExample123..."
     - Owner: Địa chỉ ví của người dùng
     - Created_at: Timestamp hiện tại
     - Verified: false (chưa xác minh)

  b) Tạo Plutus Datum (dữ liệu on-chain):
     @dataclass
     class DIDDatum(PlutusData):
       did_id: bytes              # "did:cardano:sonson0910"
       face_ipfs_hash: bytes      # "QmExample123..."
       owner: bytes               # Khóa công khai chủ sở hữu
       created_at: int            # 1728019200
       verified: bool             # False

  c) Xây dựng Giao dịch (Transaction):
     - Input: UTxO từ ví (2 ADA)
     - Output: 3 ADA → Địa chỉ Smart Contract
     - Đính kèm: DID Datum + Script validator
     - Phí: ~0.2 ADA

  d) Ký giao dịch:
     - Sử dụng khóa riêng người dùng (me_preprod.sk)
     - Tạo chữ ký số
     - Tạo TX Hash

  e) Gửi lên Cardano Preprod Testnet:
     - Blockfrost API tiếp nhận
     - Ghi vào mempool
     - Đợi ~40 giây để confirm

  f) Kết quả:
     TX Hash: 4374fa5c17abeb977e008d0568cf1cdf458ce66025ef92871dcbfe2685242149

     Trên blockchain:
     - DID được lưu vĩnh viễn
     - IPFS hash được gắn với DID
     - Không ai có thể sửa đổi (immutable)


═══════════════════════════════════════════════════════════════════════════════
5️⃣  THỰC HIỆN HÀNH ĐỘNG (Redeemer - Register/Update/Verify/Revoke)
═══════════════════════════════════════════════════════════════════════════════

Quy trình xác minh/cập nhật:

  a) Chọn hành động:
     - Register: Đăng ký DID lần đầu (chạy validation)
     - Update: Cập nhật IPFS hash mới
     - Verify: Xác minh khuôn mặt (face matching)
     - Revoke: Hủy DID (vĩnh viễn)

  b) Tạo Redeemer (chứng chỉ để unlock):
     Aiken Enum:
       pub type Action {
         Register    # Constructor 0
         Update      # Constructor 1
         Verify      # Constructor 2
         Revoke      # Constructor 3
       }

     Python:
       @dataclass
       class Register(PlutusData):
           CONSTR_ID = 0  # Enum variant, NO fields

  c) Xây dựng TX Spend (Unlock):
     - Input từ Script: 3 ADA (từ create_did.py)
     - Redeemer: Register()
     - Output: Trả lại ~ 2.8 ADA vào ví
     - Phí: ~0.2 ADA

  d) Validator kiểm tra:
     Trên blockchain, Aiken validator chạy:

     validator did_manager {
       spend(datum, action, _own_ref, _self) {
         True  # Hiện tại chỉ return True (proof of concept)
       }
     }

     Trong tương lai sẽ kiểm tra:
     - Có đúng chủ sở hữu không?
     - Face embedding hợp lệ không?
     - Đã hết hạn không?

  e) Nếu hợp lệ → Giao dịch được confirm

     Kết quả:
     TX Hash: 1519bf1bf1ef5a38ccdf46cba4089e7210288f44dfa1f9d27c294bfa906dd952

     Trên blockchain:
     - DID được cập nhật trạng thái
     - IPFS hash mới được gắn (nếu là Update)
     - UTxO cũ được "xoá" (spent)


═══════════════════════════════════════════════════════════════════════════════
6️⃣  TRUY VẤN DID (Verification)
═══════════════════════════════════════════════════════════════════════════════

Quy trình xác minh định danh:

  a) Frontend gọi API:
     GET /api/v1/did/did:cardano:sonson0910

  b) Backend:
     - Tìm kiếm trên blockchain
     - Lấy UTxO chứa DID data
     - Giải mã Datum:
       {
         "did_id": "did:cardano:sonson0910",
         "face_ipfs_hash": "QmExample123...",
         "owner": "4d17ab606e...",
         "created_at": 1728019200,
         "verified": false
       }

     - Lấy data từ IPFS:
       {
         "face_embedding": [0.1, 0.2, ...],
         "metadata": {...}
       }

  c) Trả kết quả:
     {
       "did_id": "...",
       "status": "active",
       "created_at": "2025-10-16",
       "verified": false,
       "ipfs_hash": "QmExample123...",
       "face_data": {...}
     }

  d) Frontend:
     - Hiển thị thông tin DID
     - Cho phép người dùng verify khuôn mặt


═══════════════════════════════════════════════════════════════════════════════
📊 TÓME TẮT QUY TRÌNH HOÀN CHỈNH
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. NGƯỜI DÙNG UPLOAD ẢNH                                                    │
│    ↓                                                                         │
│ 2. PHÁT HIỆN KHUÔN MẶT (MediaPipe)                                          │
│    ↓                                                                         │
│ 3. TÍNH EMBEDDING & LƯU IPFS                                                │
│    ↓                                                                         │
│ 4. TẠO DID & LOCK VÀO SMART CONTRACT (Create)                               │
│    ↓                                                                         │
│ 5. UNLOCK & XÁC MINH (Register/Verify/Update/Revoke)                        │
│    ↓                                                                         │
│ 6. TRUY VẤN & ĐỌC DID DATA                                                  │
└─────────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════════
🏛️  CÁC THÀNH PHẦN CHÍNH
═══════════════════════════════════════════════════════════════════════════════

┌─ FRONTEND (React) ─────────────────────────┐
│ • Giao diện người dùng                     │
│ • Upload/Chụp ảnh                         │
│ • Xem danh sách DIDs                       │
│ • Kết nối ví Cardano                      │
└────────────────────────────────────────────┘
              ↓ HTTP API
┌─ BACKEND (FastAPI) ────────────────────────┐
│ • Phát hiện khuôn mặt (MediaPipe)          │
│ • Quản lý API endpoints                    │
│ • Xử lý giao dịch blockchain              │
│ • Tương tác IPFS                          │
└────────────────────────────────────────────┘
         ↙          ↓          ↘
    ┌───────┐  ┌─────────┐  ┌──────────┐
    │ IPFS  │  │ Cardano │  │ Database │
    │ (P2P) │  │Blockchain│ │(SQLite)  │
    └───────┘  └─────────┘  └──────────┘


═══════════════════════════════════════════════════════════════════════════════
💡 TẠI SAO THIẾT KẾ NHƯ THẾ?
═══════════════════════════════════════════════════════════════════════════════

✓ Face Embedding + IPFS:
  - Dữ liệu lớn (vector 512 chiều) không phù hợp trên blockchain (đắt)
  - IPFS cung cấp hash bất biến → xác minh data
  - On-chain chỉ lưu IPFS hash (100 byte, rẻ)

✓ Smart Contract (Aiken):
  - Validator chạy on-chain → bảo vệ quy tắc
  - Hiện tại: always True (proof of concept)
  - Tương lai: Kiểm tra chủ sở hữu, hết hạn, etc.

✓ UTxO Model (Cardano):
  - Mỗi DID là 1 UTxO
  - Để sửa DID → phải "spend" UTxO cũ + tạo UTxO mới
  - Tự động loại trừ trùng lặp

✓ Decentralization:
  - Không cần trusted server
  - Data được bảo vệ bằng cryptography
  - Ai cũng có thể verify DIDs


═══════════════════════════════════════════════════════════════════════════════
🔐 BẢOMẬT
═══════════════════════════════════════════════════════════════════════════════

✓ Private Key:
  - Lưu secure trong me_preprod.sk
  - Chỉ dùng để ký giao dịch
  - Không bao giờ gửi lên server

✓ On-chain:
  - Tất cả giao dịch là public
  - Bất kỳ ai cũng có thể xác minh
  - Validator đảm bảo chỉ chủ sở hữu mới có thể sửa

✓ IPFS:
  - Data được hash → không thể sửa
  - Phân tán trên mạng → không thể xóa


═══════════════════════════════════════════════════════════════════════════════

✅ HOÀN THÀNH!

Dự án này kết hợp:
  • 🎥 Computer Vision (MediaPipe) → Phát hiện khuôn mặt
  • 🔗 Blockchain (Cardano) → Lưu định danh vĩnh viễn
  • 📦 IPFS → Lưu dữ liệu lớn off-chain
  • 🌐 Web DApp → Giao diện cho người dùng

Kết quả: Hệ thống định danh phi tập trung, không thể bị sửa đổi!
"""
)
