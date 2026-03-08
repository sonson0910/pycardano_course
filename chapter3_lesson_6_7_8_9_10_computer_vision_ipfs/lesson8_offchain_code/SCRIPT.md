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
> Đây là bài dài nhất, nhưng cũng thực tế nhất. Ready? Let's go!

---

## [01:30 – 05:00] 📚 PlutusData Mapping: Aiken ↔ Python

**Nói:**

> Điều đầu tiên và quan trọng nhất khi viết off-chain code: **PlutusData mapping**. Tức là đảm bảo cấu trúc dữ liệu Python **khớp chính xác** với Aiken type.
>
> Tại sao quan trọng? Vì khi Python gửi transaction, datum sẽ được encode thành **CBOR** — format nhị phân chuẩn của Plutus. Nếu CBOR không khớp giữa off-chain (Python) và on-chain (Aiken), validator sẽ **từ chối** transaction. Và lỗi này cực khó debug!
>
> Hãy xem bảng mapping:

| Aiken type | Python type | Lưu ý |
|-----------|-------------|-------|
| `ByteArray` | `bytes` | Dùng `.encode("utf-8")` cho string |
| `Int` | `int` | **TUYỆT ĐỐI KHÔNG dùng `bool`** |
| Constructor enum | `CONSTR_ID` | Thứ tự phải khớp |

> Và đây là điểm mấu chốt — hãy nhìn kỹ trường `verified`:

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
    verified: int        # ← PHẢI LÀ int, KHÔNG PHẢI bool!
```

> Tại sao `int` mà không phải `bool`? Vì trong Aiken, `verified: Int` encode thành CBOR integer (0 hoặc 1). Nhưng nếu Python dùng `bool`, PyCardano sẽ encode thành CBOR **primitive true/false** — khác hoàn toàn! Validator sẽ **expect fail** khi parse datum.
>
> Đây là bài học thực tế: **khi Aiken dùng Int, Python PHẢI dùng int**. Không có ngoại lệ.
>
> Tiếp theo, redeemer actions:

```python
@dataclass
class Register(PlutusData):
    CONSTR_ID = 0    # Khớp với vị trí 0 trong Aiken Action enum

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

> `CONSTR_ID` phải khớp **chính xác** với thứ tự variant trong Aiken enum. Register = 0, Update = 1, Verify = 2, Revoke = 3. Sai thứ tự = validator từ chối!

---

## [05:00 – 08:30] 🔏 Lock TX — Gửi ADA vào Smart Contract

*(Mở `lock_did.py`)*

**Nói:**

> Bước đầu tiên trong DID lifecycle: **Lock** — gửi 2 ADA kèm DIDDatum vào script address.

```python
import json
from pathlib import Path
from pycardano import *

# 1. Load smart contract từ plutus.json
blueprint = json.loads(Path("../lesson6.../did_contract/plutus.json").read_text())
cbor_hex = blueprint["validators"][0]["compiledCode"]
script = PlutusV3Script(bytes.fromhex(cbor_hex))

# 2. Tạo script address
script_hash = plutus_script_hash(script)
script_address = Address(script_hash, network=Network.TESTNET)
print(f"📜 Script address: {script_address}")
```

> Chú ý hàm `plutus_script_hash()` — từ PyCardano v0.12+, đây là cách đúng để lấy script hash. Các phiên bản cũ dùng `script.hash()` nhưng có thể không tương thích Plutus V3.

```python
# 3. Tạo wallet từ mnemonic
mnemonic = os.getenv("MNEMONIC")
hdwallet = HDWallet.from_mnemonic(mnemonic)
staking_key = hdwallet.derive_from_path("m/1852'/1815'/0'/2/0")
payment_key = hdwallet.derive_from_path("m/1852'/1815'/0'/0/0")
pay_skey = ExtendedSigningKey.from_primitive(payment_key.xprivate_key)
pay_vkey = PaymentVerificationKey.from_primitive(payment_key.public_key)

# 4. Tạo DIDDatum
did_id = f"did:cardano:{secrets.token_hex(8)}"
datum = DIDDatum(
    did_id=did_id.encode("utf-8"),
    face_ipfs_hash=ipfs_cid.encode("utf-8"),  # CID từ Lesson 7
    owner=bytes(pay_vkey.hash()),               # 28 bytes
    created_at=int(time.time() * 1000),         # POSIX ms
    verified=0,                                  # ← 0, KHÔNG phải False!
)
```

