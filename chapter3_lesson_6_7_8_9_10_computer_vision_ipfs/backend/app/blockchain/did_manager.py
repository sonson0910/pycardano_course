"""
DID (Decentralized Identifier) Manager using Cardano Blockchain
Manages creation and verification of DIDs linked to face data
"""

import json
import uuid
from typing import Dict, Optional, List
from datetime import datetime
import logging
import hashlib
import time
from dataclasses import dataclass
from pycardano import PlutusData
from .cardano_client import CardanoClient


logger = logging.getLogger(__name__)


# ============================================================================
# DIDDatum - On-chain DID type that matches validator
# ============================================================================


@dataclass
class DIDDatum(PlutusData):
    """
    On-chain DID Datum - must match validator definition exactly

    Validator expects:
    pub type DIDDatum {
      did_id: ByteArray,
      face_ipfs_hash: ByteArray,
      owner: ByteArray,
      created_at: Int,
      verified: Int,  # 0 = false, 1 = true
    }
    """

    did_id: bytes  # ByteArray - unique DID identifier
    face_ipfs_hash: bytes  # ByteArray - IPFS hash of face embedding
    owner: bytes  # ByteArray - owner's public key hash (28 bytes)
    created_at: int  # Int - creation timestamp in milliseconds
    verified: int  # Int - verification status (0=false, 1=true)

    def __post_init__(self):
        """Validate datum fields after creation"""
        if len(self.did_id) == 0:
            raise ValueError('❌ did_id cannot be empty (validator: did_id != #"")')
        if len(self.face_ipfs_hash) == 0:
            raise ValueError(
                '❌ face_ipfs_hash cannot be empty (validator: face_ipfs_hash != #"")'
            )
        if self.created_at <= 0:
            raise ValueError("❌ created_at must be > 0 (validator: created_at > 0)")


