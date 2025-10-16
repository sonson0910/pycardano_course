"""
Corrected Offchain Code - DID Manager with Validator Integration

This module provides the complete offchain code that correctly maps to the validator:

Validator Structure:
  validator did_manager {
    spend(datum: Option<DIDDatum>, action: Action, _own_ref: OutputReference, _self: Transaction)
  }

DIDDatum: did_id, face_ipfs_hash, owner, created_at, verified
Action: Register(0), Update(1), Verify(2), Revoke(3)
Script Hash: 33d066a565bf81c6ae2e6f97bebd453161f39e02ba53351f32ea7486
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List
from enum import Enum
import uuid
import hashlib
import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# ============================================================================
# PART 1: PlutusData Types - Must match validator types exactly
# ============================================================================

from pycardano import PlutusData, RawCBOR


@dataclass
class DIDDatum(PlutusData):
    """
    ✅ On-chain DID Datum
    MUST match validator definition exactly:

    pub type DIDDatum {
      did_id: ByteArray,
      face_ipfs_hash: ByteArray,
      owner: ByteArray,
      created_at: Int,
      verified: Bool,
    }
    """

    did_id: bytes  # ByteArray - unique DID identifier
    face_ipfs_hash: bytes  # ByteArray - IPFS hash of embedding
    owner: bytes  # ByteArray - owner public key hash (28 bytes)
    created_at: int  # Int - creation timestamp in milliseconds
    verified: bool  # Bool - verification status

    def __post_init__(self):
        """Validate datum fields after creation"""
        if not isinstance(self.did_id, bytes):
            raise TypeError(f"did_id must be bytes, got {type(self.did_id)}")
        if not isinstance(self.face_ipfs_hash, bytes):
            raise TypeError(
                f"face_ipfs_hash must be bytes, got {type(self.face_ipfs_hash)}"
            )
        if not isinstance(self.owner, bytes):
            raise TypeError(f"owner must be bytes, got {type(self.owner)}")
        if not isinstance(self.created_at, int):
            raise TypeError(f"created_at must be int, got {type(self.created_at)}")
        if not isinstance(self.verified, bool):
            raise TypeError(f"verified must be bool, got {type(self.verified)}")

        # Validate field lengths
        if len(self.did_id) == 0:
            raise ValueError('❌ did_id cannot be empty (validator: did_id != #"")')
        if len(self.face_ipfs_hash) == 0:
            raise ValueError(
                '❌ face_ipfs_hash cannot be empty (validator: face_ipfs_hash != #"")'
            )
        if self.created_at <= 0:
            raise ValueError("❌ created_at must be > 0 (validator: created_at > 0)")


# ============================================================================
# PART 2: Action Redeemers - Must match validator Action enum
# ============================================================================


@dataclass
class Register(PlutusData):
    """Action index: 0 - Register new DID"""

    CONSTR_ID = 0


@dataclass
class Update(PlutusData):
    """Action index: 1 - Update DID data"""

    CONSTR_ID = 1


@dataclass
class Verify(PlutusData):
    """Action index: 2 - Verify face identity"""

    CONSTR_ID = 2


@dataclass
class Revoke(PlutusData):
    """Action index: 3 - Revoke DID"""

    CONSTR_ID = 3


# Type alias
Action = Register | Update | Verify | Revoke


# ============================================================================
# PART 3: Validation Functions - Must match validator logic
# ============================================================================


class DIDValidator:
    """
    Offchain validation - mirror validator checks

    Validator logic:
    - Register: did_id != "" AND face_ipfs_hash != "" AND created_at > 0
    - Update: did_id != ""
    - Verify: did_id != "" AND face_ipfs_hash != ""
    - Revoke: did_id != ""
    """

    @staticmethod
    def validate_register(datum: DIDDatum) -> bool:
        """
        ✅ Validator: validate_register(d) checks:
        - d.did_id != #""
        - d.face_ipfs_hash != #""
        - d.created_at > 0
        """
        if len(datum.did_id) == 0:
            raise ValueError("❌ Register: did_id cannot be empty")
        if len(datum.face_ipfs_hash) == 0:
            raise ValueError("❌ Register: face_ipfs_hash cannot be empty")
        if datum.created_at <= 0:
            raise ValueError("❌ Register: created_at must be > 0")
        logger.info("✅ Register action validation passed")
        return True

    @staticmethod
    def validate_update(datum: DIDDatum) -> bool:
        """
        ✅ Validator: validate_update(d) checks:
        - d.did_id != #""
        """
        if len(datum.did_id) == 0:
            raise ValueError("❌ Update: did_id cannot be empty")
        logger.info("✅ Update action validation passed")
        return True

    @staticmethod
    def validate_verify(datum: DIDDatum) -> bool:
        """
        ✅ Validator: validate_verify(d) checks:
        - d.did_id != #""
        - d.face_ipfs_hash != #""
        """
        if len(datum.did_id) == 0:
            raise ValueError("❌ Verify: did_id cannot be empty")
        if len(datum.face_ipfs_hash) == 0:
            raise ValueError("❌ Verify: face_ipfs_hash cannot be empty")
        logger.info("✅ Verify action validation passed")
        return True

    @staticmethod
    def validate_revoke(datum: DIDDatum) -> bool:
        """
        ✅ Validator: validate_revoke(d) checks:
        - d.did_id != #""
        """
        if len(datum.did_id) == 0:
            raise ValueError("❌ Revoke: did_id cannot be empty")
        logger.info("✅ Revoke action validation passed")
        return True

    @staticmethod
    def validate(action: Action, datum: DIDDatum) -> bool:
        """Validate action against datum"""
        if isinstance(action, Register):
            return DIDValidator.validate_register(datum)
        elif isinstance(action, Update):
            return DIDValidator.validate_update(datum)
        elif isinstance(action, Verify):
            return DIDValidator.validate_verify(datum)
        elif isinstance(action, Revoke):
            return DIDValidator.validate_revoke(datum)
        else:
            raise ValueError(f"❌ Unknown action type: {type(action)}")


# ============================================================================
# PART 4: DID Manager - Creates correct DIDDatum
# ============================================================================


class DIDManager:
    """
    Manages DIDs with correct on-chain datum structure
    """

    SCRIPT_HASH = "33d066a565bf81c6ae2e6f97bebd453161f39e02ba53351f32ea7486"
    VALIDATOR = "did_manager"

    def __init__(self):
        self.dids_local: Dict[str, DIDDatum] = {}

    def create_did_datum(
        self, face_ipfs_hash: str, owner_address: str, metadata: Optional[Dict] = None
    ) -> DIDDatum:
        """
        ✅ Create DIDDatum with correct field types and values

        Args:
            face_ipfs_hash: IPFS hash string (e.g., "QmXxxx...")
            owner_address: Cardano address string
            metadata: Optional metadata dict

        Returns:
            DIDDatum with all fields set correctly

        Validation:
            - did_id: non-empty bytes ✓
            - face_ipfs_hash: non-empty bytes ✓
            - owner: 28-byte blake2b hash ✓
            - created_at: positive millisecond timestamp ✓
            - verified: False initially ✓
        """
        try:
            # 1. ✅ Generate did_id as bytes
            did_suffix = str(uuid.uuid4())[:12]
            did_id_bytes = did_suffix.encode("utf-8")

            # Must not be empty
            if len(did_id_bytes) == 0:
                raise ValueError("did_id cannot be empty")

            # 2. ✅ Convert IPFS hash to bytes
            face_ipfs_bytes = face_ipfs_hash.encode("utf-8")

            # Must not be empty
            if len(face_ipfs_bytes) == 0:
                raise ValueError("face_ipfs_hash cannot be empty")

            # 3. ✅ Hash owner address to 28-byte blake2b
            owner_hash = hashlib.blake2b(
                owner_address.encode("utf-8"),
                digest_size=28,  # Cardano uses 28-byte hashes
            ).digest()

            if len(owner_hash) != 28:
                raise ValueError(f"owner hash must be 28 bytes, got {len(owner_hash)}")

            # 4. ✅ Create timestamp in milliseconds
            created_at_ms = int(time.time() * 1000)

            # Must be positive
            if created_at_ms <= 0:
                raise ValueError("created_at must be > 0")

            # 5. ✅ Create datum
            datum = DIDDatum(
                did_id=did_id_bytes,
                face_ipfs_hash=face_ipfs_bytes,
                owner=owner_hash,
                created_at=created_at_ms,
                verified=False,
            )

            logger.info(f"✅ DIDDatum created: {did_id_bytes.hex()[:8]}...")
            logger.info(f"   - did_id: {len(did_id_bytes)} bytes")
            logger.info(f"   - face_ipfs_hash: {len(face_ipfs_bytes)} bytes")
            logger.info(f"   - owner: {len(owner_hash)} bytes")
            logger.info(f"   - created_at: {created_at_ms} ms")
            logger.info(f"   - verified: {datum.verified}")

            # Store locally for reference
            self.dids_local[did_id_bytes.hex()] = datum

            return datum

        except Exception as e:
            logger.error(f"❌ Failed to create DIDDatum: {e}")
            raise

    def update_datum_verified(self, datum: DIDDatum) -> DIDDatum:
        """
        Update verified flag (for Verify action)

        Returns: New datum with verified=True
        """
        updated = DIDDatum(
            did_id=datum.did_id,
            face_ipfs_hash=datum.face_ipfs_hash,
            owner=datum.owner,
            created_at=datum.created_at,
            verified=True,
        )
        logger.info(f"✅ Datum verified flag updated to: True")
        return updated


# ============================================================================
# PART 5: Transaction Builder Helpers
# ============================================================================


class TransactionHelper:
    """
    Helpers for building script transactions with validator
    """

    SCRIPT_HASH = "33d066a565bf81c6ae2e6f97bebd453161f39e02ba53351f32ea7486"
    MIN_UTXO_AMOUNT = 2_000_000  # 2 ADA in Lovelace

    @staticmethod
    def build_register_action(datum: DIDDatum) -> Register:
        """Build Register action for transaction"""
        # Validate before building
        DIDValidator.validate_register(datum)
        logger.info("🔨 Building Register action...")
        return Register()

    @staticmethod
    def build_update_action(datum: DIDDatum) -> Update:
        """Build Update action for transaction"""
        # Validate before building
        DIDValidator.validate_update(datum)
        logger.info("🔨 Building Update action...")
        return Update()

    @staticmethod
    def build_verify_action(datum: DIDDatum) -> Verify:
        """Build Verify action for transaction"""
        # Validate before building
        DIDValidator.validate_verify(datum)
        logger.info("🔨 Building Verify action...")
        return Verify()

    @staticmethod
    def build_revoke_action(datum: DIDDatum) -> Revoke:
        """Build Revoke action for transaction"""
        # Validate before building
        DIDValidator.validate_revoke(datum)
        logger.info("🔨 Building Revoke action...")
        return Revoke()

    @staticmethod
    def build_script_transaction(
        action: Action,
        datum: DIDDatum,
        input_utxo,  # UTxO
        sender_address,  # Address
        change_amount,  # Coin
        client,  # PyCardano client
    ):
        """
        ✅ Build complete transaction for script interaction

        Transaction structure:
        Input 1: User UTxO (for fees)
        Input 2: Script UTxO (with redeemer)
        Output 1: New script UTxO with updated datum
        Output 2: Change to user

        Validator will validate:
        - Datum fields are non-empty/valid
        - Action matches the operation
        - Constraints are satisfied
        """
        from pycardano import (
            TransactionBuilder,
            TransactionInput,
            TransactionOutput,
            Value,
            Coin,
            ScriptHash,
        )

        try:
            logger.info(
                f"🔨 Building script transaction with action: {type(action).__name__}"
            )

            # 1. Validate datum before including in transaction
            if isinstance(action, Register):
                DIDValidator.validate_register(datum)
            elif isinstance(action, Update):
                DIDValidator.validate_update(datum)
            elif isinstance(action, Verify):
                DIDValidator.validate_verify(datum)
            elif isinstance(action, Revoke):
                DIDValidator.validate_revoke(datum)

            # 2. Create transaction builder
            builder = TransactionBuilder(client)

            # 3. Add user input for fees
            builder.add_input_address(sender_address)

            # 4. Add script input with redeemer
            script_hash = ScriptHash.from_primitive(TransactionHelper.SCRIPT_HASH)

            builder.add_script_input(
                utxo=input_utxo,
                script=script_hash,  # Script validator
                redeemer=action,  # ✅ Redeemer: Register|Update|Verify|Revoke
            )

            # 5. Add output with datum to script
            script_address = script_hash.to_address()

            # Update datum if Verify action
            output_datum = datum
            if isinstance(action, Verify):
                output_datum = DIDDatum(
                    did_id=datum.did_id,
                    face_ipfs_hash=datum.face_ipfs_hash,
                    owner=datum.owner,
                    created_at=datum.created_at,
                    verified=True,  # ✅ Set to True for Verify
                )

            builder.add_output(
                TransactionOutput(
                    address=script_address,
                    amount=Value(Coin(TransactionHelper.MIN_UTXO_AMOUNT)),
                    datum=output_datum,  # ✅ Include datum
                )
            )

            # 6. Add change output
            builder.add_output(
                TransactionOutput(address=sender_address, amount=Value(change_amount))
            )

            logger.info("✅ Script transaction built successfully")
            logger.info(
                f"   - Action: {type(action).__name__} (index: {action.CONSTR_ID})"
            )
            logger.info(f"   - Datum: {datum.did_id.hex()[:8]}...")
            logger.info(
                f"   - Script output: {TransactionHelper.MIN_UTXO_AMOUNT} Lovelace"
            )
            logger.info(f"   - Change: {change_amount} Lovelace")

            return builder

        except Exception as e:
            logger.error(f"❌ Failed to build script transaction: {e}")
            raise


# ============================================================================
# PART 6: Example Usage
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 80)
    print("OFFCHAIN CODE - VALIDATOR INTEGRATION TEST")
    print("=" * 80)

    # Initialize
    did_manager = DIDManager()

    # 1. Create DID Datum
    print("\n1️⃣ Creating DIDDatum...")
    datum = did_manager.create_did_datum(
        face_ipfs_hash="QmXxxx123456789",
        owner_address="addr_test1vq5l6dqqrruq6d7puu7ssmn3pq6xh8qsxwjz7xyd9xqnrqsf2dcx",
        metadata={"name": "User Face", "model": "MTCNN"},
    )

    print(f"\n✅ DIDDatum created:")
    print(f"  - did_id: {datum.did_id.hex()}")
    print(f"  - face_ipfs_hash: {datum.face_ipfs_hash}")
    print(f"  - owner: {datum.owner.hex()}")
    print(f"  - created_at: {datum.created_at}")
    print(f"  - verified: {datum.verified}")

    # 2. Validate Register action
    print("\n2️⃣ Validating Register action...")
    try:
        DIDValidator.validate_register(datum)
        print("✅ Register validation passed")
    except ValueError as e:
        print(f"❌ {e}")

    # 3. Build Register action
    print("\n3️⃣ Building Register action...")
    register_action = TransactionHelper.build_register_action(datum)
    print(f"✅ Register action built (index: {register_action.CONSTR_ID})")

    # 4. Verify action
    print("\n4️⃣ Verifying (updating datum)...")
    verified_datum = did_manager.update_datum_verified(datum)
    print(f"✅ Datum verified: {verified_datum.verified}")

    # 5. Build Verify action
    print("\n5️⃣ Building Verify action...")
    verify_action = TransactionHelper.build_verify_action(verified_datum)
    print(f"✅ Verify action built (index: {verify_action.CONSTR_ID})")

    print("\n" + "=" * 80)
    print("✅ ALL VALIDATIONS PASSED")
    print("=" * 80)
    print("\nNext: Use these classes in your FastAPI routes!")
    print("See: backend/app/api/routes.py")
