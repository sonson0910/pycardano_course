#!/usr/bin/env python3
"""
Create and Submit First DID Transaction to Preprod - WITH DEBUGGING
"""

import json
import os
import sys
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
)
from pycardano.hash import VerificationKeyHash

# Config
api_key = "preprod0K9MnKqsU21MJvqu00V4Laf4pz7dALPK"
base_url = "https://cardano-preprod.blockfrost.io/api/"

print("=" * 70)
print("DID TRANSACTION - CREATE AND SUBMIT (DEBUG MODE)")
print("=" * 70)
print(flush=True)

# Connect
print("[0.1] Connecting to Blockfrost...", flush=True)
context = BlockFrostChainContext(project_id=api_key, base_url=base_url)
print("[0.2] Connected!", flush=True)

# Load wallet
print("[0.3] Loading wallet...", flush=True)
sk = PaymentSigningKey.load("me_preprod.sk")
vk = PaymentVerificationKey.from_signing_key(sk)
addr = Address(payment_part=vk.hash(), network=Network.TESTNET)
print(f"[0.4] Wallet loaded: {addr}", flush=True)

print()
print("[1] Loading validator...", flush=True)
with open(os.path.join("..", "smart_contracts", "plutus.json")) as f:
    plutus = json.load(f)

validator_data = plutus["validators"][0]
script = PlutusV3Script(bytes.fromhex(validator_data["compiledCode"]))
script_hash = ScriptHash(bytes.fromhex(validator_data["hash"]))
print(f"    > Script hash: {script_hash}", flush=True)

print()
print("[2] Creating DID datum...", flush=True)


# Define DID Datum PlutusData
@dataclass
class DIDDatum(PlutusData):
    CONSTR_ID = 0
    did: bytes
    face_hash: bytes
    created_at: int


# Create datum
did_id = b"did:cardano:sonson0910"
face_hash = b"QmExample123456789abcdef"
created_at = int(datetime.now().timestamp())

datum = DIDDatum(did=did_id, face_hash=face_hash, created_at=created_at)

print(f"    > DID: {did_id.decode()}", flush=True)
print(f"    > IPFS Hash: {face_hash.decode()}", flush=True)
print(f"    > Created: {datetime.fromtimestamp(created_at)}", flush=True)

print()
print("[3] Getting UTxOs...", flush=True)
sys.stdout.flush()

# Get UTxOs
utxos = context.utxos(str(addr))
print(f"    > UTxOs available: {len(utxos)}", flush=True)

if len(utxos) == 0:
    print("ERROR: No UTxOs available!")
    sys.exit(1)

print()
print("[4] Building transaction...", flush=True)
sys.stdout.flush()

# Build transaction
builder = TransactionBuilder(context)
print("    > TransactionBuilder created", flush=True)

# Add script reference output
print("    > Adding input address...", flush=True)
builder.add_input_address(addr)
print("    > Input address added", flush=True)

print("    > Adding output with datum...", flush=True)
output = TransactionOutput(
    address=Address(payment_part=script_hash, network=Network.TESTNET),
    amount=2_000_000,  # 2 ADA for datum
    datum=datum,
)
builder.add_output(output)
print("    > Output added", flush=True)

print()
print("[5] Building and signing transaction...", flush=True)
sys.stdout.flush()

signed_tx = builder.build_and_sign(
    signing_keys=[sk],
    change_address=addr,
)
print(f"    > Transaction signed", flush=True)
print(f"    > TX ID: {signed_tx.id}", flush=True)

print()
print("[6] Submitting transaction...", flush=True)
sys.stdout.flush()

tx_id = context.submit_tx(signed_tx)
print(f"    > Submitted!", flush=True)
print(f"    > TX ID: {tx_id}", flush=True)

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
