"""Quick test: All 5 DID operations"""
import sys
sys.path.insert(0, '.')

from app.blockchain.did_manager import DIDManager
from app.blockchain.cardano_client import CardanoClient
import time

def test_all_ops():
    print("\n" + "="*80)
    print("TEST: All 5 DID Operations")
    print("="*80)
    
    try:
        # Init
        print("\n[INIT] Initializing...")
        cardano = CardanoClient()
        cardano.load_wallet("me_preprod.sk")
        did_mgr = DIDManager(cardano_client=cardano)
        print("✅ Initialized")
        
        # 1. CREATE
        print("\n[1/5] CREATE DID...")
        did_id = f"test-{int(time.time())}"
        face_hash_1 = "Qm" + "a" * 44
        tx1 = did_mgr.create_did(did_id, face_hash_1)
        print(f"✅ CREATE: {tx1[:32]}...")
        
        # 2. REGISTER
        print("\n[2/5] REGISTER DID...")
        tx2 = did_mgr.register_did(did_id)
        print(f"✅ REGISTER: {tx2[:32]}...")
        
        # 3. UPDATE
        print("\n[3/5] UPDATE DID...")
        face_hash_2 = "Qm" + "b" * 44
        tx3 = did_mgr.update_did(did_id, face_hash_2)
        print(f"✅ UPDATE: {tx3[:32]}...")
        
        # 4. VERIFY
        print("\n[4/5] VERIFY DID...")
        tx4 = did_mgr.verify_did(did_id)
        print(f"✅ VERIFY: {tx4[:32]}...")
        
        # 5. REVOKE
        print("\n[5/5] REVOKE DID...")
        tx5 = did_mgr.revoke_did(did_id)
        print(f"✅ REVOKE: {tx5[:32]}...")
        
        print("\n" + "="*80)
        print("✅ ALL 5 OPERATIONS PASSED!")
        print("="*80)
        print(f"DID: {did_id}")
        print(f"  1. CREATE:   {tx1[:32]}...")
        print(f"  2. REGISTER: {tx2[:32]}...")
        print(f"  3. UPDATE:   {tx3[:32]}...")
        print(f"  4. VERIFY:   {tx4[:32]}...")
        print(f"  5. REVOKE:   {tx5[:32]}...")
        
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_all_ops()
    sys.exit(0 if success else 1)
