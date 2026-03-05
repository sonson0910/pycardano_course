# Smart Contract Testing Documentation

## Overview
This project includes comprehensive test suites for both:
1. **Aiken Smart Contracts** - Unit tests for DID management validators
2. **Python Backend** - Integration tests for CardanoClient

---

## Aiken Smart Contract Tests

### Test File: `smart_contracts/lib.test.ak`

The test suite validates all DID management operations following Aiken testing conventions.

#### Test Categories

### 1. Registration Tests (`Register` Action)

**Valid Registration**
- `register_valid_did()`: Valid DID with all required fields
- Tests: did_id ≠ "", face_ipfs_hash ≠ "", created_at > 0

**Invalid Registrations**
- `register_empty_did_id()`: Rejects empty did_id
- `register_empty_face_hash()`: Rejects empty face_ipfs_hash
- `register_invalid_created_at_zero()`: Rejects created_at = 0
- `register_invalid_created_at_negative()`: Rejects created_at < 0
- `register_all_fields_empty()`: Rejects when all critical fields are empty

**Edge Cases**
- `large_did_id()`: Handles large ByteArray values
- `very_old_timestamp()`: Accepts created_at = 1 (minimum valid)
- `future_timestamp()`: Accepts timestamps far in future

### 2. Update Tests (`Update` Action)

**Update Behavior**
- `update_always_succeeds()`: Update is permissive, accepts any valid datum
- `update_with_empty_did()`: Update succeeds even with empty did_id

**Key Insight**: Update action always returns True (no validation required)

### 3. Verification Tests (`Verify` Action)

**Valid Verification**
- `verify_valid_did()`: Both did_id and face_ipfs_hash present

**Invalid Verifications**
- `verify_empty_did_id()`: Rejects empty did_id
- `verify_empty_face_hash()`: Rejects empty face_ipfs_hash
- `verify_both_empty()`: Rejects when both fields empty

**Requirements**: did_id ≠ "" AND face_ipfs_hash ≠ ""

### 4. Revocation Tests (`Revoke` Action)

**Valid Revocation**
- `revoke_valid_did()`: Valid did_id allows revocation
- `revoke_verified_status_irrelevant()`: Verification status doesn't affect revocation

**Invalid Revocation**
- `revoke_empty_did_id()`: Rejects empty did_id

**Requirements**: did_id ≠ ""

### 5. Integration Tests

**Complete Lifecycle**
- `complete_did_lifecycle()`: Register → Update → Verify → Revoke
  - All steps should succeed in sequence
  - Demonstrates realistic DID management flow

**Multiple DIDs**
- `multiple_dids_independent()`: Multiple DIDs don't interfere
  - Each DID maintains independent state
  - Validation is independent per DID

#### Running Aiken Tests

```bash
cd smart_contracts

# Run all tests
aiken check

# Build project (generates plutus.json)
aiken build

# View test results
aiken test
```

#### Test Validation Logic

**Register Action Validation**
```aiken
validate_register(datum):
  - did_not_empty = datum.did_id != #""
  - ipfs_hash_valid = datum.face_ipfs_hash != #""
  - created_at_valid = datum.created_at > 0
  - RETURN: all three conditions AND'ed
```

**Verify Action Validation**
```aiken
validate_verify(datum):
  - RETURN: datum.did_id != #"" && datum.face_ipfs_hash != #""
```

**Update Action Validation**
```aiken
validate_update(_datum):
  - RETURN: True  (always valid)
```

**Revoke Action Validation**
```aiken
validate_revoke(datum):
  - RETURN: datum.did_id != #""
```

---

## Python Backend Tests

### Test File: `backend/tests/test_smart_contracts.py`

Comprehensive pytest suite for CardanoClient and blockchain operations.

#### Test Classes

### 1. CardanoClientInitialization

**Success Cases**
- `test_init_with_valid_blockfrost_key()`: Creates client with valid API key
- Mocks BlockFrostApi connection
- Verifies health check passes

**Failure Cases**
- `test_init_without_blockfrost_key()`: Raises ValueError if env var not set
- `test_init_connection_failure()`: Raises exception if Blockfrost unreachable

### 2. WalletOperations

**Wallet Loading**
- `test_load_wallet_success()`: Loads signing key and creates address
- `test_load_wallet_file_not_found()`: Raises FileNotFoundError if .sk missing

**Expected Flow**:
```python
1. Load PaymentSigningKey from file
2. Derive PaymentVerificationKey
3. Create Address from verification key hash
4. Return Address object
```

### 3. BalanceOperations

**Success Cases**
- `test_get_balance_success()`: Retrieves balance from Blockfrost
- `test_get_balance_zero()`: Handles zero balance correctly

**Error Cases**
- `test_get_balance_api_error()`: Raises exception if API call fails

### 4. UTxOOperations

**Query Tests**
- `test_get_utxos_success()`: Returns list of UTxOs
- `test_get_utxos_empty()`: Handles empty UTxO list

### 5. TransactionBuilding

**Transaction Creation**
- `test_build_transaction_success()`: Builds transaction with valid parameters
- `test_build_transaction_zero_amount()`: Allows zero amount

