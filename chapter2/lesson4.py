"""
lesson4.py

Consolidate UTxOs example (based on pycardano examples/04_consolidate.py).

This script:
 - derives a payment key from a mnemonic
 - queries all UTxOs for the derived address using Blockfrost via pycardano
 - builds a single-output transaction sending the full balance back to the same address
   (i.e. consolidating inputs), accounting for fee
 - signs and optionally submits the transaction

Usage (PowerShell):
  $env:BLOCKFROST_PROJECT_ID = 'your_project_id'
  $env:WALLET_MNEMONIC = 'your 24 words'
  python lesson4.py --network testnet --confirm-submit

The script is intentionally conservative: it requires --confirm-submit to actually
submit the tx. Without it the script prints the prepared transaction and fee.
"""

from __future__ import annotations

import os
import argparse
import sys
from typing import List

from pycardano import (
    BlockFrostChainContext,
    Network,
    TransactionInput,
    TransactionOutput,
    TransactionBody,
    Transaction,
    TransactionWitnessSet,
    VerificationKeyWitness,
    Address,
    Value,
)

try:
    # fee helper function may be in transaction module
    from pycardano.transaction import fee as calc_fee
except Exception:
    calc_fee = None

from pycardano.crypto.bip32 import HDWallet

from pycardano.key import PaymentVerificationKey


def build_context(
    project_id: str, network: str = "testnet", base_url: str | None = None
):
    if not base_url:
        base_url = (
            "https://cardano-testnet.blockfrost.io/api/v0"
            if network.lower() in ("testnet", "test")
            else "https://cardano-mainnet.blockfrost.io/api/v0"
        )

    net = Network.TESTNET if network.lower() in ("testnet", "test") else Network.MAINNET
    ctx = BlockFrostChainContext(project_id=project_id, base_url=base_url, network=net)
    return ctx


def derive_payment_signing_key(mnemonic: str):
    # derive first payment key m/1852'/1815'/0'/0/0
    wallet = HDWallet.from_mnemonic(mnemonic)
    payment_hdw = wallet.derive_from_path("m/1852'/1815'/0'/0/0")

    # Prefer ExtendedSigningKey.from_hdwallet if available; else use 32-byte seed
    try:
        from pycardano.key import ExtendedSigningKey

        sk = ExtendedSigningKey.from_hdwallet(payment_hdw)
        return sk
    except Exception:
        from pycardano.key import PaymentSigningKey

        # xprivate_key is 64 bytes: kL || kR. NaCl expects 32-byte seed kL
        seed = payment_hdw.xprivate_key[:32]
        sk = PaymentSigningKey.from_primitive(seed)
        return sk


def collect_utxos_for_address(ctx: BlockFrostChainContext, addr: Address):
    try:
        utxos = ctx.utxos(str(addr))
    except TypeError:
        utxos = ctx.utxos(addr)
    return utxos


def sum_lovelace_from_utxos(utxos) -> int:
    total = 0
    for u in utxos:
        # amount representation varies: try common cases
        amt = None
        if hasattr(u, "output") and getattr(u.output, "amount", None) is not None:
            amt = u.output.amount
        elif getattr(u, "amount", None) is not None:
            amt = u.amount

        if amt is None:
            continue

        # often the first asset is lovelace
        if isinstance(amt, (list, tuple)):
            q = int(getattr(amt[0], "quantity", getattr(amt[0], "amount", 0)))
            total += q
        elif isinstance(amt, dict):
            # dict like [{'unit':'lovelace','quantity':'1000'}, ...] or mapping
            # try to find lovelace
            if "lovelace" in amt:
                total += int(amt["lovelace"])
            else:
                # sum numeric values
                for v in amt.values():
                    try:
                        total += int(v)
                    except Exception:
                        pass
        else:
            # attempt attribute access
            coin = getattr(amt, "coin", None)
            if coin is not None:
                total += int(coin)

    return total


