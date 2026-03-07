# Lesson 7 (Phần 2) — Burn NFTs

## Mục tiêu bài học

- **Burn (đốt)** các NFT đã mint ở bài Lesson 7 Phần 1
- Hiểu cách biểu diễn số lượng âm (`-1`) để burn token trong Cardano
- Ký giao dịch burn bằng đúng **policy signing key** đã dùng khi mint

## Lý thuyết

### Burn Token trong Cardano

Để burn token, giao dịch cần:
- Đặt số lượng **âm** trong phần `MultiAsset` (ví dụ: `-1` để burn 1 NFT)
- Đính kèm **Minting Script** và ký bằng **policy key** tương ứng
- Script sẽ xác thực chữ ký hợp lệ trước khi cho phép burn

### Điều kiện tiên quyết

**Bạn phải đã hoàn thành Lesson 7 Phần 1 (Mint NFTs)** và giữ lại:

- `keys/policy.skey` — policy signing key (dùng để ký burn)
- `keys/policy.vkey` — policy verification key
- **Policy ID** — để xác định đúng các NFT cần burn

## Cấu trúc thư mục

```
chapter2_lession7_burn_nfts/
├── burn_nfts.py        # Script burn NFT
└── keys/
    ├── policy.skey     # Policy signing key (phải khớp với khi mint)
    └── policy.vkey     # Policy verification key
```

> ⚠️ **Policy key phải là cùng key đã dùng khi mint.** Nếu dùng key khác, giao dịch sẽ bị từ chối.

## NFT sẽ được burn

Script mặc định sẽ burn 5 NFT sau (đã mint ở bài trước):

```python
assets = [
    {"name": "Pycardano_test_NFT_001"},
    {"name": "Pycardano_test_NFT_002"},
    {"name": "Pycardano_test_NFT_003"},
    {"name": "Pycardano_test_NFT_004"},
    {"name": "Pycardano_test_NFT_005"},
]
```

## Yêu cầu

- Python 3.9+
- Tài khoản Blockfrost với Project ID mạng **Preprod**
- Ví có seed phrase với NFT cần burn và ADA để trả phí
- **Policy key** (`keys/policy.skey`) khớp với policy đã dùng khi mint

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
| `MNEMONIC` | 24 từ seed phrase — **phải là ví đang giữ NFT** |

> ⚠️ **Không** commit file `.env` lên Git.

## Chạy script

```powershell
cd chapter2_lession7_burn_nfts
python burn_nfts.py
```

## Luồng hoạt động

1. Nạp `.env`, khôi phục ví từ mnemonic
2. Kết nối Blockfrost, tìm UTxO chứa NFT
3. Nạp **Policy Key** từ `keys/policy.skey`
4. Xây dựng lại **Native Script** → xác nhận Policy ID khớp
5. Build transaction:
   - Input: UTxO chứa các NFT cần burn
   - Mint (số lượng âm): `-1` cho mỗi NFT
   - Đính kèm Native Script
6. Ký bằng payment key + policy key → submit

## Kết quả

```
Đang burn: Pycardano_test_NFT_001 ... ✓
Tx Hash: <tx_hash>
NFT đã bị hủy vĩnh viễn trên blockchain.
```

## Xem giao dịch

👉 https://preprod.cardanoscan.io/transaction/`<tx_hash>`
