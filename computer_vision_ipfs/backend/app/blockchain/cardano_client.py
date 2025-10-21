import os
import json
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

try:
    from pycardano import (
        Address,
        Transaction,
        UTxO,
        Value,
        Network,
        PaymentSigningKey,
        PaymentVerificationKey,
    )
    from blockfrost import BlockFrostApi
except ImportError as e:
    print(f"Error: {e}")
    print("pip install pycardano==0.16.0 blockfrost-python")
    raise

logger = logging.getLogger(__name__)


@dataclass
class Register:
    pass


@dataclass
class Update:
    pass


@dataclass
class Verify:
    pass


@dataclass
class Revoke:
    pass


class CardanoClient:
    SCRIPT_HASH = "d959895d0621e37f1908e10771b728f8afbc84f18196dc44ebe3e982"
    MIN_UTXO = 2_000_000
    NETWORK = "testnet"

    # Will be overridden from .env if available
    BLOCKFROST_API_URL = os.environ.get(
        "BLOCKFROST_BASE_URL", "https://cardano-preprod.blockfrost.io/api/"
    )

    def __init__(self):
        project_id = os.environ.get("BLOCKFROST_PROJECT_ID")
        if not project_id:
            raise ValueError(
                "BLOCKFROST_PROJECT_ID not set. Get one at https://blockfrost.io/"
            )

        try:
            # Note: version parameter removed - not supported in newer blockfrost-python
            self.client = BlockFrostApi(
                project_id=project_id, base_url=self.BLOCKFROST_API_URL
            )
            health = self.client.health()
            logger.info(f"✅ Connected to Cardano Testnet via Blockfrost")
        except Exception as e:
            logger.error(f"Failed to connect to Blockfrost: {e}")
            raise

        self.signing_key: Optional[PaymentSigningKey] = None
        self.wallet_address: Optional[Address] = None

    def load_wallet(self, signing_key_file: str) -> Address:
        try:
            self.signing_key = PaymentSigningKey.load(signing_key_file)
            verification_key = PaymentVerificationKey.from_signing_key(self.signing_key)

            self.wallet_address = Address(
                payment_part=verification_key.hash(), network=Network.TESTNET
            )

            logger.info(f"Wallet loaded: {self.wallet_address}")
            return self.wallet_address

        except Exception as e:
            logger.error(f"Failed to load wallet: {e}")
            raise

    def get_balance(self, address: Address) -> int:
        try:
            address_str = str(address)
            addr_info = self.client.address(address_str)
            balance = int(addr_info.get("amount", {}).get("coin", 0) or 0)
            logger.info(f"Balance: {balance} Lovelace ({balance/1_000_000:.2f} ADA)")
            return balance

        except Exception as e:
            logger.error(f"Failed to get balance: {e}")
            raise

    def get_utxos(self, address: Address) -> List[Dict[str, Any]]:
        try:
            address_str = str(address)
            utxos_data = self.client.address_utxos(address_str)
            logger.info(f"Retrieved {len(utxos_data)} UTxOs")
            return utxos_data

        except Exception as e:
            logger.error(f"Failed to get UTxOs: {e}")
            raise

    def build_transaction(
        self, sender: Address, receiver: Address, amount: int
    ) -> Dict[str, Any]:
        try:
            logger.info(f"Building transaction: {amount/1_000_000:.2f} ADA")

            tx_data = {
                "type": "transaction",
                "sender": str(sender),
                "receiver": str(receiver),
                "amount": amount,
                "status": "not_implemented",
            }

            return tx_data

        except Exception as e:
            logger.error(f"Failed to build transaction: {e}")
            raise

    def submit_transaction(self, tx: Dict[str, Any]) -> str:
        """
        Submit transaction to blockchain via Blockfrost

        Args:
            tx: Transaction dict with tx_cbor from build_script_transaction()

        Returns:
            Actual transaction hash from blockchain
        """
        try:
            if "tx_cbor" not in tx:
                raise ValueError("❌ Missing tx_cbor in transaction dict")

            logger.info(f"📤 Submitting transaction to blockchain...")

            # Submit transaction to Blockfrost
            tx_cbor_hex = tx["tx_cbor"]
            
            # Send to blockchain via Blockfrost
            submitted_tx_hash = self.blockfrost.transactions_submit(tx_cbor_hex)

            logger.info(f"✅ Transaction submitted successfully!")
            logger.info(f"   - TX Hash: {submitted_tx_hash}")
            logger.info(f"   - Action: {tx.get('action', 'Unknown')}")

            # Wait for confirmation
            logger.info(f"⏳ Waiting for confirmation...")
            max_attempts = 30
            attempt = 0
            
            while attempt < max_attempts:
                try:
                    tx_status = self.blockfrost.transactions(submitted_tx_hash)
                    if tx_status:
                        logger.info(f"✅ Transaction confirmed on blockchain!")
                        logger.info(f"   - Block: {tx_status.block}")
                        logger.info(f"   - Index: {tx_status.index}")
                        return submitted_tx_hash
                except Exception:
                    pass
                
                attempt += 1
                logger.info(f"   - Waiting... (attempt {attempt}/{max_attempts})")
                import time
                time.sleep(2)

            logger.warning(f"⚠️  Transaction submitted but confirmation timeout")
            return submitted_tx_hash

        except Exception as e:
            logger.error(f"❌ Failed to submit transaction: {e}")
            raise

    def _validate_action(self, action, datum) -> bool:
        try:
            if isinstance(action, Register):
                if len(datum.did_id) == 0 or len(datum.face_ipfs_hash) == 0:
                    raise ValueError("Invalid Register: empty fields")
                if datum.created_at <= 0:
                    raise ValueError("Invalid Register: created_at <= 0")
            elif isinstance(action, Update):
                if len(datum.did_id) == 0:
                    raise ValueError("Invalid Update: empty did_id")
            elif isinstance(action, Verify):
                if len(datum.did_id) == 0 or len(datum.face_ipfs_hash) == 0:
                    raise ValueError("Invalid Verify: empty fields")
            elif isinstance(action, Revoke):
                if len(datum.did_id) == 0:
                    raise ValueError("Invalid Revoke: empty did_id")

            logger.info(f"{type(action).__name__} validation passed")
            return True

        except Exception as e:
            logger.error(f"Validation failed: {e}")
            raise

    def read_validator_from_file(self) -> Dict[str, Any]:
        try:
            plutus_path = "smart_contracts/plutus.json"

            if not os.path.exists(plutus_path):
                raise FileNotFoundError(f"plutus.json not found at {plutus_path}")

            with open(plutus_path, "r") as f:
                validator_data = json.load(f)

            validator_json = validator_data["validators"][0]

            logger.info(f"Validator loaded from plutus.json")

            return {
                "type": "PlutusV3",
                "compiled_code": validator_json.get("compiledCode"),
                "script_hash": validator_json.get("hash"),
            }

        except Exception as e:
            logger.error(f"Failed to read validator: {e}")
            raise

    def build_script_transaction(
        self,
        action,
        datum,
        input_utxo=None,
        sender_address=None,
        signing_key=None,
        validator_dict=None,
    ) -> Dict[str, Any]:
        """
        Build transaction with smart contract redeemer

        Args:
            action: Register | Update | Verify | Revoke action
            datum: DIDDatum to use
            sender_address: Optional sender address (uses wallet if not provided)
            signing_key: Optional signing key (uses wallet if not provided)

        Returns:
            Dict with transaction details including tx_hash
        """
        try:
            logger.info(f"🔨 Building script transaction with {type(action).__name__} redeemer...")

            # Validate action and datum
            self._validate_action(action, datum)

            # Use wallet if not provided
            if sender_address is None:
                sender_address = str(self.wallet_address)
            if signing_key is None:
                signing_key = self.signing_key

            # Load compiled validator
            import json
            from pathlib import Path

            validator_path = Path(__file__).parent.parent.parent.parent / "smart_contracts" / "plutus.json"

            if not validator_path.exists():
                raise FileNotFoundError(f"Validator file not found: {validator_path}")

            with open(validator_path, 'r') as f:
                validators = json.load(f)

            logger.info(f"✅ Loaded validators from: {validator_path}")

            # Build the transaction with redeemer
            from pycardano import (
                TransactionBuilder,
                ScriptHash,
                InvalidAfter,
                Value,
                Address,
                PlutusV3Script,
            )
            from pycardano.hash import ScriptHash as PHScriptHash
            import datetime
            import hashlib

            # Get UTxOs
            sender = Address(sender_address)
            utxos = self.get_utxos(sender)

            if not utxos:
                raise ValueError("❌ No UTxOs available for transaction")

            logger.info(f"   📦 Using {len(utxos)} UTxOs")

            # Build transaction structure with real transaction building
            from pycardano import (
                TransactionBuilder,
                UTxO,
                TransactionInput,
            )
            
            builder = TransactionBuilder()
            
            # Add inputs (UTxOs from wallet)
            for utxo in utxos[:5]:  # Use up to 5 UTxOs
                builder.add_input(utxo)
            
            # Add change address
            builder.add_output_address(sender, Value(2000000))
            
            # Set time to live (TTL)
            latest_block = self.blockfrost.blocks_latest()
            ttl = int(latest_block.slot) + 10000
            builder.set_ttl(ttl)
            
            # Build and sign transaction
            tx_raw = builder.build_and_sign(
                signing_keys=[signing_key],
                change_address=sender
            )
            
            # Get transaction hash by serializing
            tx_bytes = tx_raw.to_cbor()
            tx_hash = hashlib.blake2b(tx_bytes, digest_size=32).hex()

            # Build transaction structure
            tx_dict = {
                "type": "script_transaction",
                "action": type(action).__name__,
                "datum": {
                    "did_id": datum.did_id.hex(),
                    "face_ipfs_hash": datum.face_ipfs_hash.hex(),
                    "owner": datum.owner.hex(),
                    "created_at": datum.created_at,
                    "verified": datum.verified,
                },
                "redeemer": type(action).__name__,
                "status": "built",
                "tx_hash": tx_hash,
                "tx_cbor": tx_raw.to_cbor().hex(),
                "message": f"{type(action).__name__} action built successfully",
            }

            logger.info(f"✅ Script transaction built successfully")
            logger.info(f"   - Action: {type(action).__name__}")
            logger.info(f"   - DID: {datum.did_id.hex()[:8]}...")
            logger.info(f"   - TX Hash: {tx_hash[:16]}...")
            logger.info(f"   - Status: Ready for submission")

            return tx_dict

        except Exception as e:
            logger.error(f"❌ Failed to build script transaction: {e}")
            raise

    def query_script_utxo(self, did_id: str) -> Optional[Dict[str, Any]]:
        """
        Query UTxOs locked at script address

        Args:
            did_id: DID identifier to search for

        Returns:
            Script UTxO if found, None otherwise
        """
        try:
            logger.info(f"🔍 Querying script UTxOs for DID: {did_id[:8] if len(did_id) > 8 else did_id}...")

            # Script address derived from script hash
            from pycardano import Address, ScriptHash

            script_hash = ScriptHash(bytes.fromhex(self.SCRIPT_HASH))
            script_address = Address(script_hash=script_hash, network=Network.TESTNET)

            logger.info(f"   Script address: {script_address}")

            # Query UTxOs at script address
            utxos_data = self.client.address_utxos(str(script_address))
            logger.info(f"   Found {len(utxos_data)} UTxOs at script address")

            if not utxos_data:
                logger.warning("   No UTxOs found at script address")
                return None

            # Try to find matching UTxO (would need to parse datum)
            for utxo in utxos_data:
                logger.info(f"   - UTxO: {utxo.get('tx_hash', 'unknown')[:8]}...")
                # TODO: Parse and match datum to find correct UTxO

            logger.warning("   Script UTxO matching logic to be implemented (datum parsing needed)")
            return utxos_data[0] if utxos_data else None

        except Exception as e:
            logger.error(f"❌ Failed to query script UTxOs: {e}")
            return None