> Rồi build transaction:

```python
# 5. Build & Sign & Submit
context = BlockFrostChainContext(project_id, base_url=ApiUrls.preprod.value)
builder = TransactionBuilder(context)
builder.add_output(TransactionOutput(
    script_address,
    Value(2_000_000),    # 2 ADA
    datum=datum,         # Inline datum
))
signed_tx = builder.build_and_sign(
    signing_keys=[pay_skey, stake_skey],
    change_address=wallet_address,
)
context.submit_tx(signed_tx)
print(f"✅ Lock TX: {signed_tx.id}")
```

> Sau khi submit, 2 ADA + DIDDatum sẽ nằm tại **script address**. Bạn có thể xem trên CardanoScan!

---

## [08:30 – 13:00] 🔄 Spend TX — CKV Continuing Output

*(Mở `unlock_did.py` và `did_operations.py`)*

**Nói:**

> Bây giờ đến phần phức tạp nhất — **Spend TX** với CKV logic.
>
> Khác với "unlock đơn giản" (lấy ADA về ví), CKV yêu cầu bạn phải **tạo output mới quay lại script**. Mình gọi đó là "continuing output".
>
> Hãy xem code cho action **Register**:

```python
def perform_action(self, did_id, action_name):
    # 1. Tìm UTxO tại script address
    utxos = self.context.utxos(self.script_address)
    target = None
    for utxo in utxos:
        if str(utxo.input.transaction_id) == last_tx_hash:
            target = utxo
            break
```

> ⚠️ **Lưu ý cực quan trọng** — dòng tiếp theo:

```python
    # 2. Build TX
    builder = TransactionBuilder(self.context)
    builder.add_input_address(self.address)     # 👈 QUAN TRỌNG!!
    builder.add_script_input(
        utxo=target,
        script=self.script,
        redeemer=Redeemer(Register()),
    )
    builder.required_signers = [self.pay_vkey.hash()]
```

> Thấy dòng `builder.add_input_address()` không? Đây là **cái bẫy số 1** mà mình đã mắc phải!
>
> Khi spend UTxO từ script, ADA trong script UTxO chỉ đủ trả lại cho output (2 ADA). Nhưng transaction còn cần **fees** — khoảng 0.3–0.5 ADA. Fees này phải lấy từ **wallet** của bạn!
>
> Nếu không thêm `add_input_address()`, TransactionBuilder sẽ **không có wallet UTxOs** để dùng cho fees → lỗi: **"All UTxO selectors failed"**. Lỗi này cực khó debug vì message không rõ ràng!

```python
    # 3. CKV: Continuing output
    if action_name == "register":
        # Register: giữ nguyên datum
        builder.add_output(TransactionOutput(
            self.script_address,                      # ← quay lại CÙNG script
            Value(target.output.amount.coin),         # ← cùng số ADA
            datum=target.output.datum,                # ← cùng datum
        ))
    elif action_name == "revoke":
        # Revoke: KHÔNG output → ADA trả về ví
        pass
```

> Register tạo continuing output với **cùng datum** — validator sẽ check `cont_datum == datum`.
> Revoke thì **không** tạo output → ADA trả về ví owner.

---

## [13:00 – 15:30] ⚠️ RawCBOR Deserialization — Cái bẫy số 2

**Nói:**

> Bây giờ đến **cái bẫy số 2** — quan trọng không kém.
>
> Khi bạn đọc UTxO từ chain qua Blockfrost, PyCardano trả về datum dưới dạng **RawCBOR** — tức bytes CBOR thô, CHƯA deserialize thành DIDDatum.

```python
# Lấy UTxO từ chain
target = context.utxos(script_address)[0]

# ❌ SAI — sẽ crash!
input_datum = target.output.datum
print(input_datum.did_id)
# AttributeError: 'RawCBOR' object has no attribute 'did_id'
```

> Tại sao? Vì PyCardano không biết datum này thuộc type gì — nó chỉ thấy bytes CBOR. Bạn phải **tự deserialize**:

