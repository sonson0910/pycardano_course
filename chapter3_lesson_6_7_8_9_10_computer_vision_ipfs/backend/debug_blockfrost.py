#!/usr/bin/env python3
"""
Debug Blockfrost API - Step by step
"""

import urllib.request
import urllib.error
import json
import os
from dotenv import load_dotenv

load_dotenv("..\\.env")

api_key = os.getenv("BLOCKFROST_PROJECT_ID")
wallet = "addr_test1vzmz068kmst73c9tw6t5nzvt643k32w78n4n8q5nquq5dygequ7fd"
base_url = "https://cardano-preview.blockfrost.io/api/v0"

print("=" * 70)
print("DEBUG BLOCKFROST API")
print("=" * 70)
print()

print(f"API Key: {api_key[:20]}...")
print(f"Wallet: {wallet[:50]}...")
print()

# Test 1: Health
print("[1] Testing health endpoint...")
try:
    req = urllib.request.Request(f"{base_url}/health", headers={"project_id": api_key})
    with urllib.request.urlopen(req, timeout=5) as response:
        data = json.loads(response.read().decode("utf-8"))
        print(f"    ✓ Status: {data}")
except Exception as e:
    print(f"    ❌ Error: {e}")

print()

# Test 2: Get address info
print("[2] Getting wallet info...")
try:
    req = urllib.request.Request(
        f"{base_url}/addresses/{wallet}", headers={"project_id": api_key}
    )
    with urllib.request.urlopen(req, timeout=5) as response:
        data = json.loads(response.read().decode("utf-8"))
        print(f"    ✓ Address: {data.get('address', 'N/A')[:50]}...")
        if "amount" in data:
            lovelace = int(data["amount"][0]["quantity"])
            ada = lovelace / 1_000_000
            print(f"    ✓ Balance: {ada:.2f} ADA")
        else:
            print(f"    ✗ No amount field")
            print(f"    Response: {data}")
except Exception as e:
    print(f"    ❌ Error: {e}")
    print(f"    Type: {type(e).__name__}")

print()

# Test 3: Get UTxOs
print("[3] Getting UTxOs...")
try:
    req = urllib.request.Request(
        f"{base_url}/addresses/{wallet}/utxos", headers={"project_id": api_key}
    )
    with urllib.request.urlopen(req, timeout=5) as response:
        data = json.loads(response.read().decode("utf-8"))
        if isinstance(data, list):
            print(f"    ✓ Found {len(data)} UTxOs")
            for i, utxo in enumerate(data[:2]):
                print(
                    f"      {i+1}. {utxo['tx_hash'][:20]}... index {utxo['output_index']}"
                )
        else:
            print(f"    ? Response: {data}")
except Exception as e:
    print(f"    ❌ Error: {e}")

print()
print("=" * 70)
