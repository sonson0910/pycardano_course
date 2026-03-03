# Chapter 3 — Lesson 1: Hello World (Aiken + PyCardano)

## Mục tiêu bài học

- Xây dựng **smart contract (validator)** đầu tiên bằng **Aiken**
- Deploy và tương tác với hợp đồng từ Python bằng **PyCardano**
- Hiểu vòng đời: **Lock ADA → Unlock ADA** qua Plutus script
- Thực hành với **PlutusV3**, `datum`, `redeemer`, và `script address`

## Lý thuyết ngắn gọn

### Aiken Validator

Validator `hello_world.ak` xác thực giao dịch unlock dựa trên:
- **Datum**: chứa `owner` (hash của payment vkey)
- **Redeemer**: chứa `msg` (message phải bằng `"Hello, World!"`)
- Điều kiện: `msg == "Hello, World!"` **VÀ** giao dịch được ký bởi `owner`

### Plutus Transaction Flow

```
[Lock TX]  ví → script address (kèm datum: owner = vkey_hash)
[Unlock TX] script address → ví (kèm redeemer: msg = "Hello, World!")
```

## Cấu trúc thư mục

```
chapter3_lession1_helloworld/
├── scirpt.md                   # Hướng dẫn chi tiết bài giảng
└── hello_world/
    ├── aiken.toml              # Cấu hình project Aiken
    ├── validators/
    │   └── hello_world.ak      # Smart contract Aiken
    ├── plutus.json             # Blueprint sau khi build (output của aiken build)
    ├── lock.py                 # Script lock ADA vào hợp đồng
    └── spend.py                # Script unlock ADA từ hợp đồng
```

---

## Phần 1: Cài đặt Aiken

### Windows (PowerShell — chạy với quyền Administrator)

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://github.com/aiken-lang/aiken/releases/download/v1.1.19/aiken-installer.ps1 | iex"
```

Sau đó **đóng PowerShell và mở lại**, kiểm tra:

```powershell
aiken --version
# 1.1.19
```

### Ubuntu / Linux

```bash
sudo apt update && sudo apt install -y curl ca-certificates
curl --proto '=https' --tlsv1.2 -LsSf https://github.com/aiken-lang/aiken/releases/download/v1.1.19/aiken-installer.sh | sh
exec $SHELL
aiken --version
# 1.1.19
```

> Khuyến nghị dùng **Aiken v1.1.19** để đảm bảo tương thích với `plutus.json` trong bài học.

---

## Phần 2: Build Smart Contract

```powershell
cd chapter3_lession1_helloworld/hello_world
aiken build
```

Lệnh này sẽ compile `validators/hello_world.ak` và tạo file `plutus.json` chứa compiled code (blueprint).

Kiểm tra contract:

```powershell
aiken check
```

---

## Phần 3: Cài đặt Python & Thư viện

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

---

## Cấu hình biến môi trường

Tạo file `.env` tại **thư mục gốc** của repo:

```dotenv
BLOCKFROST_PROJECT_ID=your_blockfrost_project_id_here
BLOCKFROST_NETWORK=testnet
MNEMONIC=word1 word2 word3 ... (24 từ)
```

| Biến | Mô tả |
|------|-------|
| `BLOCKFROST_PROJECT_ID` | Project ID từ https://blockfrost.io (mạng **Preprod**) |
| `BLOCKFROST_NETWORK` | `testnet` (Preprod) hoặc `mainnet` |
| `MNEMONIC` | 24 từ seed phrase có ít nhất **3 ADA** |

> ⚠️ **Không** commit file `.env` lên Git.

---

## Phần 4: Chạy Lock & Unlock

### Bước 1: Lock ADA vào hợp đồng

```powershell
cd chapter3_lession1_helloworld/hello_world
python lock.py
```

Script sẽ:
- Đọc `plutus.json` → dựng `PlutusV3Script` + script address
- Tạo `HelloWorldDatum(owner = payment_vkey_hash)`
- Gửi **2 ADA** vào script address kèm datum
- In ra `Tx Hash` của giao dịch lock

> Sau khi lock, lưu lại **Tx Hash** để dùng cho bước unlock.

### Bước 2: Unlock ADA từ hợp đồng

Mở `spend.py` và cập nhật `lock_tx_id`:

```python
lock_tx_id = "<tx_hash_từ_bước_lock>"
```

Chạy:

```powershell
python spend.py
```

Script sẽ:
- Tìm UTxO đã lock theo `lock_tx_id`
- Tạo `HelloWorldRedeemer(msg = b"Hello, World!")`
- Build + ký giao dịch (payment key là `required_signer`)
- Submit và thu hồi ADA về ví

---

## Xem giao dịch

👉 https://preprod.cardanoscan.io/transaction/`<tx_hash>`

## Lấy tADA testnet

👉 https://docs.cardano.org/cardano-testnets/tools/faucet/
