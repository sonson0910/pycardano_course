#!/usr/bin/env python3
"""
DID Management - Deploy Following Aiken Official Tutorial
https://aiken-lang.org/example--hello-world/end-to-end/pycardano
"""

import json
import os
import sys
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

try:
    from pycardano import (
        BlockFrostChainContext,
        PaymentSigningKey,
        PaymentVerificationKey,
        PlutusV3Script,
        ScriptHash,
        Address,
        Network,
        TransactionBuilder,
        TransactionOutput,
        PlutusData,
    )
except ImportError as e:
    print(f"❌ PyCardano import error: {e}")
    print()
    print("PyCardano 0.16.0 doesn't have BlockFrostChainContext")
    print("This version is missing required APIs for transaction building")
    print()
    sys.exit(1)


def read_validator():
    """Read validator from plutus.json"""
    validator_path = os.path.join(
        os.path.dirname(__file__), "..", "smart_contracts", "plutus.json"
    )
    with open(validator_path, "r") as f:
        validator = json.load(f)

    # PyCardano expects different structure for PlutusV3
    # Use validators[0]['compiledCode'], not 'cborHex'
    validator_data = validator["validators"][0]
    script_bytes = PlutusV3Script(bytes.fromhex(validator_data["compiledCode"]))

    # Get script hash from first validator
    script_hash = ScriptHash(bytes.fromhex(validator_data["hash"]))

    return {
        "type": "PlutusV3",
        "script_bytes": script_bytes,
        "script_hash": script_hash,
    }


def main():
    print("=" * 70)
    print("DID DEPLOYMENT - AIKEN TUTORIAL APPROACH")
    print("=" * 70)
    print()

    # Step 1: Load environment
    api_key = os.getenv("BLOCKFROST_PROJECT_ID")
    base_url = os.getenv(
        "BLOCKFROST_BASE_URL", "https://cardano-preprod.blockfrost.io/api/"
    )

    if not api_key:
        print("❌ BLOCKFROST_PROJECT_ID not set in .env")
        return False

    print(f"[1] Setting up BlockFrost context...")
    print(f"    Network: Preprod")
    print(f"    Base URL: {base_url}")
    try:
        context = BlockFrostChainContext(
            project_id=api_key,
            base_url=base_url,
        )
        print("    ✓ Connected to Blockfrost")
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False

    print()
    print("[2] Loading wallet...")
    try:
        signing_key = PaymentSigningKey.load("me.sk")
        verification_key = PaymentVerificationKey.from_signing_key(signing_key)
        wallet_address = Address(
            payment_part=verification_key.hash(), network=Network.TESTNET
        )
        print(f"    ✓ Wallet: {str(wallet_address)[:50]}...")
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False

    print()
    print("[3] Loading validator...")
    try:
        validator = read_validator()
        print(f"    ✓ Type: {validator['type']}")
        print(f"    ✓ Script hash: {str(validator['script_hash'])[:30]}...")
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False

    print()
    print("[4] Checking wallet balance...")
    try:
        utxos = context.utxos(str(wallet_address))
        if utxos:
            total = sum(int(utxo.output.amount.coin) for utxo in utxos)
            ada = total / 1_000_000
            print(f"    ✓ Balance: {ada:.2f} ADA")
            print(f"    ✓ UTxOs: {len(utxos)}")
        else:
            print(f"    ❌ No UTxOs found")
            return False
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False

    print()
    print("=" * 70)
    print("✅ READY FOR DEPLOYMENT")
    print("=" * 70)
    print()
    print("To create your first DID transaction:")
    print()
    print("1. Create a datum (PlutusData subclass)")
    print("2. Use TransactionBuilder to create tx")
    print("3. Sign and submit via context.submit_tx()")
    print()

    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
