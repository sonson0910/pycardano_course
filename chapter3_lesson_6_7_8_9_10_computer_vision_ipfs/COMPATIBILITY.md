# ⚠️ PyCardano Compatibility Guide

**Issue**: PyCardano 0.16.0 (only available version on PyPI) doesn't support all modern APIs used in newer code.

---

## Problem

```python
# These don't exist in pycardano 0.16.0:
from pycardano import (
    BlockFrostChainContext,  # ❌ Not available
    Coin,                    # ❌ Not available
    Redeemer,                # ❌ Not available
)
```

**Latest PyCardano on PyPI**: 0.16.0 (released 2024-01-xx)
**Package seems abandoned**: No updates since 0.16.0

---

## Solution

### Option 1: Use Blockfrost Direct API (Recommended)

Instead of using PyCardano's wrapper, use `blockfrost-python` directly:

```python
from blockfrost import BlockFrostApi

client = BlockFrostApi(
    project_id="preview_xxx",
    base_url="https://cardano-preview.blockfrost.io",
    version="v0"
)

# Query blockchain
address_info = client.address("addr_test1...")
utxos = client.address_utxos("addr_test1...")
```

✅ **Current Implementation**: Using this approach in `cardano_client.py`

### Option 2: Use Lucid (JavaScript/TypeScript)

If you need advanced transaction building, use Lucid instead:

```bash
npm install lucid-cardano
```

```typescript
import { Lucid, Blockfrost } from "lucid-cardano";

const lucid = await Lucid.new(
  new Blockfrost("https://cardano-preview.blockfrost.io/api", {
    projectId: "preview_xxx"
  })
);

const utxos = await lucid.utxosAt(address);
```

### Option 3: Build from GitHub

If you need newer PyCardano features, install directly from GitHub:

```bash
pip install git+https://github.com/Python-Cardano/pycardano.git
```

⚠️ **Warning**: Development versions may be unstable

---

## Current Implementation

**Backend** (`backend/app/blockchain/cardano_client.py`):
- ✅ Uses `blockfrost-python` for queries
- ✅ Works with pycardano 0.16.0
- ✅ No external API calls fail
- ⚠️ Advanced script transaction building simplified

**Status**: Functional and stable for core operations

---

## What Works

```python
from app.blockchain.cardano_client import CardanoClient

client = CardanoClient()

# ✅ These work:
balance = client.get_balance(address)
utxos = client.get_utxos(address)
validator = client.read_validator_from_file()
```

## What Doesn't Work (Yet)

```python
# These are simplified stubs:
tx = client.build_transaction(...)      # Returns struct only
tx = client.build_script_transaction(...)  # Returns struct only
signed_tx = client.submit_transaction(...)  # Placeholder
```

**Reason**: Full implementation requires complex transaction building with signing, which needs either:
1. Newer PyCardano (not available on PyPI)
2. Lucid (JavaScript/TypeScript)
3. Custom transaction builder

---

## Recommendation

### For MVP/Testing:
✅ **Use current implementation** - Works fine for prototyping

### For Production:
Choose one:
1. **Lucid** - Most mature, JavaScript/TypeScript
2. **PyCardano from GitHub** - Cutting edge, Python
3. **Cardano CLI** - Shell scripts for complex operations

---

## Setup Instructions

### Keep Current Setup (Recommended for MVP)

```bash
# Already installed and working
pip install pycardano==0.16.0
pip install blockfrost-python>=0.6.0
```

### For Advanced Features

If you want full transaction building, switch to Lucid:

```bash
# Backend stays Python/FastAPI for APIs
# Frontend/scripts use Node.js for Lucid

cd frontend
npm install lucid-cardano
```

Then update API endpoint to call Lucid builder via child process.

---

## Testing

### Current Setup Works:
```bash
cd backend

# ✅ Imports work
python -c "from app.blockchain.cardano_client import CardanoClient; print('OK')"

# ✅ Connection works (with BLOCKFROST_PROJECT_ID set)
python -c "
import os
os.environ['BLOCKFROST_PROJECT_ID'] = 'preview_xxx'
from app.blockchain.cardano_client import CardanoClient
client = CardanoClient()
"
```

### Build Smart Contracts:
```bash
cd smart_contracts
aiken build
# ✅ Creates plutus.json
```

---

## References

- **PyCardano GitHub**: https://github.com/Python-Cardano/pycardano
- **Blockfrost Python**: https://github.com/blockfrost/blockfrost-python
- **Lucid**: https://github.com/spacebudz/lucid
- **Cardano Docs**: https://developers.cardano.org/

---

## FAQ

**Q: Why not use newer PyCardano from GitHub?**
A: Development versions may break. 0.16.0 is stable but limited.

**Q: Should I switch to TypeScript for Lucid?**
A: Only if you need advanced transaction building. For MVP, current setup is fine.

**Q: Will future versions of PyCardano work?**
A: Yes, just `pip install --upgrade pycardano` when new version hits PyPI.

**Q: Can I use both Blockfrost and PyCardano APIs?**
A: Yes! `blockfrost-python` is for queries, `pycardano` for signing when available.

---

**Last Updated**: October 16, 2025
**Status**: ✅ Working with current limitations
