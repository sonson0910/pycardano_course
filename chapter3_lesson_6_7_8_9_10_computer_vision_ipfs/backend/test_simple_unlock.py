#!/usr/bin/env python3
"""
Test: Simple unlock without datum matching
"""

import json
import os
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
)

api_key = "preprod0K9MnKqsU21MJvqu00V4Laf4pz7dALPK"
base_url = "https://cardano-preprod.blockfrost.io/api/"
context = BlockFrostChainContext(project_id=api_key, base_url=base_url)

# Load wallet
sk = PaymentSigningKey.load("me_preprod.sk")
vk = PaymentVerificationKey.from_signing_key(sk)
addr = Address(payment_part=vk.hash(), network=Network.TESTNET)

# Load script
with open(os.path.join("..", "smart_contracts", "plutus.json")) as f:
    plutus = json.load(f)

validator_data = plutus["validators"][0]
script = PlutusV3Script(bytes.fromhex(validator_data["compiledCode"]))
script_hash = ScriptHash(bytes.fromhex(validator_data["hash"]))
script_addr = Address(payment_part=script_hash, network=Network.TESTNET)

# Get UTxOs
script_utxos = context.utxos(str(script_addr))
print(f"[OK] Found {len(script_utxos)} UTxOs at script address")

# Use newest UTxO
if not script_utxos:
    print("[ERROR] No UTxOs")
    exit(1)

script_utxo = script_utxos[-1]  # Take last one
print(f"[OK] Using UTxO: {script_utxo.input.transaction_id}")
print(f"[OK] Amount: {script_utxo.output.amount.coin}")
print(f"[OK] Has script on-chain: {script_utxo.output.script is not None}")


# Simple redeemer
@dataclass
class DummyRedeemer(PlutusData):
    pass


redeemer = Redeemer(DummyRedeemer())

# Build TX
builder = TransactionBuilder(context)
builder.add_input_address(addr)

# TRY WITHOUT datum - just spend the UTxO
builder.add_script_input(utxo=script_utxo, script=script, redeemer=redeemer)

output_amount = int(script_utxo.output.amount.coin) - 200_000
builder.add_output(TransactionOutput(address=addr, amount=output_amount))

print()
print("[BUILD] Building...")
try:
    signed_tx = builder.build_and_sign(
        signing_keys=[sk],
        change_address=addr,
    )
    print("[OK] Built and signed!")
    print(f"[OK] TX ID: {signed_tx.id}")

    # Submit
    print("[SUBMIT] Submitting...")
    tx_id = context.submit_tx(signed_tx)
    print(f"[SUCCESS] {tx_id}")
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback

    traceback.print_exc()
