#!/usr/bin/env python3
"""Check wallet address from me_preprod.sk"""

from pycardano import PaymentSigningKey, PaymentVerificationKey, Address, Network

try:
    # Load signing key
    sk = PaymentSigningKey.load("backend/me_preprod.sk")
    print(f"✅ Loaded signing key")

    # Derive verification key
    vk = PaymentVerificationKey.from_signing_key(sk)
    print(f"✅ Derived verification key")

    # Get testnet address
    addr_testnet = Address(payment_part=vk.hash(), network=Network.TESTNET)
    print(f"\n🔑 Testnet Address (Network.TESTNET):")
    print(f"   {addr_testnet}")

    # Get preprod address
    addr_preprod = Address(payment_part=vk.hash(), network=Network.TESTNET)
    print(f"\n🔑 Preprod Address (Network.TESTNET - same as above):")
    print(f"   {addr_preprod}")

    print(f"\n💡 Use this address for preprod faucet:")
    print(f"   https://testnets.cardano.org/en/testnets/cardano/tools/faucet/")
    print(f"\n   Or check explorer:")
    print(f"   https://preprod.cexplorer.io/address/{addr_testnet}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
