#!/usr/bin/env python3
"""
Unlock DID Transaction - SPEND FROM SCRIPT
Fixed version for Windows PowerShell compatibility
"""

import json
import os
from datetime import datetime
from dataclasses import dataclass
from typing import Optional
import sys

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
    UTxO,
)
from pycardano.hash import VerificationKeyHash

# Config
api_key = "preprod0K9MnKqsU21MJvqu00V4Laf4pz7dALPK"
base_url = "https://cardano-preprod.blockfrost.io/api/"

# Transaction from create_did.py
LOCK_TX_HASH = "bb9476b549096bec77c00a0fa3ee66bdbd5542e9b6de773fad8fb5a95c1b6971"
LOCK_TX_INDEX = 0

print("=" * 70)
print("UNLOCK DID TRANSACTION - SPEND FROM SCRIPT")
print("=" * 70)
print()

# Step 1: Connect
print("[1] Connecting to Blockfrost...")
sys.stdout.flush()
try:
    context = BlockFrostChainContext(project_id=api_key, base_url=base_url)
    print("    [OK] Connected!")
    sys.stdout.flush()
except Exception as e:
    print(f"    [ERROR] Connection failed: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

# Step 2: Load wallet
print("[2] Loading wallet...")
sys.stdout.flush()
try:
    sk = PaymentSigningKey.load("me_preprod.sk")
    vk = PaymentVerificationKey.from_signing_key(sk)
    addr = Address(payment_part=vk.hash(), network=Network.TESTNET)
    print(f"    [OK] Wallet: {addr}")
    sys.stdout.flush()
except Exception as e:
    print(f"    [ERROR] Failed to load wallet: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

print()
print("[3] Loading validator...")
sys.stdout.flush()
try:
    with open(os.path.join("..", "smart_contracts", "plutus.json")) as f:
        plutus = json.load(f)

    validator_data = plutus["validators"][0]
    script = PlutusV3Script(bytes.fromhex(validator_data["compiledCode"]))
    script_hash = ScriptHash(bytes.fromhex(validator_data["hash"]))
    script_addr = Address(payment_part=script_hash, network=Network.TESTNET)
    print(f"    [OK] Script Address: {script_addr}")
    print(f"    [OK] Script Hash: {script_hash}")
    sys.stdout.flush()
except Exception as e:
    print(f"    [ERROR] Failed to load validator: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

print()
print("[4] Building redeemer...")
sys.stdout.flush()


# Define Bool PlutusData (constructor-based)
@dataclass
class BoolFalse(PlutusData):
    CONSTR_ID = 0  # False


@dataclass
class BoolTrue(PlutusData):
    CONSTR_ID = 1  # True


# Define DID Datum PlutusData (matches Aiken types.ak)
@dataclass
class DIDDatum(PlutusData):
    CONSTR_ID = 0
    did_id: bytes
    face_ipfs_hash: bytes
    owner: bytes
    created_at: int
    verified: PlutusData  # Use Bool constructor


# Define redeemer action (0 = Register)
@dataclass
class RedeemerAction(PlutusData):
    CONSTR_ID = 0  # Register action
    action: int


redeemer_action = RedeemerAction(action=0)
print(f"    [OK] Action: Register (0)")
sys.stdout.flush()

print()
print("[5] Finding UTxO to spend...")
sys.stdout.flush()

# Get UTxOs at script address
try:
    script_utxos = context.utxos(str(script_addr))
    print(f"    [OK] UTxOs at script address: {len(script_utxos)}")
    sys.stdout.flush()

    if len(script_utxos) == 0:
        print("    [ERROR] No UTxOs found at script address!")
        print()
        print("    Transaction may not have confirmed yet.")
        print("    Check: https://preprod.cardanoscan.io/transaction/" + LOCK_TX_HASH)
        print()
        sys.exit(1)

    # Find the UTxO we just created
    script_utxo = None
    for utxo in script_utxos:
        if utxo.input.transaction_id.payload.hex() == LOCK_TX_HASH:
            script_utxo = utxo
            break

    if not script_utxo:
        print("    [ERROR] Could not find UTxO from our lock transaction!")
        print(f"    Expected TX: {LOCK_TX_HASH}")
        print("    Available UTxOs:")
        for utxo in script_utxos:
            print(f"      - {utxo.input.transaction_id.payload.hex()}")
        sys.exit(1)

    print(f"    [OK] Found UTxO: {script_utxo.input.transaction_id}")
    print(f"    [OK] Amount: {script_utxo.output.amount.coin / 1_000_000} ADA")
    sys.stdout.flush()

except Exception as e:
    print(f"    [ERROR] Error finding UTxO: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

print()
print("[6] Building unlock transaction...")
sys.stdout.flush()

try:
    builder = TransactionBuilder(context)
    print("    > Creating builder...")
    sys.stdout.flush()

    # Add wallet input for fees
    print("    > Adding wallet input for fees...")
    sys.stdout.flush()
    builder.add_input_address(addr)

    # Add script input with redeemer
    print("    > Adding script input with Register redeemer...")
    sys.stdout.flush()
    builder.add_script_input(
        utxo=script_utxo, script=script, redeemer=Redeemer(redeemer_action)
    )
    print("    > Script input added")
    sys.stdout.flush()

    # Add output (send back to wallet)
    output_amount = int(script_utxo.output.amount.coin) - 200_000
    print(f"    > Output amount: {output_amount / 1_000_000} ADA (fee ~0.2 ADA)")
    sys.stdout.flush()
    builder.add_output(TransactionOutput(address=addr, amount=output_amount))
    print("    > Output added")
    sys.stdout.flush()

    print("    [OK] Transaction built successfully!")
    sys.stdout.flush()

except Exception as e:
    print(f"    [ERROR] Error building transaction: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

print()
print("[7] Signing transaction...")
sys.stdout.flush()

try:
    signed_tx = builder.build_and_sign(
        signing_keys=[sk],
        change_address=addr,
    )
    print(f"    [OK] Transaction signed!")
    print(f"    [OK] TX ID: {signed_tx.id}")
    sys.stdout.flush()

except Exception as e:
    print(f"    [ERROR] Error signing transaction: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

print()
print("[8] Submitting transaction...")
sys.stdout.flush()

try:
    tx_id = context.submit_tx(signed_tx)
    print(f"    [OK] Submitted!")
    print(f"    [OK] TX ID: {tx_id}")
    sys.stdout.flush()

except Exception as e:
    print(f"    [ERROR] Error submitting transaction: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

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
print("  1. Spends the UTxO locked by create_did.py")
print("  2. Provides the Register redeemer")
print("  3. Validates with the smart contract")
print("  4. Returns funds to wallet")
print()
