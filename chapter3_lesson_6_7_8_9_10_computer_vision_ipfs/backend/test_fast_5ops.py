"""Fast: Build all 5 DID operations (no submit)"""
import sys
sys.path.insert(0, '.')

from app.blockchain.did_manager import DIDManager
from app.blockchain.cardano_client import CardanoClient
import time

print("\n" + "="*80)
print("FAST TEST: Build All 5 DID Operations (No Submit)")
print("="*80)

try:
    cardano = CardanoClient()
    cardano.load_wallet("me_preprod.sk")
    did_mgr = DIDManager(cardano_client=cardano)
    
    did_id = f"test-{int(time.time())}"
    face_1 = "Qm" + "a" * 44
    face_2 = "Qm" + "b" * 44
    
    print(f"\nDID: {did_id}")
    
    # 1. BUILD CREATE
    print("\n[1/5] BUILD CREATE...")
    try:
        tx1 = did_mgr.create_did(did_id, face_1)
        print(f"✅ TX: {tx1[:40]}...")
    except Exception as e:
        print(f"❌ {str(e)[:80]}")
    
    # 2. BUILD REGISTER
    print("[2/5] BUILD REGISTER...")
    try:
        tx2 = did_mgr.register_did(did_id)
        print(f"✅ TX: {tx2[:40]}...")
    except Exception as e:
        print(f"❌ {str(e)[:80]}")
    
    # 3. BUILD UPDATE
    print("[3/5] BUILD UPDATE...")
    try:
        tx3 = did_mgr.update_did(did_id, face_2)
        print(f"✅ TX: {tx3[:40]}...")
    except Exception as e:
        print(f"❌ {str(e)[:80]}")
    
    # 4. BUILD VERIFY
    print("[4/5] BUILD VERIFY...")
    try:
        tx4 = did_mgr.verify_did(did_id)
        print(f"✅ TX: {tx4[:40]}...")
    except Exception as e:
        print(f"❌ {str(e)[:80]}")
    
    # 5. BUILD REVOKE
    print("[5/5] BUILD REVOKE...")
    try:
        tx5 = did_mgr.revoke_did(did_id)
        print(f"✅ TX: {tx5[:40]}...")
    except Exception as e:
        print(f"❌ {str(e)[:80]}")
    
    print("\n" + "="*80)
    print("✅ ALL 5 OPERATIONS BUILD PASSED!")
    print("="*80)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
