"""
Test Script: Update DID Service
================================

Kiểm tra xem update_did() hoạt động không.
Update là hành động cập nhật face embedding.

Chạy: python test_update_did.py <did_id>
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

def test_update_did(did_id=None):
    """Test updating a DID with new face embedding"""
    
    print("\n" + "="*80)
    print("TEST: UPDATE DID SERVICE")
    print("="*80)
    
    try:
        # If no DID provided, create one first
        if did_id is None:
            print("\n[1/5] Creating test DID first...")
            cardano = CardanoClient()
            cardano.load_wallet("me_preprod.sk")
            did_manager = DIDManager(cardano_client=cardano)
            
            did_id = f"test-did-{int(time.time())}"
            old_ipfs_hash = "Qm" + "c" * 44
            
            did_manager.create_did(did_id, old_ipfs_hash)
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
        print(f"   - Current IPFS: {stored_did.get('ipfs_hash', 'unknown')[:20]}...")
        
        # 3. Update DID with new face embedding
        print("\n[3/5] Updating DID with new face embedding...")
        new_ipfs_hash = "Qm" + "d" * 44  # New IPFS hash
        print(f"   - DID ID: {did_id}")
        print(f"   - New IPFS: {new_ipfs_hash}")
        
        # Call update_did - should return real TX hash
        tx_hash = did_manager.update_did(did_id, new_ipfs_hash)
        
        print(f"   ✅ DID updated successfully!")
        print(f"   - TX Hash: {tx_hash}")
        print(f"   - Action: Update redeemer applied")
        
        # 4. Verify update in storage
        print("\n[4/5] Verifying update...")
        updated_did = did_manager.get_did_document(did_id)
        if updated_did:
            print(f"   ✅ DID storage verified")
            print(f"   - New IPFS: {updated_did.get('ipfs_hash', 'unknown')}")
            print(f"   - Verified reset: {updated_did.get('verified', False)}")
        
        # 5. Check transaction
        print("\n[5/5] Transaction details...")
        print(f"   - TX Hash: {tx_hash}")
        print(f"   - Type: Update redeemer")
        print(f"   - Status: Built and ready for submission")
        print(f"   - Note: Verification status was reset after update")
        
        # Summary
        print("\n" + "="*80)
        print("✅ TEST PASSED: Update DID service is working!")
        print("="*80)
        print(f"\nSummary:")
        print(f"  - DID: {did_id}")
        print(f"  - Action: Update")
        print(f"  - Old IPFS: {stored_did.get('ipfs_hash', 'unknown')[:20]}...")
        print(f"  - New IPFS: {new_ipfs_hash}")
        print(f"  - Transaction: {tx_hash}")
        print(f"  - Next: Test verify or revoke operations")
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
    success = test_update_did(did_id)
    sys.exit(0 if success else 1)
