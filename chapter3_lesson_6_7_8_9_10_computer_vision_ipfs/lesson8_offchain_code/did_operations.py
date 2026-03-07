"""
Lesson 8 — DID Lifecycle Operations (CKV)

Full lifecycle: Lock DID → Register → Update → Verify → Revoke
Tất cả actions tuân thủ CKV (Continuing output Validation).

Usage:
    python did_operations.py --action create --ipfs-hash QmXxx...
    python did_operations.py --action register --tx-hash abc123...
    python did_operations.py --action verify --tx-hash abc123...
    python did_operations.py --action update --tx-hash abc123... --new-ipfs-hash QmYyy...
    python did_operations.py --action revoke --tx-hash abc123...
    python did_operations.py --action balance
    python did_operations.py --action list
"""

import argparse
import hashlib
import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
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

# Load .env
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


# ═══════════════════════════════════════════════
# PlutusData types
# ═══════════════════════════════════════════════

@dataclass
class DIDDatum(PlutusData):
    CONSTR_ID = 0
    did_id: bytes
    face_ipfs_hash: bytes
    owner: bytes
    created_at: int
    verified: int  # 0 = chưa, 1 = đã verify

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


# ═══════════════════════════════════════════════
# DID Manager class (CKV-compliant)
# ═══════════════════════════════════════════════

class DIDManager:
    """Quản lý DID lifecycle trên Cardano Preprod (CKV logic)"""

    def __init__(self):
        blockfrost_id = os.getenv("BLOCKFROST_PROJECT_ID")
        mnemonic = os.getenv("MNEMONIC")

        if not blockfrost_id or not mnemonic:
            print("❌ Cấu hình .env: BLOCKFROST_PROJECT_ID + MNEMONIC")
            sys.exit(1)

        self.context = BlockFrostChainContext(
            project_id=blockfrost_id,
            base_url="https://cardano-preprod.blockfrost.io/api/",
        )

        hd = HDWallet.from_mnemonic(mnemonic)
        pay_node = hd.derive_from_path("m/1852'/1815'/0'/0/0")
        self.pay_skey = ExtendedSigningKey.from_hdwallet(pay_node)
        self.pay_vkey = self.pay_skey.to_verification_key()
        stake_node = hd.derive_from_path("m/1852'/1815'/0'/2/0")
        self.stake_skey = ExtendedSigningKey.from_hdwallet(stake_node)
        stake_vkey = self.stake_skey.to_verification_key()

        self.address = Address(
            self.pay_vkey.hash(), stake_vkey.hash(), network=Network.TESTNET,
        )

        # Contract
        plutus_path = Path(__file__).parent.parent / "lesson6_cv_did_integration" / "did_contract" / "plutus.json"
        with open(plutus_path) as f:
            blueprint = json.load(f)
        self.script = PlutusV3Script(bytes.fromhex(blueprint["validators"][0]["compiledCode"]))
        self.script_address = Address(plutus_script_hash(self.script), network=Network.TESTNET)

        print(f"✅ DIDManager initialized")
        print(f"   Wallet: {self.address}")
        print(f"   Script: {self.script_address}")

    def create_and_lock(self, ipfs_hash: str, did_id: str = None, amount: int = 2_000_000) -> str:
        """Lock ADA + DIDDatum vào smart contract"""
        did_id = did_id or f"did:cardano:{hashlib.sha256(ipfs_hash.encode()).hexdigest()[:16]}"

        datum = DIDDatum(
            did_id=did_id.encode("utf-8"),
            face_ipfs_hash=ipfs_hash.encode("utf-8"),
            owner=bytes(self.pay_vkey.hash()),
            created_at=int(time.time() * 1000),
            verified=0,
        )

        print(f"\n📤 Creating DID: {did_id}")
        print(f"   IPFS: {ipfs_hash}")
        print(f"   Locking {amount / 1_000_000:.2f} ADA...")

        builder = TransactionBuilder(self.context)
        builder.add_input_address(self.address)
        builder.add_output(TransactionOutput(self.script_address, Value(amount), datum=datum))
        signed_tx = builder.build_and_sign([self.pay_skey, self.stake_skey], change_address=self.address)
        self.context.submit_tx(signed_tx)
        tx_hash = str(signed_tx.id)

        print(f"✅ TX: {tx_hash}")
        print(f"   Explorer: https://preprod.cardanoscan.io/transaction/{tx_hash}")
        return tx_hash

    def _find_utxo(self, lock_tx_hash: str):
        """Tìm UTxO đã lock tại script address"""
        utxos = self.context.utxos(self.script_address)
        for utxo in utxos:
            if str(utxo.input.transaction_id) == lock_tx_hash:
                return utxo
        return None

    def register(self, lock_tx_hash: str) -> str:
        """Register: spend + continuing output (same datum)"""
        print(f"\n📋 Register DID (CKV: continuing output)...")
        target = self._find_utxo(lock_tx_hash)
        if not target:
            print(f"❌ UTxO not found: {lock_tx_hash}")
            return None

        builder = TransactionBuilder(self.context)
        builder.add_script_input(target, self.script, Redeemer(Register()))
        builder.required_signers = [self.pay_vkey.hash()]
        # Continuing output: same datum, same amount
        builder.add_output(TransactionOutput(
            self.script_address, Value(target.output.amount.coin), datum=target.output.datum,
        ))
        signed_tx = builder.build_and_sign([self.pay_skey, self.stake_skey], change_address=self.address)
        self.context.submit_tx(signed_tx)
        tx_hash = str(signed_tx.id)
        print(f"✅ Register TX: {tx_hash}")
        return tx_hash

    def verify_did(self, lock_tx_hash: str) -> str:
        """Verify: spend + continuing output (verified: 0→1)"""
        print(f"\n✅ Verify DID (CKV: verified 0→1)...")
        target = self._find_utxo(lock_tx_hash)
        if not target:
            print(f"❌ UTxO not found: {lock_tx_hash}")
            return None

        input_datum = target.output.datum
        output_datum = DIDDatum(
            did_id=input_datum.did_id,
            face_ipfs_hash=input_datum.face_ipfs_hash,
            owner=input_datum.owner,
            created_at=input_datum.created_at,
            verified=1,  # 0 → 1
        )

        builder = TransactionBuilder(self.context)
        builder.add_script_input(target, self.script, Redeemer(Verify()))
        builder.add_output(TransactionOutput(
            self.script_address, Value(target.output.amount.coin), datum=output_datum,
        ))
        signed_tx = builder.build_and_sign([self.pay_skey, self.stake_skey], change_address=self.address)
        self.context.submit_tx(signed_tx)
        tx_hash = str(signed_tx.id)
        print(f"✅ Verify TX: {tx_hash}")
        return tx_hash

    def update_did(self, lock_tx_hash: str, new_ipfs_hash: str) -> str:
        """Update: spend + continuing output (new ipfs_hash)"""
        print(f"\n📝 Update DID (CKV: new IPFS hash)...")
        target = self._find_utxo(lock_tx_hash)
        if not target:
            print(f"❌ UTxO not found: {lock_tx_hash}")
            return None

        input_datum = target.output.datum
        output_datum = DIDDatum(
            did_id=input_datum.did_id,
            face_ipfs_hash=new_ipfs_hash.encode("utf-8"),
            owner=input_datum.owner,
            created_at=input_datum.created_at,
            verified=input_datum.verified,
        )

        builder = TransactionBuilder(self.context)
        builder.add_script_input(target, self.script, Redeemer(Update()))
        builder.required_signers = [self.pay_vkey.hash()]
        builder.add_output(TransactionOutput(
            self.script_address, Value(target.output.amount.coin), datum=output_datum,
        ))
        signed_tx = builder.build_and_sign([self.pay_skey, self.stake_skey], change_address=self.address)
        self.context.submit_tx(signed_tx)
        tx_hash = str(signed_tx.id)
        print(f"✅ Update TX: {tx_hash}")
        return tx_hash

    def revoke(self, lock_tx_hash: str) -> str:
        """Revoke: spend + NO continuing output (burn DID)"""
        print(f"\n🔥 Revoke DID (CKV: no continuing output = burn)...")
        target = self._find_utxo(lock_tx_hash)
        if not target:
            print(f"❌ UTxO not found: {lock_tx_hash}")
            return None

        builder = TransactionBuilder(self.context)
        builder.add_script_input(target, self.script, Redeemer(Revoke()))
        builder.required_signers = [self.pay_vkey.hash()]
        # NO continuing output — ADA returns to wallet
        signed_tx = builder.build_and_sign([self.pay_skey, self.stake_skey], change_address=self.address)
        self.context.submit_tx(signed_tx)
        tx_hash = str(signed_tx.id)
        print(f"✅ Revoke TX: {tx_hash} (DID burned 🔥)")
        return tx_hash

    def get_balance(self) -> float:
        utxos = self.context.utxos(self.address)
        return sum(u.output.amount.coin for u in utxos) / 1_000_000

    def list_script_utxos(self):
        utxos = self.context.utxos(self.script_address)
        print(f"\n📋 Script UTxOs ({len(utxos)} total):")
        for utxo in utxos:
            print(f"   TX: {str(utxo.input.transaction_id)[:16]}... | {utxo.output.amount.coin:,} lovelace")
        return utxos


