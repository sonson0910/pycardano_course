#!/usr/bin/env python3
"""Test REGISTER ONLY - không tạo DID trước"""
import sys
sys.path.insert(0, '.')

from app.blockchain.cardano_client import CardanoClient
from app.blockchain.did_manager import DIDManager

print("\n" + "="*80)
print("TEST: REGISTER ONLY (no CREATE first)")
print("="*80 + "\n")

try:
    cardano = CardanoClient()
    cardano.load_wallet('me_preprod.sk')
    did_mgr = DIDManager(cardano_client=cardano)
    
    # Use DID từ test CREATE trước (test-did-1761087553)
    did_id = "test-did-1761087553"
    
    print(f"[REGISTER] DID: {did_id}\n")
    print("[ACTION] Calling register_did()...")
    
    tx_hash = did_mgr.register_did(did_id)
    
    print(f"\n✅ REGISTER PASSED!")
    print(f"   TX Hash: {tx_hash}\n")
    
except Exception as e:
    print(f"\n❌ REGISTER FAILED: {str(e)[:200]}\n")
    sys.exit(1)
