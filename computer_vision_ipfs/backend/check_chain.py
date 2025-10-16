#!/usr/bin/env python3
"""Check if transactions are on chain"""

import requests
import json

api_key = "preprod0K9MnKqsU21MJvqu00V4Laf4pz7dALPK"
base_url = "https://cardano-preprod.blockfrost.io/api/v0"

# Transactions to check
txs = {
    "0430638b6c884926d8d7ea2960ca20d33f20a5797179caa809ae6bcce9e91865": "DID Creation"
}

print("=" * 70)
print("CHECKING TRANSACTIONS ON CHAIN")
print("=" * 70)
print()

for tx_hash, label in txs.items():
    url = f"{base_url}/txs/{tx_hash}"
    headers = {"project_id": api_key}

    try:
        r = requests.get(url, headers=headers)

        if r.status_code == 200:
            tx = r.json()
            print(f"[OK] {label}")
            print(f"     TX: {tx_hash}")
            print(f"     Status: CONFIRMED ON CHAIN")
            print(f"     Block: {tx.get('block')}")
            print(f"     Slot: {tx.get('slot')}")
            print(f"     Fees: {tx.get('fees')} Lovelace")
            print(f"     Inputs: {len(tx.get('inputs', []))}")
            print(f"     Outputs: {len(tx.get('outputs', []))}")
            print()
        else:
            print(f"[PENDING] {label}")
            print(f"     TX: {tx_hash}")
            print(f"     Status: NOT ON CHAIN YET (might still be pending)")
            print()
    except Exception as e:
        print(f"[ERROR] {label}")
        print(f"     Error: {e}")
        print()

print()
print("=" * 70)
print("CHECKING SCRIPT UTXOS")
print("=" * 70)
print()

# Check script address
script_addr = "addr_test1wqeaqe49vklcr34w9ehe004ag5ckruu7q2a9xdglxt48fpsk284d3"
url = f"{base_url}/addresses/{script_addr}/utxos"

try:
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        utxos = r.json()
        print(f"[OK] Script address: {script_addr}")
        print(f"     UTxOs available: {len(utxos)}")

        if len(utxos) > 0:
            print()
            print("     Recent UTxOs:")
            for i, utxo in enumerate(utxos[:5]):
                print(f"     [{i+1}] {utxo['tx_hash']}#{utxo['output_index']}")
                print(f"         Amount: {utxo['amount'][0]['quantity']} Lovelace")
except Exception as e:
    print(f"[ERROR] {e}")

print()
