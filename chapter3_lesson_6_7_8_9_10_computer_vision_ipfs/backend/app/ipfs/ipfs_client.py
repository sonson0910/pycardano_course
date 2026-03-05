"""
IPFS Client for storing face embeddings and metadata off-chain
"""

import json
import requests
from typing import Dict, Any, Optional
from pathlib import Path
import logging


logger = logging.getLogger(__name__)


class IPFSClient:
    """
    IPFS client for uploading and retrieving data
    Uses Kubo HTTP API or Pinata gateway
    """

    def __init__(
        self,
        gateway_url: str = "http://localhost:5001",
        pinata_jwt: Optional[str] = None,
    ):
        """
        Initialize IPFS client

        Args:
            gateway_url: IPFS node gateway URL (default: local Kubo node)
            pinata_jwt: Optional Pinata JWT for pinning to Pinata
        """
        self.gateway_url = gateway_url.rstrip("/")
        self.pinata_jwt = pinata_jwt
        self.api_url = f"{self.gateway_url}/api/v0"

    def add_json(self, data: Dict[str, Any]) -> str:
        """
        Add JSON data to IPFS

        Args:
            data: Dictionary to upload

        Returns:
            IPFS hash (CID)
        """
        try:
            json_data = json.dumps(data)
            files = {"file": ("data.json", json_data)}

            response = requests.post(f"{self.api_url}/add", files=files, timeout=30)

            if response.status_code == 200:
                result = response.json()
                cid = result.get("Hash")
                logger.info(f"Data uploaded to IPFS: {cid}")
                return cid
            else:
                raise Exception(f"IPFS upload failed: {response.text}")

        except Exception as e:
            logger.error(f"Error uploading to IPFS: {e}")
            raise

    def add_file(self, file_path: str) -> str:
        """
        Add file to IPFS

        Args:
            file_path: Path to file to upload

        Returns:
            IPFS hash (CID)
        """
        try:
            with open(file_path, "rb") as f:
                files = {"file": (Path(file_path).name, f)}

                response = requests.post(f"{self.api_url}/add", files=files, timeout=30)

            if response.status_code == 200:
                result = response.json()
                cid = result.get("Hash")
                logger.info(f"File uploaded to IPFS: {cid}")
                return cid
            else:
                raise Exception(f"IPFS upload failed: {response.text}")

        except Exception as e:
            logger.error(f"Error uploading file to IPFS: {e}")
            raise

    def add_file_bytes(self, file_bytes: bytes, filename: str = "data") -> str:
        """
        Add raw bytes to IPFS

        Args:
            file_bytes: Raw bytes to upload
            filename: Name for the file

        Returns:
            IPFS hash (CID)
        """
        try:
            files = {"file": (filename, file_bytes)}

            response = requests.post(f"{self.api_url}/add", files=files, timeout=30)

            if response.status_code == 200:
                result = response.json()
                cid = result.get("Hash")
                logger.info(f"Bytes uploaded to IPFS: {cid}")
                return cid
            else:
                raise Exception(f"IPFS upload failed: {response.text}")

        except Exception as e:
            logger.error(f"Error uploading bytes to IPFS: {e}")
            raise

    def get_json(self, cid: str) -> Dict[str, Any]:
        """
        Retrieve JSON data from IPFS

        Args:
            cid: IPFS content hash

        Returns:
            Decoded JSON data
        """
        try:
            response = requests.get(f"{self.gateway_url}/ipfs/{cid}", timeout=30)

            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to retrieve from IPFS: {response.status_code}")

        except Exception as e:
            logger.error(f"Error retrieving from IPFS: {e}")
            raise

    def pin_to_pinata(self, cid: str) -> Dict[str, Any]:
        """
        Pin content to Pinata for persistence

        Args:
            cid: IPFS content hash

        Returns:
            Pinata response
        """
        if not self.pinata_jwt:
            logger.warning("Pinata JWT not configured, skipping pinning")
            return {}

        try:
            headers = {"Authorization": f"Bearer {self.pinata_jwt}"}
            data = {"hashToPin": cid}

            response = requests.post(
                "https://api.pinata.cloud/pinning/pinByHash",
                json=data,
                headers=headers,
                timeout=30,
            )

            if response.status_code == 200:
                logger.info(f"Content pinned to Pinata: {cid}")
                return response.json()
            else:
                raise Exception(f"Pinata pin failed: {response.text}")

        except Exception as e:
            logger.error(f"Error pinning to Pinata: {e}")
            raise

    def upload_face_embedding(
        self, face_id: str, embedding: str, metadata: Dict
    ) -> str:
        """
        Upload face embedding with metadata to IPFS

        Args:
            face_id: Unique face identifier
            embedding: Face embedding hash/reference
            metadata: Additional metadata

        Returns:
            IPFS hash of the face data
        """
        data = {
            "face_id": face_id,
            "embedding": embedding,
            "metadata": metadata,
            "timestamp": metadata.get("timestamp"),
        }

        return self.add_json(data)
