#!/usr/bin/env python3
"""
Test DID Transaction Structure (No Submit)
"""

import json
import os
from dataclasses import dataclass
from datetime import datetime

from pycardano import (
    Address,
    Network,
    PaymentSigningKey,
    PaymentVerificationKey,
    PlutusData,
    PlutusV3Script,
    ScriptHash,
)

print("=" * 70)
print("DID TRANSACTION - BUILD STRUCTURE")
print("=" * 70)
print()

# Load wallet
print("[1] Wallet...")
sk = PaymentSigningKey.load("me_preprod.sk")
vk = PaymentVerificationKey.from_signing_key(sk)
wallet_addr = Address(payment_part=vk.hash(), network=Network.TESTNET)
print(f"    ✓ {str(wallet_addr)[:50]}...")

# Load validator
print()
print("[2] Validator...")
validator_path = os.path.join(
    os.path.dirname(__file__), "..", "smart_contracts", "plutus.json"
)
with open(validator_path, "r") as f:
    plutus = json.load(f)

validator_data = plutus["validators"][0]
script = PlutusV3Script(bytes.fromhex(validator_data["compiledCode"]))
script_hash = ScriptHash(bytes.fromhex(validator_data["hash"]))
script_address = Address(payment_part=script_hash, network=Network.TESTNET)
print(f"    ✓ Script: {str(script_hash)[:30]}...")
print(f"    ✓ Script Address: {str(script_address)[:50]}...")


# Create datum
@dataclass
class DIDDatum(PlutusData):
    CONSTR_ID = 0
    did: bytes
    face_ipfs_hash: bytes
    created_at: int


print()
print("[3] DID Datum...")
did_id = "did:cardano:sonson0910"
face_hash = "QmExample1234567890abcdef"
created_at = int(datetime.now().timestamp())

datum = DIDDatum(
    did=did_id.encode(), face_ipfs_hash=face_hash.encode(), created_at=created_at
)
print(f"    ✓ DID: {did_id}")
print(f"    ✓ IPFS: {face_hash}")
print(f"    ✓ Created: {created_at}")
print(f"    ✓ Datum CBOR: {datum.to_cbor_hex()[:50]}...")

print()
print("=" * 70)
print("✅ TRANSACTION STRUCTURE READY")
print("=" * 70)
print()
print("Next: Use create_did.py to submit transaction")
print()
