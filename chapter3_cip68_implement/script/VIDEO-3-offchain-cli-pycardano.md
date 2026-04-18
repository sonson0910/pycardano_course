# 🎥 VIDEO 2 — Off-chain Scripts (CLI với PyCardano)

## Tổng quan Video
- **Thời lượng ước tính:** 90–120 phút  
- **Mục tiêu:** Viết hoàn chỉnh off-chain scripts bằng PyCardano để mint, update metadata, burn CIP-68 NFT qua CLI  
- **Điều kiện tiên quyết:** Đã có `plutus.json` từ Video 1, đã cài Python 3.10+, có Blockfrost API key  
- **Cấu trúc files sẽ tạo:**
  ```
  .env
  requirements.txt
  offchain/
    __init__.py
    cip68_utils.py        ← Utilities & data types
    cip68_operations.py   ← Mint/Update/Burn logic
  demo_mint.py            ← CLI script mint
  demo_update.py          ← CLI script update
  demo_burn.py            ← CLI script burn
  ```

---

## PHẦN 1: THIẾT LẬP MÔI TRƯỜNG DỰ ÁN

### Bước 1.1 — Tạo cấu trúc thư mục dự án

**Mục tiêu:** Tạo project Python với cấu trúc module.

**Hành động code:**
```bash
mkdir offchain
```

**Nội dung giảng:**
> "Từ thư mục gốc dự án (nơi chứa folder `smart_contract/`), ta tạo folder `offchain/` — chứa toàn bộ logic tương tác với blockchain. Tách code thành 2 file: `cip68_utils.py` (tiện ích, data types) và `cip68_operations.py` (các hàm chính mint/update/burn)."

---

### Bước 1.2 — Tạo `requirements.txt`

**Mục tiêu:** Khai báo dependencies Python.

**Hành động code:** Tạo file `requirements.txt`:
```
pycardano>=0.11.0
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
python-dotenv>=1.0.0
pydantic>=2.0.0
cbor2>=5.6.0
```

**Nội dung giảng:**
> "Dependencies chính:
> - `pycardano` — thư viện Python cho Cardano, build/sign transactions
> - `python-dotenv` — đọc biến môi trường từ file `.env`
> - `fastapi`, `uvicorn` — cho backend API (sẽ dùng ở Video 3)
> - `cbor2` — serialize/deserialize CBOR (PyCardano dùng internally)"

**Hành động code tiếp:**
```bash
pip install -r requirements.txt
```

---

### Bước 1.3 — Tạo file `.env`

**Mục tiêu:** Cấu hình biến môi trường (seed phrase, Blockfrost).

**Hành động code:** Tạo file `.env`:
```env
SEED_PHRASE=your 24 word mnemonic seed phrase here
NETWORK=Preprod
BLOCKFROST_URL=https://cardano-preprod.blockfrost.io/api
BLOCKFROST_API_KEY=your_blockfrost_api_key
```

**Nội dung giảng:**
> "File `.env` chứa thông tin nhạy cảm — KHÔNG commit lên git. Cần 4 biến:
> - `SEED_PHRASE` — 24 từ mnemonic, dùng derive ra payment key + stake key
> - `NETWORK` — Preprod (testnet) hoặc Mainnet
> - `BLOCKFROST_URL` — endpoint API Blockfrost
> - `BLOCKFROST_API_KEY` — key từ blockfrost.io (đăng ký miễn phí)
> 
> Nhớ tạo ví testnet và nhận test ADA từ faucet trước khi tiếp tục."

**Lỗi thường gặp:**
- Quên dấu cách giữa các từ trong seed phrase
- Dùng API key Mainnet với URL Preprod → connection error
- File `.env` có dấu `"` bao quanh giá trị → một số parser đọc sai

---

## PHẦN 2: FILE `cip68_utils.py` — Utility & Data Types

### Bước 2.1 — Tạo file và import thư viện

**Mục tiêu:** Khởi tạo utils module, import tất cả cần thiết từ PyCardano.

**Hành động code:** Tạo file `offchain/cip68_utils.py`:
```python
"""
CIP-68 Dynamic Asset - Off-chain Utilities
==========================================
Cung cấp các utility functions để tương tác với CIP-68 smart contract.

CIP-68 Standard:
- Reference Token (100): Prefix 0x000643b0 - lưu trữ metadata on-chain
- User Token (222): Prefix 0x000de140 - token người dùng sở hữu

SIMPLIFIED VERSION - Không có parameterized scripts
- Policy ID cố định
- Store address cố định
- Owner được lưu trong datum
"""
import json
import os
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union, Tuple

from pycardano import (
    Address,
    TransactionOutput,
    TransactionInput,
    TransactionId,
    PlutusV3Script,
    PlutusData,
    Redeemer,
    RedeemerTag,
    Value,
    MultiAsset,
    Asset,
    AssetName,
    ScriptHash,
    Network,
    UTxO,
    TransactionBuilder,
    RawPlutusData,
    plutus_script_hash,
)
```

**Nội dung giảng:**
> "Import toàn bộ types cần thiết từ `pycardano`. Điểm chú ý:
> - `PlutusV3Script` — đại diện cho compiled script (bytecode)
> - `PlutusData` — base class cho datum/redeemer
> - `plutus_script_hash` — hàm tính hash (policy ID) từ script
> - `AssetName`, `MultiAsset`, `Asset` — tạo native tokens
> 
> Decorator `@dataclass` của Python kết hợp với `PlutusData` cho phép ta định nghĩa datum/redeemer giống y Aiken types."

---

### Bước 2.2 — Định nghĩa CIP-68 Prefix constants

**Mục tiêu:** Khai báo các hằng số prefix cho reference token và user token.

**Hành động code:** Thêm tiếp:
```python
# CIP-68 Asset Label Prefixes (as bytes)
CIP68_REFERENCE_PREFIX = bytes.fromhex("000643b0")  # Label 100
CIP68_USER_PREFIX = bytes.fromhex("000de140")       # Label 222
```

**Nội dung giảng:**
> "Hai hằng số này PHẢI khớp với prefix trong smart contract Aiken. `000643b0` là label 100 (Reference Token), `000de140` là label 222 (User Token). Dùng `bytes.fromhex()` để convert hex string thành bytes."

**Giải thích CIP-68:**
> Giá trị prefix này là chuẩn CIP-68, KHÔNG được thay đổi. Trên chain, asset name của reference token sẽ là `000643b0` + tên token (dạng bytes), user token là `000de140` + tên token.

---

### Bước 2.3 — Định nghĩa Redeemer types (MintToken, BurnToken)

**Mục tiêu:** Map Aiken `MintRedeemer` sang Python PlutusData.

**Hành động code:**
```python
@dataclass
class MintToken(PlutusData):
    """
    Redeemer for minting CIP-68 tokens.
    Constructor ID = 0
    """
    CONSTR_ID = 0
    token_name: bytes


@dataclass
class BurnToken(PlutusData):
    """
    Redeemer for burning CIP-68 tokens.
    Constructor ID = 1
    """
    CONSTR_ID = 1
    token_name: bytes
```

