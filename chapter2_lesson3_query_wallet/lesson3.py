import os
from dotenv import load_dotenv
from pycardano import BlockFrostChainContext, Address, Network

load_dotenv()

PROJECT_ID = os.getenv("BLOCKFROST_PROJECT_ID")
NETWORK = Network.TESTNET
BASE_URL = "https://cardano-preprod.blockfrost.io/api"

context = BlockFrostChainContext(
    project_id=PROJECT_ID,
    base_url=BASE_URL
)

my_address = "addr_test1qp9ndy73jlt4dypsefj9lkmfu6tzareu0fgpvem070m8m3gx3p0py27juswhx8py8lslr7wnrrkjg4d04aga8pfaz7qs3va3eh"

script_address = "addr_test1wzc86g4ym366hkaphryqqvaptwznqkmk2gdqz9930u534pcx58ahw"

def query_personal_wallet(address):
    utxos = context.utxos(address)

    total_balance = 0

    for i, utxo in enumerate(utxos):
        amount = utxo.output.amount.coin
        total_balance += amount

        print(f'UTXO {i}: {amount} lovelace')

        if utxo.output.amount.multi_asset:
            print(f"UTXO {i}: {utxo.output.amount.multi_asset}")

    total_ada = total_balance / 1_000_000
    print(f"Total balance: {total_ada} ADA")

    return utxos



def query_script(address):
    script_utxos = context.utxos(address)

    for i, utxo in enumerate(script_utxos):
        coin = utxo.output.amount.coin
        datum = utxo.output.datum

        print(f'Utxo {i}: {coin/1_000_000} ada')
        if datum:
            print(f"Datum: {datum}")
        else:
            print("Datum: None")


# my_utxos = query_personal_wallet(my_address)

query_script(script_address)


