# Lesson 8 — Viết Off-chain Code (Python): AI Logic & On-chain Transactions

## Mục tiêu bài học

- Định nghĩa **PlutusData** trong Python khớp chính xác với Aiken DIDDatum
- Đọc **blueprint** (`plutus.json`) và tạo **PlutusV3Script** + script address
- **Lock ADA** vào smart contract kèm DIDDatum (inline datum)
- **Unlock ADA** từ smart contract bằng redeemer actions
- Kết nối **AI logic** (face embedding) với **on-chain transactions**
- Thực hiện **full lifecycle**: Create → Register → Verify → Revoke

## Lý thuyết

### PlutusData Mapping — Kết nối Aiken ↔ Python

Aiken type → Python PlutusData:

| Aiken | Python | CBOR |
|-------|--------|------|
| `ByteArray` | `bytes` | Major type 2 |
| `Int` | `int` | Major type 0/1 |
| `Bool` | `bool` | Primitive true/false |

> ⚠️ **Quan trọng**: `Bool` trong Aiken ≠ `int`. Phải dùng `bool` Python (True/False) để CBOR encoding khớp.

### AI Logic + On-chain TX Flow

```
[Lesson 7] Face Detect → Embedding → IPFS CID
                                       ↓
[Lesson 8] CID → DIDDatum → Lock TX → Script Address
                                       ↓
           Redeemer (Register/Update/Verify/Revoke) → Unlock TX → Wallet
```

Script `lock_did.py` xử lý:
1. AI output (IPFS CID từ Lesson 7) → tạo DIDDatum
2. Build & sign Lock TX → gửi 2 ADA + datum vào script address

Script `unlock_did.py` xử lý:
1. Tìm UTxO đã lock bằng TX hash
2. Build spending TX với redeemer → thu hồi ADA

## Cấu trúc thư mục

```
lesson8_offchain_code/
├── README.md           # Bài học này
├── lock_did.py         # Lock ADA + DIDDatum vào contract
├── unlock_did.py       # Unlock ADA bằng redeemer
└── did_operations.py   # Full lifecycle operations (CLI)
```

## Yêu cầu

- Đã build smart contract (Lesson 6): `plutus.json` phải tồn tại
- File `.env` tại thư mục gốc repo với `BLOCKFROST_PROJECT_ID` và `MNEMONIC`
- Ít nhất **5 tADA** trên ví Preprod

## Cài đặt

```bash
pip install pycardano blockfrost-python python-dotenv
```

## Chạy script

### 1. Lock ADA vào smart contract

```bash
cd lesson8_offchain_code
python lock_did.py --ipfs-hash QmXxx...  # CID từ Lesson 7
```

Script sẽ:
- Đọc `plutus.json` → tạo PlutusV3Script + script address
- Tạo DIDDatum với IPFS hash
- Gửi **2 ADA** vào script address kèm datum
- In ra **TX Hash**

> 💡 **Lưu lại TX Hash** cho bước unlock!

### 2. Unlock ADA từ smart contract

Mở `unlock_did.py` và cập nhật:

```python
LOCK_TX_HASH = "<tx_hash_từ_bước_lock>"
```

Chạy:

```bash
python unlock_did.py
```

### 3. Full lifecycle (CLI)

```bash
# Tạo DID
python did_operations.py --action create --ipfs-hash QmXxx...

# Register (unlock bằng Register redeemer)
python did_operations.py --action register --tx-hash <tx_hash>

# Check balance
python did_operations.py --action balance

# List UTxOs tại script
python did_operations.py --action list
```

## Kết quả mong đợi

```
🔏 Loading smart contract from plutus.json...
✅ Script hash: abc123...
✅ Script address: addr_test1wz...
👛 Wallet: addr_test1qz...
   Balance: 45.30 ADA

📤 Building Lock TX...
   DID ID: did:cardano:a1b2c3d4e5f6
   IPFS Hash: QmTestHash123
   Amount: 2,000,000 lovelace (2.00 ADA)
✅ Lock TX submitted!
   TX Hash: 4374fa5c17abeb977e008d0568cf...
   View: https://preprod.cardanoscan.io/transaction/4374fa5c...
```