**Nội dung giảng:**
> "Trong Aiken, `MintRedeemer` có 2 variant: `MintToken` (constructor 0) và `BurnToken` (constructor 1). Ở Python, mỗi variant là một class riêng kế thừa `PlutusData`.
> 
> **Quy tắc mapping quan trọng:**
> - `CONSTR_ID = 0` → tương ứng constructor đầu tiên trong Aiken
> - `CONSTR_ID = 1` → constructor thứ hai
> - Thứ tự fields phải GIỐNG Y Aiken
> - `bytes` trong Python = `ByteArray` trong Aiken
> 
> Khi PyCardano serialize `MintToken(token_name=b'MyNFT')` thành CBOR, nó sẽ match đúng cấu trúc mà smart contract expect."

**Lỗi thường gặp:**
- Sai `CONSTR_ID` → contract nhận sai redeemer → fail
- Dùng `str` thay vì `bytes` cho `token_name` → serialize sai kiểu

---

### Bước 2.4 — Định nghĩa SpendRedeemer types

**Mục tiêu:** Map Aiken `SpendRedeemer` sang Python.

**Hành động code:**
```python
@dataclass
class UpdateMetadata(PlutusData):
    """
    Redeemer for updating metadata in spending validator.
    Constructor ID = 0
    """
    CONSTR_ID = 0


@dataclass
class BurnReference(PlutusData):
    """
    Redeemer for burning reference token in spending validator.
    Constructor ID = 1
    """
    CONSTR_ID = 1
```

**Nội dung giảng:**
> "`UpdateMetadata` và `BurnReference` không có field nào — đây là 'empty constructors'. `CONSTR_ID` vẫn quan trọng: UpdateMetadata = 0, BurnReference = 1 — đúng thứ tự khai báo trong Aiken."

---

### Bước 2.5 — Định nghĩa `CIP68Datum`

**Mục tiêu:** Map Aiken `CIP68Datum` sang Python — trung tâm của toàn bộ hệ thống.

**Hành động code:**
```python
@dataclass
class CIP68Datum(PlutusData):
    """
    Datum chứa metadata của CIP-68 NFT.
    Theo CIP-68 standard với đầy đủ thông tin để xác định token.
    
    Fields:
        policy_id: Policy ID của token (28 bytes)
        asset_name: Tên asset không có prefix
        owner: Public key hash của owner (28 bytes)
        metadata: Key-value pairs cho metadata
        version: Phiên bản metadata
    """
    CONSTR_ID = 0
    policy_id: bytes          # Policy ID (28 bytes)
    asset_name: bytes         # Asset name (không có prefix)
    owner: bytes              # Owner public key hash (28 bytes)
    metadata: Dict[bytes, Any]  # Key-value pairs cho metadata
    version: int
```

**Nội dung giảng:**
> "Đây là type quan trọng nhất — `CIP68Datum` match 1:1 với datum trong Aiken:
> 
> | Aiken              | Python              | Giải thích                |
> |---------------------|---------------------|---------------------------|
> | `policy_id: ByteArray` | `policy_id: bytes` | 28 bytes policy ID     |
> | `asset_name: ByteArray` | `asset_name: bytes` | Tên token gốc         |
> | `owner: ByteArray`    | `owner: bytes`      | Public key hash 28 bytes |
> | `metadata: Data`      | `metadata: Dict[bytes, Any]` | Map key-value   |
> | `version: Int`        | `version: int`      | Số phiên bản            |
> 
> **Chú ý đặc biệt:** `metadata` trong Aiken là generic `Data`, trong Python map thành `Dict[bytes, Any]`. PyCardano sẽ serialize dictionary thành Plutus Map — đúng format on-chain. serialize (chuyển đổi)
> 
> Thứ tự fields PHẢI giống y Aiken. Nếu đảo thứ tự → serialize sai → contract reject."

**Lỗi thường gặp:**
- Đảo thứ tự fields → datum serialize sai hoàn toàn
- Dùng `Dict[str, str]` thay vì `Dict[bytes, Any]` → Plutus chỉ hiểu bytes keys

---

### Bước 2.6 — Hàm load scripts từ `plutus.json`

**Mục tiêu:** Hàm đọc compiled code từ blueprint.

**Hành động code:**
```python
def load_scripts(blueprint_path: str) -> Dict[str, Any]:
    """
    Load compiled scripts từ plutus.json blueprint.
    """
    with open(blueprint_path, 'r', encoding='utf-8') as f:
        blueprint = json.load(f)
    
    scripts = {}
    for validator in blueprint['validators']:
        title = validator['title']
        scripts[title] = {
            'compiled_code': validator['compiledCode'],
            'hash': validator['hash'],
        }
    
    return scripts


def load_mint_script(blueprint_path: str) -> PlutusV3Script:
    """
    Load minting policy script từ blueprint.
    Script không có parameters - policy ID cố định.
    """
    scripts = load_scripts(blueprint_path)
    mint_info = scripts['cip68.cip68_mint.mint']
    return PlutusV3Script(bytes.fromhex(mint_info['compiled_code']))


def load_store_script(blueprint_path: str) -> PlutusV3Script:
    """
    Load spending validator script từ blueprint.
    Script không có parameters - store address cố định.
    """
    scripts = load_scripts(blueprint_path)
    store_info = scripts['cip68.cip68_store.spend']
    return PlutusV3Script(bytes.fromhex(store_info['compiled_code']))
```

**Nội dung giảng:**
> "Ba hàm load scripts:
> 
> 1. `load_scripts()` — đọc file `plutus.json`, parse JSON, lấy compiledCode và hash cho mỗi validator
> 2. `load_mint_script()` — lấy bytecode của minting policy, wrap thành `PlutusV3Script`
> 3. `load_store_script()` — tương tự cho spending validator
> 
> Key name trong blueprint: `'cip68.cip68_mint.mint'` = `tên_file.tên_validator.hàm`. Phải khớp chính xác.
> 
> `PlutusV3Script(bytes.fromhex(...))` — convert hex string thành bytes rồi tạo script object. Object này chứa toàn bộ bytecode sẽ gửi lên chain."

**Lỗi thường gặp:**
- Key name sai (ví dụ thiếu `.mint` suffix) → KeyError
- File path sai → FileNotFoundError

---

### Bước 2.7 — Hàm `get_policy_id` và `get_script_address`

**Mục tiêu:** Tính Policy ID và script address từ script object.

**Hành động code:**
```python
def get_policy_id(mint_script: PlutusV3Script) -> ScriptHash:
    """Lấy policy ID từ minting script."""
    return plutus_script_hash(mint_script)


def get_script_address(script: PlutusV3Script, network: Network) -> Address:
    """Lấy address của script."""
    script_hash = plutus_script_hash(script)
    return Address(script_hash, network=network)


def extract_owner_from_datum(datum: CIP68Datum) -> bytes:
    """Extract owner public key hash từ CIP68Datum."""
    return datum.owner
```

