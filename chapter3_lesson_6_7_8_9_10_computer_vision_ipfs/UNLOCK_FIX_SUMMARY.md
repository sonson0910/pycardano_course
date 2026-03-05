# UNLOCK DID - FIXES APPLIED & STATUS

## What Was Wrong
```
AttributeError: 'TransactionBuilder' object has no attribute 'add_script'. Did you mean: 'all_scripts'?
```

## What Was Fixed ✅

### 1. API Method (FIXED)
**Before:**
```python
builder.add_script(script)
builder.add_redeemer(redeemer, script_utxo)
```

**After:**
```python
builder.add_script_input(
    utxo=script_utxo,
    script=script,
    redeemer=redeemer
)
```

### 2. Datum Structure (FIXED)
**Before (3 fields):**
```python
@dataclass
class DIDDatum(PlutusData):
    did: bytes
    face_hash: bytes
    created_at: int
```

**After (5 fields - matches Aiken):**
```python
@dataclass
class DIDDatum(PlutusData):
    did_id: bytes           # "did:cardano:sonson0910"
    face_ipfs_hash: bytes   # "QmExample123456789abcdef"
    owner: bytes            # Wallet pubkey hash
    created_at: int         # Timestamp
    verified: int           # 0=False, 1=True
```

### 3. Boolean Encoding (FIXED)
- Changed from Python `bool` to `int 0/1` for proper CBOR encoding

## Test Results

✅ **DID Creation**: Works perfectly
- Transaction: `0430638b6c884926d8d7ea2960ca20d33f20a5797179caa809ae6bcce9e91865`

❌ **Unlock Transaction**: Builds but fails validator
- Error: `ScriptFailures=Namespace()` (empty failures)
- Means validator is executing but returning False

## Current Issue

The validator check is failing even though:
- ✅ Data is correctly CBOR encoded
- ✅ Redeemer is correctly passed
- ✅ Datum structure matches Aiken

Hypothesis: The validator logic itself needs review.
Possible causes:
1. Field comparison `did_id != #""` not working as expected
2. Byte encoding mismatch between PyCardano and Aiken
3. Plutus Bool constructor format issue

## How to Continue

### Option 1: Test with Always-True Validator
Create a test validator that always returns True to isolate the issue:

```aiken
validator test_did {
  spend(_datum, _action, _ref, _self) {
    True  // Always passes
  }
}
```

If this works → issue is in validation logic
If this fails → issue is in framework/encoding

### Option 2: Add Logging to Validator
Modify `did_manager.ak` to return specific values to see which check fails:

```aiken
fn validate_register(datum: DIDDatum) -> Bool {
  let check1 = datum.did_id != #""
  let check2 = datum.face_ipfs_hash != #""
  let check3 = datum.created_at > 0

  // Return True/False based on which passes
  check1 && check2 && check3
}
```

### Option 3: Check CBOR Encoding Directly
Compare what PyCardano sends vs what Aiken expects:

```python
# Print the CBOR
print(f"Datum CBOR: {datum.to_cbor()}")

# Compare with what the validator sees in the transaction logs
```

## Files Modified
- `backend/create_did.py` - ✅ Fixed (5-field datum with owner and verified)
- `backend/unlock_did.py` - ✅ Rebuilt from scratch (uses add_script_input)
- `backend/create_did.py` - ✅ Updated print statements

## Quick Test
```bash
cd backend
python create_did.py       # Creates DID
sleep 35                   # Wait for confirmation
python unlock_did.py       # Try to spend
```

## Next Phase
Once validator is fixed, we can:
1. ✅ Test all 4 redeemers (Register, Update, Verify, Revoke)
2. ✅ Build full lifecycle (Create → Register → Update → Verify → Revoke)
3. ✅ Integrate with frontend API
4. ✅ Test React component

## Key Files
- Script validator: `smart_contracts/validators/did_manager.ak`
- Datum types: `smart_contracts/lib/computer_vision_dapp/types.ak`
- Creation: `backend/create_did.py`
- Unlock: `backend/unlock_did.py`
- Debugging: `UNLOCK_DEBUG.md` and `UNLOCK_SOLUTION.md`
