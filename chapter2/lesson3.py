"""
lesson3.py — pycardano + Blockfrost only

This version follows the style of lesson1 and uses pycardano's
BlockFrostChainContext exclusively. No fallbacks to raw blockfrost client.

Usage (PowerShell):
  $env:BLOCKFROST_PROJECT_ID = 'your_project_id'
  python lesson3.py --address <cardano_address> --network testnet

You can also pass --project-id directly.
"""

from __future__ import annotations

import os
import argparse
import json
from collections import defaultdict

from pycardano import BlockFrostChainContext, Network, Address


def build_context(
    project_id: str, network: str = "testnet", base_url: str | None = None
):
    """Create a BlockFrostChainContext using pycardano.

    base_url can be provided for preprod/preview endpoints; otherwise we use
    Blockfrost's standard mainnet/testnet endpoints.
    """
    if not base_url:
        if network.lower() in ("testnet", "test"):
            base_url = "https://cardano-testnet.blockfrost.io/api/v0"
        else:
            base_url = "https://cardano-mainnet.blockfrost.io/api/v0"

    net = Network.TESTNET if network.lower() in ("testnet", "test") else Network.MAINNET
    ctx = BlockFrostChainContext(project_id=project_id, base_url=base_url, network=net)
    return ctx


def pretty_print_utxos(ctx: BlockFrostChainContext, address: str):
    addr = Address.from_primitive(address)
    print(f"Querying address (pycardano+Blockfrost): {addr}\n")

    # ctx.utxos accepts string or Address depending on pycardano version
    try:
        utxos = ctx.utxos(str(addr))
    except TypeError:
        utxos = ctx.utxos(addr)

    if not utxos:
        print("No UTxOs found for this address.")
        return

    totals = defaultdict(int)

    for u in utxos:
        # input info
        inp = getattr(u, "input", None)
        if inp is not None:
            txid = (
                getattr(inp, "transaction_id", None)
                or getattr(inp, "tx_id", None)
                or getattr(inp, "tx_hash", None)
                or str(inp)
            )
            idx = (
                getattr(inp, "index", None)
                or getattr(inp, "tx_index", None)
                or getattr(inp, "output_index", None)
            )
        else:
            txid = None
            idx = None

        # amount representation varies by pycardano version
        amount = None
        if hasattr(u, "output") and getattr(u.output, "amount", None) is not None:
            amount = u.output.amount
        elif getattr(u, "amount", None) is not None:
            amount = u.amount

        print("--- UTxO ---")
        print(f"tx: {txid}#{idx}")

        # Normalize and print amounts; also calculate totals
        if amount is None:
            print("  amount: (unknown format)")
        else:
            # amount may be list/dict/Value object; try common cases
            if isinstance(amount, (list, tuple)):
                for a in amount:
                    if isinstance(a, dict):
                        unit = a.get("unit")
                        qty = int(a.get("quantity", 0))
                    else:
                        unit = (
                            getattr(a, "unit", None)
                            or getattr(a, "policy_id", None)
                            or getattr(a, "asset_name", None)
                        )
                        qty = int(getattr(a, "quantity", getattr(a, "amount", 0)))
                    print(f"  {unit}: {qty}")
                    totals[unit] += qty
            elif isinstance(amount, dict):
                # blockfrost-like dict mapping unit->quantity
                for unit, qty in amount.items():
                    try:
                        q = int(qty)
                    except Exception:
                        q = qty
                    print(f"  {unit}: {q}")
                    totals[unit] += q
            else:
                # best-effort: print repr and try to get lovelace
                printed = False
                try:
                    # some pycardano Value has .coin and .multiasset
                    coin = getattr(amount, "coin", None)
                    if coin is not None:
                        print(f"  lovelace: {int(coin)}")
                        totals["lovelace"] += int(coin)
                        printed = True
                except Exception:
                    pass

                if not printed:
                    print(f"  {repr(amount)}")

    # Print totals summary
    print("\n=== Totals ===")
    for unit, qty in totals.items():
        print(f"{unit}: {qty}")


def main():
    parser = argparse.ArgumentParser(
        description="Lesson3: query addresses using pycardano + Blockfrost"
    )
    parser.add_argument(
        "--address", help="Cardano address to query (payment or script address)"
    )
    parser.add_argument(
        "--project-id",
        help="Blockfrost project id (or set BLOCKFROST_PROJECT_ID env var)",
    )
    parser.add_argument("--network", choices=("testnet", "mainnet"), default="testnet")
    parser.add_argument(
        "--base-url", help="Optional custom Blockfrost base URL (for preprod/preview)"
    )

    args = parser.parse_args()

    project_id = args.project_id or os.getenv("BLOCKFROST_PROJECT_ID")
    if not project_id:
        print("Please set BLOCKFROST_PROJECT_ID env var or pass --project-id")
        raise SystemExit(1)

    if not args.address:
        parser.print_help()
        raise SystemExit(0)

    ctx = build_context(
        project_id=project_id, network=args.network, base_url=args.base_url
    )
    print(
        f"Connected to Blockfrost (network={ctx.network}) using project id: {project_id}\n"
    )

    pretty_print_utxos(ctx, args.address)


if __name__ == "__main__":
    main()
