#!/usr/bin/env python3
"""
Unlock DID Transaction - Spend from Script Address with Register Redeemer
Fixed version with correct 5-field DID Datum structure
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
    UTxO,
)

# Config
api_key = "preprod0K9MnKqsU21MJvqu00V4Laf4pz7dALPK"
base_url = "https://cardano-preprod.blockfrost.io/api/"

# Transaction from create_did.py
LOCK_TX_HASH = "4374fa5c17abeb977e008d0568cf1cdf458ce66025ef92871dcbfe2685242149"

print("=" * 70)
print("UNLOCK DID TRANSACTION - SPEND FROM SCRIPT")
print("=" * 70)
print()

# Step 1: Connect
print("[1] Connecting to Blockfrost...")
try:
    context = BlockFrostChainContext(project_id=api_key, base_url=base_url)
    print("    [OK] Connected!")
except Exception as e:
    print(f"    [ERROR] {e}")
    exit(1)

# Step 2: Load wallet
print("[2] Loading wallet...")
try:
    sk = PaymentSigningKey.load("me_preprod.sk")
    vk = PaymentVerificationKey.from_signing_key(sk)
    addr = Address(payment_part=vk.hash(), network=Network.TESTNET)
    print(f"    [OK] Wallet: {addr}")
except Exception as e:
    print(f"    [ERROR] {e}")
    exit(1)

# Step 3: Load validator
print("[3] Loading validator...")
try:
    with open(os.path.join("..", "smart_contracts", "plutus.json")) as f:
        plutus = json.load(f)

    validator_data = plutus["validators"][0]
    script = PlutusV3Script(bytes.fromhex(validator_data["compiledCode"]))
    script_hash = ScriptHash(bytes.fromhex(validator_data["hash"]))
    script_addr = Address(payment_part=script_hash, network=Network.TESTNET)
    print(f"    [OK] Script Address: {script_addr}")
    print(f"    [OK] Script Hash: {script_hash}")
except Exception as e:
    print(f"    [ERROR] {e}")
    exit(1)

# Step 4: Build redeemer and datum classes
print("[4] Preparing redeemer and datum structures...")


# Define Plutus Bool (Constructor 0 = False, Constructor 1 = True)
@dataclass
class PlutusFalse(PlutusData):
    CONSTR_ID = 0


@dataclass
class PlutusTrue(PlutusData):
    CONSTR_ID = 1


# Define DID Datum PlutusData - MUST match Aiken types.ak exactly (5 fields)
@dataclass
class DIDDatum(PlutusData):
    CONSTR_ID = 0
    did_id: bytes
    face_ipfs_hash: bytes
    owner: bytes
    created_at: int
    verified: PlutusFalse  # Use Plutus Bool constructor


# Define Register redeemer action - Aiken enum variant (CONSTR_ID = 0, no fields)
@dataclass
class Register(PlutusData):
    CONSTR_ID = 0  # Register = 0 (enum variant)


@dataclass
class Update(PlutusData):
    CONSTR_ID = 1  # Update = 1


@dataclass
class Verify(PlutusData):
    CONSTR_ID = 2  # Verify = 2


@dataclass
class Revoke(PlutusData):
    CONSTR_ID = 3  # Revoke = 3


# Use Register action
redeemer = Redeemer(Register())
print(f"    [OK] Redeemer: Register (enum variant, no data)")

# Step 5: Find UTxO to spend
print("[5] Finding UTxO at script address...")
try:
    script_utxos = context.utxos(str(script_addr))
    print(f"    [OK] Found {len(script_utxos)} UTxOs")

    if len(script_utxos) == 0:
        print("    [ERROR] No UTxOs found! Transaction may not be confirmed yet.")
        print(f"    Check: https://preprod.cardanoscan.io/transaction/{LOCK_TX_HASH}")
        exit(1)

    # Find the specific UTxO from our lock transaction
    script_utxo = None
    for utxo in script_utxos:
        if utxo.input.transaction_id.payload.hex() == LOCK_TX_HASH:
            script_utxo = utxo
            break

    if not script_utxo:
        print("    [ERROR] Could not find UTxO from lock transaction!")
        print(f"    Expected: {LOCK_TX_HASH}")
        print("    Available:")
        for utxo in script_utxos:
            print(f"      - {utxo.input.transaction_id.payload.hex()}")
        exit(1)

    print(f"    [OK] Found: {script_utxo.input.transaction_id}")
    print(f"    [OK] Amount: {script_utxo.output.amount.coin / 1_000_000} ADA")

except Exception as e:
    print(f"    [ERROR] {e}")
    import traceback

    traceback.print_exc()
    exit(1)

# Step 6: Build transaction
print("[6] Building transaction...")
try:
    builder = TransactionBuilder(context)

    # Add wallet input (for fees)
    print("    > Adding wallet input...")
    builder.add_input_address(addr)

    # Add script input with redeemer
    print("    > Adding script input with redeemer...")
    builder.add_script_input(utxo=script_utxo, script=script, redeemer=redeemer)

    # Add output (send back to wallet, minus fees)
    output_amount = int(script_utxo.output.amount.coin) - 200_000  # ~0.2 ADA fee
    print(f"    > Adding output: {output_amount / 1_000_000} ADA")
    builder.add_output(TransactionOutput(address=addr, amount=output_amount))

    print("    [OK] Transaction built")

except Exception as e:
    print(f"    [ERROR] {e}")
    import traceback

    traceback.print_exc()
    exit(1)

# Step 7: Sign transaction
print("[7] Signing transaction...")
try:
    signed_tx = builder.build_and_sign(
        signing_keys=[sk],
        change_address=addr,
    )
    print(f"    [OK] Signed")
    print(f"    [OK] TX ID: {signed_tx.id}")

except Exception as e:
    print(f"    [ERROR] {e}")
    import traceback

    traceback.print_exc()
    exit(1)

# Step 8: Submit transaction
print("[8] Submitting transaction...")
try:
    tx_id = context.submit_tx(signed_tx)
    print(f"    [OK] Submitted: {tx_id}")

except Exception as e:
    print(f"    [ERROR] {e}")
    import traceback

    traceback.print_exc()
    exit(1)

print()
print("=" * 70)
print("SUCCESS - UNLOCK TRANSACTION SUBMITTED")
print("=" * 70)
print()
print(f"TX Hash: {tx_id}")
print()
print("View on Cardano Preprod:")
print(f"  https://preprod.cardanoscan.io/transaction/{tx_id}")
print()
print("This transaction:")
print("  1. Spent UTxO locked by create_did.py")
print("  2. Provided Register redeemer")
print("  3. Validated with smart contract")
print("  4. Returned funds to wallet")
print()
