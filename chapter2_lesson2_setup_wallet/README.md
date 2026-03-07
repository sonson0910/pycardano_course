# Lesson 2 — Thiết lập Ví (Setup Wallet)

## Mục tiêu bài học

- Tạo một ví Cardano mới thủ công bằng mã Python.
- Sinh ra cụm từ khôi phục (Mnemonic / Seed Phrase) 24 từ.
- Dẫn xuất (Derive) các khóa Payment Key và Staking Key từ Mnemonic theo chuẩn BIP-32 và CIP-1852.
- Tính toán băm (Hash) để tạo địa chỉ ví hoàn chỉnh trên mạng Testnet.
- Xác thực quá trình khôi phục lại ví từ chính Mnemonic vừa tạo.

## Lý thuyết

Ví Cardano HD (Hierarchical Deterministic) được xây dựng dựa trên seed phrase. Từ seed phrase, chúng ta có thể dẫn xuất ra vô số địa chỉ.
Trong Cardano, một địa chỉ tiêu chuẩn bao gồm hai phần:
- **Payment part**: Dẫn xuất từ **Payment Key**. Quản lý UTxO và số dư (ADA, Token). Đường dẫn chuẩn: `m/1852'/1815'/0'/0/0`
- **Staking part**: Dẫn xuất từ **Stake Key**. Quản lý quyền biểu quyết (Vote) và ủy quyền (Delegate) nhận phần thưởng staking. Đường dẫn chuẩn: `m/1852'/1815'/0'/2/0`

## Cấu trúc thư mục

```
chapter2_lesson2_setup_wallet/
└── lesson2.py      # Script tạo ví, dẫn xuất khóa và khôi phục ví
```

## Yêu cầu

- Python 3.9+
- Không yêu cầu API key hay kết nối mạng (thực hiện hoàn toàn offline).

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
pip install pycardano mnemonic
```

## Chạy script

```powershell
cd chapter2_lesson2_setup_wallet
python lesson2.py
```

## Luồng hoạt động

1. Sử dụng thư viện `mnemonic` để sinh ra cụm 256 bit (24 từ tiếng Anh).
2. Dùng `HDWallet.from_mnemonic()` trong `pycardano` để tạo master node.
3. Dẫn xuất **Payment Key** theo nhánh `m/1852'/1815'/0'/0/0` để lấy Khóa Private (`ExtendedSigningKey`) và Khóa Public (`VerificationKey`).
4. Dẫn xuất **Stake Key** theo nhánh `m/1852'/1815'/0'/2/0`.
5. Băm các VKeys (`hash()`) và khởi tạo đối tượng `Address` dành riêng cho mạng Testnet.
6. Thử nghiệm quá trình khôi phục: dùng lại Mnemonic ban đầu tạo một `HDWallet` mới, dẫn xuất ký khóa và so sánh với khóa tạo ở bước 3 xem có khớp không (`is_match`).
