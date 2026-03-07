# Lesson 1 — Context và Web3 Provider

## Mục tiêu bài học

- Hiểu khái niệm **Chain Context** (ngữ cảnh chuỗi) trong Cardano.
- Biết cách cấu hình và sử dụng **Blockfrost API** để kết nối với mạng lưới Cardano (Preprod).
- Biết cách cấu hình và kết nối với mạng lưới thông qua **Ogmios** Node.
- Lấy các thông số cơ bản từ mạng lưới như Slot, Epoch và Mạng (Network).

## Lý thuyết

Để tương tác với blockchain Cardano, ứng dụng cần một cổng giao tiếp (Provider/Context). Thư viện `pycardano` hỗ trợ nhiều loại context, phổ biến nhất là:
- **BlockfrostChainContext**: Kết nối thông qua dịch vụ API của bên thứ ba (Blockfrost). Dễ cấu hình, chỉ cần Project ID.
- **OgmiosChainContext**: Kết nối trực tiếp đến một Cardano Node chạy qua dịch vụ Ogmios. Cung cấp kết nối websocket ổn định và nhanh chóng hơn.

## Cấu trúc thư mục

```
chapter2_lesson1_context/
└── lesson1.py      # Script test kết nối chain context
```

## Yêu cầu

- Python 3.9+
- Tài khoản Blockfrost (https://blockfrost.io) với Project ID cho mạng **Preprod** (Dành cho việc thử nghiệm Blockfrost)

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

> ⚠️ **Lưu ý:** Trong bài này có mã nguồn truy cập Blockfrost bị comment lại để sử dụng Ogmios làm ví dụ chính, bạn có thể uncomment để thử nghiệm Blockfrost.

## Chạy script

```powershell
cd chapter2_lesson1_context
python lesson1.py
```

## Luồng hoạt động

1. Nạp thư viện `OgmiosChainContext` từ `pycardano`.
2. Khai báo các thông số kết nối Ogmios (Host, Port, Secure).
3. Khởi tạo `context` kết nối với Ogmios.
4. Truy xuất và hiển thị thông tin về `network` (hoặc `last_block_slot`, `epoch` nếu sử dụng `BlockFrostChainContext`).
