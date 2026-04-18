# 🎥 VIDEO 3 — Frontend & Backend Demo (Next.js + FastAPI)

## Tổng quan Video
- **Thời lượng ước tính:** 90–120 phút  
- **Mục tiêu:** Xây dựng web app hoàn chỉnh: FastAPI backend tạo unsigned transactions, Next.js frontend ký bằng browser wallet (CIP-30)  
- **Điều kiện tiên quyết:** Đã có offchain module từ Video 2, đã cài Node.js 18+  
- **Kiến trúc:**
  ```
  Browser Wallet (Nami/Eternl/Lace)
        ↕ CIP-30 API
  Next.js Frontend (:3000)
        ↕ REST API
  FastAPI Backend (:8000)
        ↕ BlockFrost API
  Cardano Blockchain (Preprod)
  ```

---

## PHẦN 1: FASTAPI BACKEND

### Bước 1.1 — Tạo file backend và imports

**Mục tiêu:** Khởi tạo FastAPI app, import toàn bộ dependencies.

**Hành động code:** Tạo thư mục `backend/` và file `backend/main.py`:
```python
"""
CIP-68 Dynamic Asset - Backend API
==================================
FastAPI backend để xử lý các yêu cầu từ frontend.
Tạo unsigned transactions để frontend ký bằng browser wallet.
"""

import os
import sys
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

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
    Value,
    MultiAsset,
    Asset,
    AssetName,
    ScriptHash,
    UTxO,
    Transaction,
    TransactionWitnessSet,
    RawCBOR,
    plutus_script_hash,
    min_lovelace,
)
from pycardano.serialization import NonEmptyOrderedSet

from offchain.cip68_utils import (
    CIP68_REFERENCE_PREFIX,
    CIP68_USER_PREFIX,
    MintToken,
    BurnToken,
    UpdateMetadata,
    BurnReference,
    CIP68Datum,
    create_cip68_asset_names,
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
> "Backend API có vai trò:
> 1. Nhận yêu cầu từ frontend (mint/update/burn)
> 2. Build unsigned transaction (CBOR hex)
> 3. Trả CBOR về cho frontend
> 4. Frontend ký bằng wallet → gửi witness set lại
> 5. Backend merge witness + submit
> 
> Tại sao không ký ở frontend luôn? Vì build transaction Plutus yêu cầu script bytecode, CBOR manipulation phức tạp — PyCardano handle tốt hơn JavaScript.
> 
> Import đặc biệt: `NonEmptyOrderedSet` — dùng để merge witness sets."

---

### Bước 1.2 — Định nghĩa Pydantic Models

**Mục tiêu:** Tạo schema cho request/response API.

**Hành động code:**
```python
# Global variables
chain_context: Optional[BlockFrostChainContext] = None
mint_script: Optional[PlutusV3Script] = None
store_script: Optional[PlutusV3Script] = None
policy_id: Optional[ScriptHash] = None
store_address: Optional[Address] = None
network: Network = Network.TESTNET


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class MintRequest(BaseModel):
    """Request model for minting CIP-68 token."""
    wallet_address: str = Field(..., description="Địa chỉ ví của người dùng")
    token_name: str = Field(..., min_length=1, max_length=32, description="Tên token")
    description: str = Field(..., min_length=1, max_length=256, description="Mô tả của NFT")


class UpdateRequest(BaseModel):
    """Request model for updating metadata."""
    wallet_address: str = Field(..., description="Địa chỉ ví của owner")
    token_name: str = Field(..., description="Tên token")
    new_description: str = Field(..., min_length=1, max_length=256, description="Mô tả mới")


class BurnRequest(BaseModel):
    """Request model for burning CIP-68 token."""
    wallet_address: str = Field(..., description="Địa chỉ ví của owner")
    token_name: str = Field(..., description="Tên token")


class TransactionResponse(BaseModel):
    """Response model containing unsigned transaction."""
    success: bool
    message: str
    tx_cbor: Optional[str] = None
    policy_id: Optional[str] = None
    token_name: Optional[str] = None


class SubmitRequest(BaseModel):
    """Request model for submitting signed transaction."""
    tx_cbor: str = Field(..., description="CBOR hex của unsigned transaction")
    witness_set_cbor: str = Field(..., description="CBOR hex của witness set từ wallet")


class SubmitResponse(BaseModel):
    """Response model for transaction submission."""
    success: bool
    message: str
    tx_hash: Optional[str] = None
```

**Nội dung giảng:**
> "Pydantic models define API contract:
> 
> **Request models:**
> - `MintRequest` — wallet_address + token_name + description
> - `UpdateRequest` — wallet_address + token_name + new_description
> - `BurnRequest` — wallet_address + token_name
> - `SubmitRequest` — tx_cbor (unsigned) + witness_set_cbor (từ wallet)
> 
> **Response models:**
> - `TransactionResponse` — success + message + tx_cbor (CBOR hex để wallet ký)
> - `SubmitResponse` — success + tx_hash
> 
> `wallet_address` là bech32 address — frontend sẽ convert từ hex (CIP-30 trả hex)."

---

### Bước 1.3 — Application Lifespan (Startup/Shutdown)

**Mục tiêu:** Load scripts và khởi tạo chain context khi app start.

**Hành động code:**
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    global chain_context, mint_script, store_script, network, policy_id, store_address
    
    # Startup
    print("Starting CIP-68 Backend API (Simplified)...")
    
    network_str = os.getenv("NETWORK", "Preprod")
    blockfrost_url = os.getenv("BLOCKFROST_URL", "https://cardano-preprod.blockfrost.io/api")
    blockfrost_key = os.getenv("BLOCKFROST_API_KEY")
    
    network = Network.TESTNET if network_str.lower() == "preprod" else Network.MAINNET
    
    chain_context = BlockFrostChainContext(
        project_id=blockfrost_key,
        base_url=blockfrost_url,
    )
    
    # Load scripts
    blueprint_path = os.path.join(
        os.path.dirname(__file__), '..', 'smart_contract', 'plutus.json'
    )
    
    if os.path.exists(blueprint_path):
        mint_script = load_mint_script(blueprint_path)
        store_script = load_store_script(blueprint_path)
        policy_id = get_policy_id(mint_script)
        store_address = get_script_address(store_script, network)
        print(f"Fixed Policy ID: {policy_id}")
        print(f"Fixed Store Address: {store_address}")
    
    print(f"Connected to {network_str} network")
    
    yield
    
    print("Shutting down CIP-68 Backend API...")
```

