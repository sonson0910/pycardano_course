# 🎬 SCRIPT BÀI GIẢNG — Lesson 8: Off-chain Code (PyCardano + Blockfrost)
# Thời lượng: ~20 phút
# Công cụ: Screen recording + Terminal + VS Code + CardanoScan (browser)

---

## [00:00 – 01:30] 🎯 Giới thiệu & Mục tiêu

**Nói:**

> Xin chào! Chào mừng đến **Lesson 8** — bài quan trọng nhất trong chapter này.
>
> Bài này là nơi mọi thứ **kết nối lại với nhau**: smart contract (Lesson 6), face embedding + IPFS (Lesson 7), và bây giờ chúng ta sẽ viết **off-chain code** bằng Python để tương tác trực tiếp với blockchain.
>
> Cụ thể, sau bài này các bạn sẽ:
> - Biết cách map **PlutusData** giữa Aiken và Python
> - Đọc file **plutus.json** và tạo **PlutusV3Script**
> - **Lock ADA** vào smart contract kèm DIDDatum
> - **Spend/Unlock** UTxO bằng redeemer — theo logic **CKV** (continuing output)
> - Xử lý **RawCBOR deserialization** — một cái bẫy rất hay gặp
> - Chạy **full lifecycle**: Lock → Register → Verify → Revoke trên Preprod
>
> Bài này có **3 file** Python: `lock_did.py` (lock riêng), `unlock_did.py` (unlock riêng), và `did_operations.py` (tất-cả-trong-một). Let's go!

---

## [01:30 – 05:00] 📚 PlutusData Mapping: Aiken ↔ Python

**Nói:**

> Điều đầu tiên và quan trọng nhất: **PlutusData mapping**. Cấu trúc dữ liệu Python phải **khớp chính xác** với Aiken type.
>
> Khi Python gửi transaction, datum sẽ encode thành **CBOR** — format nhị phân chuẩn Plutus. Nếu CBOR không khớp giữa Python và Aiken, validator **từ chối** transaction. Lỗi này cực khó debug!

*(Hiện code trên màn hình)*

```python
from dataclasses import dataclass
from pycardano import PlutusData

@dataclass
class DIDDatum(PlutusData):
    CONSTR_ID = 0
    did_id: bytes
    face_ipfs_hash: bytes
    owner: bytes
    created_at: int
    verified: int  # 0 = chưa, 1 = đã verify — PHẢI LÀ int, KHÔNG bool!
```

> Điểm mấu chốt — trường `verified`:
> - Trong Aiken: `verified: Int` encode CBOR integer (0 hoặc 1)
> - Nếu Python dùng `bool`, PyCardano encode thành CBOR **primitive true/false** — hoàn toàn khác!
> - Quy tắc: **Aiken dùng Int → Python PHẢI dùng int**. Không ngoại lệ.
>
> Tiếp theo, redeemer actions:

```python
@dataclass
class Register(PlutusData):
    CONSTR_ID = 0    # Khớp vị trí 0 trong Aiken Action enum

@dataclass
class Update(PlutusData):
    CONSTR_ID = 1    # Vị trí 1

@dataclass
class Verify(PlutusData):
    CONSTR_ID = 2    # Vị trí 2

@dataclass
class Revoke(PlutusData):
    CONSTR_ID = 3    # Vị trí 3
```

> `CONSTR_ID` phải khớp **chính xác** thứ tự variant trong Aiken enum. Register = 0, Update = 1, Verify = 2, Revoke = 3. Sai thứ tự = validator từ chối!

---

## [05:00 – 08:30] 🔏 Lock TX — File `lock_did.py`

*(Mở `lock_did.py` trong VS Code)*

**Nói:**

> Bước đầu tiên: **Lock** — gửi 2 ADA kèm DIDDatum vào script address.
>
> File `lock_did.py` có 3 phần chính:

> **Phần 1 — Load smart contract:**