**Nội dung giảng:**
> "Từ script bytecode, ta tính ra hash:
> - `plutus_script_hash(mint_script)` → Policy ID (28 bytes hex). Đây là identity của tất cả tokens mint từ script này.
> - `Address(script_hash, network=network)` → script address trên network (Preprod hoặc Mainnet). Reference token sẽ sống ở address này.
> 
> `extract_owner_from_datum` — helper đơn giản, chỉ lấy field `owner` từ datum."

---

### Bước 2.8 — Hàm `create_cip68_asset_names`

**Mục tiêu:** Tạo cặp asset name (ref + user) từ tên gốc.

**Hành động code:**
```python
def create_cip68_asset_names(token_name: str | bytes) -> Tuple[AssetName, AssetName]:
    """
    Tạo asset names cho CIP-68 reference và user tokens.
    """
    if isinstance(token_name, str):
        token_name_bytes = token_name.encode('utf-8')
    else:
        token_name_bytes = token_name
    
    ref_name = AssetName(CIP68_REFERENCE_PREFIX + token_name_bytes)
    user_name = AssetName(CIP68_USER_PREFIX + token_name_bytes)
    return ref_name, user_name
```

**Nội dung giảng:**
> "Hàm này nhận tên token gốc (string hoặc bytes), nối với prefix tương ứng, trả về 2 `AssetName`:
> - `AssetName(000643b0 + b'MyNFT')` → reference asset name
> - `AssetName(000de140 + b'MyNFT')` → user asset name
> 
> `AssetName` là type wrapper của PyCardano cho asset_name. Nó lưu raw bytes bên trong."

---

### Bước 2.9 — Hàm `create_cip68_metadata` và `create_cip68_datum`

**Mục tiêu:** Build metadata dictionary và CIP68Datum object.

**Hành động code:**
```python
def create_cip68_metadata(description: str, extra_fields: Optional[Dict[str, Any]] = None) -> Dict[bytes, Any]:
    """Tạo metadata dictionary cho CIP-68 datum."""
    metadata = {
        b"description": description.encode('utf-8')
    }
    
    if extra_fields:
        for key, value in extra_fields.items():
            if isinstance(value, str):
                metadata[key.encode('utf-8')] = value.encode('utf-8')
            else:
                metadata[key.encode('utf-8')] = value
    
    return metadata


def create_cip68_datum(
    policy_id: bytes,
    asset_name: bytes,
    owner_pkh: bytes,
    metadata: Union[str, Dict[str, Any]], 
    version: int = 1
) -> CIP68Datum:
    """
    Tạo CIP68Datum với đầy đủ thông tin.
    """
    if isinstance(metadata, str):
        metadata_dict = create_cip68_metadata(metadata)
    elif isinstance(metadata, dict):
        metadata_dict = {}
        for key, value in metadata.items():
            key_bytes = key.encode('utf-8') if isinstance(key, str) else key
            value_bytes = value.encode('utf-8') if isinstance(value, str) else value
            metadata_dict[key_bytes] = value_bytes
    else:
        metadata_dict = metadata
    
    return CIP68Datum(
        policy_id=policy_id,
        asset_name=asset_name,
        owner=owner_pkh,
        metadata=metadata_dict,
        version=version
    )
```

**Nội dung giảng:**
> "Hai hàm builder:
> 
> `create_cip68_metadata()` — nhận description string, tạo `Dict[bytes, bytes]`:
> - Key `b'description'` → value là description encode UTF-8
> - Có thể thêm extra fields (name, image, v.v.)
> - **Tất cả keys và values phải là bytes** — Plutus Map trên chain chỉ hiểu bytes
> 
> `create_cip68_datum()` — nhận đầy đủ 5 fields, trả về `CIP68Datum` object. Hàm này flexible: metadata có thể là string (auto tạo dict) hoặc dict có sẵn.
> 
> Object `CIP68Datum(...)` sẽ được PyCardano serialize thành Plutus Data khi gắn vào transaction output."

**Lỗi thường gặp:**
- Truyền string keys cho metadata dict → Plutus không deserialize được trên chain
- Quên encode UTF-8 → bytes literal vs string literal confusion

---

### Bước 2.10 — Tạo `offchain/__init__.py`

**Mục tiêu:** Export tất cả symbols cho package.

**Hành động code:** Tạo file `offchain/__init__.py`:
```python
"""
CIP-68 Offchain Package
=======================
Package chứa các module để tương tác với CIP-68 smart contract.

SIMPLIFIED VERSION: Non-parameterized contracts
"""

from .cip68_utils import (
    CIP68_REFERENCE_PREFIX,
    CIP68_USER_PREFIX,
    MintToken,
    BurnToken,
    UpdateMetadata,
    BurnReference,
    CIP68Datum,
    create_cip68_asset_names,
    create_cip68_metadata,
    create_cip68_datum,
    get_policy_id,
    get_script_address,
    load_mint_script,
    load_store_script,
    extract_owner_from_datum,
)

from .cip68_operations import (
    get_chain_context,
    get_wallet_from_seed,
    get_network,
    get_scripts,
    mint_cip68_token,
    update_metadata,
    burn_cip68_token,
    get_cip68_metadata,
    list_all_tokens,
)
```

**Nội dung giảng:**
> "File `__init__.py` biến folder `offchain/` thành Python package và export tất cả public functions. Giúp import ngắn gọn: `from offchain import mint_cip68_token`."

---

## PHẦN 3: FILE `cip68_operations.py` — Logic Chính

### Bước 3.1 — Imports và setup

**Mục tiêu:** Tạo file operations chính, import dependencies.

**Hành động code:** Tạo file `offchain/cip68_operations.py`:
```python
"""
CIP-68 Dynamic Asset - Main Off-chain Operations
================================================
Cung cấp các hàm chính để mint, update metadata, và burn CIP-68 tokens.
Sử dụng PyCardano để xây dựng transactions.

SIMPLIFIED VERSION: Non-parameterized contracts
"""

import os
import json
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

from pycardano import (
    BlockFrostChainContext,
    Network,
    Address,
    TransactionBuilder,
    TransactionOutput,
    TransactionInput,
    TransactionId,
    PlutusV3Script,
    PlutusData,
    Redeemer,
    RedeemerTag,
    Value,
    MultiAsset,
    Asset,
    AssetName,
    ScriptHash,
    UTxO,
    PaymentSigningKey,
    PaymentVerificationKey,
    StakeSigningKey,
    StakeVerificationKey,
    Transaction,
    HDWallet,
    plutus_script_hash,
    min_lovelace,
)

from .cip68_utils import (
    CIP68_REFERENCE_PREFIX,
    CIP68_USER_PREFIX,
    MintToken,
    BurnToken,
    UpdateMetadata,
    BurnReference,
    CIP68Datum,
    create_cip68_asset_names,
    create_cip68_metadata,
    create_cip68_datum,
    get_policy_id,
    get_script_address,
    load_mint_script,
    load_store_script,
    extract_owner_from_datum,
)

load_dotenv()
```

