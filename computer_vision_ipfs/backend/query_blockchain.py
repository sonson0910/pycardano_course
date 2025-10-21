#!/usr/bin/env python3
"""
Query blockchain để lấy các DIDs đã tạo từ trước
"""
import sys
sys.path.insert(0, '.')

from app.blockchain.cardano_client import CardanoClient
from app.blockchain.did_manager import DIDManager
from pycardano import Address, ScriptHash, Network

print("\n" + "="*80)
print("QUERY: Existing DIDs on blockchain")
print("="*80 + "\n")

try:
    cardano = CardanoClient()
    cardano.load_wallet('me_preprod.sk')
    
    # Get script address
    script_hash = ScriptHash(bytes.fromhex(cardano.SCRIPT_HASH))
    script_address = Address(script_hash, network=Network.TESTNET)
    
    print(f"[INFO] Script address: {str(script_address)}\n")
    
    # Query UTxOs at script address
    print("[ACTION] Querying blockchain for script UTxOs...")
    utxos = cardano.context.utxos(str(script_address))
    
    print(f"\n✅ Found {len(utxos)} UTxO(s) at script address\n")
    
    if len(utxos) == 0:
        print("⚠️  No DIDs found on blockchain yet")
    else:
        print("DIDs on blockchain:")
        print("-" * 80)
        for i, utxo in enumerate(utxos[:20]):  # Show first 20
            tx_id = str(utxo.input.transaction_id)
            idx = utxo.input.index
            value = utxo.output.amount.coin
            
            # Try to decode datum
            try:
                if utxo.output.datum:
                    datum = utxo.output.datum
                    did_id = datum.did_id.decode('utf-8', errors='ignore') if hasattr(datum.did_id, 'decode') else str(datum.did_id)[:20]
                    print(f"{i+1}. TX: {tx_id[:16]}#{idx}")
                    print(f"   DID ID: {did_id}")
                    print(f"   Value: {value} lovelace (~{value/1_000_000:.2f} ADA)")
                    print()
            except:
                print(f"{i+1}. TX: {tx_id[:16]}#{idx} - Value: {value} lovelace\n")
    
    print("="*80)
    
except Exception as e:
    print(f"❌ ERROR: {str(e)[:300]}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)
