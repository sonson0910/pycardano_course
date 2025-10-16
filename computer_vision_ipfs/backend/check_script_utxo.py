import requests

script_addr = "addr_test1wrv4nz2aqcs7xlceprsswudh9ru2l0yy7xqedhzya037nqssayaju"
headers = {"project_id": "preprod0K9MnKqsU21MJvqu00V4Laf4pz7dALPK"}

r = requests.get(
    f"https://cardano-preprod.blockfrost.io/api/v0/addresses/{script_addr}/utxos",
    headers=headers,
)
print(f"Status: {r.status_code}")
data = r.json()

if isinstance(data, list):
    print(f"Total UTxOs: {len(data)}")
    for i, utxo in enumerate(data[:5], 1):
        tx_hash = utxo.get("tx_hash", "")[:20]
        amount = utxo.get("amount", [{}])[0].get("quantity", "")
        print(f"{i}. TX: {tx_hash}... Amount: {amount}")
else:
    print(f"Error: {data}")