**Nội dung giảng:**
> "File `cip68_operations.py` chứa business logic: build transaction, submit lên chain. Import 2 nhóm:
> - PyCardano types: `TransactionBuilder`, `HDWallet`, `BlockFrostChainContext`, v.v.
> - Utils từ module vừa tạo: data types, helper functions"

---

### Bước 3.2 — Hàm `get_chain_context`

**Mục tiêu:** Kết nối Blockfrost để query blockchain.

**Hành động code:**
```python
def get_chain_context() -> BlockFrostChainContext:
    """Tạo BlockFrost chain context từ environment variables."""
    network_str = os.getenv("NETWORK", "Preprod")
    blockfrost_url = os.getenv("BLOCKFROST_URL")
    blockfrost_key = os.getenv("BLOCKFROST_API_KEY")
    
    network = Network.TESTNET if network_str.lower() == "preprod" else Network.MAINNET
    
    return BlockFrostChainContext(
        project_id=blockfrost_key,
        base_url=blockfrost_url,
        network=network
    )
```

**Nội dung giảng:**
> "`BlockFrostChainContext` là cổng kết nối tới blockchain qua Blockfrost API. Nó cho phép PyCardano:
> - Query UTxOs tại một address
> - Lấy protocol parameters (fee, min ADA, v.v.)
> - Submit transaction
> 
> Mọi thao tác blockchain đều cần context này."

---

### Bước 3.3 — Hàm `get_wallet_from_seed`

**Mục tiêu:** Derive keys và address từ seed phrase.

**Hành động code:**
```python
def get_wallet_from_seed(seed_phrase: str) -> tuple:
    """
    Tạo wallet từ seed phrase.
    Returns: Tuple (payment_skey, payment_vkey, stake_skey, stake_vkey, address)
    """
    hdwallet = HDWallet.from_mnemonic(seed_phrase)
    
    # Derive keys
    hdwallet_spend = hdwallet.derive_from_path("m/1852'/1815'/0'/0/0")
    hdwallet_stake = hdwallet.derive_from_path("m/1852'/1815'/0'/2/0")
    
    payment_skey = PaymentSigningKey(hdwallet_spend.xprivate_key[:32])
    payment_vkey = PaymentVerificationKey.from_signing_key(payment_skey)
    
    stake_skey = StakeSigningKey(hdwallet_stake.xprivate_key[:32])
    stake_vkey = StakeVerificationKey.from_signing_key(stake_skey)
    
    network_str = os.getenv("NETWORK", "Preprod")
    network = Network.TESTNET if network_str.lower() == "preprod" else Network.MAINNET
    
    address = Address(payment_vkey.hash(), stake_vkey.hash(), network=network)
    
    return payment_skey, payment_vkey, stake_skey, stake_vkey, address
```

**Nội dung giảng:**
> "Từ 24 từ mnemonic, derive ra keys theo chuẩn CIP-1852 (Shelley HD Wallet):
> 
> **Payment key path:** `m/1852'/1815'/0'/0/0`
> - 1852 = purpose (Shelley)
> - 1815 = coin type (ADA birth year)
> - 0 = account index
> - 0/0 = external chain, first address
> 
> **Stake key path:** `m/1852'/1815'/0'/2/0`
> - 2/0 = staking chain
> 
> `xprivate_key[:32]` — lấy 32 bytes đầu của extended private key → signing key.
> 
> `Address(payment_vkey.hash(), stake_vkey.hash(), network=network)` — tạo base address (có cả payment + stake part) cho đúng network."

**Lỗi thường gặp:**
- Seed phrase sai → `ValueError`
- Nhầm path `0/0` (external) vs `1/0` (internal/change) → address khác

---

### Bước 3.4 — Hàm `get_scripts` (helper load tất cả)

**Mục tiêu:** Convenience function load cả 2 scripts + policy ID + store address.

**Hành động code:**
```python
def get_network() -> Network:
    """Get network from environment."""
    network_str = os.getenv("NETWORK", "Preprod")
    return Network.TESTNET if network_str.lower() == "preprod" else Network.MAINNET


def get_scripts(blueprint_path: str = None) -> tuple:
    """
    Load mint and store scripts from blueprint.
    Returns: Tuple (mint_script, store_script, policy_id, store_address)
    """
    if blueprint_path is None:
        blueprint_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "smart_contract",
            "plutus.json"
        )
    
    mint_script = load_mint_script(blueprint_path)
    store_script = load_store_script(blueprint_path)
    
    policy_id = get_policy_id(mint_script)
    network = get_network()
    store_address = get_script_address(store_script, network)
    
    return mint_script, store_script, policy_id, store_address
```

**Nội dung giảng:**
> "`get_scripts()` là helper gom tất cả: load 2 scripts, tính policy ID, tính store address. Trả về tuple 4 giá trị. Nếu không truyền path, tự tìm `smart_contract/plutus.json` từ vị trí file."

---

### Bước 3.5 — Hàm `mint_cip68_token` (Phần 1: Setup)

**Mục tiêu:** Bắt đầu viết hàm mint — phần chuẩn bị dữ liệu.

**Hành động code:**
```python
def mint_cip68_token(
    context: BlockFrostChainContext,
    payment_skey: PaymentSigningKey,
    payment_vkey: PaymentVerificationKey,
    owner_address: Address,
    token_name: str,
    description: str,
    blueprint_path: str = None,
) -> dict:
    """Mint một CIP-68 Dynamic NFT."""
    network = get_network()
    
    # Load scripts
    mint_script, store_script, policy_id, store_address = get_scripts(blueprint_path)
    
    # Get owner's public key hash
    owner_pkh = bytes(payment_vkey.hash())
    
    # Tạo asset names theo CIP-68
    token_name_bytes = token_name.encode('utf-8')
    ref_asset_name, user_asset_name = create_cip68_asset_names(token_name_bytes)
    
    # Policy ID as bytes for datum
    policy_id_bytes = bytes(policy_id)
    
    # Tạo CIP68 Datum
    datum = create_cip68_datum(
        policy_id=policy_id_bytes,
        asset_name=token_name_bytes,
        owner_pkh=owner_pkh,
        metadata=description,
        version=1
    )
```

**Nội dung giảng:**
> "Hàm `mint_cip68_token` — trái tim của off-chain mint logic. Phần setup:
> 
> 1. **Load scripts** — lấy bytecode, policy ID, store address
> 2. **Owner PKH** — `bytes(payment_vkey.hash())` lấy 28 bytes public key hash. Đây sẽ ghi vào datum.
> 3. **Asset names** — tạo cặp ref + user asset name
> 4. **Datum** — tạo CIP68Datum với policy_id, asset_name, owner, metadata (description), version=1
> 
> Datum này sẽ gắn vào UTxO tại script address — chính là metadata on-chain."

---

### Bước 3.6 — Hàm `mint_cip68_token` (Phần 2: Build Transaction)

**Mục tiêu:** Xây dựng transaction body: mint, outputs, sign, submit.