```python
def load_contract(plutus_json_path: str) -> tuple:
    with open(plutus_json_path) as f:
        blueprint = json.load(f)

    compiled_code = blueprint["validators"][0]["compiledCode"]
    script = PlutusV3Script(bytes.fromhex(compiled_code))
    script_hash = plutus_script_hash(script)
    script_address = Address(script_hash, network=Network.TESTNET)
    return script, script_hash, script_address
```

> Đọc file `plutus.json` (output của `aiken build` từ Lesson 6), lấy `compiledCode` hex, tạo `PlutusV3Script`, rồi tính `script_address` trên Preprod testnet.

> **Phần 2 — Setup wallet từ mnemonic:**

```python
def setup_wallet() -> tuple:
    context = BlockFrostChainContext(
        project_id=os.getenv("BLOCKFROST_PROJECT_ID"),
        base_url="https://cardano-preprod.blockfrost.io/api/",
    )

    hd_wallet = HDWallet.from_mnemonic(os.getenv("MNEMONIC"))

    payment_node = hd_wallet.derive_from_path("m/1852'/1815'/0'/0/0")
    payment_skey = ExtendedSigningKey.from_hdwallet(payment_node)
    payment_vkey = payment_skey.to_verification_key()

    staking_node = hd_wallet.derive_from_path("m/1852'/1815'/0'/2/0")
    staking_skey = ExtendedSigningKey.from_hdwallet(staking_node)
    staking_vkey = staking_skey.to_verification_key()

    sender_address = Address(
        payment_part=payment_vkey.hash(),
        staking_part=staking_vkey.hash(),
        network=Network.TESTNET,
    )
    return context, sender_address, payment_skey, staking_skey, payment_vkey
```

> Chú ý cách tạo key:
> - `HDWallet.from_mnemonic()` → khôi phục ví từ 24 từ
> - `derive_from_path("m/1852'/1815'/0'/0/0")` → payment key (path chuẩn Cardano CIP-1852)
> - `ExtendedSigningKey.from_hdwallet()` → tạo signing key từ HD node
> - `payment_skey.to_verification_key()` → public key để tạo address

> **Phần 3 — Build, sign, submit:**

```python
# DID ID auto-generate bằng SHA256 hash
did_id = f"did:cardano:{hashlib.sha256(ipfs_hash.encode()).hexdigest()[:16]}"

datum = DIDDatum(
    did_id=did_id.encode("utf-8"),
    face_ipfs_hash=ipfs_hash.encode("utf-8"),
    owner=bytes(payment_vkey.hash()),       # 28 bytes pub key hash
    created_at=int(time.time() * 1000),     # POSIX milliseconds
    verified=0,                              # Chưa verify
)

builder = TransactionBuilder(context)
builder.add_input_address(sender_address)    # Wallet UTxOs cho input + fees
builder.add_output(TransactionOutput(
    address=script_address,
    amount=Value(2_000_000),    # 2 ADA
    datum=datum,                # Inline datum
))
signed_tx = builder.build_and_sign(
    signing_keys=[payment_skey, staking_skey],
    change_address=sender_address,
)
context.submit_tx(signed_tx)
```

> Chú ý `did_id` được tạo bằng cách hash IPFS CID → lấy 16 hex characters đầu. Cách này đảm bảo DID ID unique cho mỗi face embedding.

---

## [08:30 – 13:00] 🔄 Spend TX — Class DIDManager (CKV)

*(Mở `did_operations.py`)*

**Nói:**

> File `did_operations.py` gộp tất cả operations vào class **`DIDManager`** — OOP gọn gàng.
>
> Class có 4 methods tương ứng 4 actions:
> - `create_and_lock()` — lock ADA + datum vào script
> - `register()` — CKV continuing output (giữ nguyên datum)
> - `verify_did()` — CKV continuing output (verified: 0→1)
> - `revoke()` — KHÔNG continuing output (burn DID)

> Hãy xem method **`register()`** — mẫu CKV đơn giản nhất:

