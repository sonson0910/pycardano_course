#!/usr/bin/env python3
"""
Debug: Check script hash from UTxO vs expected
"""

import json
from pycardano import (
    BlockFrostChainContext,
    Address,
    Network,
    ScriptHash,
    PlutusV3Script,
)

api_key = "preprod0K9MnKqsU21MJvqu00V4Laf4pz7dALPK"
base_url = "https://cardano-preprod.blockfrost.io/api/"

context = BlockFrostChainContext(project_id=api_key, base_url=base_url)

# Load script from plutus.json
with open("../smart_contracts/plutus.json") as f:
    plutus = json.load(f)

validator_data = plutus["validators"][0]
expected_hash = validator_data["hash"]
print(f"Expected script hash: {expected_hash}")

expected_script = PlutusV3Script(bytes.fromhex(validator_data["compiledCode"]))
print(f"Expected script bytes loaded from plutus.json")


# Build script address
expected_script_hash = ScriptHash(bytes.fromhex(expected_hash))
expected_addr = Address(payment_part=expected_script_hash, network=Network.TESTNET)
print(f"Expected script address: {expected_addr}")

# Get UTxOs at that address
print()
print("UTxOs at script address:")
utxos = context.utxos(str(expected_addr))
print(f"Found: {len(utxos)}")

for i, utxo in enumerate(utxos, 1):
    tx_hash = utxo.input.transaction_id.payload.hex()[:20]
    amount = utxo.output.amount.coin
    has_datum = utxo.output.datum is not None
    has_script = utxo.output.script is not None

    print(f"\n{i}. TX: {tx_hash}...")
    print(f"   Amount: {amount} Lovelace")
    print(f"   Has datum: {has_datum}")
    print(f"   Has script: {has_script}")

    if has_script:
        script_on_chain = utxo.output.script
        print(f"   Script on-chain type: {type(script_on_chain)}")
        print(f"   Script attached successfully")
