#!/usr/bin/env python3

from dotenv import load_dotenv
load_dotenv()

from pycardano import UTxO, TransactionInput, TransactionOutput, Address, Value
from blockfrost import BlockFrostApi
import os

client = BlockFrostApi(project_id=os.getenv("BLOCKFROST_PROJECT_ID"))
addr = "addr_test1vpx302mqdefht0wly42wlpjmd2rm7xr85j6sgvej8pywusc38sglh"
utxos_bf = client.address_utxos(addr)

print(f"First UTXO Blockfrost: {utxos_bf[0]}\n")

# Convert to PyCardano UTxO
bf_utxo = utxos_bf[0]
print(f"tx_hash: {bf_utxo.tx_hash}")
print(f"output_index: {bf_utxo.output_index}")
print(f"amount: {bf_utxo.amount}")
print(f"address: {bf_utxo.address}")

# Create TransactionInput
tx_in = TransactionInput.from_primitive([bf_utxo.tx_hash, bf_utxo.output_index])
print(f"\nTransactionInput: {tx_in}")

# Create TransactionOutput
lovelace_amount = int(bf_utxo.amount[0].quantity)
tx_out = TransactionOutput(
    Address.from_primitive(bf_utxo.address),
    Value(lovelace_amount)
)
print(f"TransactionOutput: {tx_out}")

# Create UTxO
utxo = UTxO(tx_in, tx_out)
print(f"\nPyCardano UTxO: {utxo}")
