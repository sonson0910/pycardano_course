# QUICK COMMAND REFERENCE

## Test the System

```bash
# Navigate to backend
cd backend

# 1. Create a new DID (will lock 2 ADA to script)
python create_did.py
# Result: Shows TX hash like 0430638b6c884926d8d7ea2960ca20d33f20a5797179caa809ae6bcce9e91865

# 2. Wait for confirmation
sleep 35

# 3. Try to unlock it (spend from script)
python unlock_did.py
# Current status: Builds and submits, but validator rejects
```

## Check Results

```bash
# View on CardanoScan
# https://preprod.cardanoscan.io/transaction/{TX_HASH}

# Check wallet balance
python backend/summary.py

# Check all UTxOs
python backend/check_balance.py
```

## Debug the Validator

```bash
# Check what's deployed
grep "script_hash" backend/status.py

# View the validator code
cat smart_contracts/validators/did_manager.ak

# View the type definitions
cat smart_contracts/lib/computer_vision_dapp/types.ak

# Check compiled code
cat smart_contracts/plutus.json | python -m json.tool | head -50
```

## Key Transaction

```
Created DID:
  TX: 0430638b6c884926d8d7ea2960ca20d33f20a5797179caa809ae6bcce9e91865

View:
  https://preprod.cardanoscan.io/transaction/0430638b6c884926d8d7ea2960ca20d33f20a5797179caa809ae6bcce9e91865
```

## Important Files

```
backend/
  create_did.py       ✅ Creates DID
  unlock_did.py       ⚠️ Attempts unlock

smart_contracts/
  validators/did_manager.ak   - Main validator logic
  lib/computer_vision_dapp/types.ak - Type definitions
  plutus.json                 - Compiled validator

Documentation/
  UNLOCK_FIX_SUMMARY.md             - What was fixed
  UNLOCK_COMPLETE_DIAGNOSIS.md      - Technical details
  UNLOCK_CODE_REFERENCE.md          - Code examples
  CONTINUATION_GUIDE.md             - How to debug
```

## Key Configuration

```python
# Preprod Testnet
Network: TESTNET
API Key: preprod0K9MnKqsU21MJvqu00V4Laf4pz7dALPK
Base URL: https://cardano-preprod.blockfrost.io/api/

# Wallet
Address: addr_test1vpx302mqdefht0wly42wlpjmd2rm7xr85j6sgvej8pywusc38sglh

# Script
Script Hash: 33d066a565bf81c6ae2e6f97bebd453161f39e02ba53351f32ea7486
Script Address: addr_test1wqeaqe49vklcr34w9ehe004ag5ckruu7q2a9xdglxt48fpsk284d3
```

## The Core Fix

```python
# ❌ BEFORE (Error):
builder.add_script(script)
builder.add_redeemer(redeemer, script_utxo)

# ✅ AFTER (Fixed):
builder.add_script_input(
    utxo=script_utxo,
    script=script,
    redeemer=redeemer
)
```

## Status Codes

- ✅ = Working / Fixed
- ⚠️ = In Progress / Needs Testing
- ❌ = Not Working / Error

## Next Steps

1. Read: `CONTINUATION_GUIDE.md` (10 min)
2. Debug: Test always-true validator (15 min)
3. Fix: Address identified issue (varies)
4. Test: Verify unlock works (5 min)
5. Integrate: Full lifecycle (30 min)

## Files Modified in This Session

- ✅ `backend/create_did.py` - Fixed datum (5 fields)
- ✅ `backend/unlock_did.py` - Fixed API (add_script_input)
- ✅ All documentation files created/updated

## Support Files

For specific issues, refer to:
- API Error → `UNLOCK_CODE_REFERENCE.md`
- Validator Issue → `UNLOCK_COMPLETE_DIAGNOSIS.md`
- Debugging → `CONTINUATION_GUIDE.md`
- Overview → `UNLOCK_FIX_SUMMARY.md`