def main():
    parser = argparse.ArgumentParser(description="DID Lifecycle Operations (CKV)")
    parser.add_argument("--action", choices=["create", "register", "verify", "update", "revoke", "balance", "list"],
                       required=True)
    parser.add_argument("--ipfs-hash", type=str, default="QmTestHash", help="IPFS CID")
    parser.add_argument("--did-id", type=str, default=None)
    parser.add_argument("--tx-hash", type=str, default=None, help="Lock TX hash")
    parser.add_argument("--new-ipfs-hash", type=str, default=None, help="New IPFS hash for update")
    args = parser.parse_args()

    manager = DIDManager()

    if args.action == "create":
        tx = manager.create_and_lock(args.ipfs_hash, args.did_id)
        print(f"\n💡 Next: python did_operations.py --action register --tx-hash {tx}")

    elif args.action == "register":
        if not args.tx_hash:
            print("❌ --tx-hash required"); sys.exit(1)
        manager.register(args.tx_hash)

    elif args.action == "verify":
        if not args.tx_hash:
            print("❌ --tx-hash required"); sys.exit(1)
        manager.verify_did(args.tx_hash)

    elif args.action == "update":
        if not args.tx_hash or not args.new_ipfs_hash:
            print("❌ --tx-hash + --new-ipfs-hash required"); sys.exit(1)
        manager.update_did(args.tx_hash, args.new_ipfs_hash)

    elif args.action == "revoke":
        if not args.tx_hash:
            print("❌ --tx-hash required"); sys.exit(1)
        manager.revoke(args.tx_hash)

    elif args.action == "balance":
        print(f"💰 Balance: {manager.get_balance():.2f} ADA")

    elif args.action == "list":
        manager.list_script_utxos()


if __name__ == "__main__":
    main()
