"""Test imports one by one to find error"""

import sys
import traceback

print("1. Testing dotenv...")
try:
    from dotenv import load_dotenv

    print("   ✅ dotenv imported")
except Exception as e:
    print(f"   ❌ dotenv failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print("2. Testing FastAPI...")
try:
    from fastapi import FastAPI

    print("   ✅ FastAPI imported")
except Exception as e:
    print(f"   ❌ FastAPI failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print("3. Loading environment...")
try:
    from pathlib import Path

    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)
    print(f"   ✅ .env loaded from {env_path}")
except Exception as e:
    print(f"   ❌ .env failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print("4. Testing app.models...")
try:
    from app.models import FaceTracker

    print("   ✅ FaceTracker imported")
except Exception as e:
    print(f"   ❌ FaceTracker failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print("5. Testing app.blockchain...")
try:
    from app.blockchain import CardanoClient

    print("   ✅ CardanoClient imported")
except Exception as e:
    print(f"   ❌ CardanoClient failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print("6. Testing app.api...")
try:
    from app.api import router

    print("   ✅ Router imported")
except Exception as e:
    print(f"   ❌ Router failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n✅ All imports successful!")