**Hành động code:**
```python
    # Tạo MultiAsset cho minting
    mint_asset = Asset()
    mint_asset[ref_asset_name] = 1   # Reference token
    mint_asset[user_asset_name] = 1  # User token
    
    mint_assets = MultiAsset()
    mint_assets[policy_id] = mint_asset
    
    # Tạo redeemer
    redeemer = Redeemer(MintToken(token_name=token_name_bytes))
    
    # Tính reference token output value
    ref_asset = Asset()
    ref_asset[ref_asset_name] = 1
    ref_multi = MultiAsset()
    ref_multi[policy_id] = ref_asset
    ref_value = Value(2_000_000, ref_multi)
    
    # Build transaction
    builder = TransactionBuilder(context)
    builder.add_input_address(owner_address)
    
    # Mint tokens
    builder.mint = mint_assets
    builder.add_minting_script(mint_script, redeemer=redeemer)
    
    # Output: Reference token đến store script với datum
    builder.add_output(
        TransactionOutput(
            store_address,
            ref_value,
            datum=datum,
        )
    )
    
    # Output: User token đến owner
    user_asset = Asset()
    user_asset[user_asset_name] = 1
    user_multi = MultiAsset()
    user_multi[policy_id] = user_asset
    user_value = Value(2_000_000, user_multi)
    builder.add_output(
        TransactionOutput(
            owner_address,
            user_value,
        )
    )
    
    # Required signers
    builder.required_signers = [payment_vkey.hash()]
    
    # Build and sign
    signed_tx = builder.build_and_sign(
        signing_keys=[payment_skey],
        change_address=owner_address
    )
    
    # Submit
    tx_hash = context.submit_tx(signed_tx)
    print(f"Transaction submitted: {tx_hash}")
    
    return {
        "tx_hash": str(tx_hash),
        "policy_id": policy_id,
        "token_name": token_name,
        "ref_asset_name": ref_asset_name.payload.hex(),
        "user_asset_name": user_asset_name.payload.hex(),
        "store_address": str(store_address),
    }
```

**Nội dung giảng:**
> "Build transaction theo 7 bước:
> 
> **1. MultiAsset cho minting:**
> - Tạo `Asset()` dict → set ref=1, user=1
> - Wrap vào `MultiAsset()` với policy_id làm key
> 
> **2. Redeemer:**
> - `Redeemer(MintToken(token_name=...))` — tell contract: tôi muốn MINT token này
> 
> **3. Reference token output:**
> - `Value(2_000_000, ref_multi)` — 2 ADA + 1 ref token
> - `TransactionOutput(store_address, ref_value, datum=datum)` — gửi đến SCRIPT ADDRESS kèm DATUM
> - **Đây là output quan trọng nhất**: ref token + datum sẽ sống ở script address
> 
> **4. User token output:**
> - `TransactionOutput(owner_address, user_value)` — gửi user token về VÍ OWNER
> - Không cần datum
> 
> **5. Required signers:**
> - `builder.required_signers = [payment_vkey.hash()]` — populate `tx.extra_signatories` field
> - Smart contract check field này để verify owner
> 
> **6. Build & Sign:**
> - `build_and_sign()` tự tính fee, tự chọn UTxO input, tự tạo change output
> 
> **7. Submit:**
> - `context.submit_tx(signed_tx)` — gửi lên blockchain qua Blockfrost"

**Giải thích CIP-68 tương tác:**
> Transaction này tạo ra 2 outputs:
> - Output 1: Script address chứa ref token + inline datum → METADATA ON-CHAIN
> - Output 2: Owner address chứa user token → PROOF OF OWNERSHIP
> 
> Bất kỳ ai query script address đều đọc được metadata. Chỉ owner (có user token + ký) mới update/burn.

**Lỗi thường gặp:**
- Gửi ref token đến owner thay vì script → metadata không on-chain
- Quên `datum=datum` trong TransactionOutput → contract reject (datum required)
- Value quá nhỏ (< min ADA) → transaction fail
- Quên `required_signers` → contract không thấy owner ký

---

### Bước 3.7 — Hàm `update_metadata`

**Mục tiêu:** Viết logic update metadata — spend ref token UTxO, thay datum mới, trả lại script.

**Hành động code:**
```python
def update_metadata(
    context: BlockFrostChainContext,
    payment_skey: PaymentSigningKey,
    payment_vkey: PaymentVerificationKey,
    owner_address: Address,
    token_name: str,
    new_description: str,
    blueprint_path: str = None,
) -> dict:
    """Update metadata của một CIP-68 NFT."""
    network = get_network()
    
    # Load scripts
    mint_script, store_script, policy_id, store_address = get_scripts(blueprint_path)
    
    # Get owner's public key hash for verification
    owner_pkh = bytes(payment_vkey.hash())
    
    # Policy ID as bytes
    policy_id_bytes = bytes(policy_id)
    
    # Tạo asset name cho reference token
    token_name_bytes = token_name.encode('utf-8')
    ref_asset_name = AssetName(CIP68_REFERENCE_PREFIX + token_name_bytes)
    
    # Tìm UTxO chứa reference token
    utxos = context.utxos(store_address)
    ref_utxo = None
    for utxo in utxos:
        if utxo.output.amount.multi_asset:
            for pid, assets in utxo.output.amount.multi_asset.items():
                if pid == policy_id and ref_asset_name in assets:
                    ref_utxo = utxo
                    break
    
    if not ref_utxo:
        raise ValueError("Không tìm thấy reference token UTxO!")
    
    # Parse current datum and verify owner
    current_datum = ref_utxo.output.datum
    if isinstance(current_datum, CIP68Datum):
        current_owner = extract_owner_from_datum(current_datum)
        if current_owner != owner_pkh:
            raise ValueError("Bạn không phải owner của NFT này!")
        new_version = current_datum.version + 1
    else:
        new_version = 2
    
    # Tạo datum mới - giữ nguyên policy_id, asset_name, owner
    new_datum = create_cip68_datum(
        policy_id=policy_id_bytes,
        asset_name=token_name_bytes,
        owner_pkh=owner_pkh,
        metadata=new_description,
        version=new_version
    )
    
    # Tạo redeemer cho spending
    redeemer = Redeemer(UpdateMetadata())
    
    # Build transaction
    builder = TransactionBuilder(context)
    builder.add_input_address(owner_address)
    
    # Spend reference token UTxO
    builder.add_script_input(
        ref_utxo,
        store_script,
        redeemer=redeemer
    )
    
    # Output: Reference token trở lại store script với datum mới
    ref_asset = Asset()
    ref_asset[ref_asset_name] = 1
    ref_multi = MultiAsset()
    ref_multi[policy_id] = ref_asset
    ref_value = Value(
        ref_utxo.output.amount.coin,
        ref_multi
    )
    builder.add_output(
        TransactionOutput(
            store_address,
            ref_value,
            datum=new_datum,
        )
    )
    
    # Required signers
    builder.required_signers = [payment_vkey.hash()]
    
    # Build and sign
    signed_tx = builder.build_and_sign(
        signing_keys=[payment_skey],
        change_address=owner_address
    )
    
    # Submit
    tx_hash = context.submit_tx(signed_tx)
    print(f"Update transaction submitted: {tx_hash}")
    
    return {
        "tx_hash": str(tx_hash),
        "policy_id": policy_id,
        "token_name": token_name,
        "new_version": new_version,
    }
```

