# Lesson 3 — Truy vấn Ví (Query Wallet)

## Mục tiêu bài học

- Kết nối mạng lưới thông qua Blockfrost để đọc dữ liệu on-chain.
- Truy vấn tất cả các UTxO (Unspent Transaction Outputs) đang nằm trong một địa chỉ ví cụ thể.
- Tính tổng số dư ADA và hiển thị các Token (Multi-Asset) có trong ví.
- Truy vấn UTxO tại một địa chỉ Smart Contract (Script Address) và lấy dữ liệu **Datum** đính kèm.

## Lý thuyết

Cardano sử dụng mô hình **EUTxO** (Extended Unspent Transaction Output). Số dư của một ví không phải là một con số tổng duy nhất ghi trong cơ sở dữ liệu, mà là tổng giá trị của tất cả các đồng tiền "chưa chi tiêu" (UTxO) thuộc quyền sở hữu của địa chỉ ví đó.

- **Amount**: Mỗi UTxO có thể chứa ADA gốc (lovelace) và các token Native (multi-asset). (1 ADA = 1.000.000 lovelace).
- **Datum**: Dữ liệu tùy chỉnh đính kèm trên UTxO, chủ yếu sử dụng cho UTxO bị khóa tại các địa chỉ Smart Contract.

## Cấu trúc thư mục

```
chapter2_lesson3_query_wallet/
└── lesson3.py      # Script truy vấn và in danh sách UTxO của ví cá nhân và Script
```

## Yêu cầu

- Python 3.9+
- Tài khoản Blockfrost (https://blockfrost.io) với Project ID cho mạng **Preprod**.

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
```

| Biến | Mô tả |
|------|-------|
| `BLOCKFROST_PROJECT_ID` | Project ID lấy từ https://blockfrost.io (chọn mạng Preprod) |

## Chạy script

```powershell
cd chapter2_lesson3_query_wallet
python lesson3.py
```

## Luồng hoạt động

1. Nạp biến môi trường và kết nối API qua `BlockFrostChainContext`.
2. Khai báo địa chỉ ví cá nhân (`my_address`) và địa chỉ Smart Contract (`script_address`).
3. Khai báo hàm `query_personal_wallet`:
   - Lấy danh sách UTxO với hàm `context.utxos(address)`.
   - Vòng lặp tính tổng `lovelace` và quy đổi sang ADA.
   - Nếu UTxO chứa `multi_asset`, in kèm danh sách token đó.
4. Khai báo hàm `query_script`:
   - Truy vấn UTxO từ địa chỉ hợp đồng.
   - Nếu UTxO có chứa **Datum**, in giá trị của datum ra console. Cực kỳ hữu dụng khi debug dApp.
