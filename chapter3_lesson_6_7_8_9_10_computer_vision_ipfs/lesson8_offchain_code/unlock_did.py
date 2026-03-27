"""
Lesson 8 — Unlock ADA từ Smart Contract bằng Redeemer

CKV (Continuing output Validation) Logic:
  Register → spend UTxO + create continuing output (same datum)
  Verify   → spend UTxO + create output (verified: 0 → 1)
  Update   → spend UTxO + create output (new ipfs_hash)
  Revoke   → spend UTxO + NO output (burn DID, ADA back to wallet)

Usage:
    python unlock_did.py --action register --tx-hash abc123...
    python unlock_did.py --action revoke --tx-hash abc123...
"""

import argparse
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
# PlutusData classes — khớp Aiken types
# ═══════════════════════════════════════════════

@dataclass
class DIDDatum(PlutusData):
    CONSTR_ID = 0
    did_id: bytes
    face_ipfs_hash: bytes
    owner: bytes
    created_at: int
    verified: int  # 0 = chưa verify, 1 = đã verify

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
    "register": (Register, True),   # needs continuing output
    "verify": (Verify, True),       # needs continuing output (verified=1)
    "update": (Update, True),       # needs continuing output (new ipfs_hash)
    "revoke": (Revoke, False),      # NO continuing output (burn)
}


def main():
    parser = argparse.ArgumentParser(description="Unlock DID from Smart Contract (CKV)")
    parser.add_argument("--action", choices=ACTION_MAP.keys(), required=True)
    parser.add_argument("--tx-hash", type=str, required=True, help="Lock TX hash")
    parser.add_argument("--new-ipfs-hash", type=str, default=None, help="New IPFS hash (for update)")
    args = parser.parse_args()

    # ── Setup ──
    blockfrost_id = os.getenv("BLOCKFROST_PROJECT_ID")
    mnemonic = os.getenv("MNEMONIC")
    if not blockfrost_id or not mnemonic:
        print("❌ Cấu hình .env: BLOCKFROST_PROJECT_ID + MNEMONIC")
        sys.exit(1)

    context = BlockFrostChainContext(
        project_id=blockfrost_id,
        base_url="https://cardano-preprod.blockfrost.io/api/",
    )

    hd = HDWallet.from_mnemonic(mnemonic)
    pay_node = hd.derive_from_path("m/1852'/1815'/0'/0/0")
    pay_skey = ExtendedSigningKey.from_hdwallet(pay_node)
    pay_vkey = pay_skey.to_verification_key()
    stake_node = hd.derive_from_path("m/1852'/1815'/0'/2/0")
    stake_skey = ExtendedSigningKey.from_hdwallet(stake_node)
    stake_vkey = stake_skey.to_verification_key()
    sender = Address(pay_vkey.hash(), stake_vkey.hash(), network=Network.TESTNET)
    print(f"👛 Wallet: {sender}")

    # ── Load contract ──
    plutus_path = Path(__file__).parent.parent / "lesson6_cv_did_integration" / "did_contract" / "plutus.json"
    with open(plutus_path) as f:
        blueprint = json.load(f)
    script = PlutusV3Script(bytes.fromhex(blueprint["validators"][0]["compiledCode"]))
    script_address = Address(plutus_script_hash(script), network=Network.TESTNET)
    print(f"📜 Script: {script_address}")

    # ── Find UTxO ──
    print(f"\n🔍 Searching for UTxO (TX: {args.tx_hash[:16]}...)...")
    utxos = context.utxos(script_address)
    target = None
    for utxo in utxos:
        if str(utxo.input.transaction_id) == args.tx_hash:
            target = utxo
            break

    if not target:
        print(f"❌ UTxO not found for TX: {args.tx_hash}")
        sys.exit(1)
    print(f"✅ Found UTxO: {target.output.amount.coin:,} lovelace")

    # ── Build TX ──
    action_class, needs_continuing = ACTION_MAP[args.action]
    print(f"\n📤 Action: {args.action.upper()} (continuing_output={needs_continuing})...")

    builder = TransactionBuilder(context)
    builder.add_input_address(sender)  # Wallet UTxOs cho fees!
    builder.add_script_input(
        utxo=target,
        script=script,
        redeemer=Redeemer(action_class()),
    )
    builder.required_signers = [pay_vkey.hash()]

    if needs_continuing:
        # CKV: tạo continuing output quay lại script
        # Decode inline datum từ UTxO
        raw_datum = target.output.datum

        if args.action == "verify":
            # Verify: deserialize RawCBOR → tạo datum mới với verified=1
            input_datum = DIDDatum.from_cbor(raw_datum.cbor)
            out_datum = DIDDatum(
                did_id=input_datum.did_id,
                face_ipfs_hash=input_datum.face_ipfs_hash,
                owner=input_datum.owner,
                created_at=input_datum.created_at,
                verified=1,  # 0 → 1
            )
        elif args.action == "update":
            if not args.new_ipfs_hash:
                print("❌ --new-ipfs-hash required for update action")
                sys.exit(1)
            # Update: deserialize RawCBOR → tạo datum mới với ipfs_hash mới
            input_datum = DIDDatum.from_cbor(raw_datum.cbor)
            out_datum = DIDDatum(
                did_id=input_datum.did_id,
                face_ipfs_hash=args.new_ipfs_hash.encode("utf-8"),
                owner=input_datum.owner,
                created_at=input_datum.created_at,
                verified=input_datum.verified,
            )
        else:
            # Register: giữ nguyên datum (RawCBOR OK — không cần truy cập fields)
            out_datum = raw_datum

        builder.add_output(
            TransactionOutput(
                address=script_address,
                amount=Value(target.output.amount.coin),
                datum=out_datum,
            )
        )
        print(f"   ✅ Continuing output added (back to script)")

    # ── Sign & submit ──
    signed_tx = builder.build_and_sign([pay_skey, stake_skey], change_address=sender)
    context.submit_tx(signed_tx)
    tx_hash = str(signed_tx.id)

    print(f"\n✅ {args.action.upper()} TX submitted!")
    print(f"   TX Hash: {tx_hash}")
    print(f"   Explorer: https://preprod.cardanoscan.io/transaction/{tx_hash}")

    if args.action == "revoke":
        print(f"   🔥 DID burned — ADA returned to wallet")
    elif args.action == "verify":
        print(f"   ✅ DID verified — verified: 0 → 1")
    elif args.action == "update":
        print(f"   📝 DID updated — new IPFS hash: {args.new_ipfs_hash}")
    else:
        print(f"   📋 DID registered — continuing output at script")


if __name__ == "__main__":
    main()
