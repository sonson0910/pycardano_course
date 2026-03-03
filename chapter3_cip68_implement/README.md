# Chapter 3 — CIP-68 Dynamic NFT Implementation

## Mục tiêu bài học

- Hiểu chuẩn **CIP-68** và khái niệm **Dynamic NFT** trên Cardano
- Mint NFT với **metadata on-chain** có thể cập nhật sau khi phát hành
- Thực hành 3 thao tác: **Mint → Update Metadata → Burn**
- Chạy backend API (FastAPI) để tích hợp với frontend

## Lý thuyết CIP-68

### Chuẩn CIP-68 là gì?

CIP-68 định nghĩa cấu trúc token **Dynamic NFT** với 2 loại token đi kèm nhau:

| Token | Label | Prefix hex | Mô tả |
|-------|-------|------------|-------|
| **Reference Token** | 100 | `000643b0` | Lưu metadata on-chain trong datum, gửi về store address |
| **User Token** | 222 | `000de140` | Token người dùng thực sự sở hữu |

### Metadata On-chain

Metadata được lưu trong **datum** của Reference Token UTxO tại store address → có thể cập nhật bất kỳ lúc nào (không cần burn + mint lại như CIP-721).

### Smart Contracts (Aiken)

- **Mint Script**: kiểm soát quyền mint/burn cặp token
- **Store Script**: kiểm soát việc cập nhật metadata (chỉ owner mới được update)

---

## Cấu trúc thư mục

```
chapter3_cip68_implement/
├── demo_mint.py            # Script mint CIP-68 token
├── demo_update.py          # Script update metadata
├── demo_burn.py            # Script burn token
├── run_backend.py          # Khởi chạy FastAPI backend
├── requirements.txt        # Thư viện Python cần thiết
├── offchain/
│   ├── cip68_operations.py # Logic chính: mint, update, burn, list
│   └── cip68_utils.py      # Utilities, datums, redeemers, script helpers
├── backend/
│   └── main.py             # FastAPI app (REST API)
├── cip68_dynamic_asset/    # Aiken smart contract source
│   └── validators/
└── template_frontend_cip68/ # Next.js frontend template
```

---

## Cài đặt môi trường

### Bước 1: Tạo môi trường ảo (thực hiện tại thư mục gốc repo)

```powershell
python -m venv venv
```

### Bước 2: Kích hoạt môi trường

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
source venv/bin/activate
```

### Bước 3: Cài đặt thư viện

Bài học này yêu cầu nhiều thư viện hơn các bài trước. Cài từ file `requirements.txt` của thư mục này:

```powershell
cd chapter3_cip68_implement
pip install -r requirements.txt
```

Nội dung `requirements.txt`:

```
pycardano>=0.11.0
blockfrost-python
python-dotenv>=1.0.0
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
pydantic>=2.0.0
cbor2>=5.6.0
```

> ⚠️ Nếu cài đặt gặp lỗi với một số thư viện, thử nâng cấp pip trước: `pip install --upgrade pip`

---

## Cấu hình biến môi trường

Tạo file `.env` tại **thư mục `chapter3_cip68_implement/`** (hoặc thư mục gốc repo):

```dotenv
# Blockfrost
BLOCKFROST_PROJECT_ID=your_blockfrost_project_id_here
NETWORK=Preprod

# Wallet
SEED_PHRASE=word1 word2 word3 ... (24 từ)
```

| Biến | Mô tả |
|------|-------|
| `BLOCKFROST_PROJECT_ID` | Project ID từ https://blockfrost.io (mạng **Preprod**) |
| `NETWORK` | `Preprod` hoặc `Mainnet` |
| `SEED_PHRASE` | 24 từ seed phrase có ít nhất **10 ADA** |

> ⚠️ **Không** commit file `.env` lên Git.

---

## Chạy Demo Scripts

### 1. Mint CIP-68 Token

```powershell
cd chapter3_cip68_implement
python demo_mint.py
```

Script sẽ tự động:
- Tạo tên token unique theo timestamp: `DemoNFT_<timestamp>`
- Mint cặp Reference Token (100) + User Token (222)
- Gửi Reference Token về store address kèm metadata trong datum
- Gửi User Token về ví bạn
- Lưu thông tin token vào `minted_<token_name>.json`

Kết quả mẫu:
```
MINT THÀNH CÔNG!
Transaction Hash: abc123...
Policy ID: def456...
Token Name: DemoNFT_1770735185
```

### 2. Update Metadata

```powershell
python demo_update.py
```

Script sẽ:
- Liệt kê tất cả token bạn đang sở hữu
- Cho bạn chọn token cần update
- Cập nhật metadata (description mới theo timestamp)
- Chỉ **owner** mới có quyền update (store script xác thực)

### 3. Burn Token

```powershell
python demo_burn.py
```

Script sẽ:
- Liệt kê tokens hiện có
- Xác nhận trước khi burn
- Burn cả **Reference Token** lẫn **User Token**
- Thu hồi ADA từ store address về ví

---

## Chạy Backend API (FastAPI)

Backend cung cấp REST API để frontend có thể gọi các thao tác mint/update/burn.

```powershell
cd chapter3_cip68_implement
python run_backend.py
```

API sẽ chạy tại: **http://127.0.0.1:8000**

Xem tài liệu API tự động: **http://127.0.0.1:8000/docs**

---

## Frontend (Next.js — Tùy chọn)

```powershell
cd chapter3_cip68_implement/template_frontend_cip68
npm install
npm run dev
```

Frontend chạy tại: **http://localhost:3000**

Yêu cầu:
- Node.js 18+
- Backend API đang chạy tại port 8000
- Ví Cardano browser extension (Eternl, Nami, v.v.)

---

## Lấy tADA testnet (Preprod)

👉 https://docs.cardano.org/cardano-testnets/tools/faucet/

> Cần ít nhất **10 ADA** vì mỗi thao tác mint/update cần một lượng ADA nhất định cho minUTxO và phí.

## Xem giao dịch

👉 https://preprod.cardanoscan.io/transaction/`<tx_hash>`
