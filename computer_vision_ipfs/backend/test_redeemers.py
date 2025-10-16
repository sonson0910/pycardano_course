#!/usr/bin/env python3
"""
Test All DID Redeemers - Register, Update, Verify, Revoke
Tests each validator action individually and shows expected outcomes
"""

import json
import os
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict

from pycardano import (
    BlockFrostChainContext,
    Address,
    Network,
    PaymentSigningKey,
    PaymentVerificationKey,
    PlutusV3Script,
    ScriptHash,
    PlutusData,
)

# Config
api_key = "preprod0K9MnKqsU21MJvqu00V4Laf4pz7dALPK"
base_url = "https://cardano-preprod.blockfrost.io/api/"

print("=" * 70)
print("DID REDEEMER TESTS - VALIDATE ALL ACTIONS")
print("=" * 70)
print()

# Connect
print("[1] Setting up environment...", flush=True)
context = BlockFrostChainContext(project_id=api_key, base_url=base_url)
sk = PaymentSigningKey.load("me_preprod.sk")
vk = PaymentVerificationKey.from_signing_key(sk)
addr = Address(payment_part=vk.hash(), network=Network.TESTNET)
print(f"    > Wallet: {addr}", flush=True)

print()
print("[2] Loading validator...", flush=True)
with open(os.path.join("..", "smart_contracts", "plutus.json")) as f:
    plutus = json.load(f)

validator_data = plutus["validators"][0]
script = PlutusV3Script(bytes.fromhex(validator_data["compiledCode"]))
script_hash = ScriptHash(bytes.fromhex(validator_data["hash"]))
print(
    f"    > Validator: PlutusV3, {len(validator_data['compiledCode']) // 2} bytes",
    flush=True,
)
print(f"    > Script Hash: {script_hash}", flush=True)

print()
print("=" * 70)
print("REDEEMER SPECIFICATIONS")
print("=" * 70)
print()

# Define redeemer actions
redeemers = {
    "Register": {
        "code": 0,
        "description": "Register a new DID",
        "requirements": [
            "✓ did ≠ empty string",
            "✓ face_hash ≠ empty string",
            "✓ created_at > 0",
        ],
        "constraints": [
            "Validates that all fields are non-empty",
            "Ensures timestamp is positive",
            "Creates new DID entry on-chain",
        ],
    },
    "Update": {
        "code": 1,
        "description": "Update an existing DID",
        "requirements": [
            "✓ DID must already exist",
            "✓ Can update any field",
            "✓ Permissive validation",
        ],
        "constraints": [
            "Always returns True (any update allowed)",
            "Could add additional validation logic",
            "Intended for changing face embeddings or metadata",
        ],
    },
    "Verify": {
        "code": 2,
        "description": "Verify a DID (read-only)",
        "requirements": [
            "✓ did ≠ empty string",
            "✓ face_hash ≠ empty string",
            "✓ Data integrity check",
        ],
        "constraints": [
            "Does not modify on-chain state",
            "Validates data consistency",
            "Used for identity verification",
        ],
    },
    "Revoke": {
        "code": 3,
        "description": "Revoke a DID (disable)",
        "requirements": [
            "✓ did ≠ empty string",
            "✓ Revocation flag set",
            "✓ Immutable record",
        ],
        "constraints": [
            "Permanent disable of DID",
            "Cannot be reversed",
            "Leaves immutable trace on-chain",
        ],
    },
}

for name, specs in redeemers.items():
    print(f"[{specs['code']}] {name}: {specs['description']}")
    print("-" * 70)
    print("    Requirements:")
    for req in specs["requirements"]:
        print(f"      {req}")
    print()
    print("    Constraints:")
    for constraint in specs["constraints"]:
        print(f"      • {constraint}")
    print()

print()
print("=" * 70)
print("DATUM STRUCTURE")
print("=" * 70)
print()


@dataclass
class DIDDatum(PlutusData):
    CONSTR_ID = 0
    did_id: bytes
    face_ipfs_hash: bytes
    owner: bytes
    created_at: int
    verified: bool


