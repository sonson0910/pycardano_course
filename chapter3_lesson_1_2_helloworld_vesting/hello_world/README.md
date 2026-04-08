# Chapter 3 — Lesson 1: Hello World (Aiken + PyCardano)

## Mục tiêu bài học

- Xây dựng **smart contract (validator)** đầu tiên bằng **Aiken**
- Deploy và tương tác với hợp đồng từ Python bằng **PyCardano**
- Hiểu vòng đời: **Lock ADA → Unlock ADA** qua Plutus script
- Thực hành với **PlutusV3**, `datum`, `redeemer`, và `script address`

## Lý thuyết ngắn gọn

### Aiken Validator

Validator `hello_world.ak` xác thực giao dịch unlock dựa trên:
- **Datum**: chứa `owner` — hash của payment vkey người lock
- **Redeemer**: chứa `msg` — thông điệp phải bằng `"Hello, World!"`
- Điều kiện: `msg == "Hello, World!"` **VÀ** giao dịch được ký bởi `owner`

### Plutus Transaction Flow

```
[Lock TX]   ví → script address (kèm datum: owner = payment_vkey_hash)
[Unlock TX] script address → ví (kèm redeemer: msg = "Hello, World!")
```

## Cấu trúc thư mục

```
hello_world/
├── .env.example                  # Mẫu biến môi trường
├── app/
│   ├── lock.py                   # Script lock ADA vào hợp đồng
│   └── unlock.py                 # Script unlock ADA từ hợp đồng
├── contract/
│   ├── aiken.toml                # Cấu hình project Aiken
│   ├── plutus.json               # Blueprint sau khi build (output của aiken build)
│   └── validators/
│       └── hello_world.ak        # Smart contract Aiken

```

---

## Phần 1: Cài đặt Aiken

### Windows (PowerShell — chạy với quyền Administrator)

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://github.com/aiken-lang/aiken/releases/download/v1.1.21/aiken-installer.ps1 | iex"
```

Sau đó **đóng PowerShell và mở lại**, kiểm tra:

```powershell
aiken --version
# 1.1.21
```

### Ubuntu / Linux

```bash
sudo apt update && sudo apt install -y curl ca-certificates
curl --proto '=https' --tlsv1.2 -LsSf https://github.com/aiken-lang/aiken/releases/download/v1.1.21/aiken-installer.sh | sh
exec $SHELL
aiken --version
# 1.1.21
```

> Khuyến nghị dùng **Aiken v1.1.21** để đảm bảo tương thích với `plutus.json` trong bài học.

---

## Phần 2: Build Smart Contract

```powershell
cd hello_world/contract
aiken build
```

Lệnh này compile `validators/hello_world.ak` và tạo file `plutus.json` chứa compiled code (blueprint).

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

Tạo file `.env` trong thư mục `hello_world/app/` (hoặc copy từ `.env.example`):

```dotenv
BLOCKFROST_PROJECT_ID=your_blockfrost_project_id_here
MNEMONIC=word1 word2 word3 ... (24 từ)
```

| Biến | Mô tả |
|------|-------|
| `BLOCKFROST_PROJECT_ID` | Project ID từ https://blockfrost.io (mạng **Preprod**) |
| `MNEMONIC` | 24 từ seed phrase của ví Cardano có ít nhất **3 ADA** trên Preprod |

> ⚠️ **Không** commit file `.env` lên Git.

---

## Phần 4: Chạy Lock & Unlock

### Bước 1: Lock ADA vào hợp đồng

```powershell
cd hello_world/app
python lock.py
```

Script sẽ:
1. Đọc `../contract/plutus.json` → lấy `script_hash` để tạo script address
2. Khôi phục ví từ mnemonic (BIP-32 / CIP-1852)
3. Tạo `HelloWorldDatum(owner = payment_vkey_hash)`
4. Gửi **2 ADA** vào script address kèm datum inline
5. In ra `Tx Hash` của giao dịch lock

### Bước 2: Chờ xác nhận (~20–60 giây)

Kiểm tra giao dịch tại:
👉 https://preprod.cardanoscan.io/transaction/`<tx_hash>`

### Bước 3: Unlock ADA từ hợp đồng

```powershell
python unlock.py
```

Script sẽ:
1. Đọc `../contract/plutus.json` → lấy `PlutusV3Script` và `script_hash`
2. Tìm UTxO đang nằm tại script address
3. Tạo `HelloWorldRedeemer(msg = b"Hello, World!")`
4. Gắn script và redeemer vào giao dịch, ký bằng ví owner
5. Submit và in ra `Tx Hash` của giao dịch unlock

---

## Luồng hoạt động

```
Ví (owner)
    │
    │── [lock.py] ──► Script Address
    │                    UTxO: 2 ADA
    │                    Datum: { owner: vkey_hash }
    │
    │◄─ [unlock.py] ── Script Address
         Redeemer: { msg: "Hello, World!" }
         Xác thực: msg đúng VÀ giao dịch ký bởi owner
```

---

## Lấy tADA testnet

Nếu chưa có ADA trên mạng Preprod, vào faucet:
👉 https://docs.cardano.org/cardano-testnets/tools/faucet/

## Xem giao dịch

Sau khi submit thành công, xem transaction tại:
👉 https://preprod.cardanoscan.io/transaction/`<tx_hash>`
