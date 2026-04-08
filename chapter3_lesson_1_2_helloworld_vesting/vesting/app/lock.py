from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import json
import os

from dotenv import load_dotenv
from pycardano import (
    Address,
    BlockFrostChainContext,
    HDWallet,
    Network,
    PaymentExtendedSigningKey,
    PlutusData,
    StakeExtendedSigningKey,
    TransactionBuilder,
    TransactionOutput,
)
from pycardano.hash import ScriptHash, TransactionId


# Load biến môi trường từ file .env
load_dotenv()


# Datum sẽ được đính kèm vào UTxO tại script address
# Datum của vesting gồm:
# - lock_until: thời điểm mở khóa (POSIX time tính theo milliseconds)
# - owner: người có thể unlock bất kỳ lúc nào
# - beneficiary: người có thể unlock sau lock_until
@dataclass
class VestingDatum(PlutusData):
    CONSTR_ID = 0
    lock_until: int
    owner: bytes
    beneficiary: bytes


# Đọc script hash từ file plutus.json đã được build sẵn từ contract
# Script hash này dùng để tạo contract address
def read_script_hash() -> ScriptHash:
    with open("../contract/plutus.json", "r", encoding="utf-8") as file:
        plutus_json = json.load(file)

    validator_data = plutus_json["validators"][0]
    return ScriptHash(bytes.fromhex(validator_data["hash"]))


# Từ mnemonic trong .env, derive ra:
# - payment signing key để ký giao dịch
# - stake key để tạo địa chỉ ví đầy đủ
# - wallet address để lấy UTxO đầu vào và nhận tiền thừa
def get_signing_key_and_address_from_mnemonic(
    mnemonic: str,
) -> tuple[PaymentExtendedSigningKey, Address]:
    wallet = HDWallet.from_mnemonic(mnemonic)

    # Derive payment key theo chuẩn CIP1852: m/1852'/1815'/0'/0/0
    payment_wallet = wallet.derive_from_path("m/1852'/1815'/0'/0/0")
    payment_signing_key = PaymentExtendedSigningKey.from_hdwallet(payment_wallet)
    payment_verification_key = payment_signing_key.to_verification_key()

    # Derive stake key theo chuẩn CIP1852: m/1852'/1815'/0'/2/0
    stake_wallet = wallet.derive_from_path("m/1852'/1815'/0'/2/0")
    stake_signing_key = StakeExtendedSigningKey.from_hdwallet(stake_wallet)
    stake_verification_key = stake_signing_key.to_verification_key()

    # Tạo địa chỉ ví testnet từ payment key hash và stake key hash
    wallet_address = Address(
        payment_part=payment_verification_key.hash(),
        staking_part=stake_verification_key.hash(),
        network=Network.TESTNET,
    )

    return payment_signing_key, wallet_address


# Tạo và submit giao dịch lock ADA vào contract
# Giao dịch này sẽ:
# - lấy UTxO từ ví owner
# - tạo 1 output gửi vào script address
# - đính kèm datum vesting vào output đó
def lock(
    amount: int,
    contract_address: Address,
    datum: PlutusData,
    signing_key: PaymentExtendedSigningKey,
    sender_address: Address,
    context: BlockFrostChainContext,
) -> TransactionId:
    # In ra các giá trị thực sự đang được lock vào contract
    print("=== Lock parameters ===")
    print(f"Amount: {amount}")
    print(f"Contract address: {contract_address}")
    print(f"Datum CBOR: {datum.to_cbor_hex()}")
    print(f"Sender address: {sender_address}")

    # Khởi tạo transaction builder và tự chọn input từ ví người gửi
    builder = TransactionBuilder(context=context)
    builder.add_input_address(sender_address)

    # Tạo output gửi amount vào contract address kèm datum
    builder.add_output(
        TransactionOutput(
            address=contract_address,
            amount=amount,
            datum=datum,
        )
    )

    # Build giao dịch, tự trả tiền thừa về ví người gửi, rồi ký giao dịch
    signed_tx = builder.build_and_sign(
        signing_keys=[signing_key],
        change_address=sender_address,
    )

    # Submit giao dịch lên mạng preview testnet
    context.submit_tx(signed_tx.to_cbor())
    return signed_tx.id


# Hàm main để gom toàn bộ luồng chạy chính:
# - đọc config từ env
# - tạo context kết nối Blockfrost
# - derive ví owner và beneficiary từ mnemonic
# - đọc script hash
# - tạo datum vesting
# - lock ADA vào contract
def main() -> None:
    blockfrost_project_id = os.environ["BLOCKFROST_PROJECT_ID"]
    owner_mnemonic = os.environ["OWNER_MNEMONIC"]
    beneficiary_mnemonic = os.environ["BENEFICIARY_MNEMONIC"]

    # Kết nối tới Cardano Preview testnet thông qua Blockfrost
    context = BlockFrostChainContext(
        project_id=blockfrost_project_id,
        base_url="https://cardano-preview.blockfrost.io/api/",
    )

    # Lấy signing key và địa chỉ ví từ mnemonic
    owner_signing_key, owner_address = get_signing_key_and_address_from_mnemonic(
        owner_mnemonic
    )
    beneficiary_signing_key, beneficiary_address = (
        get_signing_key_and_address_from_mnemonic(beneficiary_mnemonic)
    )

    # Đọc script hash từ file contract đã build
    script_hash = read_script_hash()

    # Owner và beneficiary là payment key hash của 2 ví
    owner = owner_signing_key.to_verification_key().hash()
    beneficiary = beneficiary_signing_key.to_verification_key().hash()

    # Set lock time là 1 phút kể từ lúc chạy script, giống tutorial vesting
    lock_until = int(
        (datetime.now(timezone.utc) + timedelta(minutes=1)).timestamp() * 1000
    )

    datum = VestingDatum(
        lock_until=lock_until,
        owner=owner.to_primitive(),
        beneficiary=beneficiary.to_primitive(),
    )

    # In ra field chính trong datum để tiện kiểm tra
    print("=== Datum fields ===")
    print(f"Lock until (ms): {lock_until}")
    print(f"Owner PKH: {owner}")
    print(f"Owner bytes: {owner.to_primitive().hex()}")
    print(f"Beneficiary PKH: {beneficiary}")
    print(f"Beneficiary bytes: {beneficiary.to_primitive().hex()}")
    print(f"Beneficiary address: {beneficiary_address}")

    # Lock 3 ADA vào contract
    # Tạo địa chỉ contract từ script hash trên testnet
    contract_address = Address(
        payment_part=script_hash,
        network=Network.TESTNET,
    )
    tx_hash = lock(
        amount=3_000_000,
        contract_address=contract_address,
        datum=datum,
        signing_key=owner_signing_key,
        sender_address=owner_address,
        context=context,
    )

    # In link tra cứu giao dịch sau khi submit thành công
    print("=== Success ===")
    print(f"https://preview.cardanoscan.io/transaction/{tx_hash}")


if __name__ == "__main__":
    main()