```python
def register(self, lock_tx_hash: str) -> str:
    target = self._find_utxo(lock_tx_hash)  # Tìm UTxO bằng TX hash

    builder = TransactionBuilder(self.context)
    builder.add_input_address(self.address)     # ← QUAN TRỌNG: Wallet UTxOs cho fees!
    builder.add_script_input(target, self.script, Redeemer(Register()))
    builder.required_signers = [self.pay_vkey.hash()]

    # CKV: Continuing output — giữ nguyên datum (RawCBOR OK)
    builder.add_output(TransactionOutput(
        self.script_address,
        Value(target.output.amount.coin),
        datum=target.output.datum,        # ← Copy nguyên RawCBOR
    ))

    signed_tx = builder.build_and_sign([self.pay_skey, self.stake_skey], change_address=self.address)
    self.context.submit_tx(signed_tx)
```

> ⚠️ **Cái bẫy số 1 — `add_input_address()`**:
>
> Khi spend UTxO từ script, ADA trong script UTxO chỉ đủ trả lại cho continuing output (2 ADA). Nhưng transaction cần **fees** — khoảng 0.3–0.5 ADA. Fees phải lấy từ **wallet**!
>
> Nếu quên `add_input_address()`, TransactionBuilder không có wallet UTxOs → lỗi **"All UTxO selectors failed"**. Lỗi này cực khó debug vì message không rõ ràng!
>
> Tiếp theo, method **`verify_did()`** — chuyển `verified` từ 0 sang 1:

```python
def verify_did(self, lock_tx_hash: str) -> str:
    target = self._find_utxo(lock_tx_hash)

    # ← QUAN TRỌNG: Deserialize RawCBOR trước!
    raw_datum = target.output.datum
    input_datum = DIDDatum.from_cbor(raw_datum.cbor)

    output_datum = DIDDatum(
        did_id=input_datum.did_id,
        face_ipfs_hash=input_datum.face_ipfs_hash,
        owner=input_datum.owner,
        created_at=input_datum.created_at,
        verified=1,  # 0 → 1
    )

    builder = TransactionBuilder(self.context)
    builder.add_input_address(self.address)
    builder.add_script_input(target, self.script, Redeemer(Verify()))
    builder.add_output(TransactionOutput(
        self.script_address, Value(target.output.amount.coin), datum=output_datum,
    ))
```

> Và **`revoke()`** — trường hợp đặc biệt, KHÔNG có continuing output:

```python
def revoke(self, lock_tx_hash: str) -> str:
    target = self._find_utxo(lock_tx_hash)

    builder = TransactionBuilder(self.context)
    builder.add_input_address(self.address)
    builder.add_script_input(target, self.script, Redeemer(Revoke()))
    builder.required_signers = [self.pay_vkey.hash()]
    # KHÔNG add_output → ADA trả về wallet qua change_address
    signed_tx = builder.build_and_sign(...)
```

---

## [13:00 – 15:30] ⚠️ RawCBOR Deserialization — Cái bẫy số 2

**Nói:**

> Bây giờ đến **cái bẫy số 2** — quan trọng không kém.
>
> Khi đọc UTxO từ chain qua Blockfrost, PyCardano trả datum dưới dạng **RawCBOR** — bytes CBOR thô, CHƯA deserialize thành DIDDatum.

```python
target = context.utxos(script_address)[0]

# ❌ SAI — crash!
input_datum = target.output.datum
print(input_datum.did_id)
# AttributeError: 'RawCBOR' object has no attribute 'did_id'
```

> PyCardano không biết datum thuộc type gì — nó chỉ thấy bytes. Phải **tự deserialize**:

```python
# ✅ ĐÚNG
raw_datum = target.output.datum
input_datum = DIDDatum.from_cbor(raw_datum.cbor)   # ← Key!
print(input_datum.did_id)    # b'did:cardano:abc123'
print(input_datum.verified)  # 0
```

> **Khi nào cần `from_cbor()`?**
> - **Verify, Update** — cần đọc fields cũ để tạo datum mới → **PHẢI** deserialize
> - **Register** — chỉ copy nguyên datum cũ, không truy cập fields → `target.output.datum` (RawCBOR) truyền thẳng vào output OK
> - **Revoke** — không cần datum output → không cần

