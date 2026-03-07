"""
IPFS Service — Pinata wrapper

Upload/retrieve JSON to IPFS via Pinata API.
"""

import json
import logging
import os
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

PINATA_API = "https://api.pinata.cloud"

# Singleton
_instance: Optional["IPFSService"] = None


def get_ipfs_service() -> "IPFSService":
    global _instance
    if _instance is None:
        _instance = IPFSService()
    return _instance


class IPFSService:
    """Pinata IPFS upload & retrieve"""

    def __init__(self):
        self.jwt = os.getenv("PINATA_JWT")
        if not self.jwt:
            logger.warning("⚠️ PINATA_JWT not set — IPFS uploads will fail")
            return
        self.headers = {"Authorization": f"Bearer {self.jwt}"}
        logger.info("✅ IPFSService initialized")

    def upload_json(self, data: dict, name: str = "face_embedding") -> str:
        """Upload JSON → returns CID"""
        if not self.jwt:
            raise ValueError("PINATA_JWT not configured")

        payload = {
            "pinataContent": data,
            "pinataMetadata": {"name": name},
        }

        resp = requests.post(
            f"{PINATA_API}/pinning/pinJSONToIPFS",
            json=payload,
            headers={**self.headers, "Content-Type": "application/json"},
            timeout=30,
        )

        if resp.status_code != 200:
            raise Exception(f"IPFS upload failed: {resp.text}")

        cid = resp.json()["IpfsHash"]
        logger.info(f"📤 Uploaded to IPFS: {cid}")
        return cid

    def get_json(self, cid: str) -> dict:
        """Retrieve JSON from IPFS by CID"""
        resp = requests.get(
            f"https://gateway.pinata.cloud/ipfs/{cid}",
            timeout=30,
        )
        if resp.status_code != 200:
            raise Exception(f"IPFS fetch failed: {resp.status_code}")
        return resp.json()
