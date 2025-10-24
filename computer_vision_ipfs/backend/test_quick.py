"""Quick test of transaction submission"""

import sys
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent))

from app.blockchain.did_manager import DIDManager
from app.blockchain.cardano_client import CardanoClient

print("Init...")
cardano = CardanoClient()
cardano.load_wallet("me_preprod.sk")
did_mgr = DIDManager(cardano_client=cardano)

print("Creating DID 1...")
did_id_1 = f"test-{int(time.time())}"
tx1 = did_mgr.create_did(did_id_1, "Qm" + "a" * 44)
print(f"TX 1: {tx1[:32]}...")

print("\nCreating DID 2...")
did_id_2 = f"test-{int(time.time()+1)}"
tx2 = did_mgr.create_did(did_id_2, "Qm" + "b" * 44)
print(f"TX 2: {tx2[:32]}...")

if tx1 != tx2:
    print(f"\n✅ SUCCESS: TX hashes are DIFFERENT!")
    print(f"   TX 1: {tx1}")
    print(f"   TX 2: {tx2}")
else:
    print(f"\n❌ FAIL: TX hashes are IDENTICAL (still using mock!)")
