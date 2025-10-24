#!/usr/bin/env python3
import sys
import time

sys.path.insert(0, ".")

from app.blockchain.cardano_client import CardanoClient
from app.blockchain.did_manager import DIDManager

print("TEST: CREATE only\n")

cardano = CardanoClient()
cardano.load_wallet("me_preprod.sk")
did_mgr = DIDManager(cardano_client=cardano)

did_id = f"test-{int(time.time())}"
print(f"Creating: {did_id}")
t0 = time.time()

tx = did_mgr.create_did(did_id, "Qm" + "x" * 44)

t_elapsed = time.time() - t0
print(f"✅ TX: {tx[:16]}...")
print(f"⏱️  Time: {t_elapsed:.1f}s")
