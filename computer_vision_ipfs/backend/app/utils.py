"""
API Server Configuration and Utils
"""

import logging
from typing import Optional


def setup_logging(level: int = logging.INFO) -> None:
    """Setup application logging"""
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler("app.log")],
    )


def validate_ipfs_hash(ipfs_hash: str) -> bool:
    """Validate IPFS hash format"""
    return ipfs_hash.startswith("Qm") and len(ipfs_hash) >= 46


def validate_did(did: str) -> bool:
    """Validate DID format"""
    return did.startswith("did:cardano:")
