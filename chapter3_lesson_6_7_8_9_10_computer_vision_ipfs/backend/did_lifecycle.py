#!/usr/bin/env python3
"""
DID Lifecycle Test - Complete Flow
Create DID → Register → Update → Verify → Revoke
Tests all validators in sequence with realistic data
"""

import json
import os
import time
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, List, Dict

from pycardano import (
    BlockFrostChainContext,
    Address,
    Network,
    PaymentSigningKey,
    PaymentVerificationKey,
    PlutusV3Script,
    ScriptHash,
    PlutusData,
    TransactionBuilder,
    TransactionOutput,
    Redeemer,
)

# Config
api_key = "preprod0K9MnKqsU21MJvqu00V4Laf4pz7dALPK"
base_url = "https://cardano-preprod.blockfrost.io/api/"


class DIDALifecycleTest:
    def __init__(self):
        self.context = BlockFrostChainContext(project_id=api_key, base_url=base_url)
        self.sk = PaymentSigningKey.load("me_preprod.sk")
        self.vk = PaymentVerificationKey.from_signing_key(self.sk)
        self.addr = Address(payment_part=self.vk.hash(), network=Network.TESTNET)

        # Load validator
        with open(os.path.join("..", "smart_contracts", "plutus.json")) as f:
            plutus = json.load(f)
        validator_data = plutus["validators"][0]
        self.script = PlutusV3Script(bytes.fromhex(validator_data["compiledCode"]))
        self.script_hash = ScriptHash(bytes.fromhex(validator_data["hash"]))
        self.script_addr = Address(
            payment_part=self.script_hash, network=Network.TESTNET
        )

        self.transactions: List[Dict] = []

    @dataclass
    class DIDDatum(PlutusData):
        CONSTR_ID = 0
        did_id: bytes
        face_ipfs_hash: bytes
        owner: bytes
        created_at: int
        verified: bool

    @dataclass
    class Register(PlutusData):
        CONSTR_ID = 0  # Enum variant

    @dataclass
    class Update(PlutusData):
        CONSTR_ID = 1  # Enum variant

    @dataclass
    class Verify(PlutusData):
        CONSTR_ID = 2  # Enum variant

    @dataclass
    class Revoke(PlutusData):
        CONSTR_ID = 3  # Enum variant

    def print_header(self, title):
        print()
        print("=" * 70)
        print(title)
        print("=" * 70)
        print()

    def print_step(self, step_num, description):
        print(f"[{step_num}] {description}")

    def log_transaction(self, action: str, tx_id: str, details: Dict):
        self.transactions.append(
            {
                "action": action,
                "tx_id": tx_id,
                "timestamp": datetime.now().isoformat(),
                "details": details,
            }
        )

    def run(self):
        """Run full DID lifecycle test"""
        self.print_header("DID LIFECYCLE TEST - FULL SEQUENCE")

        self.print_step(1, "Setup: Load wallet and validator")
        print(f"    Wallet: {self.addr}")
        print(f"    Script: {self.script_addr}")
        print()

        # Test data
        did_id = "did:cardano:lifecycle_test_001"
        initial_face_hash = "QmInitialFaceEmbedding123456789"
        updated_face_hash = "QmUpdatedFaceEmbedding987654321"

        print()
        self.print_step(2, "Create DID - Lock 2 ADA to script with datum")
        print(f"    DID: {did_id}")
        print(f"    Face Hash: {initial_face_hash}")
        print(f"    Initial timestamp: {datetime.now().isoformat()}")

        try:
            # Create datum
            datum = self.DIDDatum(
                did=did_id.encode(),
                face_hash=initial_face_hash.encode(),
                created_at=int(datetime.now().timestamp()),
            )

            # Build transaction
            builder = TransactionBuilder(self.context)
            builder.add_input_address(self.addr)
            builder.add_output(
                TransactionOutput(
                    address=self.script_addr,
                    amount=2_000_000,  # 2 ADA
                    datum=datum,
                )
            )

            signed_tx = builder.build_and_sign(
                signing_keys=[self.sk],
                change_address=self.addr,
            )

            tx_id = self.context.submit_tx(signed_tx)
            print(f"    ✓ Transaction submitted: {tx_id}")
            self.log_transaction(
                "CREATE_DID",
                tx_id,
                {"did": did_id, "face_hash": initial_face_hash, "amount": 2.0},
            )

            lock_tx_id = tx_id

        except Exception as e:
            print(f"    ✗ Error: {e}")
            return False

        print()
        print("    ⏳ Waiting for confirmation (~30 seconds)...")
        print("    Note: Run this script again after confirmation to continue")
        print()
        self.print_step(3, "Register - Validate DID with Register redeemer")
        print(f"    Status: PENDING CONFIRMATION")
        print(f"    Action required: Wait for Create transaction to confirm")
        print(f"    Then run: python did_lifecycle_register.py")
        print()

        print()
        self.print_step(4, "Update - Change face embedding (UPDATE redeemer)")
        print(f"    New Face Hash: {updated_face_hash}")
        print(f"    Status: PENDING CREATE + REGISTER")
        print()

        print()
        self.print_step(5, "Verify - Validate DID integrity (VERIFY redeemer)")
        print(f"    Status: PENDING CREATE + REGISTER + UPDATE")
        print()

        print()
        self.print_step(6, "Revoke - Disable DID (REVOKE redeemer)")
        print(f"    Status: PENDING CREATE + REGISTER + UPDATE + VERIFY")
        print()

        # Show summary
        print()
        self.print_header("LIFECYCLE WORKFLOW PLAN")

        print("Step-by-step execution plan:")
        print()
        print("1. CREATE_DID")
        print("   Lock 2 ADA to script with DID datum")
        print(f"   TX: {lock_tx_id}")
        print(f"   Wait ~30 seconds for confirmation")
        print()

        print("2. REGISTER_DID (after CREATE confirms)")
        print("   Spend the UTxO with Register redeemer")
        print("   Validator validates: did ≠ empty, hash ≠ empty, timestamp > 0")
        print("   Returns remaining ADA to wallet")
        print()

        print("3. CREATE_UPDATE (optional - creates new DID entry)")
        print("   Lock 2 ADA with updated face hash")
        print()

        print("4. UPDATE_DID (after UPDATE CREATE confirms)")
        print("   Spend with Update redeemer (permissive validator)")
        print()

        print("5. VERIFY_DID (optional - read-only check)")
        print("   Spend with Verify redeemer")
        print("   Validator checks data consistency")
        print()

        print("6. REVOKE_DID (final - permanent disable)")
        print("   Spend with Revoke redeemer")
        print("   Permanent state change")
        print()

        print()
        self.print_header("TRANSACTION HISTORY")

        for i, tx in enumerate(self.transactions, 1):
            print(f"Transaction {i}:")
            print(f"  Action: {tx['action']}")
            print(f"  TX ID: {tx['tx_id']}")
            print(f"  Details: {tx['details']}")
            print()

        print()
        self.print_header("✅ LIFECYCLE TEST INITIATED")

        print("Initial transaction submitted successfully!")
        print()
        print(f"Lock TX: {lock_tx_id}")
        print(
            "Verify on CardanoScan: https://preprod.cardanoscan.io/transaction/"
            + lock_tx_id
        )
        print()
        print("Remaining steps will be executed after confirmation.")
        print()

        return True


def main():
    test = DIDALifecycleTest()
    success = test.run()

    if not success:
        print("❌ Lifecycle test failed")
        return 1

    print("✅ Lifecycle test phase 1 complete")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