**Nội dung giảng:**
> "Update metadata — thao tác phức tạp nhất, gồm 6 bước chính:
> 
> **1. Tìm reference token UTxO:** Query tất cả UTxOs ở store_address, tìm cái chứa đúng ref token (cùng policy_id, cùng asset_name). Đây là UTxO sẽ bị 'spend'.
> 
> **2. Verify owner:** Parse datum hiện tại, so sánh `owner` field với PKH đang ký. Nếu không match → reject off-chain luôn (không cần gửi transaction lỗi lên chain).
> 
> **3. Tạo datum mới:** Giữ nguyên `policy_id`, `asset_name`, `owner` — chỉ thay `metadata` và tăng `version`. Đây là quy tắc bất biến mà smart contract enforce.
> 
> **4. `add_script_input`:** Khác với `add_input`. Khi spend UTxO từ script, cần truyền:
>    - `ref_utxo` — UTxO đang spend
>    - `store_script` — bytecode script (để node verify)
>    - `redeemer` — UpdateMetadata
> 
> **5. Output trả lại script:** Ref token PHẢI quay về CÙNG script address, với datum MỚI. Value giữ nguyên ADA amount (`ref_utxo.output.amount.coin`).
> 
> **6. Build, sign, submit** — giống mint."

**Giải thích CIP-68 tương tác:**
> Flow on-chain: `spend old UTxO (ref token + old datum)` → `create new UTxO (ref token + new datum)` tại cùng script address. Smart contract verify: ref token present, same address, identity fields unchanged.

**Lỗi thường gặp:**
- Quên include `store_script` trong `add_script_input` → node không verify được
- Gửi ref token đến address khác → smart contract reject
- Thay đổi owner trong datum → smart contract reject
- Collateral không đủ → transation build fail (PyCardano tự handle nếu có UTxO ADA thuần)

---

### Bước 3.8 — Hàm `burn_cip68_token`

**Mục tiêu:** Burn cả reference token và user token trong 1 transaction.

**Hành động code:**
```python
def burn_cip68_token(
    context: BlockFrostChainContext,
    payment_skey: PaymentSigningKey,
    payment_vkey: PaymentVerificationKey,
    owner_address: Address,
    token_name: str,
    blueprint_path: str = None,
) -> dict:
    """Burn một CIP-68 NFT (cả reference token và user token)."""
    network = get_network()
    
    # Load scripts
    mint_script, store_script, policy_id, store_address = get_scripts(blueprint_path)
    
    # Get owner's public key hash
    owner_pkh = bytes(payment_vkey.hash())
    
    # Tạo asset names
    token_name_bytes = token_name.encode('utf-8')
    ref_asset_name, user_asset_name = create_cip68_asset_names(token_name_bytes)
    
    # Tìm UTxO chứa reference token tại store script
    store_utxos = context.utxos(store_address)
    ref_utxo = None
    for utxo in store_utxos:
        if utxo.output.amount.multi_asset:
            for pid, assets in utxo.output.amount.multi_asset.items():
                if pid == policy_id and ref_asset_name in assets:
                    ref_utxo = utxo
                    break
    
    if not ref_utxo:
        raise ValueError("Không tìm thấy reference token UTxO!")
    
    # Verify owner from datum
    current_datum = ref_utxo.output.datum
    if isinstance(current_datum, CIP68Datum):
        current_owner = extract_owner_from_datum(current_datum)
        if current_owner != owner_pkh:
            raise ValueError("Bạn không phải owner của NFT này!")
    
    # Tìm UTxO chứa user token trong ví owner
    owner_utxos = context.utxos(owner_address)
    user_utxo = None
    for utxo in owner_utxos:
        if utxo.output.amount.multi_asset:
            for pid, assets in utxo.output.amount.multi_asset.items():
                if pid == policy_id and user_asset_name in assets:
                    user_utxo = utxo
                    break
    
    if not user_utxo:
        raise ValueError("Không tìm thấy user token UTxO!")
    
    # Tạo MultiAsset cho burning (số âm)
    burn_asset = Asset()
    burn_asset[ref_asset_name] = -1   # Burn reference token
    burn_asset[user_asset_name] = -1  # Burn user token
    
    burn_assets = MultiAsset()
    burn_assets[policy_id] = burn_asset
    
    # Tạo redeemers
    mint_redeemer = Redeemer(BurnToken(token_name=token_name_bytes))
    spend_redeemer = Redeemer(BurnReference())
    
    # Build transaction
    builder = TransactionBuilder(context)
    builder.add_input_address(owner_address)
    
    # Spend reference token UTxO (từ script)
    builder.add_script_input(
        ref_utxo,
        store_script,
        redeemer=spend_redeemer
    )
    
    # Add user token input (từ ví owner)
    builder.add_input(user_utxo)
    
    # Burn tokens
    builder.mint = burn_assets
    builder.add_minting_script(mint_script, redeemer=mint_redeemer)
    
    # Required signers
    builder.required_signers = [payment_vkey.hash()]
    
    # Build and sign
    signed_tx = builder.build_and_sign(
        signing_keys=[payment_skey],
        change_address=owner_address
    )
    
    # Submit
    tx_hash = context.submit_tx(signed_tx)
    print(f"Burn transaction submitted: {tx_hash}")
    
    return {
        "tx_hash": str(tx_hash),
        "policy_id": policy_id,
        "token_name": token_name,
        "burned": True,
    }
```

**Nội dung giảng:**
> "Burn là thao tác cần CẢ HAI validators hoạt động cùng lúc:
> 
> **Tìm 2 UTxOs:**
> 1. Reference token UTxO — ở store script address
> 2. User token UTxO — ở ví owner
> 
> **2 Redeemers trong 1 transaction:**
> - `spend_redeemer = BurnReference()` → cho spending validator
> - `mint_redeemer = BurnToken(...)` → cho minting policy
> 
> **Transaction build:**
> - `add_script_input(ref_utxo, store_script, redeemer=spend_redeemer)` — spend ref token từ script, kèm BurnReference redeemer
> - `add_input(user_utxo)` — spend user token từ ví (input bình thường, không phải script)
> - `builder.mint = burn_assets` — burn -1 ref, -1 user
> - `add_minting_script(mint_script, redeemer=mint_redeemer)` — attach minting script + BurnToken redeemer
> 
> **Kết quả:** Cả 2 token bị destroy, UTxO tại script address bị consume. NFT không còn tồn tại."

**Giải thích CIP-68 tương tác:**
> Hai validators chạy song song:
> - Minting policy check: burn -1 ref + -1 user ✓
> - Spending validator check: owner signed ✓
> Nếu bất kỳ validator nào fail → toàn bộ transaction fail (atomicity).

**Lỗi thường gặp:**
- Quên `add_input(user_utxo)` → user token không nằm trong inputs → minting policy fail
- Chỉ burn 1 trong 2 token → minting policy reject
- User token đã gửi cho người khác → không tìm thấy trong ví

