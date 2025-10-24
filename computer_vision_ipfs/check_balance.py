#!/usr/bin/env python3
"""Check balance on preprod testnet"""

import urllib.request
import json
import os
from dotenv import load_dotenv

load_dotenv(".env")

api_key = os.getenv("BLOCKFROST_PROJECT_ID")
wallet = "addr_test1vpx302mqdefht0wly42wlpjmd2rm7xr85j6sgvej8pywusc38sglh"
base_url = "https://cardano-preprod.blockfrost.io/api/v0"

print("=" * 70)
print("CHECK WALLET BALANCE ON PREPROD")
print("=" * 70)
print()

if not api_key:
    print("❌ BLOCKFROST_PROJECT_ID not set in .env")
    print("   Get one at: https://blockfrost.io/")
    exit(1)

print(f"API Key: {api_key[:20]}...")
print(f"Wallet: {wallet}")
print(f"Network: Preprod Testnet")
print()

# Test 1: Health check
print("[1] Testing Blockfrost API health...")
try:
    req = urllib.request.Request(f"{base_url}/health", headers={"project_id": api_key})
    with urllib.request.urlopen(req, timeout=5) as response:
        data = json.loads(response.read().decode("utf-8"))
        print(f"    ✓ API is {data.get('is_healthy', 'unknown')}")
except Exception as e:
    print(f"    ❌ Error: {e}")
    exit(1)

print()

# Test 2: Get address info
print("[2] Getting wallet balance...")
try:
    req = urllib.request.Request(
        f"{base_url}/addresses/{wallet}", headers={"project_id": api_key}
    )
    with urllib.request.urlopen(req, timeout=5) as response:
        data = json.loads(response.read().decode("utf-8"))

        if "amount" in data and len(data["amount"]) > 0:
            lovelace = int(data["amount"][0]["quantity"])
            ada = lovelace / 1_000_000
            print(f"    ✅ Balance: {ada:.2f} ADA ({lovelace} lovelace)")

            if ada == 0:
                print(f"\n    ⚠️  Wallet is EMPTY! Need to request faucet")
                print(
                    f"    https://testnets.cardano.org/en/testnets/cardano/tools/faucet/"
                )
            elif ada < 2:
                print(f"\n    ⚠️  Low balance. May not be enough for transactions.")
            else:
                print(f"\n    ✅ Balance is sufficient!")
        else:
            print(f"    ❌ No balance info found")
            print(f"    Response: {data}")
except urllib.error.HTTPError as e:
    print(f"    ❌ HTTP Error {e.code}: {e.reason}")
    try:
        error_data = json.loads(e.read().decode("utf-8"))
        print(f"    Details: {error_data}")
    except:
        pass
except Exception as e:
    print(f"    ❌ Error: {e}")

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
            if len(data) == 0:
                print(f"    ❌ NO UTxOs found (wallet is empty)")
            else:
                print(f"    ✅ Found {len(data)} UTxO(s)")
                for i, utxo in enumerate(data[:3]):
                    amount = int(utxo["amount"][0]["quantity"])
                    ada = amount / 1_000_000
                    print(f"      {i+1}. TX {utxo['tx_hash'][:16]}... = {ada:.2f} ADA")
        else:
            print(f"    ? Response: {data}")
except urllib.error.HTTPError as e:
    print(f"    ❌ HTTP Error {e.code}")
except Exception as e:
    print(f"    ❌ Error: {e}")

print()
print("=" * 70)
