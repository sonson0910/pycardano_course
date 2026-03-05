#!/usr/bin/env python3

from dotenv import load_dotenv
load_dotenv()

from app.blockchain.cardano_client import CardanoClient

c = CardanoClient()
c.load_wallet('me_preprod.sk')
u = c.get_utxos(str(c.wallet_address))

print(f"Type: {type(u[0])}")
print(f"Vars: {vars(u[0])}")
print(f"\nFirst UTxO: {u[0]}")
print(f"\nAccessing amount: {u[0].amount}")
