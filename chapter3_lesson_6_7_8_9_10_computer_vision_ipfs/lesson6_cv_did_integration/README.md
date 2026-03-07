# Lesson 6 — Tích hợp Computer Vision cho Xác minh Khuôn mặt & Liên kết DID

## Mục tiêu bài học

- Hiểu khái niệm **Decentralized Identity (DID)** trên Cardano
- Thiết kế **DIDDatum** — cấu trúc dữ liệu lưu danh tính on-chain
- Viết **smart contract (validator)** bằng **Aiken** quản lý DID lifecycle
- Implement **kiểm tra chữ ký owner** qua `ScriptContext` (bảo mật)
- Viết và chạy **test suite** hoàn chỉnh
- Liên kết **face embedding** (computer vision) với **DID on-chain**

## Lý thuyết

### Computer Vision + DID — Tổng quan kiến trúc

```
Camera → Face Detection → Embedding 512D
                         → Upload IPFS → CID
                                          ↓
                         Smart Contract DIDDatum {
                           did_id,
                           face_ipfs_hash: CID,  ← liên kết tới CV data
                           owner,
                           created_at,
                           verified
                         }
```

Ý tưởng cốt lõi: **kết hợp face embedding (AI/CV) với blockchain identity (DID)**.
- Face embedding là dữ liệu sinh trắc học, quá lớn để lưu on-chain
- Lưu embedding lên **IPFS** → nhận **CID** (content hash)
- Lưu CID on-chain trong **DIDDatum** → liên kết xác minh danh tính

### DIDDatum — Dữ liệu on-chain

```aiken
pub type DIDDatum {
  did_id: ByteArray,         // Unique DID identifier
  face_ipfs_hash: ByteArray, // IPFS CID chứa face embedding
  owner: ByteArray,          // Public key hash (28 bytes)
  created_at: Int,           // POSIX timestamp (ms)
  verified: Bool,            // Trạng thái xác minh
}
```

### Redeemer Actions

| Action | Ý nghĩa | Yêu cầu |
|--------|---------|----------|
| `Register` | Đăng ký DID mới | Datum hợp lệ + chữ ký owner |
| `Update` | Cập nhật dữ liệu | did_id non-empty + chữ ký owner |
| `Verify` | Xác minh danh tính | did_id + face_hash non-empty |
| `Revoke` | Thu hồi DID vĩnh viễn | did_id non-empty + chữ ký owner |

### Owner Authorization

Validator kiểm tra `self.extra_signatories` chứa `datum.owner`:
- **Register, Update, Revoke** → cần chữ ký owner (mutating actions)
- **Verify** → ai cũng có thể verify (read-only)

## Cấu trúc thư mục

```
lesson6_cv_did_integration/
├── README.md
└── did_contract/
    ├── aiken.toml                  # Cấu hình project Aiken
    ├── lib/
    │   ├── types.ak                # DIDDatum + Action types
    │   └── validation.ak           # Pure validation functions
    ├── validators/
    │   └── did_manager.ak          # Main validator (owner auth)
    └── lib.test.ak                 # Test suite (12 tests)
```

## Cài đặt Aiken

### macOS

```bash
brew install aiken-lang/tap/aiken
aiken --version
# v1.1.21
```

### Linux

```bash
curl --proto '=https' --tlsv1.2 -LsSf \
  https://github.com/aiken-lang/aiken/releases/download/v1.1.21/aiken-installer.sh | sh
aiken --version
```

## Build & Test

```bash
cd lesson6_cv_did_integration/did_contract
aiken build    # Compile → plutus.json
aiken check    # Chạy tất cả tests
```

### Kết quả mong đợi

```
    Testing ...

    ┍━ did_contract ━━━━━━━━━━━━━━━━━━━━━━
    │ PASS register_valid_did
    │ PASS register_empty_did_fails
    │ PASS register_empty_hash_fails
    │ PASS register_invalid_timestamp_fails
    │ PASS register_negative_timestamp_fails
    │ PASS update_valid_did
    │ PASS update_empty_did_fails
    │ PASS verify_valid_did
    │ PASS verify_empty_did_fails
    │ PASS verify_empty_hash_fails
    │ PASS revoke_valid_did
    │ PASS revoke_empty_did_fails
    │ PASS full_lifecycle
    ┕━━━━━━━━━━━━━━━━━━━━━━ 13 tests | 13 passed | 0 failed
```

> 💡 File `plutus.json` (blueprint) sẽ được dùng trong Lesson 8 để build off-chain transactions.

## Xem giao dịch

👉 https://preprod.cardanoscan.io/transaction/`<tx_hash>`
