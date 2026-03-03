# Lesson 5 — Consolidate UTxOs

## Mục tiêu bài học

Gộp tất cả UTxO lẻ của một địa chỉ về một UTxO duy nhất nhằm:

- Giảm số lượng inputs trong các giao dịch tương lai
- Tiết kiệm phí giao dịch
- Đơn giản hóa việc quản lý tài sản

## Lý thuyết

Trong Cardano, mỗi lần nhận tiền bạn sẽ nhận một **UTxO (Unspent Transaction Output)** riêng biệt. Khi bạn có nhiều UTxO lẻ, mỗi giao dịch sẽ cần nhiều inputs hơn → kích thước giao dịch lớn hơn → phí cao hơn.

Kỹ thuật **consolidate** giúp gom tất cả UTxO vào một transaction, với tất cả làm input và một output duy nhất trả về chính địa chỉ mình (sau khi trừ phí).

## Cấu trúc thư mục

```
chapter2_lession5_consolidate_utxo/
└── consolidate.py      # Script gộp UTxO chính
```

## Yêu cầu

- Python 3.9+
- Tài khoản Blockfrost (https://blockfrost.io) với Project ID cho mạng **Preprod**
- Ví Cardano có seed phrase (mnemonic) và ít nhất một vài UTxO

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

Khi thành công, terminal sẽ hiển thị `(venv)` ở đầu dòng lệnh.

### Bước 3: Cài đặt thư viện

```powershell
pip install pycardano blockfrost-python python-dotenv
```

## Cấu hình biến môi trường

Tạo file `.env` tại **thư mục gốc** của repo (cùng cấp với `requirements.txt`):

```dotenv
BLOCKFROST_PROJECT_ID=your_blockfrost_project_id_here
BLOCKFROST_NETWORK=testnet
MNEMONIC=word1 word2 word3 ... (24 từ)
```

| Biến | Mô tả |
|------|-------|
| `BLOCKFROST_PROJECT_ID` | Project ID lấy từ https://blockfrost.io (chọn mạng Preprod) |
| `BLOCKFROST_NETWORK` | `testnet` cho Preprod, `mainnet` cho Mainnet |
| `MNEMONIC` | 24 từ seed phrase của ví Cardano |

> ⚠️ **Lưu ý:** File `.env` chứa seed phrase — **không** commit lên Git.

## Chạy script

```powershell
cd chapter2_lession5_consolidate_utxo
python consolidate.py
```

## Luồng hoạt động

1. Nạp biến môi trường và kết nối Blockfrost
2. Khôi phục ví từ mnemonic theo chuẩn BIP-32 / CIP-1852
3. Lấy toàn bộ UTxO của địa chỉ
4. Thêm **tất cả** UTxO làm input của giao dịch
5. Output duy nhất: toàn bộ tài sản → trả lại chính địa chỉ (trừ phí)
6. Ký và submit giao dịch, chờ xác nhận trên blockchain

## Lấy tADA testnet

Nếu chưa có ADA trên mạng Preprod, vào faucet:
👉 https://docs.cardano.org/cardano-testnets/tools/faucet/

## Xem giao dịch

Sau khi submit thành công, xem transaction tại:
👉 https://preprod.cardanoscan.io/transaction/`<tx_hash>`
