"""
Cardano Service — PyCardano + DID Operations

Quản lý ví, smart contract, và DID lifecycle trên Cardano Preprod.
"""

import hashlib
import json
import logging
import os
import time
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv
from dataclasses import dataclass
from pycardano import (
    Address,
    BlockFrostChainContext,
    ExtendedSigningKey,
    HDWallet,
    Network,
    PlutusData,
    PlutusV3Script,
    Redeemer,
    TransactionBuilder,
    TransactionOutput,
    Value,
    plutus_script_hash,
)

logger = logging.getLogger(__name__)
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


# ═══════════════════════════════════════════════
# PlutusData — khớp Aiken types
# ═══════════════════════════════════════════════

@dataclass
class DIDDatum(PlutusData):
    CONSTR_ID = 0
    did_id: bytes
    face_ipfs_hash: bytes
    owner: bytes
    created_at: int
    verified: int


@dataclass
class Register(PlutusData):
    CONSTR_ID = 0

@dataclass
class Update(PlutusData):
    CONSTR_ID = 1

@dataclass
class Verify(PlutusData):
    CONSTR_ID = 2

@dataclass
class Revoke(PlutusData):
    CONSTR_ID = 3


ACTION_MAP = {
    "register": Register,
    "update": Update,
    "verify": Verify,
    "revoke": Revoke,
}


# Singleton
_instance: Optional["CardanoService"] = None


def get_cardano_service() -> "CardanoService":
    global _instance
    if _instance is None:
        _instance = CardanoService()
    return _instance


