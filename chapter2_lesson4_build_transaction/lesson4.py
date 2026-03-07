import os
from mnemonic import Mnemonic
from pycardano import (
    BlockFrostChainContext,
    Network,
    TransactionBuilder,
    TransactionOutput,
    HDWallet,
    ExtendedSigningKey,
    Address
)

BLOCKFROST_ID="preprodCtJxvR4JpFpGEwm7G3SmkGWmrYUjNAc4"
SENDER_MNEMONIC="shrimp rhythm issue enter rule youth forum outdoor snow verb beauty hair bulb hybrid doll plastic fork visual jealous someone battle daring eagle fork"
RECEIVER_ADDRESS="addr_test1wzc86g4ym366hkaphryqqvaptwznqkmk2gdqz9930u534pcx58ahw"

context = BlockFrostChainContext(project_id=BLOCKFROST_ID)

sender_hd = HDWallet.from_mnemonic(SENDER_MNEMONIC)

sender_payment_node = sender_hd.derive_from_path("m/1852'/1815'/0'/0/0")
sender_payment_skey = ExtendedSigningKey.from_hdwallet(sender_payment_node)
sender_payment_vkey = sender_payment_skey.to_verification_key()

sender_staking_node = sender_hd.derive_from_path("m/1852'/1815'/0'/2/0")
sender_staking_skey = ExtendedSigningKey.from_hdwallet(sender_staking_node)
sender_staking_vkey = sender_staking_skey.to_verification_key()

sender_address = Address(
    payment_part=sender_payment_vkey.hash(),
    staking_part=sender_staking_vkey.hash(),
    network=Network.TESTNET
)

print(f"Sender Address: {sender_address}")

utxos = context.utxos(sender_address)
balance = sum([u.output.amount.coin for u in utxos])
print(f'Balance: {balance/1_000_000} ADA')

builder = TransactionBuilder(context)
builder.add_input_address(sender_address)

SEND_AMOUNT = 5
send_mount_lovelace = SEND_AMOUNT * 1_000_000

receiver_address = Address.from_primitive(RECEIVER_ADDRESS)

builder.add_output(
    TransactionOutput(
        address=receiver_address,
        amount=send_mount_lovelace
    )
)

signed_tx = builder.build_and_sign(
    signing_keys=[
        sender_payment_skey,
        sender_staking_skey
    ],
    change_address=sender_address
)

context.submit_tx(signed_tx)

print(f'Transaction submitted: {signed_tx.id}')
