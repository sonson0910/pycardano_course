# UNLOCK DID TRANSACTION - DEBUGGING SUMMARY

## Current Issue Status
Script validation is failing with empty `ScriptFailures` namespace

## Latest Fix Applied
- ✅ Changed from add_script() + add_redeemer() to add_script_input()
- ✅ Updated datum to 5 fields (matching Aiken types.ak)
- ✅ Using int 0/1 for boolean encoding
- ✅ TX 0430638b6c884926... created successfully
- ⚠️ Unlock validation still failing with empty ScriptFailures

## Debug Path Forward

## Issue Summary

Attempting to spend from a PlutusV3 script address on Cardano Preprod testnet using a Register redeemer.

## Root Causes Identified

### 1. **Datum Structure Mismatch** ✅ FIXED
- **Problem**: Created datum had 3 fields (did, face_hash, created_at)
- **Validator Expected**: 5 fields (did_id, face_ipfs_hash, owner, created_at, verified)
- **Solution**: Updated create_did.py to include all 5 fields with correct names

### 2. **Boolean Type Encoding** ⚠️ IN PROGRESS
- **Problem**: Aiken Bool is not Python bool - it's a constructor type (False=0, True=1)
- **Validator Expected**: `verified: Bool` (algebraic data type)
- **Current Attempt**: Using RawPlutusData and constructor-based Bool types

### 3. **API Issue: add_script_input()**  ✅ FIXED
- **Problem**: Originally used `builder.add_script()` which doesn't exist
- **Solution**: Changed to `builder.add_script_input(utxo=..., script=..., redeemer=...)`

## Test Transactions Created

1. **TX: bb9476b549096bec77c00a0fa3ee66bdbd5542e9b6de773fad8fb5a95c1b6971**
   - 5-field datum structure
   - Int-based `verified` field (0 = False)
   - Status: CREATED ON-CHAIN

2. **TX: d912ceb4c310777b6e96f4bfa9498ddc99b6d4290cc995430f2381308520694a**
   - Int-based `verified` field
   - Submission FAILED - CBOR decode error: "expected 4 fields, found 3"
   - Reason: Boolean encoding issue

## Files Modified

- `backend/create_did.py` - Updated datum structure with 5 fields + Bool type
- `backend/unlock_did_fixed.py` - Fixed API calls, correct datum structure
- `backend/unlock_did.py` - Same fixes applied
- `backend/deploy.py` through `backend/status.py` - PlutusV2→V3 migration (COMPLETED)

## Next Steps

### Option A: Simplify with Integer Boolean
- Change Bool field to just use integers (0/1) in Python
- Let PyCardano handle encoding automatically
- Check if Aiken validator accepts this

### Option B: Use RawCBOR
- Manually construct Bool as CBOR
- Explicit control over serialization format

### Option C: Modify Validator
- Create simpler validator that doesn't require Bool field
- Or use Option type for Bool

## API Reference

### Correct PyCardano Script Spending Pattern
```python
# Load script
script = PlutusV3Script(bytes.fromhex(compiled_code))

# Build transaction
builder = TransactionBuilder(context)
builder.add_input_address(wallet_addr)  # For fees

# CORRECT way to add script input:
builder.add_script_input(
    utxo=script_utxo,          # UTxO to spend
    script=script,              # The validator
    redeemer=Redeemer(action)   # The action/redeemer
)

# Add output and sign
builder.add_output(...)
signed_tx = builder.build_and_sign(...)
```

## Validator Status

- **Type**: PlutusV3 (confirmed)
- **Size**: 473 bytes
- **Hash**: 33d066a565bf81c6ae2e6f97bebd453161f39e02ba53351f32ea7486
- **Validators**: 4 (Register=0, Update=1, Verify=2, Revoke=3)
- **Datum Fields**: 5 (did_id, face_ipfs_hash, owner, created_at, verified)
- **Bool Encoding**: Constructor-based (False=0, True=1)

## Current Status

- ✅ Wallet funded (10,000 ADA)
- ✅ Create transaction implemented and tested
- ✅ API call corrected (add_script_input)
- ✅ PlutusV2→V3 migration complete
- ⏳ Bool encoding - needs resolution
- ⏳ Unlock transaction - waiting for Bool fix

## Commands to Resume

```bash
# After Bool issue resolved:
python create_did.py                 # Create new DID
sleep 35                            # Wait for confirmation
python unlock_did_fixed.py          # Spend from script
```

## Reference Links

- Blockfrost Preprod: https://preprod.cardanoscan.io/
- Wallet: addr_test1vpx302mqdefht0wly42wlpjmd2rm7xr85j6sgvej8pywusc38sglh
- Script Address: addr_test1wqeaqe49vklcr34w9ehe004ag5ckruu7q2a9xdglxt48fpsk284d3
