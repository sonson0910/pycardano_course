# Lesson 7 (Phần 1) — Mint Multiple NFTs with CIP-721 Metadata

## Mục tiêu bài học

- Đúc nhiều **NFT** (Non-Fungible Token) trong một giao dịch
- Áp dụng chuẩn **CIP-721** để đính kèm metadata on-chain
- Hiểu điểm khác biệt giữa **FT** (Fungible Token) và **NFT**: `quantity = 1`
- Gán thuộc tính ngẫu nhiên cho từng NFT (attack, speed, defense, health, type)

## Lý thuyết

### NFT vs FT

| Đặc điểm | FT (Fungible) | NFT (Non-Fungible) |
|----------|---------------|---------------------|
| Số lượng | Tuỳ ý (vd: 100) | Luôn bằng **1** |
| Tính thay thế | Có (giống nhau) | Không (độc nhất) |
| Metadata | Không bắt buộc | CIP-721 (on-chain) |

### CIP-721 Metadata

Metadata được đính kèm vào transaction theo chuẩn CIP-721:

```json
{
  "721": {
    "<policy_id>": {
      "<asset_name>": {
        "name": "...",
        "image": "ipfs://...",
        "attack": "...",
        ...
      }
    }
  }
}
```

## Cấu trúc thư mục

```
chapter2_lession7_mint_nfts/
├── mint_nfts.py        # Script mint nhiều NFT
└── keys/
    ├── policy.skey     # Policy signing key
    └── policy.vkey     # Policy verification key
```

## Dữ liệu NFT mẫu

```python
assets = [
    {"name": "Pycardano_test_NFT_001", "attack": "45", "speed": "30", ...},
    {"name": "Pycardano_test_NFT_002", ...},
    ...  # tổng 5 NFT
]
```

Các thuộc tính (`attack`, `speed`, `defense`, `health`, `type`) được tạo ngẫu nhiên mỗi lần chạy.

## Yêu cầu

- Python 3.9+
- Tài khoản Blockfrost với Project ID mạng **Preprod**
- Ví có seed phrase và ít nhất **5 ADA** (minUTxO cho mỗi NFT + phí)

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
| `BLOCKFROST_NETWORK` | `testnet` hoặc `mainnet` |
| `MNEMONIC` | 24 từ seed phrase của ví Cardano |

> ⚠️ **Không** commit file `.env` lên Git.

## Chạy script

```powershell
cd chapter2_lession7_mint_nfts
python mint_nfts.py
```

## Luồng hoạt động

1. Nạp `.env`, khôi phục ví từ mnemonic
2. Kết nối Blockfrost, kiểm tra UTxO & số dư
3. Tạo/nạp **Policy Key** từ `keys/`
4. Xây dựng **Native Script** → tính **Policy ID**
5. Build transaction:
   - Mint **5 NFT** (quantity = 1 mỗi cái)
   - Tạo **CIP-721 metadata** với thuộc tính riêng cho từng NFT
   - Output VÀo ví cùng với ADA tối thiểu
6. Ký bằng payment key + policy key → submit

## Kết quả

```
Policy ID: <policy_id>
Đã mint: Pycardano_test_NFT_001 | Pycardano_test_NFT_002 | ...
Tx Hash: <tx_hash>
```

## Lưu ý

- **Giữ lại Policy Key** (`keys/policy.skey`) — cần dùng trong bài Lesson 7 Phần 2 (Burn NFTs)
- Sau khi mint thành công, bài tiếp theo sẽ hướng dẫn burn (đốt) các NFT này

## Lấy tADA testnet

👉 https://docs.cardano.org/cardano-testnets/tools/faucet/

## Xem giao dịch

👉 https://preprod.cardanoscan.io/transaction/`<tx_hash>`