class CardanoService:
    """Cardano blockchain operations for DID management"""

    def __init__(self):
        blockfrost_id = os.getenv("BLOCKFROST_PROJECT_ID")
        mnemonic = os.getenv("MNEMONIC")

        if not blockfrost_id or not mnemonic:
            logger.warning("⚠️ BLOCKFROST_PROJECT_ID or MNEMONIC not set")
            self.ready = False
            return

        # Blockfrost
        self.context = BlockFrostChainContext(
            project_id=blockfrost_id,
            base_url="https://cardano-preprod.blockfrost.io/api/",
        )

        # Wallet
        hd = HDWallet.from_mnemonic(mnemonic)
        pay_node = hd.derive_from_path("m/1852'/1815'/0'/0/0")
        self.pay_skey = ExtendedSigningKey.from_hdwallet(pay_node)
        self.pay_vkey = self.pay_skey.to_verification_key()

        stake_node = hd.derive_from_path("m/1852'/1815'/0'/2/0")
        self.stake_skey = ExtendedSigningKey.from_hdwallet(stake_node)
        stake_vkey = self.stake_skey.to_verification_key()

        self.address = Address(
            payment_part=self.pay_vkey.hash(),
            staking_part=stake_vkey.hash(),
            network=Network.TESTNET,
        )

        # Contract
        plutus_path = Path(__file__).parent.parent.parent.parent / "lesson6_cv_did_integration" / "did_contract" / "plutus.json"
        if plutus_path.exists():
            with open(plutus_path) as f:
                blueprint = json.load(f)
            compiled = blueprint["validators"][0]["compiledCode"]
            self.script = PlutusV3Script(bytes.fromhex(compiled))
            self.script_address = Address(plutus_script_hash(self.script), network=Network.TESTNET)
        else:
            logger.warning(f"⚠️ plutus.json not found at {plutus_path}")
            self.script = None
            self.script_address = None

        # In-memory DID registry
        self.dids: Dict[str, dict] = {}
        self.ready = True

        logger.info(f"✅ CardanoService initialized")
        logger.info(f"   Wallet: {self.address}")
        if self.script_address:
            logger.info(f"   Script: {self.script_address}")

    def get_balance(self) -> float:
        """Balance in ADA"""
        utxos = self.context.utxos(self.address)
        return sum(u.output.amount.coin for u in utxos) / 1_000_000

    def create_did(self, ipfs_hash: str, did_id: str = None, amount: int = 2_000_000) -> dict:
        """Tạo DID mới + Lock vào smart contract"""
        if not self.ready or not self.script:
            raise ValueError("CardanoService not ready")

        did_id = did_id or f"did:cardano:{hashlib.sha256(ipfs_hash.encode()).hexdigest()[:16]}"

        datum = DIDDatum(
            did_id=did_id.encode("utf-8"),
            face_ipfs_hash=ipfs_hash.encode("utf-8"),
            owner=bytes(self.pay_vkey.hash()),
            created_at=int(time.time() * 1000),
            verified=0,
        )

        builder = TransactionBuilder(self.context)
        builder.add_input_address(self.address)
        builder.add_output(
            TransactionOutput(
                address=self.script_address,
                amount=Value(amount),
                datum=datum,
            )
        )

        signed_tx = builder.build_and_sign(
            signing_keys=[self.pay_skey, self.stake_skey],
            change_address=self.address,
        )
        self.context.submit_tx(signed_tx)
        tx_hash = str(signed_tx.id)

        # Lưu vào registry
        self.dids[did_id] = {
            "did_id": did_id,
            "ipfs_hash": ipfs_hash,
            "owner": bytes(self.pay_vkey.hash()).hex(),
            "created_at": datum.created_at,
            "verified": False,
            "status": "locked",
            "tx_history": [{"action": "create", "tx_hash": tx_hash}],
        }

        logger.info(f"✅ DID created: {did_id} | TX: {tx_hash}")
        return {
            "did_id": did_id,
            "tx_hash": tx_hash,
            "ipfs_hash": ipfs_hash,
            "status": "locked",
            "explorer_url": f"https://preprod.cardanoscan.io/transaction/{tx_hash}",
        }

    def perform_action(self, did_id: str, action_name: str, new_ipfs_hash: str = None) -> dict:
        """Thực hiện action (register/verify/update/revoke) trên DID — CKV logic"""
        if did_id not in self.dids:
            raise ValueError(f"DID not found: {did_id}")

        action_class = ACTION_MAP.get(action_name.lower())
        if not action_class:
            raise ValueError(f"Unknown action: {action_name}")

        did_info = self.dids[did_id]
        last_tx = did_info["tx_history"][-1]["tx_hash"]

        # Tìm UTxO
        utxos = self.context.utxos(self.script_address)
        target = None
        for utxo in utxos:
            if str(utxo.input.transaction_id) == last_tx:
                target = utxo
                break

        if not target:
            raise ValueError(f"UTxO not found for TX: {last_tx}")

        builder = TransactionBuilder(self.context)
        builder.add_input_address(self.address)  # Wallet UTxOs for fees
        builder.add_script_input(
            utxo=target,
            script=self.script,
            redeemer=Redeemer(action_class()),
        )
        builder.required_signers = [self.pay_vkey.hash()]

        # CKV: continuing output logic
        if action_name == "revoke":
            # Revoke: NO continuing output (burn DID)
            pass
        elif action_name == "verify":
            # Verify: continuing output with verified=1
            # Deserialize RawCBOR from chain into DIDDatum
            raw_datum = target.output.datum
            input_datum = DIDDatum.from_cbor(raw_datum.cbor)
            out_datum = DIDDatum(
                did_id=input_datum.did_id,
                face_ipfs_hash=input_datum.face_ipfs_hash,
                owner=input_datum.owner,
                created_at=input_datum.created_at,
                verified=1,
            )
            builder.add_output(TransactionOutput(
                self.script_address, Value(target.output.amount.coin), datum=out_datum,
            ))
        elif action_name == "update" and new_ipfs_hash:
            # Update: continuing output with new ipfs_hash
            raw_datum = target.output.datum
            input_datum = DIDDatum.from_cbor(raw_datum.cbor)
            out_datum = DIDDatum(
                did_id=input_datum.did_id,
                face_ipfs_hash=new_ipfs_hash.encode("utf-8"),
                owner=input_datum.owner,
                created_at=input_datum.created_at,
                verified=input_datum.verified,
            )
            builder.add_output(TransactionOutput(
                self.script_address, Value(target.output.amount.coin), datum=out_datum,
            ))
        else:
            # Register: continuing output with same raw datum (no deserialization needed)
            builder.add_output(TransactionOutput(
                self.script_address, Value(target.output.amount.coin), datum=target.output.datum,
            ))

        signed_tx = builder.build_and_sign(
            signing_keys=[self.pay_skey, self.stake_skey],
            change_address=self.address,
        )
        self.context.submit_tx(signed_tx)
        tx_hash = str(signed_tx.id)

        # Update registry — map action to proper status name
        STATUS_MAP = {"register": "registered", "verify": "verified", "update": "locked", "revoke": "revoked"}
        did_info["status"] = STATUS_MAP.get(action_name, action_name)
        did_info["tx_history"].append({"action": action_name, "tx_hash": tx_hash})
        if action_name == "verify":
            did_info["verified"] = True

        logger.info(f"✅ {action_name.upper()} DID: {did_id} | TX: {tx_hash}")
        return {
            "did_id": did_id,
            "action": action_name,
            "tx_hash": tx_hash,
            "status": did_info["status"],
            "explorer_url": f"https://preprod.cardanoscan.io/transaction/{tx_hash}",
        }

    def get_did(self, did_id: str) -> Optional[dict]:
        return self.dids.get(did_id)

    def list_dids(self) -> List[dict]:
        return list(self.dids.values())