> Ngoài ra, file `unlock_did.py` cũng xử lý tương tự — dùng `ACTION_MAP` dict để map action name → (class, needs_continuing_output):

```python
ACTION_MAP = {
    "register": (Register, True),   # needs continuing
    "verify":   (Verify,   True),   # needs continuing (verified=1)
    "update":   (Update,   True),   # needs continuing (new ipfs_hash)
    "revoke":   (Revoke,   False),  # NO continuing (burn)
}
```

---

## [15:30 – 18:00] 💻 Live Demo: Full Lifecycle

*(Chạy terminal)*

**Nói:**

> Demo thực tế trên Preprod testnet!

```bash
cd lesson8_offchain_code

# Bước 1: Lock DID (dùng lock_did.py riêng)
python lock_did.py --ipfs-hash QmXLaBYop7bGLQ2uWtDUo5tk7niVDLdKpLTRfULAAwp6gz
```

```
🔏 Loading smart contract from plutus.json...
✅ Script hash: abcd1234...
✅ Script address: addr_test1wz...
👛 Wallet: addr_test1qz...
   Balance: 45.30 ADA
   UTxOs: 3

📤 Building Lock TX...
   DID ID: did:cardano:8090aa0a2a983078
   IPFS Hash: QmXLaBYop7bGLQ2u...
   Amount: 2,000,000 lovelace (2.00 ADA)
✅ Lock TX submitted!
   TX Hash: d5cd7e06547fa0ea...
```

*(Mở CardanoScan)*

> Trên CardanoScan, TX có 1 output tại script address kèm inline datum chứa DIDDatum.

```bash
# Bước 2-4: dùng did_operations.py (tất-cả-trong-một)
python did_operations.py --action register --tx-hash d5cd7e06547fa0ea...
# ✅ Register TX: 9af27d30b46727d5...

python did_operations.py --action verify --tx-hash 9af27d30b46727d5...
# ✅ Verify TX: 4c21ed16b33ec487... (verified: 0→1)

python did_operations.py --action revoke --tx-hash 4c21ed16b33ec487...
# ✅ Revoke TX: 8659b1b24573c484... (DID burned 🔥)
```

> Full lifecycle: **Lock → Register → Verify → Revoke**. 4 transactions on Preprod!
>
> Hoặc có thể dùng `unlock_did.py` riêng cho từng action:

```bash
python unlock_did.py --action register --tx-hash d5cd7e06547fa0ea...
```

---

## [18:00 – 20:00] 🔑 Tổng kết & Preview

**Nói:**

> Tổng kết Lesson 8 — bài dài nhất nhưng quan trọng nhất:
>
> **3 trap phải nhớ:**
> 1. **Int vs Bool** — `verified` phải dùng `int`, tuyệt đối không dùng `bool`
> 2. **`add_input_address()`** — luôn thêm wallet UTxOs cho fees khi spend script
> 3. **RawCBOR** — datum từ chain cần `DIDDatum.from_cbor(raw_datum.cbor)` trước khi truy cập fields (verify, update). Register copy nguyên RawCBOR nên OK.
>
> **3 file Python:**
> - `lock_did.py` — lock riêng, hàm `load_contract()` + `setup_wallet()`
> - `unlock_did.py` — unlock riêng, dùng `ACTION_MAP` dict
> - `did_operations.py` — class `DIDManager` gộp tất cả, OOP clean
>
> **CKV Continuing Output:**
> - Register/Update/Verify → output quay lại script
> - Revoke → không output = burn DID
>
> Bây giờ ta đã có off-chain code hoạt động. Nhưng chạy bằng CLI thì user thường không xài được. Bài tiếp — **Lesson 9** — wrap tất cả thành **REST API** bằng FastAPI, để frontend gọi dễ dàng.
>
> Hẹn gặp ở Lesson 9!

---

*Kết thúc Lesson 8 — ~20 phút*
