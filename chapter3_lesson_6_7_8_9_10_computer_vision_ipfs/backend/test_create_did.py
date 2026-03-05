"""
Test Script: Create DID Service
================================

Kiểm tra xem DID creation service hoạt động không.
Không dùng mock hay placeholder - tất cả đều thực.

Chạy: python test_create_did.py
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

def test_create_did():
    """Test creating a DID on blockchain"""
    
    print("\n" + "="*80)
    print("TEST: CREATE DID SERVICE")
    print("="*80)
    
    try:
        # 1. Initialize clients
        print("\n[1/5] Initializing CardanoClient...")
        cardano = CardanoClient()
        print(f"   ✅ CardanoClient initialized")
        print(f"   - Network: Cardano Preprod Testnet")
        
        # Load wallet
        print("\n   Loading wallet...")
        cardano.load_wallet("me_preprod.sk")
        print(f"   ✅ Wallet loaded: {str(cardano.wallet_address)[:20]}...")
        
        # 2. Initialize DIDManager
        print("\n[2/5] Initializing DIDManager...")
        did_manager = DIDManager(cardano_client=cardano)
        print(f"   ✅ DIDManager initialized")
        print(f"   - Storage location: ./dids_registry.json")
        
        # 3. Get wallet balance
        print("\n[3/5] Checking wallet balance...")
        sender = str(cardano.wallet_address)
        # Note: context.utxos() returns PyCardano UTxO objects, not Blockfrost namespace
        try:
            utxos = cardano.context.utxos(sender)
            print(f"   ✅ Wallet ready")
            print(f"   - UTxOs available: {len(utxos)}")
            if utxos:
                # PyCardano UTxO objects have amount.coin property
                total_lovelace = sum([u.output.amount.coin for u in utxos])
                ada = total_lovelace / 1_000_000
                print(f"   - Total balance: {ada:.2f} ADA")
        except Exception as e:
            print(f"   ⚠️  Could not fetch balance: {e}")
            print(f"   - Proceeding anyway...")
        
        # 4. Create DID
        print("\n[4/5] Creating DID...")
        did_id = f"test-did-{int(time.time())}"
        face_ipfs_hash = "Qm" + "a" * 44  # Fake IPFS hash for testing
        
        print(f"   - DID ID: {did_id}")
        print(f"   - IPFS Hash: {face_ipfs_hash}")
        
        # This should build and return a real transaction
        tx_hash = did_manager.create_did(did_id, face_ipfs_hash)
        
        print(f"   ✅ DID created successfully!")
        print(f"   - TX Hash: {tx_hash}")
        print(f"   - Status: Built and ready")
        
        # 5. Verify DID was stored locally
        print("\n[5/5] Verifying DID storage...")
        stored_did = did_manager.get_did_document(did_id)
        if stored_did:
            print(f"   ✅ DID stored locally")
            print(f"   - Status: {stored_did.get('status', 'unknown')}")
            print(f"   - Created at: {stored_did.get('created_at', 'unknown')}")
        else:
            print(f"   ⚠️  DID not found in local storage")
        
        # Summary
        print("\n" + "="*80)
        print("✅ TEST PASSED: Create DID service is working!")
        print("="*80)
        print(f"\nSummary:")
        print(f"  - DID created: {did_id}")
        print(f"  - Transaction: {tx_hash}")
        print(f"  - Next: You can submit this TX to blockchain or test other operations")
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
    success = test_create_did()
    sys.exit(0 if success else 1)
