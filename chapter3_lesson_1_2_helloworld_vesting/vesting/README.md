# Chapter 3 — Lesson 2: Vesting (Aiken + PyCardano)

## Mục tiêu bài học

- Xây dựng **smart contract Vesting** bằng **Aiken** + thư viện **vodka**
- Triển khai cơ chế **time-locked fund**: chỉ được rút tiền sau một thời điểm nhất định
- Hỗ trợ 2 vai trò: **owner** (rút bất kỳ lúc nào) và **beneficiary** (rút sau `lock_until`)
- Sử dụng **PyCardano** để lock và unlock tiền qua hợp đồng

## Lý thuyết ngắn gọn

### Vesting là gì?

**Vesting** là cơ chế trao quyền sở hữu tài sản theo điều kiện thời gian. Thay vì chuyển tiền trực tiếp, người gửi (owner) khóa tiền trong smart contract và chỉ cho phép người nhận (beneficiary) rút sau một khoảng thời gian định trước.

### Aiken Validator

Validator `vesting.ak` xác thực giao dịch unlock dựa trên:
- **Datum**: gồm 3 trường
  - `lock_until` — thời điểm mở khóa (POSIX time, milliseconds)
  - `owner` — hash của payment vkey người lock (có thể rút bất kỳ lúc nào)
  - `beneficiary` — hash của payment vkey người thụ hưởng (chỉ rút được sau `lock_until`)
- **Redeemer**: không dùng (`Data`)
- Logic:
  - Nhánh 1: `owner` ký giao dịch → luôn hợp lệ
  - Nhánh 2: `beneficiary` ký giao dịch **VÀ** giao dịch diễn ra sau `lock_until`

> Sử dụng thư viện **vodka** (`key_signed`, `valid_after`) để viết ngắn gọn và an toàn hơn.

### Plutus Transaction Flow

```
[Lock TX]   ví (owner) → script address
            Datum: { lock_until, owner, beneficiary }

[Unlock TX — owner]      script address → ví (bất kỳ lúc nào)
[Unlock TX — beneficiary] script address → ví (sau lock_until)
```

## Cấu trúc thư mục

```
vesting/
├── .env.example               # Mẫu biến môi trường
├── app/
│   ├── lock.py                # Script lock ADA vào hợp đồng
│   └── unlock.py              # Script unlock ADA từ hợp đồng
├── contract/
│   ├── aiken.toml             # Cấu hình project Aiken (bao gồm stdlib + vodka)
│   ├── plutus.json            # Blueprint sau khi build (output của aiken build)
│   └── validators/
│       └── vesting.ak         # Smart contract Aiken
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

Contract sử dụng thư viện **vodka** — đã được khai báo sẵn trong `contract/aiken.toml`:

```toml
[[dependencies]]
name = "sidan-lab/vodka"
version = "0.1.1-beta"
source = "github"
```

Build contract:

```powershell
cd vesting/contract
aiken build
```

Lệnh này compile `validators/vesting.ak` và tạo file `plutus.json` chứa compiled code (blueprint). Aiken sẽ tự tải thư viện vodka qua mạng lần đầu nếu chưa có cache.

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

Tạo file `.env` trong thư mục `vesting/app/` (hoặc copy từ `.env.example`):

```dotenv
BLOCKFROST_PROJECT_ID=your_blockfrost_project_id_here
MNEMONIC=word1 word2 word3 ... (24 từ)
```

| Biến | Mô tả |
|------|-------|
| `BLOCKFROST_PROJECT_ID` | Project ID từ https://blockfrost.io (mạng **Preprod**) |
| `MNEMONIC` | 24 từ seed phrase của ví Cardano (owner) có ít nhất **3 ADA** trên Preprod |

> ⚠️ **Không** commit file `.env` lên Git.

---

## Phần 4: Chạy Lock & Unlock

### Bước 1: Lock ADA vào hợp đồng

```powershell
cd vesting/app
python lock.py
```

Script sẽ:
1. Đọc `../contract/plutus.json` → lấy `script_hash` để tạo script address
2. Khôi phục ví từ mnemonic (BIP-32 / CIP-1852)
3. Tạo `VestingDatum` với:
   - `lock_until` = thời điểm hiện tại + 10 phút (tính theo milliseconds)
   - `owner` = payment vkey hash của ví hiện tại
   - `beneficiary` = payment vkey hash của ví hiện tại (có thể thay đổi thành ví khác)
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
3. Tạo giao dịch với `validity_start` sau `lock_until` (để contract xác nhận đã qua thời gian)
4. Ký bằng ví owner hoặc beneficiary tương ứng
5. Submit và in ra `Tx Hash` của giao dịch unlock

---

## Luồng hoạt động

```
Ví (owner)
    │
    │── [lock.py] ──► Script Address
    │                    UTxO: 2 ADA
    │                    Datum: { lock_until, owner, beneficiary }
    │
    ├── [unlock.py — owner]       ──► bất kỳ lúc nào
    │
    └── [unlock.py — beneficiary] ──► chỉ sau lock_until
         Giao dịch phải có valid_after > lock_until
```

### Điều kiện hợp lệ

| Người ký | Điều kiện thời gian | Hợp lệ? |
|----------|---------------------|---------|
| `owner` | bất kỳ | ✅ |
| `beneficiary` | trước `lock_until` | ❌ |
| `beneficiary` | sau `lock_until` | ✅ |
| Người khác | bất kỳ | ❌ |

---

## Lấy tADA testnet

Nếu chưa có ADA trên mạng Preprod, vào faucet:
👉 https://docs.cardano.org/cardano-testnets/tools/faucet/

## Xem giao dịch

Sau khi submit thành công, xem transaction tại:
👉 https://preprod.cardanoscan.io/transaction/`<tx_hash>`