---

### Bước 3.9 — Hàm `list_all_tokens`

**Mục tiêu:** Query blockchain, liệt kê tất cả CIP-68 NFT thuộc user.

**Hành động code:**
```python
def list_all_tokens(
    context: BlockFrostChainContext,
    user_address_str: str
) -> List[Dict[str, Any]]:
    """Lấy danh sách CIP-68 NFT từ ví người dùng và gộp với metadata từ Script."""
    
    network = get_network()
    mint_script, store_script, policy_id, store_address = get_scripts()
    
    user_token_prefix = bytes.fromhex("000de140") 
    ref_token_prefix = bytes.fromhex("000643b0")  

    user_tokens_list = []
    
    # BƯỚC 1: QUÉT VÍ USER — tìm user tokens (222)
    try:
        user_utxos = context.utxos(user_address_str)
    except:
        return []

    holding_token_names = set()

    for utxo in user_utxos:
        if utxo.output.amount.multi_asset:
            for pid, assets in utxo.output.amount.multi_asset.items():
                if pid == policy_id:
                    for asset_name, quantity in assets.items():
                        payload = asset_name.payload
                        if payload.startswith(user_token_prefix) and quantity > 0:
                            real_name_bytes = payload[len(user_token_prefix):]
                            holding_token_names.add(real_name_bytes)

    if not holding_token_names:
        return []

    # BƯỚC 2: TRA CỨU METADATA TỪ STORE SCRIPT
    store_utxos = context.utxos(store_address)
    
    for utxo in store_utxos:
        if utxo.output.amount.multi_asset:
            for pid, assets in utxo.output.amount.multi_asset.items():
                if pid == policy_id:
                    for asset_name in assets.keys():
                        payload = asset_name.payload
                        if payload.startswith(ref_token_prefix):
                            real_name_bytes = payload[len(ref_token_prefix):]
                            
                            if real_name_bytes in holding_token_names:
                                datum = utxo.output.datum
                                token_data = {
                                    "token_name": real_name_bytes.decode("utf-8"),
                                    "policy_id": str(policy_id),
                                    "amount": 1,
                                    "metadata": {}
                                }
                                
                                if isinstance(datum, CIP68Datum):
                                    meta_dict = {}
                                    for k, v in datum.metadata.items():
                                        key = k.decode("utf-8") if isinstance(k, bytes) else str(k)
                                        val = v.decode("utf-8") if isinstance(v, bytes) else str(v)
                                        meta_dict[key] = val
                                        
                                    token_data["metadata"] = meta_dict
                                    token_data["version"] = datum.version
                                
                                user_tokens_list.append(token_data)

    return user_tokens_list
```

**Nội dung giảng:**
> "Liệt kê NFT của user theo 2 bước:
> 
> **Bước 1 — Quét ví user:** Tìm tất cả user tokens (prefix 222) thuộc policy_id của dự án. Cắt prefix để lấy tên gốc.
> 
> **Bước 2 — Cross-reference với store:** Với mỗi tên token user đang giữ, tìm reference token tương ứng tại store address → lấy datum → parse metadata.
> 
> Đây là đặc điểm CIP-68: metadata LUÔN nằm ở script address (ref token), không nằm trong ví user."

---

## PHẦN 4: CLI DEMO SCRIPTS

### Bước 4.1 — Tạo `demo_mint.py`

**Mục tiêu:** Script CLI để demo mint NFT.

**Hành động code:** Tạo file `demo_mint.py` ở root:
```python
#!/usr/bin/env python3
"""Demo Mint CIP-68 Token"""

import os
import sys
import time
import json
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from offchain.cip68_operations import (
    get_chain_context,
    get_wallet_from_seed,
    mint_cip68_token,
)

load_dotenv()


def main():
    print("=" * 60)
    print("DEMO: Mint CIP-68 Dynamic NFT (Simplified)")
    print("=" * 60)
    
    # Load wallet
    seed_phrase = os.getenv("SEED_PHRASE")
    if not seed_phrase:
        print("ERROR: SEED_PHRASE không tìm thấy trong .env")
        return
    
    payment_skey, payment_vkey, stake_skey, stake_vkey, address = get_wallet_from_seed(seed_phrase)
    print(f"\nWallet address: {address}")
    
    # Get chain context
    context = get_chain_context()
    
    # Check balance
    utxos = context.utxos(address)
    total_ada = sum(utxo.output.amount.coin for utxo in utxos) / 1_000_000
    print(f"Balance: {total_ada:.2f} ADA")
    
    if total_ada < 10:
        print("ERROR: Không đủ ADA để mint (cần ít nhất 10 ADA)")
        return
    
    # Token info
    timestamp = int(time.time())
    token_name = f"DemoNFT_{timestamp}"
    description = f"Demo CIP-68 NFT created at {timestamp}"
    
    print(f"\nMinting token:")
    print(f"  Name: {token_name}")
    print(f"  Description: {description}")
    print("-" * 60)
    
    try:
        result = mint_cip68_token(
            context=context,
            payment_skey=payment_skey,
            payment_vkey=payment_vkey,
            owner_address=address,
            token_name=token_name,
            description=description,
        )
        
        print("\n" + "=" * 60)
        print("MINT THÀNH CÔNG!")
        print(f"Transaction Hash: {result['tx_hash']}")
        print(f"Policy ID: {result['policy_id']}")
        print(f"Token Name: {result['token_name']}")
        print(f"Store Address: {result['store_address']}")
        print("=" * 60)
        
        print(f"\nXem transaction tại:")
        print(f"https://preprod.cardanoscan.io/transaction/{result['tx_hash']}")
        
        # Save token info for later use
        token_info = {
            "tx_hash": result['tx_hash'],
            "policy_id": result['policy_id'],
            "token_name": token_name,
            "description": description,
            "timestamp": timestamp,
        }
        
        with open(f"minted_{token_name}.json", "w") as f:
            json.dump(token_info, f, indent=2)
        print(f"\nToken info saved to: minted_{token_name}.json")
        
    except Exception as e:
        print(f"\nLỗi: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
```

**Nội dung giảng:**
> "Script demo mint:
> 1. Load seed phrase → derive wallet
> 2. Check balance (cần >= 10 ADA)
> 3. Tạo token name unique bằng timestamp
> 4. Gọi `mint_cip68_token()` — tất cả logic đã nằm trong module
> 5. In kết quả + link xem trên CardanoScan
> 6. Lưu info vào JSON file để dùng cho update/burn sau
> 
> Chạy: `python demo_mint.py`
> 
> Sau khi submit, chờ ~20 giây để transaction confirm trên Preprod."

**Lỗi thường gặp:**
- Balance không đủ → nhận test ADA từ faucet.cardano-testnet.iohkdev.io
- Transaction đã submit nhưng fail on-chain → check CardanoScan error tab

---

### Bước 4.2 — Tạo `demo_update.py`

**Mục tiêu:** Script CLI để update metadata.

