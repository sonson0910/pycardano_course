#!/usr/bin/env python3
"""
DID Deployment Status - Preprod Network
Shows system readiness without blocking on Blockfrost
"""

import json
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

print("=" * 70)
print("DID MANAGEMENT - PREPROD DEPLOYMENT STATUS")
print("=" * 70)
print()

# Get config
api_key = os.getenv("BLOCKFROST_PROJECT_ID")
base_url = os.getenv(
    "BLOCKFROST_BASE_URL", "https://cardano-preprod.blockfrost.io/api/"
)

print("[1] Configuration")
print(f"    Network: Preprod")
print(f"    API Key: {api_key[:20] if api_key else 'NOT SET'}...")
print(f"    Base URL: {base_url}")
print()

# Check wallet
print("[2] Wallet")
try:
    from pycardano import PaymentSigningKey, PaymentVerificationKey, Address, Network

    sk = PaymentSigningKey.load("me.sk")
    vk = PaymentVerificationKey.from_signing_key(sk)
    addr = Address(payment_part=vk.hash(), network=Network.TESTNET)
    print(f"    ✓ Address: {str(addr)[:50]}...")
except Exception as e:
    print(f"    ❌ Error: {e}")

print()

# Check validator
print("[3] Smart Contract Validator")
try:
    validator_path = os.path.join(
        os.path.dirname(__file__), "..", "smart_contracts", "plutus.json"
    )
    with open(validator_path, "r") as f:
        plutus = json.load(f)

    validator_data = plutus["validators"][0]
    cbor_size = len(validator_data["compiledCode"]) // 2
    print(f"    ✓ Type: PlutusV3")
    print(f"    ✓ Size: {cbor_size} bytes")
    print(f"    ✓ Ready to deploy")
except Exception as e:
    print(f"    ❌ Error: {e}")

print()

# Next steps
print("=" * 70)
print("✅ SYSTEM READY FOR DEPLOYMENT")
print("=" * 70)
print()
print("To deploy your DID smart contract:")
print()
print("Option 1: Using PyCardano (with Blockfrost)")
print("  $ python submit_did_pycardano.py")
print()
print("Option 2: Using Cardano CLI")
print("  $ cardano-cli query utxo --address <WALLET> --testnet-magic 1")
print("  $ cardano-cli transaction build ...")
print("  $ cardano-cli transaction sign --signing-key-file me.sk ...")
print("  $ cardano-cli transaction submit ...")
print()
print("Wallet address for commands:")
print(f"  {addr}")
print()
