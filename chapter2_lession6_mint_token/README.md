# Lesson 6 — Mint Fungible Token (FT) with Native Script

## Mục tiêu bài học

- Hiểu cơ chế mint token trên Cardano
- Phát hành **100 Fungible Token (FT)** với Native Script Policy
- Sử dụng **Native Script** (policy dựa trên khóa công khai — `ScriptPubkey`)
- Thực hành với thư viện PyCardano và Blockfrost

## Lý thuyết

### Minting Policy là gì?

Khi phát hành token, blockchain cần trả lời: *"Ai có quyền mint hoặc burn token này?"*

Cardano giải quyết bằng **Minting Policy**. Có 2 cơ chế:

| Cơ chế | Mô tả |
|--------|-------|
| **Native Script** | Policy đơn giản dựa trên chữ ký khoá công khai hoặc thời gian |
| **Plutus Script** | Smart contract phức tạp, có thể chứa logic tuỳ ý |

Bài học này dùng **Native Script (ScriptPubkey)**: chỉ chủ sở hữu khóa policy (policy key) mới có thể mint/burn token.

### Policy Key

Riêng trong bài này, **policy key** được dùng là khóa của chính ví người dùng (không cần tạo key riêng).

## Cấu trúc thư mục

```
chapter2_lession6_mint_token/
├── mint_token.py       # Script mint FT chính
└── keys/
    ├── policy.skey     # Signing key của policy (tự tạo khi chạy lần đầu)
    └── policy.vkey     # Verification key của policy
```

> Nếu thư mục `keys/` chưa có policy key, script sẽ tự động tạo khi chạy.

## Yêu cầu

- Python 3.9+
- Tài khoản Blockfrost với Project ID mạng **Preprod**
- Ví có seed phrase và ít nhất **2 ADA** (để trả phí + minUTxO)

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

```powershell
pip install pycardano blockfrost-python python-dotenv
```

## Cấu hình biến môi trường

Tạo file `.env` tại **thư mục gốc** của repo:

```dotenv
BLOCKFROST_PROJECT_ID=your_blockfrost_project_id_here
BLOCKFROST_NETWORK=testnet
MNEMONIC=word1 word2 word3 ... (24 từ)
```

| Biến | Mô tả |
|------|-------|
| `BLOCKFROST_PROJECT_ID` | Project ID từ https://blockfrost.io (mạng Preprod) |
| `BLOCKFROST_NETWORK` | `testnet` cho Preprod, `mainnet` cho Mainnet |
| `MNEMONIC` | 24 từ seed phrase của ví Cardano |

> ⚠️ **Không** commit file `.env` lên Git.

## Chạy script

```powershell
cd chapter2_lession6_mint_token
python mint_token.py
```

## Luồng hoạt động

1. Nạp `.env`, khôi phục ví từ mnemonic (BIP-32 / CIP-1852)
2. Kết nối Blockfrost, lấy UTxO và kiểm tra số dư
3. Tạo hoặc nạp **Policy Key** từ thư mục `keys/`
4. Xây dựng **Native Script**: `ScriptPubkey(policy_vkey_hash)`
5. Tính **Policy ID** từ hash của Native Script
6. Build transaction:
   - Input: UTxO từ ví
   - Mint: 100 token (tên do bạn đặt)
   - Output: token + ADA → trả về ví
   - Attach Native Script và ký bằng cả payment key + policy key
7. Submit và xác nhận

## Kết quả

Sau khi thành công:

```
Policy ID: <policy_id>
Token Name: <token_name>
Số lượng đã mint: 100
Tx Hash: <tx_hash>
```

## Lấy tADA testnet

👉 https://docs.cardano.org/cardano-testnets/tools/faucet/

## Xem giao dịch

👉 https://preprod.cardanoscan.io/transaction/`<tx_hash>`