**Nội dung giảng:**
> "Lifespan handler chạy 1 lần khi app start:
> - Khởi tạo `BlockFrostChainContext` — kết nối Blockfrost
> - Load scripts từ `plutus.json` — bytecode contract
> - Tính `policy_id` và `store_address` — cố định
> 
> Dùng global variables vì scripts không thay đổi suốt vòng đời app. `yield` phân cách startup và shutdown."

---

### Bước 1.4 — Tạo FastAPI app với CORS

**Mục tiêu:** Khởi tạo app, cấu hình CORS cho frontend.

**Hành động code:**
```python
app = FastAPI(
    title="CIP-68 Dynamic Asset API",
    description="Backend API cho CIP-68 Dynamic Asset Demo.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Nội dung giảng:**
> "CORS middleware BẮT BUỘC vì frontend (port 3000) và backend (port 8000) khác origin. Không có CORS → browser block request. Chỉ allow `localhost:3000` — đủ cho demo."

---

### Bước 1.5 — Endpoint `/api/convert-address`

**Mục tiêu:** Convert hex address (CIP-30) sang bech32.

**Hành động code:**
```python
@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "CIP-68 Dynamic Asset API",
        "network": os.getenv("NETWORK", "Preprod"),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/convert-address")
async def convert_address(hex_address: str = Query(..., description="Hex-encoded address from CIP-30")):
    """Convert hex-encoded address to bech32 format."""
    try:
        address_bytes = bytes.fromhex(hex_address)
        addr = Address.from_primitive(address_bytes)
        
        return {
            "success": True,
            "hex_address": hex_address,
            "bech32_address": str(addr)
        }
    except Exception as e:
        try:
            addr = Address.from_primitive(hex_address)
            return {
                "success": True,
                "hex_address": hex_address,
                "bech32_address": str(addr)
            }
        except:
            return {
                "success": False,
                "message": f"Failed to convert address: {str(e)}",
            }
