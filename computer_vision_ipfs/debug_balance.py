#!/usr/bin/env python3
"""Debug script to check wallet balance and UTxOs"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.blockchain.cardano_client import CardanoClient
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def main():
    try:
        # Initialize Cardano client
        client = CardanoClient()

        # Load wallet
        logger.info("Loading wallet...")
        client.load_wallet("me_preprod.sk")

        wallet_address = str(client.wallet_address)
        logger.info(f"✅ Wallet: {wallet_address}")

        # Check UTxOs
        logger.info(f"\n📦 Fetching UTxOs...")
        utxos = client.context.utxos(wallet_address)

        if not utxos:
            logger.error("❌ NO UTxOs found!")
            logger.info("\n🔧 Solutions:")
            logger.info(
                "1. Request testnet faucet: https://testnets.cardano.org/en/testnets/cardano/tools/faucet/"
            )
            logger.info("2. Wait 2-3 minutes for faucet to process")
            logger.info("3. Check balance: https://preview.cexplorer.io/")
            return False

        logger.info(f"✅ Found {len(utxos)} UTxO(s)")

        total_balance = 0
        for i, utxo in enumerate(utxos):
            amount = utxo.output.amount.coin
            total_balance += amount
            logger.info(f"   UTxO {i}: {amount} lovelace ({amount/1_000_000:.2f} ADA)")

            # Check if it's a script-locked UTxO
            if utxo.output.datum:
                logger.info(f"      ⚠️  Has datum (script-locked)")
            if utxo.output.script:
                logger.info(f"      ⚠️  Has script")

        logger.info(
            f"\n💰 Total balance: {total_balance} lovelace ({total_balance/1_000_000:.2f} ADA)"
        )

        if total_balance == 0:
            logger.error("❌ Wallet has 0 balance! Need to request faucet")
            return False

        logger.info("✅ Wallet is ready!")
        return True

    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
