# Lesson 4 — Xây dựng Giao dịch (Build Transaction)

## Mục tiêu bài học

- Khôi phục ví người gửi (Sender) từ một cụm từ khôi phục (Mnemonic).
- Khởi tạo thư viện `TransactionBuilder` để xây dựng giao dịch chuyển tiền.
- Thêm địa chỉ đầu vào (Input) từ UTxO của người gửi.
- Thêm địa chỉ đầu ra (Output) gửi tới một người nhận (Receiver) cùng một lượng ADA xác định.
- Ký giao dịch (Sign) và gửi lên mạng blockchain (Submit).

## Lý thuyết

Để chuyển ADA hoặc token trên Cardano:
1. **Gom UTxO (Inputs)**: Bạn phải gom đủ lượng UTxO đầu vào sao cho tổng số tiền lớn hơn số tiền muốn chuyển đi cộng với phí mạng (Fee).
2. **Định dạng Output (Outputs)**: Đích đến của số tiền (người nhận).
3. **Tiền thừa (Change)**: Khi số tiền trong các Inputs lớn hơn Output + Fee, lượng dư sẽ được trả lại ví của chính bạn thông qua một UTxO Change. May mắn thay, `TransactionBuilder` tự động tính toán Fee và tạo UTxO Change.
4. **Ký duyệt (Sign)**: Giao dịch phải được ký bởi Private Key hợp lệ (Payment SkeY).
5. **Gửi (Submit)**: Đẩy giao dịch đã ký lên mạng lưới.

## Cấu trúc thư mục

```
chapter2_lesson4_build_transaction/
└── lesson4.py      # Script tạo, ký và gửi giao dịch chuyển 5 ADA
```

## Yêu cầu

- Python 3.9+
- Tài khoản Blockfrost (https://blockfrost.io) với Project ID cho mạng **Preprod**
- Ví Cardano có seed phrase (mnemonic) và có tối thiểu **5 ADA** cộng với phí giao dịch. (Có thể thay đổi lượng gửi trong code).

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
pip install pycardano blockfrost-python mnemonic
```

*(Lưu ý: Mnemonic trong mã nguồn được hard-code và Blockfrost_ID cũng đang được gắn trực tiếp vào script. Hãy cẩn thận khi cấu hình với ví thật).*

## Chạy script

```powershell
cd chapter2_lesson4_build_transaction
python lesson4.py
```

## Luồng hoạt động

1. Kết nối mạng qua `BlockFrostChainContext` với ID trực tiếp.
2. Khôi phục ví Sender qua `HDWallet.from_mnemonic()` và tạo `Address` từ path chuẩn bip-32.
3. In ra địa chỉ gửi và số dư hiện tại của Sender để xác minh đủ tiền.
4. Khởi tạo `builder = TransactionBuilder(context)`.
5. Đẩy địa chỉ gửi vào `builder.add_input_address(sender_address)`. Mặc định builder sẽ kéo tất cả UTxO từ địa chỉ này vào.
6. Thêm một Output `TransactionOutput` gửi cho `RECEIVER_ADDRESS` giá trị **5,000,000 lovelace** (5 ADA).
7. Sử dụng `build_and_sign()` để ký bởi 2 key (Payment, Staking) và gán `change_address` lại cho Sender.
8. Gọi `context.submit_tx()` đẩy lên mạng Preprod.
9. In ra ID giao dịch (Transaction ID / Tx Hash).

## Lấy tADA testnet

Nếu chưa có ADA trên mạng Preprod để thử nghiệm chuyển tiền, hãy truy cập vào faucet:
👉 https://docs.cardano.org/cardano-testnets/tools/faucet/

## Xem giao dịch

Sau khi submit thành công, bạn lấy đoạn Transaction ID và tra cứu trạng thái giao dịch trên Cardano Scan:
👉 https://preprod.cardanoscan.io/transaction/`<tx_hash>`
