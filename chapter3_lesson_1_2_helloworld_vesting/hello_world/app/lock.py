from dataclasses import dataclass
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
# Ở đây datum chỉ chứa 1 field là owner
@dataclass
class HelloWorldDatum(PlutusData):
    CONSTR_ID = 0
    owner: bytes


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
# - lấy UTxO từ ví người gửi
# - tạo 1 output gửi vào script address
# - đính kèm datum vào output đó
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
# - derive ví từ mnemonic
# - đọc script hash
# - tạo datum
# - lock ADA vào contract
def main() -> None:
    blockfrost_project_id = os.environ["BLOCKFROST_PROJECT_ID"]
    mnemonic = os.environ["MNEMONIC"]

    # Kết nối tới Cardano Preview testnet thông qua Blockfrost
    context = BlockFrostChainContext(
        project_id=blockfrost_project_id,
        base_url="https://cardano-preview.blockfrost.io/api/",
    )

    # Lấy signing key và địa chỉ ví từ mnemonic
    signing_key, wallet_address = get_signing_key_and_address_from_mnemonic(mnemonic)

    # Đọc script hash từ file contract đã build
    script_hash = read_script_hash()

    # Tạo địa chỉ contract từ script hash trên testnet
    contract_address = Address(
        payment_part=script_hash,
        network=Network.TESTNET,
    )

    # Owner là payment key hash của người ký giao dịch
    # Giá trị này sẽ được nhét vào datum để contract dùng khi unlock/validate
    owner = signing_key.to_verification_key().hash()
    datum = HelloWorldDatum(owner=owner.to_primitive())

    # In ra field chính trong datum để tiện kiểm tra
    print("=== Datum fields ===")
    print(f"Owner PKH: {owner}")
    print(f"Owner bytes: {owner.to_primitive().hex()}")

    # Lock 2 ADA vào contract
    tx_hash = lock(
        amount=2_000_000,
        contract_address=contract_address,
        datum=datum,
        signing_key=signing_key,
        sender_address=wallet_address,
        context=context,
    )

    # In link tra cứu giao dịch sau khi submit thành công
    print("=== Success ===")
    print(f"https://preview.cexplorer.io/tx/{tx_hash}")


if __name__ == "__main__":
    main()