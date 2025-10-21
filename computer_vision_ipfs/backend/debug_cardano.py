"""Debug script to trace exact failure point"""

import sys
import os

print("Loading .env...")
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

print(f"BLOCKFROST_PROJECT_ID set: {bool(os.environ.get('BLOCKFROST_PROJECT_ID'))}")

print("\nImporting CardanoClient...")
from app.blockchain.cardano_client import CardanoClient

print("Creating CardanoClient instance...")
try:
    client = CardanoClient()
    print("✅ CardanoClient created successfully!")
except Exception as e:
    print(f"❌ CardanoClient failed: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

print("\nAll tests passed!")
