# PyCardano Integration Guide

This guide explains how to use PyCardano in this project.

## Installation

```bash
pip install pycardano
```

## Basic Setup

### 1. Initialize Client

```python
from pycardano import PyCardano, Network

# Connect to testnet
client = PyCardano(
    network=Network.TESTNET,
    kupo_url="http://localhost:1442",
    ogmios_url="http://localhost:1337"
)
```

### 2. Load Wallet

```python
from pycardano import PaymentSigningKey, PaymentVerificationKey

# From mnemonic (see documentation)
signing_key = PaymentSigningKey.from_mnemonic("your 12 or 24 word phrase")
verification_key = PaymentVerificationKey.from_signing_key(signing_key)
```

### 3. Query Balance

```python
address = signing_key.to_address()
utxos = client.utxos(address)
balance = sum(utxo.amount.coin for utxo in utxos)
print(f"Balance: {balance} Lovelace")
```

## Building Transactions

### Simple Transfer

```python
from pycardano import (
    TransactionBuilder,
    Address,
    Value,
    Coin
)

# Build transaction
builder = TransactionBuilder()
builder.add_input_address(sender_address)
builder.add_output(
    Address.from_primitive("addr_test1..."),
    Value(Coin(1000000))  # 1 ADA
)
tx = builder.build()
```

### With Metadata

```python
from pycardano import Metadata, AuxiliaryData

# Add metadata
metadata = Metadata({
    1: "Face Embedding",
    2: {"face_id": "face_001", "ipfs": "QmXxx"}
})
tx.auxiliary_data = AuxiliaryData(metadata)
```

## Smart Contract Interaction

### Query Script UTxOs

```python
script_hash = ScriptHash.from_primitive("...")
script_address = Address(script_hash, network=Network.TESTNET)
utxos = client.utxos(script_address)
```

### Lock Funds at Script

```python
builder = TransactionBuilder()
builder.add_input_address(user_address)
builder.add_output(
    script_address,
    Value(Coin(2000000))  # Lock 2 ADA
)
tx = builder.build()
```

## Transaction Signing & Submission

```python
# Sign transaction
signed_tx = signing_key.sign(tx)

# Submit to blockchain
tx_id = client.submit_tx(signed_tx)
print(f"Transaction submitted: {tx_id}")
```

## Useful Links

- [PyCardano GitHub](https://github.com/dcspark/pycardano)
- [Cardano Testnet Faucet](https://testnets.cardano.org/en/testnets/cardano/tools/faucet/)
- [Cardano Blockchain Explorer](https://testnet.cardanoscan.io/)
- [PyCardano Examples](https://github.com/dcspark/pycardano/tree/main/examples)

## Common Tasks

### Get UTxOs for Address

```python
def get_utxos(client, address):
    return client.utxos(address)
```

### Build and Sign Transaction

```python
def build_transaction(client, sender, receiver, amount):
    builder = TransactionBuilder()
    builder.add_input_address(sender)
    builder.add_output(receiver, Value(Coin(amount)))
    return builder.build()

def sign_transaction(tx, signing_key):
    return signing_key.sign(tx)
```

### Submit Transaction

```python
def submit_transaction(client, signed_tx):
    return client.submit_tx(signed_tx)
```

## Integration in DApp

The `CardanoClient` class in `backend/app/blockchain/cardano_client.py` wraps PyCardano functionality:

```python
from app.blockchain import CardanoClient

client = CardanoClient(network="testnet")
balance = client.get_balance(address)
utxos = client.get_utxos(address)
tx = client.build_transaction(sender, receiver, 1000000)
```

## Testing

For development/testing:
1. Use testnet only
2. Get free tADA from [faucet](https://testnets.cardano.org/en/testnets/cardano/tools/faucet/)
3. Use [Cardano Preview testnet](https://testnets.cardano.org/)
4. Monitor with [Cardanoscan](https://testnet.cardanoscan.io/)

## Error Handling

```python
try:
    tx_id = client.submit_tx(signed_tx)
except Exception as e:
    print(f"Transaction failed: {e}")
    # Handle error appropriately
```

## Next Steps

1. Setup local Cardano node
2. Load wallet with test ADA
3. Create transactions
4. Deploy smart contracts
5. Interact with contracts
