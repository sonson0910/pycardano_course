# UNLOCK DID - WORKING CODE REFERENCE

## Complete Fixed Code

### 1. Create DID (WORKING ✅)

**File:** `backend/create_did.py`

Key parts:
```python
# Correct 5-field DID Datum
@dataclass
class DIDDatum(PlutusData):
    CONSTR_ID = 0
    did_id: bytes           # "did:cardano:sonson0910"
    face_ipfs_hash: bytes   # "QmExample123456789abcdef"
    owner: bytes            # Wallet pubkey hash
    created_at: int         # Unix timestamp
    verified: int           # 0 = False, 1 = True

# Create with correct values
datum = DIDDatum(
    did_id=b"did:cardano:sonson0910",
    face_ipfs_hash=b"QmExample123456789abcdef",
    owner=bytes.fromhex(str(vk_hash)),
    created_at=int(datetime.now().timestamp()),
    verified=0  # False
)

# Normal transaction building
builder = TransactionBuilder(context)
builder.add_input_address(addr)
builder.add_output(
    TransactionOutput(
        address=Address(payment_part=script_hash, network=Network.TESTNET),
        amount=2_000_000,
        datum=datum
    )
)
```

**Usage:**
```bash
cd backend
python create_did.py
```

**Result:** ✅ Creates and submits DID successfully

---

### 2. Unlock DID (BUILDS BUT VALIDATES FAIL ⚠️)

**File:** `backend/unlock_did.py`

Key parts:
```python
# Correct Datum Structure
@dataclass
class DIDDatum(PlutusData):
    CONSTR_ID = 0
    did_id: bytes
    face_ipfs_hash: bytes
    owner: bytes
    created_at: int
    verified: int

# Correct Redeemer Structure
@dataclass
class RegisterAction(PlutusData):
    CONSTR_ID = 0
    action: int  # 0=Register, 1=Update, 2=Verify, 3=Revoke

# CORRECT API: Use add_script_input()
redeemer = Redeemer(RegisterAction(action=0))

builder = TransactionBuilder(context)
builder.add_input_address(addr)  # Wallet input for fees

# ✅ THIS IS THE FIX:
builder.add_script_input(
    utxo=script_utxo,
    script=script,
    redeemer=redeemer
)

builder.add_output(
    TransactionOutput(
        address=addr,
        amount=output_amount
    )
)

signed_tx = builder.build_and_sign(
    signing_keys=[sk],
    change_address=addr,
)
```

**Usage:**
```bash
cd backend
python create_did.py
sleep 35  # Wait for confirmation
python unlock_did.py
```

**Result:** ⚠️ Builds and submits, but validator rejects

---

## The ONE Key Fix

### BEFORE (Broken):
```python
builder.add_script(script)
builder.add_redeemer(redeemer, script_utxo)
```

### AFTER (Fixed):
```python
builder.add_script_input(
    utxo=script_utxo,
    script=script,
    redeemer=redeemer
)
```

---

## Other Important Fixes

### Datum Structure
Ensure 5 fields in correct order:
1. `did_id: bytes`
2. `face_ipfs_hash: bytes`
3. `owner: bytes`
4. `created_at: int`
5. `verified: int` (0 or 1, NOT bool)

### Imports
```python
from pycardano import (
    BlockFrostChainContext,
    Address,
    Network,
    PaymentSigningKey,
    PaymentVerificationKey,
    PlutusV3Script,      # NOT PlutusV2Script
    ScriptHash,
    PlutusData,
    TransactionBuilder,
    TransactionOutput,
    Redeemer,
)
```

### Configuration
```python
api_key = 'preprod0K9MnKqsU21MJvqu00V4Laf4pz7dALPK'
base_url = 'https://cardano-preprod.blockfrost.io/api/'

# Load validator
with open(os.path.join('..', 'smart_contracts', 'plutus.json')) as f:
    plutus = json.load(f)

validator_data = plutus['validators'][0]
script = PlutusV3Script(bytes.fromhex(validator_data['compiledCode']))
script_hash = ScriptHash(bytes.fromhex(validator_data['hash']))
```

---

## Test Status

### ✅ Working
- Transaction building
- Transaction signing
- Transaction submission
- Blockfrost communication
- Datum encoding
- Redeemer encoding
- CBOR serialization

### ⚠️ Debugging
- Validator execution (returns False)
- Validator logic (need to check Aiken code)

---

## Current Test

```
Created DID:
  TX: 0430638b6c884926d8d7ea2960ca20d33f20a5797179caa809ae6bcce9e91865
  URL: https://preprod.cardanoscan.io/transaction/0430638b6c884926d8d7ea2960ca20d33f20a5797179caa809ae6bcce9e91865

Unlock Attempt:
  Status: Builds successfully ✅
  Result: Validator rejects ❌
  Error: ScriptFailures=Namespace() (empty)
  Meaning: Validator ran but returned False
```

---

## Next Steps

1. Test with always-true validator
2. Check Aiken validator logic
3. Verify byte comparison works in Plutus
4. Once fixed, full system is ready

## Quick Copy-Paste

Save this for reference when debugging:

```python
# The key fix:
builder.add_script_input(utxo=script_utxo, script=script, redeemer=redeemer)

# Not this (wrong):
builder.add_script(script)
builder.add_redeemer(redeemer, script_utxo)
```
