from mnemonic import Mnemonic
from pycardano import (
    HDWallet,
    Address,
    Network,
    ExtendedSigningKey
)

m = Mnemonic("english")
mnemonic_phrase = m.generate(strength=256)

print(f"Mnemonic: {mnemonic_phrase}")

hdwallet = HDWallet.from_mnemonic(mnemonic_phrase)

payment_path = "m/1852'/1815'/0'/0/0"
payment_node = hdwallet.derive_from_path(payment_path)
payment_skey = ExtendedSigningKey.from_hdwallet(payment_node)
payment_vkey = payment_skey.to_verification_key()

staking_path = "m/1852'/1815'/0'/2/0"
staking_node = hdwallet.derive_from_path(staking_path)
stake_skey = ExtendedSigningKey.from_hdwallet(staking_node)
stake_vkey = stake_skey.to_verification_key()

print(f"Payment VKey Hash: {payment_vkey.hash()}")
print(f"Stake VKey Hash:   {stake_vkey.hash()}")

address = Address(
    payment_part=payment_vkey.hash(),
    staking_part=stake_vkey.hash(),
    network=Network.TESTNET
)

print(f"Address: {address}")

recovered_hd = HDWallet.from_mnemonic(mnemonic_phrase)
recovered_payment_node = recovered_hd.derive_from_path(payment_path)
recovered_payment_skey = ExtendedSigningKey.from_hdwallet(recovered_payment_node)

is_match = recovered_payment_skey == payment_skey
print(f"Khôi phục thành công? {'✅ CÓ' if is_match else '❌ KHÔNG'}")
