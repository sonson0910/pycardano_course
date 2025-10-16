import requests
import time

tx_hash = "1519bf1bf1ef5a38ccdf46cba4089e7210288f44dfa1f9d27c294bfa906dd952"
print(f"Waiting 60 seconds for confirmation...")
time.sleep(60)

r = requests.get(
    f"https://cardano-preprod.blockfrost.io/api/v0/txs/{tx_hash}",
    headers={"project_id": "preprod0K9MnKqsU21MJvqu00V4Laf4pz7dALPK"},
)

if r.status_code == 200:
    data = r.json()
    print(f"\n[SUCCESS] TX CONFIRMED!")
    print(f"Block: {data.get('block_height')}")
    print(f"Slot: {data.get('slot')}")
else:
    print(f"\n[PENDING] Status: {r.status_code}")
    print(f"Response: {r.text[:200]}")