def main():
    parser = argparse.ArgumentParser(
        description="Consolidate UTxOs into a single output using pycardano + Blockfrost"
    )
    parser.add_argument(
        "--project-id",
        help="Blockfrost project id (or set BLOCKFROST_PROJECT_ID env var)",
    )
    parser.add_argument(
        "--mnemonic", help="Wallet mnemonic (or set WALLET_MNEMONIC env var)"
    )
    parser.add_argument("--network", choices=("testnet", "mainnet"), default="testnet")
    parser.add_argument(
        "--base-url", help="Optional custom Blockfrost base URL (for preprod/preview)"
    )
    parser.add_argument(
        "--confirm-submit",
        action="store_true",
        help="Actually submit the transaction. Otherwise script does a dry run.",
    )

    args = parser.parse_args()

    project_id = args.project_id or os.getenv("BLOCKFROST_PROJECT_ID")
    if not project_id:
        print("Please set BLOCKFROST_PROJECT_ID or pass --project-id")
        raise SystemExit(1)

    mnemonic = args.mnemonic or os.getenv("WALLET_MNEMONIC")
    if not mnemonic:
        print(
            "Please provide wallet mnemonic via --mnemonic or WALLET_MNEMONIC env var"
        )
        raise SystemExit(1)

    ctx = build_context(
        project_id=project_id, network=args.network, base_url=args.base_url
    )

    # derive keys and address
    sk = derive_payment_signing_key(mnemonic)
    vk = PaymentVerificationKey.from_signing_key(sk)

    # staking key not required for consolidation; build address from payment key only
    main_address = Address(payment_part=vk.hash(), network=ctx.network)

    print(f"Derived address: {main_address}\n")

    # fetch utxos
    try:
        utxos = collect_utxos_for_address(ctx, main_address)
    except Exception as e:
        print(f"Error fetching UTxOs: {e}")
        raise SystemExit(1)

    if not utxos:
        print("No UTxOs to consolidate.")
        raise SystemExit(0)

    total_lovelace = sum_lovelace_from_utxos(utxos)
    print(f"Found {len(utxos)} UTxOs, total lovelace: {total_lovelace}")

    # Build inputs list
    inputs: List[TransactionInput] = []
    for u in utxos:
        tx_hash = (
            getattr(u, "tx_hash", None)
            or getattr(u.input, "transaction_id", None)
            or getattr(u.input, "tx_id", None)
            or getattr(u.input, "tx_hash", None)
        )
        tx_index = (
            getattr(u, "tx_index", None)
            or getattr(u.input, "index", None)
            or getattr(u, "tx_index", None)
            or getattr(u, "output_index", None)
        )
        inputs.append(TransactionInput.from_primitive([tx_hash, tx_index]))

    # Preliminary build: assume a placeholder fee (e.g., 100000 lovelace) to compute a signed shell
    placeholder_fee = 100000
    output = TransactionOutput(main_address, Value(total_lovelace))
    tx_body = TransactionBody(inputs=inputs, outputs=[output], fee=placeholder_fee)

    # sign
    signature = sk.sign(tx_body.hash())
    vkey = PaymentVerificationKey.from_signing_key(sk)
    vk_witnesses = [VerificationKeyWitness(vkey, signature)]
    signed_tx = Transaction(tx_body, TransactionWitnessSet(vkey_witnesses=vk_witnesses))

    # calculate fee: try pycardano.transaction.fee, else try ctx.fee
    calculated_fee = None
    try:
        if calc_fee is not None:
            calculated_fee = calc_fee(ctx, len(signed_tx.to_cbor()))
        else:
            # BlockFrostChainContext may expose a fee function
            calculated_fee = ctx.fee(len(signed_tx.to_cbor()))
    except Exception:
        # If we cannot calculate fee automatically, fall back to the placeholder
        calculated_fee = placeholder_fee

    print(f"Estimated fee: {calculated_fee} lovelace")

    total_available = total_lovelace - int(calculated_fee)
    if total_available <= 0:
        print("Not enough balance to cover fee. Aborting.")
        raise SystemExit(1)

    # Final tx body
    final_output = TransactionOutput(main_address, Value(total_available))
    final_body = TransactionBody(
        inputs=inputs, outputs=[final_output], fee=int(calculated_fee)
    )

    signature = sk.sign(final_body.hash())
    vk_witnesses = [VerificationKeyWitness(vkey, signature)]
    final_signed = Transaction(
        final_body, TransactionWitnessSet(vkey_witnesses=vk_witnesses)
    )

    print(
        f"Prepared transaction: inputs={len(inputs)} outputs=1 fee={calculated_fee} lovelace"
    )

    if args.confirm_submit:
        try:
            tx_hash = ctx.submit_tx(final_signed.to_cbor())
            print(f"Transaction submitted: {tx_hash}")
        except Exception as e:
            print(f"Submission failed: {e}")
            # handle common errors
            if "BadInputsUTxO" in str(e):
                print("One or more inputs are invalid or already spent.")
            elif "ValueNotConservedUTxO" in str(e):
                print("Transaction not balanced — inputs != outputs + fee.")
            raise SystemExit(1)
    else:
        print("Dry run complete. To submit, re-run with --confirm-submit.")


if __name__ == "__main__":
    main()