**Returned Structure**:
```python
{
  "type": "transaction",
  "sender": address_str,
  "receiver": address_str,
  "amount": int,
  "status": "not_implemented"
}
```

### 6. ActionValidation

**Register Validation**
- `test_validate_register_valid()`: Accepts valid Register action
- `test_validate_register_empty_did()`: Rejects empty did_id

**Update Validation**
- `test_validate_update_always_valid()`: Update always passes

**Verify Validation**
- `test_validate_verify_valid()`: Requires both did_id and face_ipfs_hash

**Revoke Validation**
- `test_validate_revoke_valid()`: Requires non-empty did_id

### 7. ValidatorFileOperations

**File Handling**
- `test_read_validator_file_not_found()`: Raises FileNotFoundError if plutus.json missing
- `test_read_validator_file_success()`: Reads and parses validator from plutus.json

**Expected Return**:
```python
{
  "type": "PlutusV3",
  "compiled_code": bytes,
  "script_hash": "hash_string"
}
```

### 8. ScriptTransactions

**Script Transaction Building**
- `test_build_script_transaction_register()`: Builds script tx for Register
- `test_build_script_transaction_invalid_action()`: Validates action before building

### 9. QueryScriptUTxO

**Script Address Queries**
- `test_query_script_utxo_not_found()`: Returns None if no UTxOs
- `test_query_script_utxo_with_utxos()`: Handles case when UTxOs exist

#### Running Python Tests

```bash
cd backend

# Install test dependencies
pip install pytest pytest-cov pytest-mock

# Run all tests
pytest tests/test_smart_contracts.py -v

# Run specific test class
pytest tests/test_smart_contracts.py::TestCardanoClientInitialization -v

# Run with coverage report
pytest tests/test_smart_contracts.py --cov=app.blockchain --cov-report=html

# Run specific test
pytest tests/test_smart_contracts.py::TestActionValidation::test_validate_register_valid -v
```

#### Test Mocking Strategy

All tests use mocks to avoid actual Blockfrost API calls:

```python
@patch("app.blockchain.cardano_client.BlockFrostApi")
def test_example(mock_blockfrost):
    mock_client = MagicMock()
    mock_blockfrost.return_value = mock_client

    # Mock API responses
    mock_client.health.return_value = {"time": "2024-10-16"}
    mock_client.address.return_value = {"amount": {"coin": "5000000"}}
```

---

## Test Data

### Sample DID Datum

```python
DIDDatum(
  did_id: b"0001",
  face_ipfs_hash: b"QmHash123456789",
  owner: b"owner_pubkey_hash",
  created_at: 1696000000,
  verified: False
)
```

### Action Types

```python
Register()  # Register new DID
Update()    # Update existing DID
Verify()    # Verify identity
Revoke()    # Revoke DID
```

---

## Validation Rules Summary

### Register Requirements
- ✅ did_id ≠ ""
- ✅ face_ipfs_hash ≠ ""
- ✅ created_at > 0
- ❌ All must pass (AND logic)

### Update Requirements
- ✅ Always passes (no validation)

### Verify Requirements
- ✅ did_id ≠ ""
- ✅ face_ipfs_hash ≠ ""
- ❌ Both must pass (AND logic)

### Revoke Requirements
- ✅ did_id ≠ ""

---

## Current Limitations

### Aiken Tests (lib.test.ak)
- Tests return True/False indicators (Aiken test framework limitations)
- Full integration tests should be run via `aiken check`
- Some edge cases noted but not fully executable in current Aiken version

### Python Tests (test_smart_contracts.py)
- Uses mocks instead of real Blockfrost API
- Full transaction signing not implemented
- Script transaction building returns stubs

### Full End-to-End Testing
- Requires live Blockfrost testnet access
- Needs valid Cardano Preview testnet wallet with ADA
- Should test after deployment to testnet

---

## Running Full Test Suite

```bash
# 1. Check Aiken syntax and build
cd smart_contracts
aiken build

# 2. Run Python unit tests
cd ../backend
pip install -r requirements.txt
pip install pytest pytest-cov pytest-mock
pytest tests/test_smart_contracts.py -v --cov

# 3. Integration testing (manual, with testnet)
export BLOCKFROST_PROJECT_ID="preview_xxx..."
python -m app.blockchain.cardano_client
```

---

## Expected Test Results

### Aiken Build
```
✓ 0 errors, 0 warnings
✓ plutus.json generated
✓ All validators compile
```

### Python Tests
```
✓ 30+ tests total
✓ All mocked API calls succeed
✓ Validation logic verified
✓ Error handling tested
```

---

## Next Steps

1. **Deploy to Testnet**
   - Use plutus.json from aiken build
   - Test with real Blockfrost API

2. **Add Integration Tests**
   - Connect to Cardano Preview testnet
   - Create real DIDs and test lifecycle

3. **Frontend Testing**
   - Test React DApp components
   - Verify blockchain interactions

4. **Security Testing**
   - Verify no fund loss scenarios
   - Test edge cases with real UTxOs

---

## References

- [Aiken Documentation](https://aiken-lang.org)
- [Cardano Documentation](https://developers.cardano.org)
- [Blockfrost API](https://blockfrost.io)
- [PyCardano](https://github.com/Python-Cardano/PyCardano)
