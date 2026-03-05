#!/usr/bin/env python3
"""
Create and Submit First DID Transaction to Preprod
"""

import json
import os
from datetime import datetime
from dataclasses import dataclass

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
    RawCBOR,
)
from pycardano.hash import VerificationKeyHash

# Config
api_key = "preprod0K9MnKqsU21MJvqu00V4Laf4pz7dALPK"
base_url = "https://cardano-preprod.blockfrost.io/api/"

print("=" * 70)
print("DID TRANSACTION - CREATE AND SUBMIT")
print("=" * 70)
print()

# Connect
context = BlockFrostChainContext(project_id=api_key, base_url=base_url)

# Load wallet
sk = PaymentSigningKey.load("me_preprod.sk")
vk = PaymentVerificationKey.from_signing_key(sk)
addr = Address(payment_part=vk.hash(), network=Network.TESTNET)

print("[1] Loading validator...")
with open(os.path.join("..", "smart_contracts", "plutus.json")) as f:
    plutus = json.load(f)

validator_data = plutus["validators"][0]
script = PlutusV3Script(bytes.fromhex(validator_data["compiledCode"]))
script_hash = ScriptHash(bytes.fromhex(validator_data["hash"]))
print(f"    > Script hash: {script_hash}")

print()
print("[2] Creating DID datum...")


# Define Plutus Bool (Constructor 0 = False, Constructor 1 = True)
@dataclass
class PlutusFalse(PlutusData):
    CONSTR_ID = 0


@dataclass
class PlutusTrue(PlutusData):
    CONSTR_ID = 1


# Define DID Datum PlutusData (matches Aiken types.ak - 5 fields)
@dataclass
class DIDDatum(PlutusData):
    CONSTR_ID = 0
    did_id: bytes
    face_ipfs_hash: bytes
    owner: bytes
    created_at: int
    verified: PlutusFalse  # Use Plutus Bool constructor


# Get owner's verification key hash for owner field
vk_hash = vk.hash()

# Create datum
did_id = b"did:cardano:sonson0910"
face_ipfs_hash = b"QmExample123456789abcdef"
owner = bytes.fromhex(str(vk_hash))
created_at = int(datetime.now().timestamp())

datum = DIDDatum(
    did_id=did_id,
    face_ipfs_hash=face_ipfs_hash,
    owner=owner,
    created_at=created_at,
    verified=PlutusFalse(),  # Use Plutus Bool constructor instead of int
)

print(f"    [OK] DID: {did_id.decode()}")
print(f"    [OK] IPFS Hash: {face_ipfs_hash.decode()}")
print(f"    [OK] Owner: {str(vk_hash)}")
print(f"    [OK] Created: {datetime.fromtimestamp(created_at)}")
print(f"    [OK] Verified: False (Plutus Constructor 0)")

print()
print("[3] Building transaction...")

# Get UTxOs
utxos = context.utxos(str(addr))
print(f"    [OK] UTxOs available: {len(utxos)}")

# Build transaction
builder = TransactionBuilder(context)

# Add script reference output WITH script embedded
builder.add_input_address(addr)
builder.add_output(
    TransactionOutput(
        address=Address(payment_part=script_hash, network=Network.TESTNET),
        amount=3_000_000,  # 3 ADA (need extra for script + datum size)
        datum=datum,
        script=script,  # IMPORTANT: Include script so it's available on-chain
    )
)

# Build and sign
print()
print("[4] Signing transaction...")
signed_tx = builder.build_and_sign(
    signing_keys=[sk],
    change_address=addr,
)

print(f"    [OK] Transaction signed")
print(f"    [OK] TX ID: {signed_tx.id}")

print()
print("[5] Submitting transaction...")
tx_id = context.submit_tx(signed_tx)
print(f"    [OK] Submitted!")
print(f"    [OK] TX ID: {tx_id}")

print()
print("=" * 70)
print("SUCCESS - DID TRANSACTION SUBMITTED")
print("=" * 70)
print()
print(f"TX Hash: {tx_id}")
print()
print("View on Cardano Preprod:")
print(f"  https://preprod.cardanoscan.io/transaction/{tx_id}")
print()
