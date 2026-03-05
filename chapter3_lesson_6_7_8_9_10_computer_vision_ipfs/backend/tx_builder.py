#!/usr/bin/env python3
"""
Direct Blockfrost API Transaction Builder for DID Registration
- Uses Blockfrost directly to build and submit transactions
- Avoids PyCardano bottlenecks
"""

import os
import json
import hashlib
import binascii
from datetime import datetime
import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))


class CardanoTransactionBuilder:
    """Build and submit transactions using Blockfrost API"""

    def __init__(self):
        self.api_key = os.getenv("BLOCKFROST_PROJECT_ID")
        self.base_url = "https://cardano-preview.blockfrost.io/api/v0"
        self.wallet_address = (
            "addr_test1vzmz068kmst73c9tw6t5nzvt643k32w78n4n8q5nquq5dygequ7fd"
        )

    def get_utxos(self):
        """Get UTxOs for wallet"""
        try:
            response = requests.get(
                f"{self.base_url}/addresses/{self.wallet_address}/utxos",
                headers={"project_id": self.api_key},
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Error getting UTxOs: {e}")
            return None

    def get_protocol_params(self):
        """Get Cardano protocol parameters"""
        try:
            response = requests.get(
                f"{self.base_url}/epochs/latest/parameters",
                headers={"project_id": self.api_key},
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Error getting protocol params: {e}")
            return None

    def estimate_fee(self, tx_bytes):
        """Estimate transaction fee"""
        params = self.get_protocol_params()
        if params:
            min_fee = int(params["min_fee_a"])
            fixed_fee = int(params["min_fee_b"])
            return fixed_fee + (len(tx_bytes) * min_fee // 16)
        return 200000  # Default: 0.2 ADA

    def create_did_datum(self, did_id, face_hash_ipfs, owner_addr, action="Register"):
        """
        Create DID datum for smart contract
        Datum format: {did: Bytes, face_ipfs_hash: Bytes, owner: Bytes, created_at: Int, action: Int}
        """
        # Encode strings to bytes
        did_bytes = did_id.encode().hex()
        ipfs_bytes = face_hash_ipfs.encode().hex()
        owner_bytes = owner_addr.encode().hex()

        # Action codes: 0=Register, 1=Update, 2=Verify, 3=Revoke
        action_code = {"Register": 0, "Update": 1, "Verify": 2, "Revoke": 3}.get(
            action, 0
        )

        # Created at: unix timestamp
        created_at = int(datetime.now().timestamp())

        datum = {
            "constructor": 0,
            "fields": [
                {"bytes": did_bytes},
                {"bytes": ipfs_bytes},
                {"bytes": owner_bytes},
                {"int": created_at},
                {"int": action_code},
            ],
        }

        return datum


def main():
    print("=" * 70)
    print("DID MANAGEMENT - TRANSACTION BUILDER")
    print("=" * 70)
    print()

    builder = CardanoTransactionBuilder()

    print("[1] Checking wallet UTxOs...")
    utxos = builder.get_utxos()

    if utxos:
        print(f"✓ Found {len(utxos)} UTxOs")
        total_lovelace = sum(
            int(u["amount"][0]["quantity"]) for u in utxos if len(u["amount"]) > 0
        )
        print(f"  Total: {total_lovelace / 1_000_000:.2f} ADA")
    else:
        print("✗ Could not fetch UTxOs")
        print("  Check if Blockfrost API key is valid")
        return False

    print()
    print("[2] Protocol parameters...")
    params = builder.get_protocol_params()
    if params:
        print(f"✓ Min fee: {params['min_fee_b']} Lovelace")
        print(f"✓ Min fee A: {params['min_fee_a']} Lovelace/byte")
    else:
        print("✗ Could not fetch protocol parameters")
        return False

    print()
    print("[3] Creating DID datum...")

    # Example DID
    did_id = "did:cardano:sonson0910"
    face_hash_ipfs = "QmXxxx..."  # IPFS hash

    datum = builder.create_did_datum(
        did_id=did_id,
        face_hash_ipfs=face_hash_ipfs,
        owner_addr=builder.wallet_address,
        action="Register",
    )

    print(f"✓ DID datum created")
    print(f"  DID: {did_id}")
    print(f"  IPFS: {face_hash_ipfs}")
    print(f"  Action: Register")
    print()

    print("=" * 70)
    print("✅ TRANSACTION BUILDER READY")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. Build transaction with validator script")
    print("  2. Estimate fee and adjust inputs")
    print("  3. Sign with wallet (me.sk)")
    print("  4. Submit to chain")
    print()

    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
