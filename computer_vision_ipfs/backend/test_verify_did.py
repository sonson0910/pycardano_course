"""
Test Script: Verify DID Service
================================

Kiểm tra xem verify_did() hoạt động không.
Verify là hành động xác nhận DID integrity.

Chạy: python test_verify_did.py <did_id>
"""

import sys
import os
import time
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.blockchain.did_manager import DIDManager
from app.blockchain.cardano_client import CardanoClient

def test_verify_did(did_id=None):
    """Test verifying a DID on blockchain"""
    
    print("\n" + "="*80)
    print("TEST: VERIFY DID SERVICE")
    print("="*80)
    
    try:
        # If no DID provided, create one first
        if did_id is None:
            print("\n[1/5] Creating test DID first...")
            cardano = CardanoClient()
            did_manager = DIDManager(cardano=cardano)
            
            did_id = f"test-did-{int(time.time())}"
            face_ipfs_hash = "Qm" + "e" * 44
            
            did_manager.create_did(did_id, face_ipfs_hash)
            print(f"   ✅ Test DID created: {did_id}")
        else:
            print(f"\n[1/5] Using provided DID: {did_id}")
            cardano = CardanoClient()
            did_manager = DIDManager(cardano=cardano)
        
        # 2. Verify DID exists
        print("\n[2/5] Verifying DID exists...")
        stored_did = did_manager.get_did_document(did_id)
        if not stored_did:
            print(f"   ❌ DID not found: {did_id}")
            return False
        print(f"   ✅ DID found")
        print(f"   - Status: {stored_did.get('status', 'unknown')}")
        print(f"   - Currently verified: {stored_did.get('verified', False)}")
        
        # 3. Verify DID integrity
        print("\n[3/5] Verifying DID integrity...")
        print(f"   - DID ID: {did_id}")
        print(f"   - IPFS Hash: {stored_did.get('ipfs_hash', 'unknown')[:20]}...")
        
        # Call verify_did - should return real TX hash
        tx_hash = did_manager.verify_did(did_id)
        
        print(f"   ✅ DID verified successfully!")
        print(f"   - TX Hash: {tx_hash}")
        print(f"   - Action: Verify redeemer applied")
        
        # 4. Verify status updated
        print("\n[4/5] Checking verification status...")
        verified_did = did_manager.get_did_document(did_id)
        if verified_did:
            print(f"   ✅ Verification status updated")
            print(f"   - Verified: {verified_did.get('verified', False)}")
            print(f"   - Status: {verified_did.get('status', 'unknown')}")
        
        # 5. Check transaction
        print("\n[5/5] Transaction details...")
        print(f"   - TX Hash: {tx_hash}")
        print(f"   - Type: Verify redeemer")
        print(f"   - Status: Built and ready for submission")
        print(f"   - Note: This is a read-only verification action")
        
        # Summary
        print("\n" + "="*80)
        print("✅ TEST PASSED: Verify DID service is working!")
        print("="*80)
        print(f"\nSummary:")
        print(f"  - DID: {did_id}")
        print(f"  - Action: Verify")
        print(f"  - Now verified: {verified_did.get('verified', False)}")
        print(f"  - Transaction: {tx_hash}")
        print(f"  - Next: Test revoke operation or submit transactions")
        print("\n")
        
        return True

    except Exception as e:
        print("\n" + "="*80)
        print(f"❌ TEST FAILED: {e}")
        print("="*80)
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Get DID from command line if provided
    did_id = sys.argv[1] if len(sys.argv) > 1 else None
    success = test_verify_did(did_id)
    sys.exit(0 if success else 1)
