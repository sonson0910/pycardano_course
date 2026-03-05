"""
Configuration file for backend services
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Cardano Configuration
CARDANO_NETWORK = os.getenv("CARDANO_NETWORK", "testnet")
CARDANO_KUPO_URL = os.getenv("CARDANO_KUPO_URL", "http://localhost:1442")
CARDANO_OGMIOS_URL = os.getenv("CARDANO_OGMIOS_URL", "http://localhost:1337")

# IPFS Configuration
IPFS_GATEWAY_URL = os.getenv("IPFS_GATEWAY_URL", "http://localhost:5001")
PINATA_JWT = os.getenv("PINATA_JWT", "")

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Face Tracking Configuration
FACE_DETECTION_CONFIDENCE = float(os.getenv("FACE_DETECTION_CONFIDENCE", 0.5))
MAX_TRACKED_FACES = int(os.getenv("MAX_TRACKED_FACES", 10))

# CORS Configuration
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS", "http://localhost:3000,http://localhost:5173"
).split(",")

print(f"Configuration loaded:")
print(f"  Cardano Network: {CARDANO_NETWORK}")
print(f"  IPFS Gateway: {IPFS_GATEWAY_URL}")
print(f"  API: {API_HOST}:{API_PORT}")
