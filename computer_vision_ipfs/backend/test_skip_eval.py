#!/usr/bin/env python3
"""
Test unlock - SKIP evaluation, submit directly to see real error
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
print(f"[1] Found {len(script_utxos)} UTxOs")

if not script_utxos:
    print("[ERROR] No UTxOs")
    exit(1)

# Use UTxO with script
script_utxo = script_utxos[-1]
tx_hash = script_utxo.input.transaction_id.payload.hex()[:20]
print(
    f"[2] Using UTxO: {tx_hash}... (has script: {script_utxo.output.script is not None})"
)


# Simple redeemer
@dataclass
class DummyRedeemer(PlutusData):
    pass


redeemer = Redeemer(DummyRedeemer())

# Build TX - WITHOUT evaluation
print("[3] Building TX without validation...")
builder = TransactionBuilder(context)
builder.add_input_address(addr)

builder.add_script_input(utxo=script_utxo, script=script, redeemer=redeemer)

output_amount = int(script_utxo.output.amount.coin) - 200_000
builder.add_output(TransactionOutput(address=addr, amount=output_amount))

# Build without signing/validation
print("[4] Building transaction body...")
try:
    # This will try to estimate units - let's catch that
    tx = builder.build(change_address=addr)
    print("[ERROR] Should have failed on estimation")
except Exception as e:
    error_msg = str(e)
    print(f"[CAUGHT] {error_msg[:200]}")

    # Now build the transaction BODY manually without estimation
    print("[5] Will attempt to submit with zero ex_units...")

    # Try to build without estimating
    from pycardano import TransactionBody, UtxoSelectionStrategy

    # Manual build - just construct and sign
    builder2 = TransactionBuilder(context)
    builder2.add_input_address(addr)
    builder2.add_script_input(utxo=script_utxo, script=script, redeemer=redeemer)
    builder2.add_output(TransactionOutput(address=addr, amount=output_amount))

    # Don't estimate - just sign with zeros
    print("[6] Signing with manual ex_units...")
    try:
        tx_body = builder2.build(change_address=addr, merge_change=True)
        print("[SUCCESS] Built!")
        print(f"[7] Submitting...")
        tx_id = context.submit_tx(tx_body)
        print(f"[SUBMIT SUCCESS] {tx_id}")
    except Exception as e2:
        error = str(e2)
        if "ScriptFailures" in error:
            print(f"[SCRIPT ERROR] {error[:500]}")
        else:
            print(f"[ERROR] {error[:500]}")
