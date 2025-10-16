#!/usr/bin/env python3
"""
Setup Blockfrost API Key - Interactive Guide
"""

import os
import sys


def show_setup_guide():
    """Show how to get and set Blockfrost API key"""

    print("\n" + "=" * 70)
    print("🔑 BLOCKFROST API KEY SETUP GUIDE")
    print("=" * 70)
    print()

    print("Your current .env has a TEST key that won't work.")
    print("You need a REAL FREE API key from Blockfrost.")
    print()

    print("STEP 1: Get your FREE API key")
    print("-" * 70)
    print("  1. Go to: https://blockfrost.io")
    print("  2. Click 'Sign Up' (top right)")
    print("  3. Create free account")
    print("  4. Verify your email")
    print("  5. Log in to dashboard")
    print("  6. Create new project:")
    print("     • Name: computer-vision-did (or any name)")
    print("     • Network: CARDANO PREVIEW TESTNET")
    print("  7. Copy your API key (starts with 'preview')")
    print()

    print("STEP 2: Update your .env file")
    print("-" * 70)
    print("  Replace this line in .env:")
    print()
    print("  OLD: BLOCKFROST_PROJECT_ID=preview2n7yYufxFE7ipgxV24dOtxQLLn5JCAjI")
    print()
    print("  WITH: BLOCKFROST_PROJECT_ID=<your-new-api-key>")
    print()
    print("  Example: BLOCKFROST_PROJECT_ID=previewAbCdEfGhIjKlMnOpQrStUvWxYz")
    print()

    print("STEP 3: Test the connection")
    print("-" * 70)
    print("  After updating .env, run:")
    print()
    print("  $ python deploy.py")
    print()

    print("⚠️  IMPORTANT")
    print("-" * 70)
    print("  • Keep your API key SECRET - don't share it!")
    print("  • The free tier is sufficient for testing")
    print("  • Blockfrost free tier has rate limits but enough for development")
    print()

    print("QUICK ALTERNATIVE (If Blockfrost is slow)")
    print("-" * 70)
    print("  You can also use Cardano CLI directly:")
    print()
    print("  $ cardano-cli query utxo --address <YOUR_ADDRESS> --testnet-magic 2")
    print("  $ cardano-cli transaction build ...")
    print("  $ cardano-cli transaction sign ...")
    print("  $ cardano-cli transaction submit ...")
    print()

    print("✅ Once complete, run: python deploy.py")
    print()


if __name__ == "__main__":
    show_setup_guide()
