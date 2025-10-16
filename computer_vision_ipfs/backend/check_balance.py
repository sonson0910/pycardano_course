#!/usr/bin/env python3
"""
Check Preprod Wallet Balance
"""

from pycardano import (
    BlockFrostChainContext,
    Address,
    Network,
    PaymentSigningKey,
    PaymentVerificationKey,
)

# Load Preprod wallet
sk = PaymentSigningKey.load("me_preprod.sk")
vk = PaymentVerificationKey.from_signing_key(sk)
addr = Address(payment_part=vk.hash(), network=Network.TESTNET)

print("=" * 70)
print("CHECKING PREPROD WALLET BALANCE")
print("=" * 70)
print()
print(f"Wallet: {str(addr)[:50]}...")
print()

# Connect
context = BlockFrostChainContext(
    project_id="preprod0K9MnKqsU21MJvqu00V4Laf4pz7dALPK",
    base_url="https://cardano-preprod.blockfrost.io/api/",
)

# Get UTxOs
utxos = context.utxos(str(addr))

if utxos:
    total = sum(int(u.output.amount.coin) for u in utxos)
    ada = total / 1_000_000
    print(f"✅ Balance: {ada:.2f} ADA")
    print(f"✅ UTxOs: {len(utxos)}")
    for i, utxo in enumerate(utxos):
        coin = int(utxo.output.amount.coin)
        print(f"   {i+1}. {coin/1_000_000:.2f} ADA")
else:
    print("⏳ No UTxOs yet")
    print("   Faucet might still be processing...")
    print("   Try again in a few seconds")

print()