**Hành động code:** Tạo file `demo_update.py`:
```python
#!/usr/bin/env python3
"""Demo Update CIP-68 Token Metadata"""

import os
import sys
import time
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from offchain.cip68_operations import (
    get_chain_context,
    get_wallet_from_seed,
    update_metadata,
    list_all_tokens,
)

load_dotenv()


def main():
    print("=" * 60)
    print("DEMO: Update CIP-68 Metadata (Simplified)")
    print("=" * 60)
    
    seed_phrase = os.getenv("SEED_PHRASE")
    if not seed_phrase:
        print("ERROR: SEED_PHRASE không tìm thấy trong .env")
        return
    
    payment_skey, payment_vkey, stake_skey, stake_vkey, address = get_wallet_from_seed(seed_phrase)
    print(f"\nWallet address: {address}")
    
    context = get_chain_context()
    
    # List tokens owned by this address
    print("\nTìm tokens bạn sở hữu...")
    tokens = list_all_tokens(context, address)
    
    if not tokens:
        print("Không tìm thấy token nào! Hãy chạy demo_mint.py trước.")
        return
    
    print(f"\nTìm thấy {len(tokens)} token(s):")
    for i, token in enumerate(tokens):
        print(f"  {i + 1}. {token['token_name']} (version {token.get('version', '?')})")
    
    # Select token to update
    if len(tokens) == 1:
        selected = tokens[0]
    else:
        choice = input("\nChọn token để update (số): ").strip()
        try:
            idx = int(choice) - 1
            selected = tokens[idx]
        except (ValueError, IndexError):
            print("Lựa chọn không hợp lệ!")
            return
    
    token_name = selected['token_name']
    new_description = f"Updated metadata at {int(time.time())}"
    
    print(f"\nUpdating token: {token_name}")
    print(f"New description: {new_description}")
    print("-" * 60)
    
    try:
        result = update_metadata(
            context=context,
            payment_skey=payment_skey,
            payment_vkey=payment_vkey,
            owner_address=address,
            token_name=token_name,
            new_description=new_description,
        )
        
        print("\n" + "=" * 60)
        print("UPDATE THÀNH CÔNG!")
        print(f"Transaction Hash: {result['tx_hash']}")
        print(f"New Version: {result['new_version']}")
        print(f"\nXem tại: https://preprod.cardanoscan.io/transaction/{result['tx_hash']}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nLỗi: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
```

**Nội dung giảng:**
> "Demo update metadata:
> 1. List tất cả NFT thuộc ví hiện tại
> 2. Cho chọn token cần update
> 3. Tạo description mới (dùng timestamp)
> 4. Gọi `update_metadata()` → build tx, spend old UTxO, create new UTxO
> 
> Chạy: `python demo_update.py`
> 
> Sau khi update, version tăng lên (1 → 2 → 3...). Kiểm tra trên CardanoScan: UTxO cũ bị tiêu thụ, UTxO mới tạo với datum mới."

**Lỗi thường gặp:**
- Chạy update ngay sau mint mà chưa chờ confirm → UTxO chưa available
- Token name sai chính tả → không tìm thấy ref token

---

### Bước 4.3 — Tạo `demo_burn.py`

**Mục tiêu:** Script CLI để burn NFT.

**Hành động code:** Tạo file `demo_burn.py`:
```python
#!/usr/bin/env python3
"""Demo Burn CIP-68 Token"""

import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from offchain.cip68_operations import (
    get_chain_context,
    get_wallet_from_seed,
    burn_cip68_token,
    list_all_tokens,
)

load_dotenv()


def main():
    print("=" * 60)
    print("DEMO: Burn CIP-68 Token (Simplified)")
    print("=" * 60)
    
    seed_phrase = os.getenv("SEED_PHRASE")
    if not seed_phrase:
        print("ERROR: SEED_PHRASE không tìm thấy trong .env")
        return
    
    payment_skey, payment_vkey, stake_skey, stake_vkey, address = get_wallet_from_seed(seed_phrase)
    print(f"\nWallet address: {address}")
    
    context = get_chain_context()
    
    # List tokens
    print("\nTìm tokens bạn sở hữu...")
    tokens = list_all_tokens(context, address)
    
    if not tokens:
        print("Không tìm thấy token nào! Hãy chạy demo_mint.py trước.")
        return
    
    print(f"\nTìm thấy {len(tokens)} token(s):")
    for i, token in enumerate(tokens):
        print(f"  {i + 1}. {token['token_name']} (version {token.get('version', '?')})")
    
    # Select token to burn
    if len(tokens) == 1:
        selected = tokens[0]
        confirm = input(f"\nBạn có chắc muốn burn '{selected['token_name']}'? (y/n): ")
        if confirm.lower() != 'y':
            print("Đã hủy.")
            return
    else:
        choice = input("\nChọn token để burn (số): ").strip()
        try:
            idx = int(choice) - 1
            selected = tokens[idx]
        except (ValueError, IndexError):
            print("Lựa chọn không hợp lệ!")
            return
    
    token_name = selected['token_name']
    
    print(f"\nBurning token: {token_name}")
    print("-" * 60)
    
    try:
        result = burn_cip68_token(
            context=context,
            payment_skey=payment_skey,
            payment_vkey=payment_vkey,
            owner_address=address,
            token_name=token_name,
        )
        
        print("\n" + "=" * 60)
        print("BURN THÀNH CÔNG!")
        print(f"Transaction Hash: {result['tx_hash']}")
        print(f"\nXem tại: https://preprod.cardanoscan.io/transaction/{result['tx_hash']}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nLỗi: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
```

**Nội dung giảng:**
> "Demo burn — hủy vĩnh viễn NFT:
> 1. List tokens, chọn token cần burn
> 2. Confirm action (không thể undo!)
> 3. Gọi `burn_cip68_token()` → tìm cả 2 token, burn cùng lúc
> 
> Chạy: `python demo_burn.py`
> 
> Sau khi burn, cả reference token và user token biến mất. UTxO tại script address bị tiêu thụ, ADA trả về ví owner."

---

## PHẦN 5: CHẠY DEMO & VERIFY

### Bước 5.1 — Demo workflow đầy đủ

**Hành động:**
```bash
# 1. Mint NFT mới
python demo_mint.py

# 2. Chờ ~30 giây cho transaction confirm

# 3. Update metadata
python demo_update.py

# 4. Chờ ~30 giây

# 5. Burn NFT (optional)
python demo_burn.py
```

**Nội dung giảng:**
> "Chạy 3 scripts theo thứ tự: Mint → Update → Burn. Giữa mỗi action chờ khoảng 20-30 giây cho transaction được confirm trên Preprod (1 block = ~20s). Kiểm tra trên CardanoScan sau mỗi bước.
> 
> **Tổng kết Video 2:** Chúng ta đã viết hoàn chỉnh off-chain code bằng PyCardano:
> - `cip68_utils.py` — data types mapping 1:1 với Aiken, utility functions  
> - `cip68_operations.py` — mint, update, burn logic
> - 3 demo scripts — CLI interface
> 
> Video tiếp theo: Xây dựng web frontend + FastAPI backend để tương tác qua browser wallet."