```

**Nội dung giảng:**
> "CIP-30 wallets trả address dạng hex (CBOR encoded). Backend cần bech32 (addr_test1...) để query Blockfrost. Endpoint này dùng PyCardano `Address.from_primitive()` để convert. Try 2 cách parse: bytes trước, string sau — xử lý các format khác nhau giữa wallets."

**Điểm nhấn:**
> Đây là điểm hay gặp bug: mỗi wallet có thể trả address format hơi khác nhau. Luôn có fallback.

---

### Bước 1.6 — Endpoint `POST /api/mint`

**Mục tiêu:** Build unsigned mint transaction.

**Hành động code:**
```python
@app.post("/api/mint", response_model=TransactionResponse)
async def create_mint_transaction(request: MintRequest):
    """Tạo unsigned transaction để mint CIP-68 NFT."""
    try:
        if not mint_script or not store_script:
            raise HTTPException(status_code=500, detail="Scripts not loaded")
        
        # Parse wallet address
        owner_address = Address.from_primitive(request.wallet_address)
        owner_pkh = owner_address.payment_part.to_primitive()
        
        # Create asset names
        token_name_bytes = request.token_name.encode('utf-8')
        ref_asset_name, user_asset_name = create_cip68_asset_names(token_name_bytes)
        
        # Policy ID as bytes for datum
        policy_id_bytes = bytes(policy_id)
        
        # Create CIP68 Datum
        datum = create_cip68_datum(
            policy_id=policy_id_bytes,
            asset_name=token_name_bytes,
            owner_pkh=owner_pkh,
            metadata=request.description,
            version=1
        )
        
        # Create MultiAsset for minting
        mint_asset = Asset()
        mint_asset[ref_asset_name] = 1
        mint_asset[user_asset_name] = 1
        
        mint_assets = MultiAsset()
        mint_assets[policy_id] = mint_asset
        
        # Create redeemer
        redeemer = Redeemer(MintToken(token_name=token_name_bytes))
        
        # Calculate values
        ref_asset_only = Asset()
        ref_asset_only[ref_asset_name] = 1
        ref_multi = MultiAsset()
        ref_multi[policy_id] = ref_asset_only
        ref_value = Value(2_000_000, ref_multi)
        
        user_asset_only = Asset()
        user_asset_only[user_asset_name] = 1
        user_multi = MultiAsset()
        user_multi[policy_id] = user_asset_only
        user_value = Value(2_000_000, user_multi)
        
        # Build transaction
        builder = TransactionBuilder(chain_context)
        builder.add_input_address(owner_address)
        
        builder.mint = mint_assets
        builder.add_minting_script(mint_script, redeemer=redeemer)
        
        builder.add_output(
            TransactionOutput(store_address, ref_value, datum=datum)
        )
        builder.add_output(
            TransactionOutput(owner_address, user_value)
        )
        
        builder.required_signers = [owner_address.payment_part]
        
        # Build transaction body (NOT signed — wallet will sign)
        tx_body = builder.build(change_address=owner_address)
        witness_set = builder.build_witness_set()
        
        tx = Transaction(tx_body, witness_set)
        tx_cbor = tx.to_cbor().hex()
        
        return TransactionResponse(
            success=True,
            message="Unsigned transaction created successfully",
            tx_cbor=tx_cbor,
            policy_id=str(policy_id),
            token_name=request.token_name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        return TransactionResponse(
            success=False,
            message=f"Error creating transaction: {str(e)}"
        )
```

**Nội dung giảng:**
> "So sánh với CLI script (`mint_cip68_token`), endpoint này KHÁC ở bước cuối:
> 
> **CLI:** `builder.build_and_sign()` → tự ký bằng payment_skey → submit luôn
> 
> **Backend API:** `builder.build()` → chỉ build body → `builder.build_witness_set()` → tạo witness set (chứa scripts, redeemers nhưng CHƯA có chữ ký) → serialize thành CBOR hex → trả về frontend
> 
> Frontend nhận CBOR → đưa cho wallet ký → wallet trả witness set (chứa chữ ký) → gửi lại backend.
> 
> **Điểm khác biệt quan trọng:**
> - `owner_pkh` lấy từ `owner_address.payment_part` (không cần payment_vkey)
> - `required_signers` dùng `owner_address.payment_part` (PaymentKeyHash từ address)
> - Transaction CHƯA signed → tx_cbor là unsigned CBOR"

**Điểm nhấn:**
> Đây là pattern chuẩn cho dApp: backend build transaction, frontend (wallet) ký. Bảo mật vì private key KHÔNG BAO GIỜ rời khỏi wallet extension.

---

### Bước 1.7 — Endpoint `POST /api/update`

**Mục tiêu:** Build unsigned update metadata transaction.

**Hành động code:**
```python
@app.post("/api/update", response_model=TransactionResponse)
async def create_update_transaction(request: UpdateRequest):
    """Tạo unsigned transaction để update metadata."""
    try:
        if not store_script:
            raise HTTPException(status_code=500, detail="Store script not loaded")
        
        owner_address = Address.from_primitive(request.wallet_address)
        owner_pkh = owner_address.payment_part.to_primitive()
        
        policy_id_bytes = bytes(policy_id)
        token_name_bytes = request.token_name.encode('utf-8')
        ref_asset_name = AssetName(CIP68_REFERENCE_PREFIX + token_name_bytes)
        
        # Find reference token UTxO
        utxos = chain_context.utxos(store_address)
        ref_utxo = None
        for utxo in utxos:
            if utxo.output.amount.multi_asset:
                for pid, assets in utxo.output.amount.multi_asset.items():
                    if pid == policy_id and ref_asset_name in assets:
                        ref_utxo = utxo
                        break
        
        if not ref_utxo:
            raise HTTPException(status_code=404, detail="Reference token not found")
        
        # Get current datum and verify owner
        current_datum = ref_utxo.output.datum
        new_version = 2
        if isinstance(current_datum, CIP68Datum):
            current_owner = extract_owner_from_datum(current_datum)
            if current_owner != owner_pkh:
                raise HTTPException(status_code=403, detail="You are not the owner of this NFT")
            new_version = current_datum.version + 1
        
        # Create new datum — giữ nguyên identity fields
        new_datum = create_cip68_datum(
            policy_id=policy_id_bytes,
            asset_name=token_name_bytes,
            owner_pkh=owner_pkh,
            metadata=request.new_description,
            version=new_version
        )
        
        redeemer = Redeemer(UpdateMetadata())
        
        builder = TransactionBuilder(chain_context)
        builder.add_input_address(owner_address)
        
        builder.add_script_input(ref_utxo, store_script, redeemer=redeemer)
        
        ref_asset = Asset()
        ref_asset[ref_asset_name] = 1
        ref_multi = MultiAsset()
        ref_multi[policy_id] = ref_asset
        ref_value = Value(ref_utxo.output.amount.coin, ref_multi)
        
        builder.add_output(
            TransactionOutput(store_address, ref_value, datum=new_datum)
        )
        
        builder.required_signers = [owner_address.payment_part]
        
        tx_body = builder.build(change_address=owner_address)
        witness_set = builder.build_witness_set()
        
        tx = Transaction(tx_body, witness_set)
        tx_cbor = tx.to_cbor().hex()
        
        return TransactionResponse(
            success=True,
            message="Update transaction created successfully",
            tx_cbor=tx_cbor,
            policy_id=str(policy_id),
            token_name=request.token_name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return TransactionResponse(
            success=False,
            message=f"Error creating update transaction: {str(e)}"
        )
```

**Nội dung giảng:**
> "Update endpoint gần giống CLI nhưng:
> - Verify owner off-chain TRƯỚC (403 nếu không phải owner) — tránh gửi tx lỗi
> - Build unsigned → trả CBOR
> - Owner check dùng `owner_address.payment_part` thay vì payment_vkey
> - Cùng pattern: find UTxO → build datum mới → script input → output trả lại script"

---

### Bước 1.8 — Endpoint `POST /api/burn`

**Mục tiêu:** Build unsigned burn transaction.

**Hành động code:**
```python
@app.post("/api/burn", response_model=TransactionResponse)
async def create_burn_transaction(request: BurnRequest):
    """Tạo unsigned transaction để burn CIP-68 NFT."""
    try:
        if not mint_script or not store_script:
            raise HTTPException(status_code=500, detail="Scripts not loaded")
        
        owner_address = Address.from_primitive(request.wallet_address)
        owner_pkh = owner_address.payment_part.to_primitive()
        
        token_name_bytes = request.token_name.encode('utf-8')
        ref_asset_name, user_asset_name = create_cip68_asset_names(token_name_bytes)
        
        # Find reference token UTxO at store
        store_utxos = chain_context.utxos(store_address)
        ref_utxo = None
        for utxo in store_utxos:
            if utxo.output.amount.multi_asset:
                for pid, assets in utxo.output.amount.multi_asset.items():
                    if pid == policy_id and ref_asset_name in assets:
                        ref_utxo = utxo
                        break
        
        if not ref_utxo:
            raise HTTPException(status_code=404, detail="Reference token not found")
        
        # Verify owner
        current_datum = ref_utxo.output.datum
        if isinstance(current_datum, CIP68Datum):
            current_owner = extract_owner_from_datum(current_datum)
            if current_owner != owner_pkh:
                raise HTTPException(status_code=403, detail="You are not the owner")
        
        # Find user token UTxO in wallet
        owner_utxos = chain_context.utxos(owner_address)
        user_utxo = None
        for utxo in owner_utxos:
            if utxo.output.amount.multi_asset:
                for pid, assets in utxo.output.amount.multi_asset.items():
                    if pid == policy_id and user_asset_name in assets:
                        user_utxo = utxo
                        break
        
        if not user_utxo:
            raise HTTPException(status_code=404, detail="User token not found in wallet")
        
        # Burn assets (negative)
        burn_asset = Asset()
        burn_asset[ref_asset_name] = -1
        burn_asset[user_asset_name] = -1
        burn_assets = MultiAsset()
        burn_assets[policy_id] = burn_asset
        
        mint_redeemer = Redeemer(BurnToken(token_name=token_name_bytes))
        spend_redeemer = Redeemer(BurnReference())
        
        builder = TransactionBuilder(chain_context)
        builder.add_input_address(owner_address)
        
        builder.add_script_input(ref_utxo, store_script, redeemer=spend_redeemer)
        builder.add_input(user_utxo)
        
        builder.mint = burn_assets
        builder.add_minting_script(mint_script, redeemer=mint_redeemer)
        
        builder.required_signers = [owner_address.payment_part]
        
        tx_body = builder.build(change_address=owner_address)
        witness_set = builder.build_witness_set()
        
        tx = Transaction(tx_body, witness_set)
        tx_cbor = tx.to_cbor().hex()
        
        return TransactionResponse(
            success=True,
            message="Burn transaction created successfully",
            tx_cbor=tx_cbor,
            policy_id=str(policy_id),
            token_name=request.token_name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        return TransactionResponse(
            success=False,
            message=f"Error creating burn transaction: {str(e)}"
        )
```

**Nội dung giảng:**
> "Burn endpoint — phức tạp nhất vì cần cả 2 validators:
> - Tìm ref token UTxO ở store + user token UTxO ở ví
> - 2 redeemers: `BurnReference` (spending) + `BurnToken` (minting)
> - `add_script_input` cho ref + `add_input` cho user
> - Mint negative (-1) để burn
> - Tất cả trong 1 transaction"

---

### Bước 1.9 — Endpoint `POST /api/submit` (Merge witnesses)

**Mục tiêu:** Nhận witness set từ wallet, merge với transaction, submit.

**Hành động code:**
```python
@app.post("/api/submit", response_model=SubmitResponse)
async def submit_transaction(request: SubmitRequest):
    """Submit signed transaction to blockchain."""
    try:
        # 1. Load lại Transaction gốc từ CBOR
        backend_tx = Transaction.from_cbor(bytes.fromhex(request.tx_cbor))
        
        # 2. Parse Witness Set từ Frontend (chỉ chứa vkey_witnesses)
        wallet_witness = TransactionWitnessSet.from_cbor(bytes.fromhex(request.witness_set_cbor))
        
        # 3. Merge witnesses
        final_witness_set = backend_tx.transaction_witness_set
        
        if wallet_witness.vkey_witnesses:
            if final_witness_set.vkey_witnesses:
                existing_vkeys = list(final_witness_set.vkey_witnesses)
                new_vkeys = list(wallet_witness.vkey_witnesses)
                final_witness_set.vkey_witnesses = NonEmptyOrderedSet(existing_vkeys + new_vkeys)
            else:
                final_witness_set.vkey_witnesses = wallet_witness.vkey_witnesses

        backend_tx.transaction_witness_set = final_witness_set
        
        # 4. Submit
        tx_hash = chain_context.submit_tx_cbor(backend_tx.to_cbor())
        
        return SubmitResponse(
            success=True,
            message="Transaction submitted successfully",
            tx_hash=str(tx_hash)
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return SubmitResponse(
            success=False,
            message=f"Error submitting transaction: {str(e)}"
        )
```

**Nội dung giảng:**
> "Đây là endpoint QUAN TRỌNG NHẤT — nơi hợp nhất chữ ký wallet với transaction body:
> 
> **Bước 1:** Deserialize transaction gốc từ CBOR (chứa body + scripts + redeemers nhưng CHƯA có chữ ký)
> 
> **Bước 2:** Deserialize witness set từ wallet (chỉ chứa `vkey_witnesses` = chữ ký)
> 
> **Bước 3:** Merge: Thêm chữ ký ví vào witness set của transaction gốc. Dùng `NonEmptyOrderedSet` vì PyCardano yêu cầu format này.
> 
> **Bước 4:** Submit CBOR hoàn chỉnh (body + scripts + redeemers + chữ ký) lên blockchain
> 
> Pattern: `backend builds` → `wallet signs` → `backend merges & submits`"

**Điểm nhấn:**
> `submit_tx_cbor()` gửi raw CBOR — quan trọng để giữ nguyên cấu trúc body. Nếu serialize lại body → hash thay đổi → chữ ký invalid.

**Lỗi thường gặp:**
- Serialize/deserialize làm thay đổi byte order → tx hash khác → witness invalid
- Wallet trả witness set format không chuẩn → parse fail
- Quên `partialSign: true` ở frontend → wallet ký khác format

---

### Bước 1.10 — Endpoint query metadata & list tokens

**Mục tiêu:** API đọc metadata on-chain và list tất cả tokens.

**Hành động code:**
```python
@app.get("/api/metadata/{token_name}")
async def get_metadata(token_name: str):
    """Lấy metadata hiện tại của CIP-68 NFT."""
    try:
        token_name_bytes = token_name.encode('utf-8')
        ref_asset_name = AssetName(CIP68_REFERENCE_PREFIX + token_name_bytes)
        
        utxos = chain_context.utxos(store_address)
        
        for utxo in utxos:
            if utxo.output.amount.multi_asset:
                for p, assets in utxo.output.amount.multi_asset.items():
                    if p == policy_id and ref_asset_name in assets:
                        datum = utxo.output.datum
                        
                        if isinstance(datum, RawCBOR):
                            try:
                                datum = CIP68Datum.from_cbor(datum.cbor)
                            except:
                                continue
                        
                        if isinstance(datum, CIP68Datum):
                            metadata = {}
                            for k, v in datum.metadata.items():
                                key = k.decode('utf-8') if isinstance(k, bytes) else str(k)
                                if isinstance(v, bytes):
                                    value = v.decode('utf-8')
                                elif hasattr(v, 'to_primitive'):
                                    prim = v.to_primitive()
                                    value = prim.decode('utf-8') if isinstance(prim, bytes) else str(prim)
                                else:
                                    value = str(v)
                                metadata[key] = value
                            
                            return {
                                "success": True,
                                "message": "Metadata found",
                                "metadata": metadata,
                                "version": datum.version
                            }
        
        return {"success": False, "message": "NFT not found"}
        
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}


@app.get("/api/wallet/{address}")
async def get_wallet_info(address: str):
    """Lấy thông tin ví."""
    try:
        addr = Address.from_primitive(address)
        utxos = chain_context.utxos(addr)
        
        total_lovelace = sum(utxo.output.amount.coin for utxo in utxos)
        
        assets = []
        for utxo in utxos:
            if utxo.output.amount.multi_asset:
                for pid, asset_dict in utxo.output.amount.multi_asset.items():
                    for asset_name, quantity in asset_dict.items():
                        assets.append({
                            "policy_id": str(pid),
                            "asset_name": asset_name.payload.hex(),
                            "quantity": quantity
                        })
        
        return {
            "success": True,
            "address": address,
            "balance_lovelace": total_lovelace,
            "utxo_count": len(utxos),
            "assets": assets
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/script-info")
async def get_script_info():
    """Lấy thông tin về smart contracts."""
    return {
        "policy_id": str(policy_id) if policy_id else None,
        "store_address": str(store_address) if store_address else None,
        "network": os.getenv("NETWORK", "Preprod"),
    }
```

**Nội dung giảng:**
> "Các endpoint query:
> - `/api/metadata/{token_name}` — đọc datum từ reference token UTxO, parse bytes → string
> - `/api/wallet/{address}` — list UTxOs và assets trong ví
> - `/api/script-info` — trả policy ID, store address cho frontend hiển thị
> 
> Lưu ý xử lý `RawCBOR`: đôi khi PyCardano trả datum dạng raw CBOR thay vì parsed object → cần `CIP68Datum.from_cbor()` để deserialize."

---

### Bước 1.11 — Tạo `run_backend.py`

**Mục tiêu:** Script khởi chạy backend.

**Hành động code:** Tạo file `run_backend.py` ở root:
```python
"""Startup script for the Backend API"""
import os
import sys

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'backend'))

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=[project_root]
    )
```

**Nội dung giảng:**
> "Chạy `python run_backend.py` sẽ start FastAPI trên port 8000 với hot-reload. Truy cập `http://localhost:8000/docs` để xem Swagger UI — test API trực tiếp."

================================= Hết phần backend =========================
---

# 🎥 VIDEO 3 (Tiếp) — Frontend & Backend Integration (Code frontend Template-based)

## Tổng quan Video
- **Thời lượng ước tính:** 60–90 phút  
- **Phương pháp:** Clone template có sẵn UI → Điền logic vào 16 TODOs  
- **Mục tiêu:** Người học hiểu **flow 3 bước** (build→sign→submit) và **CIP-30 wallet integration**  
- **Điều kiện tiên quyết:** 
  - Backend FastAPI đã chạy (port 8000)
  - Browser có Nami/Eternl/Lace extension
  - Node.js 18+ đã cài

---
================================= Bắt đầu phần frontend============================
## PHẦN 1: SETUP TEMPLATE

### Bước 1.1 — Clone template và cài dependencies

**Mục tiêu:** Khởi chạy template với UI hoàn chỉnh nhưng logic trống.

**Hành động code:**
```bash
# clone template về máy tính
git clone https://github.com/TienTung2501/template_frontend_cip68.git

# Đã có sẵn folder frontend_template/
cd template_frontend_cip68
npm install
npm run dev
```

**Nội dung giảng:**
> "Template đã chuẩn bị sẵn:
> - ✅ UI components đầy đủ (forms, buttons, modals)
> - ✅ Tailwind styling
> - ✅ CIP-30 types
> - ✅ Config files (Next.js, TypeScript)
> 
> Những gì CÒN THIẾU:
> - ❌ Logic kết nối ví
> - ❌ Logic build/sign/submit transaction
> - ❌ Logic fetch NFTs, metadata
> 
> Chúng ta sẽ điền logic vào 16 TODOs. Mở http://localhost:3000 → thấy UI đẹp nhưng nút chưa hoạt động."

**Điểm nhấn:**
> Phương pháp này tiết kiệm thời gian — thay vì code UI 2 tiếng, ta tập trung vào **business logic** và **Cardano concepts**.

---

## PHẦN 2: WALLET INTEGRATION (TODOs 1-7)

### Bước 2.1 — Implement getAvailableWallets (TODO 1)

**Mục tiêu:** Scan browser tìm Cardano wallets đã cài.

**File:** `src/context/WalletContext.tsx`

**Hành động code:** Thay TODO 1 bằng:
```typescript
const getAvailableWallets = useCallback((): WalletInfo[] => {
  if (typeof window === 'undefined' || !window.cardano) return [];
  
  return SUPPORTED_WALLETS.map(wallet => ({
    ...wallet,
    available: !!window.cardano?.[wallet.id],
  })).filter(w => w.available);
}, []);
```

**Nội dung giảng:**
> "CIP-30 wallets inject object vào `window.cardano`:
> - Nami → `window.cardano.nami`
> - Eternl → `window.cardano.eternl`
> - Lace → `window.cardano.lace`
> 
> Function này:
> 1. Check `window` tồn tại (SSR safety)
> 2. Map qua `SUPPORTED_WALLETS` (đã define sẵn trong types)
> 3. Check từng wallet: `!!window.cardano?.[wallet.id]`
> 4. Filter chỉ giữ `available: true`
> 
> Dùng trong WalletConnect dropdown để hiển thị ví nào có thể kết nối."

---

### Bước 2.2 — Implement getAddress helper (TODO 2)

**Mục tiêu:** Lấy address từ wallet (ưu tiên used → unused → change).

**Hành động code:** Thay TODO 2 bằng:
```typescript
const getAddress = async (api: CardanoWalletAPI): Promise<string> => {
  const addresses = await api.getUsedAddresses();
  if (addresses && addresses.length > 0) return addresses[0];
  
  const unusedAddresses = await api.getUnusedAddresses();
  if (unusedAddresses && unusedAddresses.length > 0) return unusedAddresses[0];
  
  return await api.getChangeAddress();
};
```

**Nội dung giảng:**
> "CIP-30 wallets có 3 loại address:
> - **Used addresses** — đã từng giao dịch (ưu tiên nhất)
> - **Unused addresses** — chưa dùng (fallback)
> - **Change address** — nhận tiền thừa (last resort)
> 
> Mỗi wallet trả format hơi khác → ta thử 3 cách. Address trả về là **hex CBOR** — backend sẽ convert sang bech32."

---

### Bước 2.3 — Implement connect function (TODO 3)

**Mục tiêu:** Kết nối ví qua CIP-30, popup cho user approve.

**Hành động code:** Thay TODO 3 bằng:
```typescript
const connect = useCallback(async (walletId: keyof CardanoWindow) => {
  if (typeof window === 'undefined' || !window.cardano) {
    setError('Cardano wallet not found.');
    return;
  }
  
  const wallet = window.cardano[walletId];
  if (!wallet) {
    setError(`${walletId} wallet not found.`);
    return;
  }
  
  setConnecting(true);
  setError(null);
  
  try {
    const api = await wallet.enable();
    const addressHex = await getAddress(api);
    
    setWalletApi(api);
    setWalletName(wallet.name);
    setWalletAddress(addressHex);
    setConnected(true);
    localStorage.setItem('connectedWallet', walletId);
  } catch (err: any) {
    setError(err.message || 'Failed to connect wallet');
  } finally {
    setConnecting(false);
  }
}, []);
```

**Nội dung giảng:**
> "Flow kết nối ví:
> 1. Check `window.cardano` và wallet tồn tại
> 2. Gọi `wallet.enable()` → **wallet popup** → user approve
> 3. Nhận `api` object — interface để ký transaction, lấy UTxOs, v.v.
> 4. Gọi `getAddress(api)` → lấy hex address
> 5. Save state: `walletApi`, `walletName`, `walletAddress`, `connected`
> 6. Lưu `walletId` vào localStorage → auto-reconnect khi reload
> 
> **Đây là bước quan trọng nhất** — không có connection này, không thể ký transaction."

**Điểm nhấn:**
> `wallet.enable()` là **async** — user có thể từ chối → catch error. `setConnecting(true/false)` để hiển thị loading spinner.

---

### Bước 2.4 — Implement disconnect (TODO 4)

**Hành động code:**
```typescript
const disconnect = useCallback(() => {
  setWalletApi(null);
  setWalletName(null);
  setWalletAddress(null);
  setConnected(false);
  setError(null);
  localStorage.removeItem('connectedWallet');
}, []);
```

**Nội dung giảng:**
> "Clear toàn bộ state và localStorage. Simple nhưng quan trọng — đảm bảo không còn reference tới wallet cũ."

---

### Bước 2.5 — Implement signTx (TODO 5)

**Hành động code:**
```typescript
const signTx = useCallback(async (txCbor: string, partialSign = false): Promise<string> => {
  if (!walletApi) throw new Error('Wallet not connected');
  
  try {
    return await walletApi.signTx(txCbor, partialSign);
  } catch (err: any) {
    throw new Error(err.message || 'Failed to sign transaction');
  }
}, [walletApi]);
```

**Nội dung giảng:**
> "Function ký transaction:
> - Input: `txCbor` (unsigned CBOR hex từ backend)
> - Output: `witnessSet` (CBOR chứa chữ ký)
> 
> **`partialSign: true` BẮT BUỘC** cho Plutus transactions vì:
> - Backend đã cung cấp script witnesses (Plutus scripts)
> - Wallet chỉ cần ký phần liên quan đến user keys
> - Nếu `partialSign: false` → wallet cố ký toàn bộ → fail (vì không có script private key)
> 
> `walletApi.signTx()` sẽ popup wallet → user approve → trả witness set CBOR."

**Lỗi thường gặp:**
> Quên `partialSign: true` → error "Missing witnesses" hoặc "Invalid signature".

---

### Bước 2.6 — Auto-reconnect effect (TODO 6)

**Hành động code:** Thêm vào cuối `WalletProvider` (trước return):
```typescript
React.useEffect(() => {
  const savedWallet = localStorage.getItem('connectedWallet') as keyof CardanoWindow | null;
  if (savedWallet && typeof window !== 'undefined' && window.cardano?.[savedWallet]) {
    connect(savedWallet);
  }
}, [connect]);
```

**Nội dung giảng:**
> "Auto-reconnect khi reload trang:
> 1. Lấy `savedWallet` từ localStorage (đã lưu ở bước connect)
> 2. Nếu có và wallet vẫn tồn tại → tự gọi `connect()`
> 3. User không cần kết nối lại mỗi lần reload
> 
> Dependency `[connect]` — chạy 1 lần khi mount."

---

### Bước 2.7 — WalletConnect handleConnect (TODO 7)

**Mục tiêu:** Xử lý click chọn ví trong dropdown.

**File:** `src/components/WalletConnect.tsx`

**Hành động code:**
```typescript
const handleConnect = async (walletId: keyof CardanoWindow) => {
  await connect(walletId);
  setShowDropdown(false);
};
```

**Nội dung giảng:**
> "Khi user click ví trong dropdown:
> 1. Gọi `connect(walletId)` (từ Context)
> 2. Đóng dropdown
> 
> Simple nhưng quan trọng — link UI với logic."

---

**TEST CHECKPOINT 1:**
```bash
npm run dev
# Mở localhost:3000
# Click "Kết nối ví" → thấy dropdown Nami/Eternl/Lace
# Click chọn → wallet popup → approve → thấy address xanh
```

---

## PHẦN 3: TRANSACTION FLOWS (TODOs 8-10)

### Bước 3.1 — MintForm handleMint (TODO 8)

**Mục tiêu:** Implement flow 3 bước mint NFT.

**File:** `src/components/MintForm.tsx`

**Hành động code:** Thay TODO 8 bằng:
```typescript
const handleMint = async (e: React.FormEvent) => {
  e.preventDefault();
  
  if (!connected || !walletAddress) {
    setTxStatus({ status: 'error', message: 'Vui lòng kết nối ví trước!' });
    return;
  }

  try {
    setIsLoading(true);
    setTxStatus({ status: 'building', message: 'Đang tạo transaction...' });

    // BƯỚC 1: BUILD TRANSACTION
    const response = await fetch('http://localhost:8000/api/mint', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        wallet_address: walletAddress,
        token_name: tokenName,
        description: description,
      }),
    });
    const data = await response.json();
    if (!data.success) throw new Error(data.message);

    // BƯỚC 2: SIGN TRANSACTION
    setTxStatus({ status: 'signing', message: 'Vui lòng ký transaction trong ví...' });
    const witnessSet = await signTx(data.tx_cbor, true);

    // BƯỚC 3: SUBMIT TRANSACTION
    setTxStatus({ status: 'submitting', message: 'Đang gửi transaction...' });
    const submitResponse = await fetch('http://localhost:8000/api/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tx_cbor: data.tx_cbor, witness_set_cbor: witnessSet }),
    });
    const submitData = await submitResponse.json();
    if (!submitData.success) throw new Error(submitData.message);

    // SUCCESS
    setTxStatus({
      status: 'success',
      message: `NFT "${tokenName}" đã được mint thành công!`,
      txHash: submitData.tx_hash,
    });

    setTokenName('');
    setDescription('');
    
    if (onMintSuccess) {
      setTimeout(() => onMintSuccess(), 2000);
    }
  } catch (error: any) {
    setTxStatus({ status: 'error', message: error.message || 'Lỗi khi mint' });
  } finally {
    setIsLoading(false);
  }
};
```

**Nội dung giảng:**
> "Đây là **core pattern** của dApp:
> 
> **BƯỚC 1 — BUILD (Backend):**
> - POST `/api/mint` với wallet_address, token_name, description
> - Backend:
>   + Parse address
>   + Tạo CIP68Datum
>   + Build TransactionBuilder
>   + Add mint assets, script, outputs
>   + `builder.build()` → unsigned CBOR
> - Return: `tx_cbor` (unsigned), `policy_id`
> 
> **BƯỚC 2 — SIGN (Wallet):**
> - `await signTx(tx_cbor, true)` → wallet popup
> - User xem chi tiết transaction: mint 2 tokens, output về store address, output về ví
> - User approve → wallet ký → trả `witnessSet` (CBOR chứa signature)
> 
> **BƯỚC 3 — SUBMIT (Backend):**
> - POST `/api/submit` với `tx_cbor` + `witness_set_cbor`
> - Backend:
>   + Deserialize transaction + witness set
>   + Merge witnesses (dùng `NonEmptyOrderedSet`)
>   + Submit CBOR lên blockchain
> - Return: `tx_hash`
> 
> **WHY 3 STEPS?**
> - Build ở backend: PyCardano handle Plutus scripts tốt hơn JS
> - Sign ở wallet: Private key KHÔNG BAO GIỜ rời browser
> - Submit ở backend: Có thể log, monitor, retry
> 
> State machine: `building` → `signing` (popup) → `submitting` → `success` (show tx hash) hoặc `error`."

**Điểm nhấn:**
> `partialSign: true` ở bước 2 — nếu quên, transaction fail.  
> `setTimeout(() => onMintSuccess(), 2000)` — chờ 2s cho blockchain propagate → refresh NFT list.

---

### Bước 3.2 — UpdateModal handleUpdate (TODO 9)

**File:** `src/components/UpdateModal.tsx`

**Hành động code:**
```typescript
const handleUpdate = async (e: React.FormEvent) => {
  e.preventDefault();
  
  try {
    setIsLoading(true);
    setTxStatus({ status: 'building', message: 'Đang tạo update transaction...' });

    const response = await fetch('http://localhost:8000/api/update', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        wallet_address: walletAddress,
        token_name: tokenName,
        new_description: newDescription,
      }),
    });
    const data = await response.json();
    if (!data.success) throw new Error(data.message);

    setTxStatus({ status: 'signing', message: 'Vui lòng ký transaction...' });
    const witnessSet = await signTx(data.tx_cbor, true);

    setTxStatus({ status: 'submitting', message: 'Đang gửi...' });
    const submitResponse = await fetch('http://localhost:8000/api/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tx_cbor: data.tx_cbor, witness_set_cbor: witnessSet }),
    });
    const submitData = await submitResponse.json();
    if (!submitData.success) throw new Error(submitData.message);

    setTxStatus({ status: 'success', message: 'Metadata đã được cập nhật!', txHash: submitData.tx_hash });
    onClose();
    
    if (onUpdateSuccess) {
      setTimeout(() => onUpdateSuccess(), 2000);
    }
  } catch (error: any) {
    setTxStatus({ status: 'error', message: error.message });
  } finally {
    setIsLoading(false);
  }
};
```

**Nội dung giảng:**
> "Update follow cùng pattern 3 bước, khác ở:
> - Endpoint: `/api/update`
> - Backend:
>   + Tìm ref token UTxO ở store address
>   + Verify owner (403 nếu không match)
>   + Tạo datum mới (giữ nguyên policy_id, asset_name, owner — CHỈ đổi metadata + tăng version)
>   + `add_script_input()` ref UTxO
>   + Output trả lại store với datum mới
> - Wallet ký → submit → metadata on-chain thay đổi"

---

### Bước 3.3 — BurnModal handleBurn (TODO 10)

**File:** `src/components/BurnModal.tsx`

**Hành động code:**
```typescript
const handleBurn = async (e: React.FormEvent) => {
  e.preventDefault();
  
  try {
    setIsLoading(true);
    setTxStatus({ status: 'building', message: 'Đang tạo burn transaction...' });

    const response = await fetch('http://localhost:8000/api/burn', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        wallet_address: walletAddress,
        token_name: tokenName,
      }),
    });
    const data = await response.json();
    if (!data.success) throw new Error(data.message);

    setTxStatus({ status: 'signing', message: 'Vui lòng ký transaction...' });
    const witnessSet = await signTx(data.tx_cbor, true);

    setTxStatus({ status: 'submitting', message: 'Đang gửi...' });
    const submitResponse = await fetch('http://localhost:8000/api/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tx_cbor: data.tx_cbor, witness_set_cbor: witnessSet }),
    });
    const submitData = await submitResponse.json();
    if (!submitData.success) throw new Error(submitData.message);

    setTxStatus({ status: 'success', message: 'NFT đã được burn!', txHash: submitData.tx_hash });
    onClose();
    
    if (onBurnSuccess) {
      setTimeout(() => onBurnSuccess(), 2000);
    }
  } catch (error: any) {
    setTxStatus({ status: 'error', message: error.message });
  } finally {
    setIsLoading(false);
  }
};
```

**Nội dung giảng:**
> "Burn phức tạp hơn vì cần 2 validators:
> - Backend:
>   + Tìm ref token UTxO (store) + user token UTxO (wallet)
>   + 2 inputs: `add_script_input(ref)` + `add_input(user)`
>   + Mint -1 (negative) cho cả 2 tokens
>   + 2 redeemers: `BurnReference` (spending) + `BurnToken` (minting)
> - 1 transaction xóa cả 2 tokens → NFT biến mất khỏi chain"

---

**TEST CHECKPOINT 2:**
```bash
# Kết nối ví → Mint NFT → thấy popup wallet
# Approve → chờ → "Thành công!" + link CardanoScan
```

---

## PHẦN 4: NFT DISPLAY & METADATA (TODOs 11-13)

### Bước 4.1 — fetchNFTs (TODO 11)

**File:** `src/components/NFTList.tsx`

**Hành động code:**
```typescript
const fetchNFTs = async () => {
  setLoading(true);
  try {
    const response = await fetch(`http://localhost:8000/api/wallet/${walletAddress}`);
    const data = await response.json();
    
    if (!data.success) return;
    
    // Filter CIP-68 user tokens (policy ID + prefix 000de140)
    const cip68Assets = data.assets.filter((asset: any) => 
      asset.policy_id === PLATFORM_POLICY_ID && 
      asset.asset_name.startsWith(USER_TOKEN_PREFIX)
    );
    
    // Decode token names from hex
    const nftList: NFTData[] = cip68Assets.map((asset: any) => {
      const nameHex = asset.asset_name.slice(8); // Remove prefix
      const tokenName = Buffer.from(nameHex, 'hex').toString('utf-8');
      return {
        tokenName,
        description: '',
        version: 0,
        loading: true,
      };
    });
    
    setNfts(nftList);
    
    // Load metadata for each NFT
    nftList.forEach((nft, index) => {
      loadMetadata(nft.tokenName, index);
    });
  } catch (error) {
    console.error('Error fetching NFTs:', error);
  } finally {
    setLoading(false);
  }
};
```

**Nội dung giảng:**
> "Lấy danh sách NFT:
> 1. GET `/api/wallet/${address}` → backend trả tất cả assets (ADA + native tokens)
> 2. Filter:
>    - `policy_id === PLATFORM_POLICY_ID` (hardcode policy ID của dự án)
>    - `asset_name.startsWith('000de140')` (CIP-68 user token prefix)
> 3. Decode asset name:
>    - CIP-68 format: `000de140` + token_name_hex
>    - Cắt 8 ký tự đầu → hex decode → UTF-8 string
> 4. Khởi tạo NFT với `loading: true`, `description: ''`
> 5. Gọi `loadMetadata()` cho từng NFT để lấy description"

**Điểm nhấn:**
> `Buffer.from(hex, 'hex')` — browser support, không cần thư viện external.

---

### Bước 4.2 — loadMetadata (TODO 12)

**Hành động code:**
```typescript
const loadMetadata = async (tokenName: string, index: number) => {
  try {
    const response = await fetch(`http://localhost:8000/api/metadata/${tokenName}`);
    const data = await response.json();
    
    if (data.success) {
      let description = '';
      
      // Parse metadata (might be object with "description" key or direct string)
      if (typeof data.metadata === 'object') {
        description = data.metadata.description || JSON.stringify(data.metadata);
      } else {
        description = String(data.metadata);
      }
      
      setNfts(prev => prev.map((nft, i) => 
        i === index ? { ...nft, description, version: data.version, loading: false } : nft
      ));
    }
  } catch (error) {
    console.error(`Error loading metadata for ${tokenName}:`, error);
    setNfts(prev => prev.map((nft, i) => 
      i === index ? { ...nft, loading: false } : nft
    ));
  }
};
```

**Nội dung giảng:**
> "Load metadata cho 1 NFT:
> 1. GET `/api/metadata/${tokenName}`
> 2. Backend:
>    - Tìm ref token UTxO
>    - Parse datum → metadata map (bytes → string)
> 3. Parse metadata object:
>    - Có thể là `{ "description": "..." }` hoặc direct string
>    - Extract description
> 4. Update NFT tại index: `loading: false`, fill description + version
> 
> Gọi async cho từng NFT → load parallel → UI hiển thị dần."

---

### Bước 4.3 — Auto-fetch effect (TODO 13)

**Hành động code:** Thêm vào `NFTList` component:
```typescript
useEffect(() => {
  fetchNFTs();
}, [walletAddress, refreshTrigger]);
```

**Nội dung giảng:**
> "Auto-fetch khi:
> - Component mount (`walletAddress` lần đầu)
> - `refreshTrigger` thay đổi (từ MintForm sau khi mint thành công)
> 
> Dependency array `[walletAddress, refreshTrigger]` — re-run khi 1 trong 2 thay đổi."

---

## PHẦN 5: INTEGRATION (TODOs 14-16)

### Bước 5.1 — convertAddress (TODO 14)

**File:** `src/app/HomeContent.tsx`

**Hành động code:**
```typescript
const convertAddress = async () => {
  if (!walletAddress) {
    setBech32Address('');
    return;
  }
  
  try {
    const response = await fetch(
      `http://localhost:8000/api/convert-address?hex_address=${walletAddress}`
    );
    const data = await response.json();
    
    if (data.success) {
      setBech32Address(data.bech32_address);
    }
  } catch (error) {
    console.error('Error converting address:', error);
  }
};
```

**Nội dung giảng:**
> "Wallet trả hex address (CBOR), backend cần bech32 (addr_test1...). Endpoint convert:
> - Backend dùng PyCardano `Address.from_primitive(hex)`
> - Return bech32 string
> - Frontend lưu vào `bech32Address` → truyền cho components"

---

### Bước 5.2 — fetchScriptInfo (TODO 15)

**Hành động code:**
```typescript
const fetchScriptInfo = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/script-info');
    const data = await response.json();
    setScriptInfo(data);
  } catch (error) {
    console.error('Error fetching script info:', error);
  }
};
```

**Nội dung giảng:**
> "Lấy policy ID và store address từ backend để hiển thị. Backend tính sẵn khi startup (lifespan)."

---

### Bước 5.3 — Initialization effect (TODO 16)

**Hành động code:**
```typescript
useEffect(() => {
  convertAddress();
  fetchScriptInfo();
}, [walletAddress]);
```

**Nội dung giảng:**
> "Khi `walletAddress` thay đổi (kết nối ví mới):
> - Convert hex → bech32
> - Fetch script info
> 
> Dependency `[walletAddress]` — chạy lại khi đổi ví."

---


### Cuối cùng — Demo Flow hoàn chỉnh

**Hành động demo:**
1. Mở browser → `localhost:3000`
2. Click "Kết nối ví" → chọn Nami/Eternl
3. Nhập tên token + mô tả → click "Mint NFT"
4. Wallet popup → Approve → chờ confirm
5. NFT xuất hiện trong danh sách bên phải
6. Click "Update" → nhập mô tả mới → Approve
7. Click "Burn" → confirm → Approve

**Nội dung giảng:**
> "Demo flow hoàn chỉnh CIP-68:
> 
> **Mint:** Frontend gửi request → Backend build CBOR → Wallet ký → Backend submit → NFT sống trên chain
> 
> **Update:** Click Update → Backend tìm ref token → build update tx → Wallet ký → Metadata thay đổi on-chain
> 
> **Burn:** Click Burn → Backend tìm cả 2 token → build burn tx → Wallet ký → NFT bị destroy
> 
> Kiểm tra trên CardanoScan: ref token ở script address, user token ở ví, datum chứa metadata."

---

## TỔNG KẾT KHOÁ HỌC

> "Qua 3 video, chúng ta đã xây dựng hoàn chỉnh:
> 
> **Video 2:** Smart contract Aiken — 2 validators (mint + store),
> 
> **Video 3:** Off-chain Python — mint/update/burn với PyCardano, CLI scripts
> 
> **Video 4:** Web dApp — FastAPI backend + Next.js frontend + CIP-30 wallet integration
> 
> Người học giờ có thể:
> - Viết smart contract CIP-68 chuẩn
> - Build transaction Plutus bằng PyCardano  
> - Tạo dApp hoàn chỉnh với browser wallet signing
> - Deploy và test trên Preprod testnet
> 
> Bước tiếp theo cho người học tự nghiên cứu: parameterized contracts, thêm metadata fields (image, attributes), royalty, marketplace integration."
