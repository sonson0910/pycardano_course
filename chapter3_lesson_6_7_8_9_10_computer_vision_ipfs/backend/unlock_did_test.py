#!/usr/bin/env python3
"""
Unlock DID Transaction - FIXED VERSION
This script unlocks the 2 ADA that was locked to the smart contract with DID datum
by providing a redeemer and using the validator to validate the spending action.
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
LOCK_TX_HASH = "50f3f29ec225fd5e108b85d4f9023914be2f044922cf08871e2b1fe91bef0c0b"
LOCK_TX_INDEX = 0  # Output index where we locked the 2 ADA

print("=" * 70)
print("UNLOCK DID TRANSACTION - FIXED TEST")
print("=" * 70)
print(flush=True)

# Connect
print("[1] Connecting to Blockfrost...", flush=True)
sys.stdout.flush()
try:
    context = BlockFrostChainContext(project_id=api_key, base_url=base_url)
    print("    [OK] Connected!", flush=True)
    sys.stdout.flush()
except Exception as e:
    print(f"    [ERR] Connection failed: {e}", flush=True)
    sys.exit(1)

# Load wallet
print("[2] Loading wallet...", flush=True)
sys.stdout.flush()
try:
    sk = PaymentSigningKey.load("me_preprod.sk")
    vk = PaymentVerificationKey.from_signing_key(sk)
    addr = Address(payment_part=vk.hash(), network=Network.TESTNET)
    print(f"    ✓ Wallet: {addr}", flush=True)
    sys.stdout.flush()
except Exception as e:
    print(f"    ✗ Failed to load wallet: {e}", flush=True)
    sys.exit(1)

print()
print("[3] Loading validator...", flush=True)
sys.stdout.flush()
try:
    with open(os.path.join("..", "smart_contracts", "plutus.json")) as f:
        plutus = json.load(f)

    validator_data = plutus["validators"][0]
    script = PlutusV3Script(bytes.fromhex(validator_data["compiledCode"]))
    script_hash = ScriptHash(bytes.fromhex(validator_data["hash"]))
    script_addr = Address(payment_part=script_hash, network=Network.TESTNET)
    print(f"    ✓ Script Address: {script_addr}", flush=True)
    print(f"    ✓ Script Hash: {script_hash}", flush=True)
    sys.stdout.flush()
except Exception as e:
    print(f"    ✗ Failed to load validator: {e}", flush=True)
    sys.exit(1)

print()
print("[4] Building redeemer...", flush=True)
sys.stdout.flush()


# Define redeemer action (0 = Register)
@dataclass
class RedeemerAction(PlutusData):
    CONSTR_ID = 0  # Register action
    action: int


redeemer_action = RedeemerAction(action=0)
print(f"    ✓ Action: Register (0)", flush=True)
sys.stdout.flush()

print()
print("[5] Finding UTxO to spend...", flush=True)
sys.stdout.flush()

# Get UTxOs at script address
try:
    script_utxos = context.utxos(str(script_addr))
    print(f"    ✓ UTxOs at script address: {len(script_utxos)}", flush=True)
    sys.stdout.flush()

    if len(script_utxos) == 0:
        print("    ✗ No UTxOs found at script address!", flush=True)
        print(flush=True)
        print("    Transaction may not have confirmed yet.", flush=True)
        print(
            "    Check: https://preprod.cardanoscan.io/transaction/" + LOCK_TX_HASH,
            flush=True,
        )
        print(flush=True)
        sys.exit(1)

    # Find the UTxO we just created
    script_utxo = None
    for utxo in script_utxos:
        if utxo.input.transaction_id.payload.hex() == LOCK_TX_HASH:
            script_utxo = utxo
            break

    if not script_utxo:
        print("    ✗ Could not find UTxO from our lock transaction!", flush=True)
        print(f"    Expected TX: {LOCK_TX_HASH}", flush=True)
        print("    Available UTxOs:", flush=True)
        for utxo in script_utxos:
            print(f"      - {utxo.input.transaction_id.payload.hex()}", flush=True)
        sys.exit(1)

    print(f"    ✓ Found UTxO: {script_utxo.input.transaction_id}", flush=True)
    print(f"    ✓ Amount: {script_utxo.output.amount.coin / 1_000_000} ADA", flush=True)
    sys.stdout.flush()

except Exception as e:
    print(f"    ✗ Error finding UTxO: {e}", flush=True)
    import traceback

    traceback.print_exc()
    sys.exit(1)

print()
print("[6] Building unlock transaction...", flush=True)
sys.stdout.flush()

try:
    builder = TransactionBuilder(context)
    print("    > TransactionBuilder created", flush=True)
    sys.stdout.flush()

    # Add wallet input for fees
    print("    > Adding wallet input for fees...", flush=True)
    sys.stdout.flush()
    builder.add_input_address(addr)

    # Add script input with redeemer
    print("    > Adding script input with Register redeemer...", flush=True)
    sys.stdout.flush()
    builder.add_script_input(
        utxo=script_utxo, script=script, redeemer=Redeemer(redeemer_action)
    )
    print("    > Script input added successfully", flush=True)
    sys.stdout.flush()

    # Add output (send back to wallet)
    output_amount = int(script_utxo.output.amount.coin) - 200_000  # Subtract fee
    print(
        f"    > Output amount: {output_amount / 1_000_000} ADA (after ~0.2 ADA fee)",
        flush=True,
    )
    sys.stdout.flush()
    builder.add_output(TransactionOutput(address=addr, amount=output_amount))
    print("    > Output added successfully", flush=True)
    sys.stdout.flush()

    print("    ✓ Transaction built successfully!", flush=True)
    sys.stdout.flush()

except Exception as e:
    print(f"    ✗ Error building transaction: {e}", flush=True)
    import traceback

    traceback.print_exc()
    sys.exit(1)

print()
print("[7] Signing transaction...", flush=True)
sys.stdout.flush()

try:
    signed_tx = builder.build_and_sign(
        signing_keys=[sk],
        change_address=addr,
    )
    print(f"    ✓ Transaction signed!", flush=True)
    print(f"    ✓ TX ID: {signed_tx.id}", flush=True)
    sys.stdout.flush()

except Exception as e:
    print(f"    ✗ Error signing transaction: {e}", flush=True)
    import traceback

    traceback.print_exc()
    sys.exit(1)

print()
print("[8] Submitting transaction...", flush=True)
sys.stdout.flush()

try:
    tx_id = context.submit_tx(signed_tx)
    print(f"    ✓ Submitted!", flush=True)
    print(f"    ✓ TX ID: {tx_id}", flush=True)
    sys.stdout.flush()

except Exception as e:
    print(f"    ✗ Error submitting transaction: {e}", flush=True)
    import traceback

    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 70)
print("✅ UNLOCK TRANSACTION SUBMITTED")
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
