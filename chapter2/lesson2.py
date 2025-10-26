# 1. Import Mnemonic từ thư viện "mnemonic" riêng biệt
from mnemonic.mnemonic import Mnemonic

# 2. Import HDWallet và các khóa từ các mô-đun con của pycardano
from pycardano.crypto.bip32 import HDWallet
from pycardano.key import (
    PaymentSigningKey,
    PaymentVerificationKey,
    StakeSigningKey,
    StakeVerificationKey,
)
from pycardano.address import Address
from pycardano.network import Network

print("Import thành công!\n")

# --- 1. Tạo Mnemonic (Hạt giống 🌰) ---
# Chúng ta dùng lớp Mnemonic từ thư viện 'mnemonic'
mnemo = Mnemonic("english")
mnemonic_words = mnemo.generate(256)  # 256 bits = 24 từ

print("Cụm từ ghi nhớ MỚI của bạn:")
print(mnemonic_words)

# --- 2. Khởi tạo HDWallet (Thân cây 🌳) ---
# Lấy "hạt giống" (seed) nhị phân từ các từ
mnemonic_seed = mnemo.to_seed(mnemonic_words)

# Tạo ví chủ (master wallet) từ hạt giống
# HDWallet.from_seed expects a hex string; mnemonic_seed is bytes, so
# convert to hex before passing it.
hd_wallet = HDWallet.from_seed(mnemonic_seed.hex())

print("\nĐã tạo HDWallet (ví chủ).")

# --- 3. Phái sinh Khóa (Cành & Lá 🌿) ---
# Đường dẫn phái sinh CIP-1852 tiêu chuẩn

# Lấy khóa thanh toán (Payment - role 0, index 0)
payment_path = "m/1852'/1815'/0'/0/0"
payment_hdwallet_child = hd_wallet.derive_from_path(payment_path)

# Tạo cặp khóa thanh toán từ khóa con
# PaymentSigningKey expects raw key bytes; use the derived xprivate_key
# xprivate_key is 64 bytes (kL || kR). The signing seed should be 32 bytes (kL).
payment_signing_key = PaymentSigningKey.from_primitive(
    payment_hdwallet_child.xprivate_key[:32]
)
payment_verification_key = PaymentVerificationKey.from_signing_key(payment_signing_key)

print(
    f"\nKhóa ký thanh toán (Payment SK) (CBOR hex): {payment_signing_key.to_cbor_hex()}"
)

# Lấy khóa stake (Staking - role 2, index 0)
stake_path = "m/1852'/1815'/0'/2/0"
stake_hdwallet_child = hd_wallet.derive_from_path(stake_path)

# Tạo cặp khóa stake từ khóa con
# Use first 32 bytes of xprivate_key as the signing seed.
stake_signing_key = StakeSigningKey.from_primitive(
    stake_hdwallet_child.xprivate_key[:32]
)
stake_verification_key = StakeVerificationKey.from_signing_key(stake_signing_key)

print(f"Khóa ký Stake (Stake SK) (CBOR hex): {stake_signing_key.to_cbor_hex()}")

# --- Bước 4 (Bonus): Tạo địa chỉ từ các khóa ---
print("\n--- Tạo địa chỉ ví ---")
address = Address(
    payment_part=payment_verification_key.hash(),
    staking_part=stake_verification_key.hash(),
    network=Network.TESTNET,  # Hoặc Network.MAINNET
)

print(f"Địa chỉ ví (Testnet) của bạn: {address}")
