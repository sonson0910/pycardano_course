#!/usr/bin/env python3
"""
Test REGISTER DID operation ONLY (not CREATE)
"""
import sys
import time

sys.path.insert(0, ".")

from app.blockchain.cardano_client import CardanoClient
from app.blockchain.did_manager import DIDManager


def test_register():
    """Test REGISTER operation"""
    print("\n" + "=" * 80)
    print("TEST: REGISTER DID (Skip CREATE)")
    print("=" * 80 + "\n")

    try:
        # Initialize
        print("[INIT] Initializing...")
        cardano = CardanoClient()
        cardano.load_wallet("me_preprod.sk")
        did_mgr = DIDManager(cardano_client=cardano)
        print("   ✅ Initialized\n")

        # Use fixed DID from previous test
        did_id = "test-did-1761086899"  # This one should exist from earlier test
        face_hash = "Qm" + "a" * 44

        print(f"[REGISTER] Registering DID: {did_id}")
        print(f"   - Face IPFS: {face_hash}\n")

        # Call REGISTER directly (skip CREATE)
        print("[ACTION] Calling register_did()...")
        tx_result = did_mgr.register_did(did_id, face_hash)

        print(f"\n[RESULT] Transaction:")
        print(f"   TX Hash: {tx_result}\n")

        if tx_result and len(tx_result) > 20:
            print("✅ REGISTER PASSED - Real transaction submitted!")
            return True
        else:
            print("❌ REGISTER FAILED - Invalid TX hash")
            return False

    except Exception as e:
        print(f"\n❌ REGISTER FAILED:")
        print(f"   Error: {type(e).__name__}: {str(e)[:200]}")
        return False


if __name__ == "__main__":
    success = test_register()
    sys.exit(0 if success else 1)
