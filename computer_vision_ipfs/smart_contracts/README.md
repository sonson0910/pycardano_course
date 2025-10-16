# Smart Contracts for DID Management

This directory contains Aiken smart contracts for managing DIDs on Cardano blockchain.

## Project Structure

```
smart_contracts/
├── validators/          # Aiken validators (smart contracts)
├── lib.ak              # Main library
└── aiken.toml          # Project configuration
```

## Building Contracts

### Prerequisites

```bash
# Install Aiken
curl --proto '=https' --tlsv1.2 -sSfL https://install.aiken-lang.org | sh

# Verify installation
aiken version
```

### Build

```bash
cd smart_contracts
aiken build
```

### Testing

```bash
aiken check
```

## Contract Concepts

### DID Validator

Validates creation and updates of DIDs linked to face data on IPFS.

```aiken
validator did_manager {
  pub fn register(datum: DIDDatum, action: Action) -> Bool {
    // Validation logic
  }
}
```

### Key Features

- Register new DIDs
- Link face embeddings (IPFS hashes)
- Verify face identity
- Update DID metadata
- Revoke DIDs

## Integration

Smart contracts are compiled and deployed to Cardano testnet/mainnet. PyCardano handles interaction:

```python
from pycardano import PlutusData, Address, ScriptHash

script_hash = ScriptHash.from_primitive("...")
script_address = Address(script_hash, network=Network.TESTNET)
```

## Resources

- [Aiken Documentation](https://aiken-lang.org/)
- [Cardano Smart Contracts](https://developers.cardano.org/docs/smart-contracts/)
- [Plutus Reference](https://github.com/IntersectMBO/plutus)

## Next Steps

1. Write DID validator in Aiken
2. Build and test contracts
3. Deploy to testnet
4. Create PyCardano wrappers for interaction
5. Integrate with FastAPI backend