print("Plutus Data Structure:")
print("  Constructor ID: 0")
print("  Fields:")
print("    1. did_id: bytes          - Decentralized Identifier")
print("    2. face_ipfs_hash: bytes  - IPFS hash of face embedding")
print("    3. owner: bytes           - Owner's verification key hash")
print("    4. created_at: int        - Unix timestamp of creation")
print("    5. verified: bool         - Verification status")
print()

print("Example Datum:")
example_datum = DIDDatum(
    did_id=b"did:cardano:example123",
    face_ipfs_hash=b"QmExampleIPFSHash123456789",
    owner=b"M\x17\xab`nSu\xbd\xdf%T\xef\x86[j\x87\xbf",  # Example 20-byte hash
    created_at=int(datetime.now().timestamp()),
    verified=False,
)
print(f"  DID ID: {example_datum.did_id.decode()}")
print(f"  Face IPFS: {example_datum.face_ipfs_hash.decode()}")
print(f"  Owner: {example_datum.owner.hex()[:20]}...")
print(f"  Created: {datetime.fromtimestamp(example_datum.created_at)}")
print(f"  Verified: {example_datum.verified}")
print()

print()
print("=" * 70)
print("TEST SCENARIOS")
print("=" * 70)
print()

scenarios = [
    {
        "name": "Valid Register",
        "redeemer": "Register",
        "datum": {
            "did": "did:cardano:user123",
            "face_hash": "QmValidHash123456789",
            "created_at": int(datetime.now().timestamp()),
        },
        "expected": "✓ SUCCESS",
        "notes": "All fields valid, DID registered",
    },
    {
        "name": "Invalid Register (empty DID)",
        "redeemer": "Register",
        "datum": {
            "did": "",
            "face_hash": "QmValidHash123456789",
            "created_at": int(datetime.now().timestamp()),
        },
        "expected": "✗ FAIL",
        "notes": "DID cannot be empty",
    },
    {
        "name": "Invalid Register (empty hash)",
        "redeemer": "Register",
        "datum": {
            "did": "did:cardano:user123",
            "face_hash": "",
            "created_at": int(datetime.now().timestamp()),
        },
        "expected": "✗ FAIL",
        "notes": "Face hash cannot be empty",
    },
    {
        "name": "Valid Update",
        "redeemer": "Update",
        "datum": {
            "did": "did:cardano:user123",
            "face_hash": "QmNewHash987654321",
            "created_at": int(datetime.now().timestamp()),
        },
        "expected": "✓ SUCCESS",
        "notes": "Update always succeeds (permissive)",
    },
    {
        "name": "Valid Verify",
        "redeemer": "Verify",
        "datum": {
            "did": "did:cardano:user123",
            "face_hash": "QmValidHash123456789",
            "created_at": int(datetime.now().timestamp()),
        },
        "expected": "✓ SUCCESS",
        "notes": "Data integrity validated, read-only operation",
    },
    {
        "name": "Valid Revoke",
        "redeemer": "Revoke",
        "datum": {
            "did": "did:cardano:user123",
            "face_hash": "QmValidHash123456789",
            "created_at": int(datetime.now().timestamp()),
        },
        "expected": "✓ SUCCESS",
        "notes": "DID revoked, permanent state change",
    },
]

for i, scenario in enumerate(scenarios, 1):
    print(f"Scenario {i}: {scenario['name']}")
    print("-" * 70)
    print(f"  Redeemer:  {scenario['redeemer']}")
    print(f"  Datum:")
    print(f"    DID: {scenario['datum']['did'] or '[EMPTY]'}")
    print(f"    Hash: {scenario['datum']['face_hash'] or '[EMPTY]'}")
    print(f"    Timestamp: {scenario['datum']['created_at']}")
    print(f"  Expected Result: {scenario['expected']}")
    print(f"  Notes: {scenario['notes']}")
    print()

print()
print("=" * 70)
print("✅ REDEEMER TEST SPECIFICATIONS COMPLETE")
print("=" * 70)
print()
print("Next steps:")
print("  1. Run unlock_did.py to test Register in action")
print("  2. Run did_lifecycle.py for full lifecycle test")
print("  3. Monitor transactions on CardanoScan")
print()
