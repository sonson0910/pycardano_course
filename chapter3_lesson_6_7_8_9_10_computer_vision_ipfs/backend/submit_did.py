#!/usr/bin/env python3
"""
DID Deployment - Submit to Preprod
"""

import json
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from pycardano import (
    BlockFrostChainContext,
    Address,
    Network,
    PaymentSigningKey,
    PaymentVerificationKey,
    PlutusV3Script,
    ScriptHash,
    PlutusData,
    TransactionBuilder,
    TransactionOutput,
    Redeemer,
)

# Get config
api_key = "preprod0K9MnKqsU21MJvqu00V4Laf4pz7dALPK"
base_url = "https://cardano-preprod.blockfrost.io/api/"

print("=" * 70)
print("DID MANAGEMENT - PREPROD DEPLOYMENT")
print("=" * 70)
print()

# Connect to Preprod
print("[1] Connecting to Preprod...")
context = BlockFrostChainContext(
    project_id=api_key,
    base_url=base_url,
)
print("    ✓ Connected!")

# Load wallet (Preprod)
print()
print("[2] Loading wallet...")
sk = PaymentSigningKey.load("me_preprod.sk")
vk = PaymentVerificationKey.from_signing_key(sk)
addr = Address(payment_part=vk.hash(), network=Network.TESTNET)
print(f"    ✓ Address: {str(addr)[:50]}...")

# Check balance
print()
print("[3] Checking balance...")
utxos = context.utxos(str(addr))
if utxos:
    total = sum(int(u.output.amount.coin) for u in utxos)
    ada = total / 1_000_000
    print(f"    ✓ UTxOs: {len(utxos)}")
    print(f"    ✓ Balance: {ada:.2f} ADA")
else:
    print("    ❌ No UTxOs found")
    exit(1)

# Load validator
print()
print("[4] Loading validator...")
validator_path = os.path.join(
    os.path.dirname(__file__), "..", "smart_contracts", "plutus.json"
)
with open(validator_path, "r") as f:
    plutus = json.load(f)

# Get first validator from the list
validator_data = plutus["validators"][0]
script = PlutusV3Script(bytes.fromhex(validator_data["compiledCode"]))
script_hash = ScriptHash(bytes.fromhex(validator_data["hash"]))
cbor_size = len(validator_data["compiledCode"]) // 2
print(f"    ✓ Validator loaded")
print(f"    ✓ Script hash: {str(script_hash)[:30]}...")
print(f"    ✓ Size: {cbor_size} bytes")

print()
print("=" * 70)
print("✅ READY FOR DID TRANSACTION")
print("=" * 70)
print()
print("System ready:")
print(f"  • Network: Cardano Preprod")
print(f"  • Wallet: {str(addr)[:50]}...")
print(f"  • Balance: {ada:.2f} ADA")
print(f"  • Validator: PlutusV3 ({cbor_size} bytes)")
print()
print("Next step: Create and submit DID datum transaction")
print()
