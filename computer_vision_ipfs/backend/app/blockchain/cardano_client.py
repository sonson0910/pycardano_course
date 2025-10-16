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
    BLOCKFROST_API_URL = "https://cardano-preview.blockfrost.io"

    def __init__(self):
        project_id = os.environ.get("BLOCKFROST_PROJECT_ID")
        if not project_id:
            raise ValueError(
                "BLOCKFROST_PROJECT_ID not set. Get one at https://blockfrost.io/"
            )

        try:
            self.client = BlockFrostApi(
                project_id=project_id, base_url=self.BLOCKFROST_API_URL, version="v0"
            )
            health = self.client.health()
            logger.info(f"Connected to Cardano Preview Testnet")
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
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
        try:
            logger.warning("Transaction submission not implemented")
            return "txid_placeholder"

        except Exception as e:
            logger.error(f"Failed to submit: {e}")
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
        try:
            logger.info(f"Building script transaction with {type(action).__name__}...")

            self._validate_action(action, datum)

            return {
                "type": "script_transaction",
                "action": type(action).__name__,
                "status": "not_implemented",
            }

        except Exception as e:
            logger.error(f"Failed to build script transaction: {e}")
            raise

    def query_script_utxo(self, did_id: str) -> Optional[Dict[str, Any]]:
        try:
            logger.info(f"Querying script UTxOs for DID: {did_id[:8]}...")

            script_address = f"addr_test1w{self.SCRIPT_HASH}"

            utxos = self.client.address_utxos(script_address)
            logger.info(f"Found {len(utxos)} UTxOs at script address")

            logger.warning(f"Script UTxO matching not implemented")
            return None

        except Exception as e:
            logger.error(f"Failed to query: {e}")
            return None