class DIDManager:
    """
    Manages DIDs on Cardano blockchain with proper on-chain integration
    Links face embeddings (stored on IPFS) to on-chain DID identifiers
    """

    def __init__(self, cardano_client: CardanoClient):
        """
        Initialize DID Manager

        Args:
            cardano_client: CardanoClient instance
        """
        self.cardano = cardano_client
        self.dids: Dict[str, Dict] = {}

    def create_did_datum(
        self, face_ipfs_hash: str, owner_address: str, metadata: Optional[Dict] = None
    ) -> DIDDatum:
        """
        Create DIDDatum with correct on-chain fields

        Args:
            face_ipfs_hash: IPFS hash of face embedding (e.g., "QmXxxx...")
            owner_address: Cardano address string
            metadata: Optional metadata dict

        Returns:
            DIDDatum with all fields set correctly for validator

        Validation:
            ✅ did_id: non-empty bytes
            ✅ face_ipfs_hash: non-empty bytes
            ✅ owner: 28-byte blake2b hash
            ✅ created_at: positive millisecond timestamp
            ✅ verified: False initially
        """
        try:
            # 1. Generate did_id as bytes
            did_suffix = str(uuid.uuid4())[:12]
            did_id_bytes = did_suffix.encode("utf-8")

            # Validate not empty
            if len(did_id_bytes) == 0:
                raise ValueError("did_id cannot be empty")

            # 2. Convert IPFS hash to bytes
            face_ipfs_bytes = face_ipfs_hash.encode("utf-8")

            # Validate not empty
            if len(face_ipfs_bytes) == 0:
                raise ValueError("face_ipfs_hash cannot be empty")

            # 3. Hash owner address to 28-byte blake2b (Cardano standard)
            owner_hash = hashlib.blake2b(
                owner_address.encode("utf-8"), digest_size=28
            ).digest()

            if len(owner_hash) != 28:
                raise ValueError(f"owner hash must be 28 bytes, got {len(owner_hash)}")

            # 4. Create timestamp in milliseconds
            created_at_ms = int(time.time() * 1000)

            # Validate > 0
            if created_at_ms <= 0:
                raise ValueError("created_at must be > 0")

            # 5. Create datum
            datum = DIDDatum(
                did_id=did_id_bytes,
                face_ipfs_hash=face_ipfs_bytes,
                owner=owner_hash,
                created_at=created_at_ms,
                verified=0,  # 0 = not verified
            )

            logger.info(f"✅ DIDDatum created: {did_id_bytes.hex()[:8]}...")
            logger.info(f"   - did_id: {len(did_id_bytes)} bytes")
            logger.info(f"   - face_ipfs_hash: {len(face_ipfs_bytes)} bytes")
            logger.info(f"   - owner: {len(owner_hash)} bytes")
            logger.info(f"   - created_at: {created_at_ms} ms")
            logger.info(f"   - verified: {datum.verified}")

            # Store locally for reference
            self.dids[did_id_bytes.hex()] = {
                "datum": datum,
                "created_at": datetime.utcnow().isoformat(),
                "metadata": metadata or {},
            }

            return datum

        except Exception as e:
            logger.error(f"❌ Failed to create DIDDatum: {e}")
            raise

    def validate_register_datum(self, datum: DIDDatum) -> bool:
        """
        Validate datum for Register action
        Mirrors validator logic: validate_register(d)

        Checks:
        ✓ datum.did_id != #""
        ✓ datum.face_ipfs_hash != #""
        ✓ datum.created_at > 0
        """
        try:
            if len(datum.did_id) == 0:
                raise ValueError("❌ Register: did_id cannot be empty")
            if len(datum.face_ipfs_hash) == 0:
                raise ValueError("❌ Register: face_ipfs_hash cannot be empty")
            if datum.created_at <= 0:
                raise ValueError("❌ Register: created_at must be > 0")
            logger.info("✅ Register action validation passed")
            return True
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            raise

    def validate_update_datum(self, datum: DIDDatum) -> bool:
        """
        Validate datum for Update action
        Mirrors validator logic: validate_update(d)

        Checks:
        ✓ datum.did_id != #""
        """
        try:
            if len(datum.did_id) == 0:
                raise ValueError("❌ Update: did_id cannot be empty")
            logger.info("✅ Update action validation passed")
            return True
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            raise

    def validate_verify_datum(self, datum: DIDDatum) -> bool:
        """
        Validate datum for Verify action
        Mirrors validator logic: validate_verify(d)

        Checks:
        ✓ datum.did_id != #""
        ✓ datum.face_ipfs_hash != #""
        """
        try:
            if len(datum.did_id) == 0:
                raise ValueError("❌ Verify: did_id cannot be empty")
            if len(datum.face_ipfs_hash) == 0:
                raise ValueError("❌ Verify: face_ipfs_hash cannot be empty")
            logger.info("✅ Verify action validation passed")
            return True
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            raise

    def validate_revoke_datum(self, datum: DIDDatum) -> bool:
        """
        Validate datum for Revoke action
        Mirrors validator logic: validate_revoke(d)

        Checks:
        ✓ datum.did_id != #""
        """
        try:
            if len(datum.did_id) == 0:
                raise ValueError("❌ Revoke: did_id cannot be empty")
            logger.info("✅ Revoke action validation passed")
            return True
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            raise

    def register_did_on_chain(self, did: str, tx_hash: str) -> bool:
        """
        Register DID on Cardano blockchain

        Args:
            did: DID to register
            tx_hash: Cardano transaction hash

        Returns:
            True if registration successful
        """
        try:
            if did not in self.dids:
                raise ValueError(f"DID not found: {did}")

            self.dids[did]["tx_hash"] = tx_hash
            self.dids[did]["on_chain"] = True
            self.dids[did]["registered_at"] = datetime.utcnow().isoformat()

            logger.info(f"DID registered on-chain: {did} (tx: {tx_hash})")
            return True

        except Exception as e:
            logger.error(f"Failed to register DID: {e}")
            raise

    def verify_face_identity(self, did: str, face_ipfs_hash: str) -> bool:
        """
        Verify if face hash matches DID

        Args:
            did: DID to verify against
            face_ipfs_hash: IPFS hash of face to verify

        Returns:
            True if verification successful
        """
        try:
            if did not in self.dids:
                raise ValueError(f"DID not found: {did}")

            stored_hash = self.dids[did]["datum"].face_ipfs_hash.decode()

            if stored_hash == face_ipfs_hash:
                self.dids[did]["datum"].verified = True
                logger.info(f"Face verified for DID: {did}")
                return True
            else:
                logger.warning(f"Face verification failed for DID: {did}")
                return False

        except Exception as e:
            logger.error(f"Face verification error: {e}")
            raise

    def get_did_document(self, did: str) -> Dict:
        """
        Get DID document

        Args:
            did: DID to retrieve

        Returns:
            DID document
        """
        if did not in self.dids:
            raise ValueError(f"DID not found: {did}")

        datum = self.dids[did]["datum"]
        return {
            "did_id": datum.did_id.hex(),
            "face_ipfs_hash": datum.face_ipfs_hash.decode(),
            "owner": datum.owner.hex(),
            "created_at": datum.created_at,
            "verified": datum.verified,
            "metadata": self.dids[did].get("metadata", {}),
            "on_chain": self.dids[did].get("on_chain", False),
            "tx_hash": self.dids[did].get("tx_hash"),
        }

    def update_did_metadata(self, did: str, metadata: Dict) -> bool:
        """
        Update DID metadata

        Args:
            did: DID to update
            metadata: New metadata

        Returns:
            True if update successful
        """
        try:
            if did not in self.dids:
                raise ValueError(f"DID not found: {did}")

            self.dids[did]["metadata"].update(metadata)
            self.dids[did]["updated_at"] = datetime.utcnow().isoformat()

            logger.info(f"DID metadata updated: {did}")
            return True

        except Exception as e:
            logger.error(f"Failed to update DID metadata: {e}")
            raise

    def list_dids(self) -> List[str]:
        """
        List all DIDs

        Returns:
            List of DID strings
        """
        return list(self.dids.keys())

    def export_did_registry(self) -> Dict:
        """
        Export all DIDs and their documents

        Returns:
            Dictionary of all DIDs and their documents
        """
        result = {}
        for did_id, did_info in self.dids.items():
            datum = did_info["datum"]
            result[did_id] = {
                "did_id": datum.did_id.hex(),
                "face_ipfs_hash": datum.face_ipfs_hash.decode(),
                "owner": datum.owner.hex(),
                "created_at": datum.created_at,
                "verified": datum.verified,
                "on_chain": did_info.get("on_chain", False),
                "tx_hash": did_info.get("tx_hash"),
                "metadata": did_info.get("metadata", {}),
            }
        return result

    # ================================================================
    # HIGH-LEVEL DID OPERATIONS (Called by API endpoints)
    # ================================================================

    def create_did(self, did_id: str, face_ipfs_hash: str) -> str:
        """
        Create new DID and lock to blockchain script

        Args:
            did_id: DID identifier
            face_ipfs_hash: IPFS hash of face embedding

        Returns:
            Transaction hash
        """
        try:
            logger.info(f"📝 Creating DID: {did_id[:20]}...")

            # 1. Create DIDDatum
            owner_address = str(self.cardano.wallet_address)
            datum = self.create_did_datum(face_ipfs_hash, owner_address)

            # 2. Validate datum
            self.validate_register_datum(datum)

            # 3. Build transaction to lock DID to script
            from .cardano_client import Create

            action = Create()
            tx = self.cardano.build_script_transaction(
                action=action, datum=datum, sender_address=owner_address
            )

            # 4. SUBMIT transaction to blockchain
            submitted_tx_hash = self.cardano.submit_transaction(tx)

            # Store locally
            self.dids[did_id] = {
                "datum": datum,
                "created_at": datetime.utcnow().isoformat(),
                "status": "created",
                "tx_hash": submitted_tx_hash,
            }

            logger.info(f"✅ DID created (TX submitted): {did_id}")
            return submitted_tx_hash

        except Exception as e:
            logger.error(f"❌ Failed to create DID: {e}")
            raise

    def register_did(self, did_id: str) -> str:
        """
        Register DID - Execute Register redeemer on blockchain

        Args:
            did_id: DID to register

        Returns:
            Transaction hash
        """
        try:
            logger.info(f"🔐 Registering DID: {did_id}")

            if did_id not in self.dids:
                raise ValueError(f"DID not found locally: {did_id}")

            datum = self.dids[did_id]["datum"]

            # Validate Register action
            self.validate_register_datum(datum)

            # Build Register transaction
            from .cardano_client import Register

            action = Register()
            owner_address = str(self.cardano.wallet_address)

            tx = self.cardano.build_script_transaction(
                action=action,
                datum=datum,
                sender_address=owner_address,
            )

            # Submit transaction to blockchain
            submitted_tx_hash = self.cardano.submit_transaction(tx)

            # Update status
            self.dids[did_id]["status"] = "registered"
            self.dids[did_id]["tx_hash"] = submitted_tx_hash

            logger.info(f"✅ DID registered (TX submitted: {submitted_tx_hash})")
            return submitted_tx_hash

        except Exception as e:
            logger.error(f"❌ Failed to register DID: {e}")
            raise

    def update_did(self, did_id: str, new_face_ipfs_hash: str) -> str:
        """
        Update DID with new face embedding - Execute Update redeemer

        Args:
            did_id: DID to update
            new_face_ipfs_hash: New IPFS hash of face embedding

        Returns:
            Transaction hash
        """
        try:
            logger.info(f"🔄 Updating DID: {did_id}")

            if did_id not in self.dids:
                raise ValueError(f"DID not found: {did_id}")

            # Create new datum with updated embedding
            old_datum = self.dids[did_id]["datum"]
            new_datum = DIDDatum(
                did_id=old_datum.did_id,
                face_ipfs_hash=new_face_ipfs_hash.encode("utf-8"),
                owner=old_datum.owner,
                created_at=old_datum.created_at,
                verified=0,  # Reset verification after update
            )

            # Validate Update action
            self.validate_update_datum(new_datum)

            # Build Update transaction
            from .cardano_client import Update

            action = Update()
            owner_address = str(self.cardano.wallet_address)

            tx = self.cardano.build_script_transaction(
                action=action,
                datum=new_datum,
                sender_address=owner_address,
            )

            # Submit transaction to blockchain
            submitted_tx_hash = self.cardano.submit_transaction(tx)

            # Update local state
            self.dids[did_id]["datum"] = new_datum
            self.dids[did_id]["status"] = "updated"
            self.dids[did_id]["updated_at"] = datetime.utcnow().isoformat()
            self.dids[did_id]["tx_hash"] = submitted_tx_hash

            logger.info(f"✅ DID updated (TX submitted: {submitted_tx_hash})")
            return submitted_tx_hash

        except Exception as e:
            logger.error(f"❌ Failed to update DID: {e}")
            raise

    def verify_did(self, did_id: str) -> str:
        """
        Verify DID - Execute Verify redeemer (read-only check)

        Args:
            did_id: DID to verify

        Returns:
            Transaction hash
        """
        try:
            logger.info(f"✅ Verifying DID: {did_id}")

            if did_id not in self.dids:
                raise ValueError(f"DID not found: {did_id}")

            datum = self.dids[did_id]["datum"]

            # Validate Verify action
            self.validate_verify_datum(datum)

            # Build Verify transaction
            from .cardano_client import Verify

            action = Verify()
            owner_address = str(self.cardano.wallet_address)

            tx = self.cardano.build_script_transaction(
                action=action,
                datum=datum,
                sender_address=owner_address,
            )

            # Submit transaction to blockchain
            submitted_tx_hash = self.cardano.submit_transaction(tx)

            # Update status
            self.dids[did_id]["status"] = "verified"
            self.dids[did_id]["verified"] = True
            self.dids[did_id]["tx_hash"] = submitted_tx_hash

            logger.info(f"✅ DID verified (TX submitted: {submitted_tx_hash})")
            return submitted_tx_hash

        except Exception as e:
            logger.error(f"❌ Failed to verify DID: {e}")
            raise

    def revoke_did(self, did_id: str) -> str:
        """
        Revoke DID - Execute Revoke redeemer (permanent disable)

        Args:
            did_id: DID to revoke

        Returns:
            Transaction hash
        """
        try:
            logger.info(f"🚫 Revoking DID: {did_id}")

            if did_id not in self.dids:
                raise ValueError(f"DID not found: {did_id}")

            datum = self.dids[did_id]["datum"]

            # Validate Revoke action
            self.validate_revoke_datum(datum)

            # Build Revoke transaction
            from .cardano_client import Revoke

            action = Revoke()
            owner_address = str(self.cardano.wallet_address)

            tx = self.cardano.build_script_transaction(
                action=action,
                datum=datum,
                sender_address=owner_address,
            )

            # Submit transaction to blockchain
            submitted_tx_hash = self.cardano.submit_transaction(tx)

            # Update status
            self.dids[did_id]["status"] = "revoked"
            self.dids[did_id]["tx_hash"] = submitted_tx_hash

            logger.info(f"✅ DID revoked (TX submitted: {submitted_tx_hash})")
            return submitted_tx_hash

        except Exception as e:
            logger.error(f"❌ Failed to revoke DID: {e}")
            raise