```python
# ✅ ĐÚNG — deserialize trước
raw_datum = target.output.datum
input_datum = DIDDatum.from_cbor(raw_datum.cbor)   # ← Key!
print(input_datum.did_id)    # b'did:cardano:abc123'
print(input_datum.verified)  # 0
```

> Cái này ảnh hưởng đến action **Verify** — khi bạn cần đọc datum cũ (verified=0) rồi tạo datum mới (verified=1):

```python
elif action_name == "verify":
    raw_datum = target.output.datum
    input_datum = DIDDatum.from_cbor(raw_datum.cbor)    # Deserialize!
    out_datum = DIDDatum(
        did_id=input_datum.did_id,
        face_ipfs_hash=input_datum.face_ipfs_hash,
        owner=input_datum.owner,
        created_at=input_datum.created_at,
        verified=1,            # ← 0 → 1
    )
    builder.add_output(TransactionOutput(
        self.script_address, Value(coin), datum=out_datum,
    ))
```

> Với **Register**, bạn không cần deserialize vì chỉ copy nguyên datum cũ — `target.output.datum` (RawCBOR) vẫn OK để truyền vào output.

---

## [15:30 – 18:00] 💻 Live Demo: Full Lifecycle

*(Chạy terminal)*

**Nói:**

> Chạy thực tế trên Preprod testnet!

```bash
cd lesson8_offchain_code

# Bước 1: Lock DID
python lock_did.py --ipfs-hash QmXLaBYop7bGLQ2uWtDUo5tk7niVDLdKpLTRfULAAwp6gz
```

```
🔏 Loading smart contract from plutus.json...
✅ Script address: addr_test1wz...
👛 Wallet: addr_test1qz... (Balance: 45.30 ADA)
📤 Building Lock TX...
   DID ID: did:cardano:8090aa0a2a983078
   IPFS Hash: QmXLaBYop7bGLQ2u...
   Amount: 2,000,000 lovelace (2.00 ADA)
✅ Lock TX submitted!
   TX Hash: d5cd7e06547fa0ea...
   View: https://preprod.cardanoscan.io/transaction/d5cd7e06...
```

*(Mở CardanoScan — show TX)*

> Trên CardanoScan, bạn thấy TX có:
> - **Input**: 1 UTxO từ ví (trả ADA + fees)
> - **Output**: 1 UTxO tại script address, kèm **inline datum** chứa DIDDatum

```bash
# Bước 2: Register
python did_operations.py --action register --tx-hash d5cd7e06547fa0ea...
# ✅ TX: 9af27d30b46727d5...

# Bước 3: Verify (chuyển verified 0→1)
python did_operations.py --action verify --tx-hash 9af27d30b46727d5...
# ✅ TX: 4c21ed16b33ec487...

# Bước 4: Revoke (burn DID)
python did_operations.py --action revoke --tx-hash 4c21ed16b33ec487...
# ✅ TX: 8659b1b24573c484...
```

> Full lifecycle hoàn chỉnh: **Lock → Register → Verify → Revoke**. 4 transactions trên Preprod!

---

## [18:00 – 20:00] 🔑 Tổng kết & Preview

**Nói:**

> Tổng kết Lesson 8 — bài dài nhất nhưng quan trọng nhất:
>
> **3 trap thường gặp:**
> 1. **Int vs Bool** — `verified` phải dùng `int`, không phải `bool`
> 2. **add_input_address()** — quên thêm wallet UTxOs cho fees
> 3. **RawCBOR** — datum từ chain cần `DIDDatum.from_cbor()` trước khi truy cập fields
>
> **CKV Continuing Output:**
> - Register/Update/Verify → output quay lại script
> - Revoke → không output = burn DID
>
> Bây giờ ta đã có off-chain code hoạt động. Nhưng chạy bằng script CLI thì user thường không xài được. Bài tiếp — **Lesson 9** — chúng ta sẽ wrap tất cả thành **REST API** bằng FastAPI, để frontend có thể gọi dễ dàng.
>
> Hẹn gặp ở Lesson 9!

---

*Kết thúc Lesson 8 — ~20 phút*
