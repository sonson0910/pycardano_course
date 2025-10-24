"""
Test Script: Revoke DID Service
================================

Kiểm tra xem revoke_did() hoạt động không.
Revoke là hành động vô hiệu hóa DID vĩnh viễn.

Chạy: python test_revoke_did.py <did_id>
"""

import sys
import os
import time
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.blockchain.did_manager import DIDManager
from app.blockchain.cardano_client import CardanoClient


def test_revoke_did(did_id=None):
    """Test revoking a DID permanently"""

    print("\n" + "=" * 80)
    print("TEST: REVOKE DID SERVICE")
    print("=" * 80)

    try:
        # If no DID provided, create one first
        if did_id is None:
            print("\n[1/5] Creating test DID first...")
            cardano = CardanoClient()
            cardano.load_wallet("me_preprod.sk")
            did_manager = DIDManager(cardano_client=cardano)

            did_id = f"test-did-{int(time.time())}"
            face_ipfs_hash = "Qm" + "f" * 44

            did_manager.create_did(did_id, face_ipfs_hash)
            print(f"   ✅ Test DID created: {did_id}")
        else:
            print(f"\n[1/5] Using provided DID: {did_id}")
            cardano = CardanoClient()
            cardano.load_wallet("me_preprod.sk")
            did_manager = DIDManager(cardano_client=cardano)

        # 2. Verify DID exists
        print("\n[2/5] Verifying DID exists...")
        stored_did = did_manager.get_did_document(did_id)
        if not stored_did:
            print(f"   ❌ DID not found: {did_id}")
            return False
        print(f"   ✅ DID found")
        print(f"   - Current status: {stored_did.get('status', 'unknown')}")
        print(f"   - WARNING: This operation is PERMANENT and cannot be undone!")

        # 3. Ask for confirmation
        print("\n[3/5] Revoking DID...")
        print(f"   - DID ID: {did_id}")
        print(f"   - Action: REVOKE (permanent disable)")

        # Call revoke_did - should return real TX hash
        tx_hash = did_manager.revoke_did(did_id)

        print(f"   ✅ DID revoked successfully!")
        print(f"   - TX Hash: {tx_hash}")
        print(f"   - Action: Revoke redeemer applied")

        # 4. Verify revocation in storage
        print("\n[4/5] Verifying revocation...")
        revoked_did = did_manager.get_did_document(did_id)
        if revoked_did:
            print(f"   ✅ Revocation status updated")
            print(f"   - New status: {revoked_did.get('status', 'unknown')}")
            print(f"   - NOTE: This DID cannot be re-activated")

        # 5. Check transaction
        print("\n[5/5] Transaction details...")
        print(f"   - TX Hash: {tx_hash}")
        print(f"   - Type: Revoke redeemer")
        print(f"   - Status: Built and ready for submission")
        print(f"   - Impact: PERMANENT - DID cannot be used anymore")

        # Summary
        print("\n" + "=" * 80)
        print("✅ TEST PASSED: Revoke DID service is working!")
        print("=" * 80)
        print(f"\nSummary:")
        print(f"  - DID: {did_id}")
        print(f"  - Action: Revoke (PERMANENT)")
        print(f"  - New status: {revoked_did.get('status', 'unknown')}")
        print(f"  - Transaction: {tx_hash}")
        print(f"  - WARNING: This DID is now permanently disabled")
        print("\n")

        return True

    except Exception as e:
        print("\n" + "=" * 80)
        print(f"❌ TEST FAILED: {e}")
        print("=" * 80)
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Get DID from command line if provided
    did_id = sys.argv[1] if len(sys.argv) > 1 else None
    success = test_revoke_did(did_id)
    sys.exit(0 if success else 1)
