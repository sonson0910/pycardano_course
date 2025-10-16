# 🚀 Quick Start - Run Smart Contract Tests

## Choose Your Method

### Method 1: Automatic (Recommended) ⭐

**Windows**:
```powershell
cd d:\venera\cardano\pycardano_course\computer_vision_ipfs
.\run_tests.bat
```

**Linux/Mac**:
```bash
cd computer_vision_ipfs
chmod +x run_tests.sh
./run_tests.sh
```

---

### Method 2: Manual Step-by-Step

#### Step 1: Build Smart Contracts
```bash
cd smart_contracts
aiken build
```

Expected: `✓ 0 errors, 0 warnings`

#### Step 2: Run Python Tests
```bash
cd ../backend
pip install pytest pytest-mock
pytest tests/test_smart_contracts.py -v
```

Expected: `30 passed`

---

## What Gets Tested

### Aiken Smart Contracts (25+ tests)
✓ Register DID validation
✓ Update DID operations
✓ Verify face identity
✓ Revoke DID access
✓ Edge cases & boundaries
✓ Complete lifecycle

### Python Backend (30+ tests)
✓ Blockfrost API connection
✓ Wallet operations
✓ Balance queries
✓ UTxO management
✓ Transaction building
✓ Action validation
✓ Error handling

---

## Documentation

| File | Purpose |
|------|---------|
| `TESTCASE_README.md` | This file - Quick overview |
| `TESTING.md` | Detailed test explanations |
| `TEST_CASES_SUMMARY.md` | Coverage matrix & statistics |
| `TEST_CREATION_SUMMARY.md` | What was created |

---

## Expected Results

```
✅ Aiken Build
   - 0 errors, 0 warnings
   - plutus.json generated

✅ Python Tests
   - 30+ tests passed
   - ~95% code coverage
```

---

## After Testing

1. ✅ Review `TESTING.md` for detailed explanations
2. ✅ Check coverage report: `pytest tests/test_smart_contracts.py --cov`
3. ✅ Deploy to Cardano Preview testnet
4. ✅ Run integration tests with real Blockfrost API

---

**Total Tests**: 55+
**Status**: Ready ✨
