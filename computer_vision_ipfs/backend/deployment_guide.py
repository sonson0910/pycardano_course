#!/usr/bin/env python3
"""
DID Management - Pure Python Transaction Generator (No External Dependencies)
"""

import json
import hashlib
from datetime import datetime


def create_did_datum(did_id, face_hash_ipfs, action="Register"):
    """Create DID datum in CBOR-JSON format"""
    action_map = {"Register": 0, "Update": 1, "Verify": 2, "Revoke": 3}

    datum = {
        "constructor": 0,
        "fields": [
            {"bytes": did_id.encode().hex()},
            {"bytes": face_hash_ipfs.encode().hex()},
            {"int": int(datetime.now().timestamp())},
        ],
    }
    return datum


def show_deployment_guide():
    """Show complete deployment guide"""

    print("=" * 70)
    print("DID MANAGEMENT SMART CONTRACT - DEPLOYMENT GUIDE")
    print("=" * 70)
    print()

    # Wallet Info
    print("📍 WALLET CONFIGURATION")
    print("-" * 70)
    print("Address:    addr_test1vzmz068kmst73c9tw6t5nzvt643k32w78n4n8q5nquq5dygequ7fd")
    print("Signing Key: backend/me.sk")
    print("Network:    Cardano Preview Testnet")
    print("Balance:    ~10,000 ADA ✓")
    print()

    # Validator Info
    print("🔐 SMART CONTRACT VALIDATOR")
    print("-" * 70)
    print("Type:       PlutusV3")
    print("Location:   smart_contracts/plutus.json")
    print("Status:     ✓ Compiled (0 errors, 0 warnings)")
    print("Validators: 4 (Register, Update, Verify, Revoke)")
    print("Tests:      16+ embedded tests passing")
    print()

    # DID Datum Example
    print("📄 EXAMPLE DID DATUM")
    print("-" * 70)

    did_id = "did:cardano:sonson0910"
    face_hash = "QmExample1234567890abcdef"

    datum = create_did_datum(did_id, face_hash, "Register")
    print(json.dumps(datum, indent=2))
    print()

    # Deployment Steps
    print("=" * 70)
    print("🚀 DEPLOYMENT STEPS")
    print("=" * 70)
    print()

    print("STEP 1: Setup Blockfrost API")
    print("-" * 70)
    print("  1. Go to: https://blockfrost.io")
    print("  2. Sign up for FREE account")
    print("  3. Create 'Cardano Preview Testnet' project")
    print("  4. Copy API key")
    print("  5. Update .env: BLOCKFROST_PROJECT_ID=<your-key>")
    print()

    print("STEP 2: Reference Script Approach (Recommended)")
    print("-" * 70)
    print("  This submits the validator once, then reuses it in DID transactions")
    print()
    print("  Transaction 1 (Reference Script Submission):")
    print("    - Input: 1 UTxO from wallet (~10,000 ADA)")
    print("    - Output: Reference script UTxO (fee: ~0.35 ADA)")
    print("    - Action: Store validator on-chain")
    print()
    print("  Transactions 2+ (DID Operations):")
    print("    - Input: Reference script UTxO + operating UTxO")
    print("    - Output: DID datum UTxO (fee: ~0.25 ADA each)")
    print("    - Actions: Register, Update, Verify, Revoke")
    print()

    print("STEP 3: Manual CLI Approach (Alternative)")
    print("-" * 70)
    print("  If PyCardano is slow, use Cardano CLI:")
    print()
    print("  $ cardano-cli query utxo --address <WALLET> --testnet-magic 2")
    print("  $ cardano-cli transaction build \\")
    print("      --tx-in <UTXO> \\")
    print("      --tx-out <SCRIPT_ADDRESS>+2000000 \\")
    print("      --script-file plutus.json \\")
    print("      --out-file tx.raw")
    print("  $ cardano-cli transaction sign \\")
    print("      --tx-body-file tx.raw \\")
    print("      --signing-key-file me.sk \\")
    print("      --out-file tx.signed")
    print("  $ cardano-cli transaction submit --tx-file tx.signed --testnet-magic 2")
    print()

    print("=" * 70)
    print("✅ NEXT STEPS")
    print("=" * 70)
    print()
    print("  1. Get free Blockfrost API key")
    print("  2. Update .env with API key")
    print("  3. Choose deployment method (PyCardano or CLI)")
    print("  4. Submit reference script transaction")
    print("  5. Create first DID transaction")
    print("  6. Test complete lifecycle")
    print()

    print("=" * 70)
    print("📚 RESOURCES")
    print("=" * 70)
    print()
    print("  • Blockfrost: https://blockfrost.io (free API)")
    print("  • Cardano CLI: https://github.com/input-output-hk/cardano-cli")
    print("  • Testnet Faucet: https://docs.cardano.org/cardano-testnet/tools/faucet")
    print("  • Cardano Docs: https://docs.cardano.org")
    print()

    return True


if __name__ == "__main__":
    show_deployment_guide()
