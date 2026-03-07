"""
Lesson 8 — Lock ADA + DIDDatum vào Smart Contract

Tạo transaction lock 2 ADA vào DID validator kèm inline datum.
Giống pattern chapter3 lesson1 lock.py.

Usage:
    python lock_did.py
    python lock_did.py --amount 3000000 --ipfs-hash QmXxx...
"""

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

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
    ScriptHash,
    TransactionBuilder,
    TransactionOutput,
    Value,
    plutus_script_hash,
)

# Load .env từ thư mục gốc repo
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


# ═══════════════════════════════════════════════
# DIDDatum — Phải khớp chính xác với Aiken type
# ═══════════════════════════════════════════════

@dataclass
class DIDDatum(PlutusData):
    """
    On-chain datum matching Aiken DIDDatum:

        pub type DIDDatum {
          did_id: ByteArray,
          face_ipfs_hash: ByteArray,
          owner: ByteArray,
          created_at: Int,
          verified: Bool,
        }
    """
    CONSTR_ID = 0

    did_id: bytes
    face_ipfs_hash: bytes
    owner: bytes
    created_at: int
    verified: int  # 0 = False, 1 = True (Plutus Int, NOT CBOR bool)


@dataclass
class Register(PlutusData):
    """Redeemer: Register action (CONSTR_ID = 0)"""
    CONSTR_ID = 0


def load_contract(plutus_json_path: str) -> tuple:
    """
    Đọc plutus.json và tạo PlutusV3Script + script address

    Returns:
        (script, script_hash, script_address)
    """
    print(f"🔏 Loading smart contract from {plutus_json_path}...")

    with open(plutus_json_path) as f:
        blueprint = json.load(f)

    # Lấy compiled code từ blueprint
    validators = blueprint.get("validators", [])
    if not validators:
        raise ValueError("No validators found in plutus.json")

    compiled_code = validators[0]["compiledCode"]
    script = PlutusV3Script(bytes.fromhex(compiled_code))
    script_hash = plutus_script_hash(script)
    script_address = Address(script_hash, network=Network.TESTNET)

    print(f"✅ Script hash: {script_hash}")
    print(f"✅ Script address: {script_address}")

    return script, script_hash, script_address


def setup_wallet() -> tuple:
    """
    Khôi phục ví từ mnemonic (giống chapter2 lesson4)

    Returns:
        (context, sender_address, payment_skey, staking_skey, payment_vkey)
    """
    blockfrost_id = os.getenv("BLOCKFROST_PROJECT_ID")
    mnemonic = os.getenv("MNEMONIC")

    if not blockfrost_id or not mnemonic:
        print("❌ Cần cấu hình trong .env:")
        print("   BLOCKFROST_PROJECT_ID=preprod_xxx")
        print("   MNEMONIC=word1 word2 ... word24")
        sys.exit(1)

    # Kết nối Blockfrost Preprod
    context = BlockFrostChainContext(
        project_id=blockfrost_id,
        base_url="https://cardano-preprod.blockfrost.io/api/",
    )

    # Khôi phục ví từ mnemonic
    hd_wallet = HDWallet.from_mnemonic(mnemonic)

    payment_node = hd_wallet.derive_from_path("m/1852'/1815'/0'/0/0")
    payment_skey = ExtendedSigningKey.from_hdwallet(payment_node)
    payment_vkey = payment_skey.to_verification_key()

    staking_node = hd_wallet.derive_from_path("m/1852'/1815'/0'/2/0")
    staking_skey = ExtendedSigningKey.from_hdwallet(staking_node)
    staking_vkey = staking_skey.to_verification_key()

    sender_address = Address(
        payment_part=payment_vkey.hash(),
        staking_part=staking_vkey.hash(),
        network=Network.TESTNET,
    )

    # Hiển thị thông tin ví
    utxos = context.utxos(sender_address)
    balance = sum(u.output.amount.coin for u in utxos)
    print(f"👛 Wallet: {sender_address}")
    print(f"   Balance: {balance / 1_000_000:.2f} ADA")
    print(f"   UTxOs: {len(utxos)}")

    return context, sender_address, payment_skey, staking_skey, payment_vkey


def main():
    parser = argparse.ArgumentParser(description="Lock ADA + DIDDatum vào contract")
    parser.add_argument("--amount", type=int, default=2_000_000, help="Lovelace (default: 2 ADA)")
    parser.add_argument("--ipfs-hash", type=str, default="QmTestHash123", help="IPFS CID từ Lesson 6")
    parser.add_argument("--did-id", type=str, default=None, help="DID ID (auto-generate nếu bỏ trống)")
    args = parser.parse_args()

    # Setup
    plutus_path = str(Path(__file__).parent.parent / "lesson6_cv_did_integration" / "did_contract" / "plutus.json")
    script, script_hash, script_address = load_contract(plutus_path)
    context, sender_address, payment_skey, staking_skey, payment_vkey = setup_wallet()

    # Tạo DID ID (auto-generate từ IPFS hash nếu không cung cấp)
    did_id = args.did_id or f"did:cardano:{hashlib.sha256(args.ipfs_hash.encode()).hexdigest()[:16]}"

    # Tạo DIDDatum
    datum = DIDDatum(
        did_id=did_id.encode("utf-8"),
        face_ipfs_hash=args.ipfs_hash.encode("utf-8"),
        owner=bytes(payment_vkey.hash()),  # 28 bytes pub key hash
        created_at=int(time.time() * 1000),  # POSIX ms
        verified=0,
    )

    print(f"\n📤 Building Lock TX...")
    print(f"   DID ID: {did_id}")
    print(f"   IPFS Hash: {args.ipfs_hash}")
    print(f"   Owner: {bytes(payment_vkey.hash()).hex()[:16]}...")
    print(f"   Amount: {args.amount:,} lovelace ({args.amount / 1_000_000:.2f} ADA)")

    # Build transaction
    builder = TransactionBuilder(context)
    builder.add_input_address(sender_address)
    builder.add_output(
        TransactionOutput(
            address=script_address,
            amount=Value(args.amount),
            datum=datum,  # Inline datum
        )
    )

    # Sign & submit
    signed_tx = builder.build_and_sign(
        signing_keys=[payment_skey, staking_skey],
        change_address=sender_address,
    )

    context.submit_tx(signed_tx)
    tx_hash = str(signed_tx.id)

    print(f"\n✅ Lock TX submitted!")
    print(f"   TX Hash: {tx_hash}")
    print(f"   View: https://preprod.cardanoscan.io/transaction/{tx_hash}")
    print(f"\n💡 Dùng TX Hash này trong unlock_did.py:")
    print(f'   LOCK_TX_HASH = "{tx_hash}"')


if __name__ == "__main__":
    main()
