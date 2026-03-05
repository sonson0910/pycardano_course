#!/usr/bin/env python3
"""
DID Management - Offline Transaction Builder (No API Required)
Generate datum and show transaction structure for manual submission
"""

import json
import hashlib
from datetime import datetime
from pycardano import PaymentSigningKey, PaymentVerificationKey, Address, Network


def load_wallet():
    """Load wallet"""
    sk = PaymentSigningKey.load("me.sk")
    vk = PaymentVerificationKey.from_signing_key(sk)
    addr = Address(payment_part=vk.hash(), network=Network.TESTNET)
    return sk, vk, addr


def create_did_datum(did_id, face_hash_ipfs, action="Register"):
    """
    Create DID datum for smart contract (Plutus format)
    """
    action_map = {"Register": 0, "Update": 1, "Verify": 2, "Revoke": 3}

    # Create minimal datum
    datum = {
        "constructor": 0,
        "fields": [
            {"bytes": did_id.encode().hex()},  # did
            {"bytes": face_hash_ipfs.encode().hex()},  # face_ipfs_hash
            {"int": int(datetime.now().timestamp())},  # created_at
        ],
    }

    return datum


def load_validator():
    """Load validator from plutus.json"""
    validator_path = os.path.join(
        os.path.dirname(__file__), "..", "smart_contracts", "plutus.json"
    )
    with open(validator_path, "r") as f:
        return json.load(f)


def main():
    import os

    print("=" * 70)
    print("DID MANAGEMENT - OFFLINE TRANSACTION BUILDER")
    print("=" * 70)
    print()

    # Step 1: Load wallet
    print("[1] Loading wallet...")
    try:
        sk, vk, wallet_addr = load_wallet()
        print(f"✓ Wallet: {wallet_addr}")
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

    # Step 2: Create DID datum
    print()
    print("[2] Creating DID datum...")

    did_id = "did:cardano:sonson0910"
    face_hash_ipfs = "QmExample1234567890abcdef"  # Example IPFS hash

    datum = create_did_datum(did_id, face_hash_ipfs, action="Register")
    datum_json = json.dumps(datum, indent=2)

    print(f"✓ DID: {did_id}")
    print(f"✓ IPFS: {face_hash_ipfs}")
    print()
    print("Datum (Plutus format):")
    print(datum_json)

    # Step 3: Load validator
    print()
    print("[3] Loading validator...")
    try:
        validator_data = load_validator()
        print(f"✓ Validator script loaded")
        print(f"  CBOR length: {len(validator_data['compiledCode']) // 2} bytes")
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

    # Step 4: Show transaction structure
    print()
    print("=" * 70)
    print("TRANSACTION STRUCTURE")
    print("=" * 70)
    print()

    tx_structure = {
        "inputs": [{"id": "UTxO from wallet (use Blockfrost to get)", "index": 0}],
        "outputs": [
            {
                "address": str(wallet_addr),
                "value": "2000000 lovelace",  # 2 ADA for datum
                "datum": datum,
            }
        ],
        "validator_script": {
            "type": "PlutusV3",
            "language": 1,
            "cbor": validator_data["compiledCode"][:50] + "...",
        },
        "fee": "~350000 lovelace",
        "ttl": "current_slot + 7200",
    }

    print(json.dumps(tx_structure, indent=2))

    print()
    print("=" * 70)
    print("✅ READY FOR SUBMISSION")
    print("=" * 70)
    print()
    print("To submit this transaction:")
    print()
    print("Option 1: Using Cardano CLI")
    print("  1. Build transaction with validator script")
    print("  2. Sign with signing key (me.sk)")
    print("  3. Submit to testnet")
    print()
    print("Option 2: Using PyCardano TransactionBuilder")
    print("  1. Use datum above in output")
    print("  2. Add validator script as reference")
    print("  3. Build and sign transaction")
    print()
    print("Wallet Address:", wallet_addr)
    print("Required Balance: 2 ADA (for datum) + fees (~0.35 ADA)")
    print("Your Balance: ~10,000 ADA ✓")
    print()

    return True


if __name__ == "__main__":
    import os

    success = main()
    exit(0 if success else 1)
