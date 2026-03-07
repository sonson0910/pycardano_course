# Chapter 1 - Lesson 5: First Project (Lấy Thông Tin Block Hiện Tại)

## Mục tiêu bài học

- Viết kịch bản (script) Python đầu tiên tương tác với nền tảng Cardano.
- Khởi tạo kết nối mạng lưới với **BlockFrostChainContext** sử dụng Blockfrost API.
- Gọi API để truy xuất dữ liệu của khối (Block) mới nhất trên mạng Preprod.
- Hiểu và hiển thị các trường dữ liệu quan trọng của một Block như: Hash, Slot, Epoch, Số lượng giao dịch (Tx count), Phí (Gas fee) và Kích thước (Size).

## Lý thuyết

Trong các dự án blockchain, việc theo dõi trạng thái mạng lưới là bước đầu tiên để đảm bảo bạn đang kết nối đúng mạng và có dữ liệu cập nhật nhất.
Blockfrost cung cấp các API thông qua đối tượng `context.api`. Trong ví dụ này, hàm `block_latest()` sẽ trả về dữ liệu của khối mới nhất vừa được thêm vào blockchain.

- **Block Hash**: Mã định danh độc nhất của khối.
- **Absolute Slot**: Vị trí tuyệt đối của khối tính từ khi mạng (hoặc chuỗi) bắt đầu.
- **Epoch**: Chu kỳ thời gian của mạng Cardano (ví dụ mỗi Epoch trên Mainnet kéo dài 5 ngày).
- **Tx count**: Tổng số giao dịch (Transactions) được đóng gói trong khối này.
- **Fees**: Tổng lượng phí được trả cho tất cả các giao dịch trong khối (tính bằng lovelace).
- **Size**: Kích thước của khối (bytes).

## Cấu trúc thư mục

```
chapter1_lesson5_first_project/
└── first_project.py      # Script truy xuất thông tin khối mới nhất
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
pip install pycardano blockfrost-python
```

*(Lưu ý: Project ID trong bài này hiện đang được hard-code. Trong thực tế bạn nên dùng biến môi trường `.env` như các bài học sau.)*

## Chạy script

```powershell
cd chapter1_lesson5_first_project
python first_project.py
```

## Luồng hoạt động

1. Nhập khẩu (import) `BlockFrostChainContext` từ thư viện `pycardano`.
2. Khai báo `PROJECT_ID` được lấy từ bảng điều khiển của Blockfrost.
3. Khởi tạo đối tượng `context` với mạng lưới Preprod API: `https://cardano-preprod.blockfrost.io/api`.
4. Gọi phương thức `context.api.block_latest()` để lấy thông tin block cuối.
5. In ra màn hình các thuộc tính của block vừa nhận được.
