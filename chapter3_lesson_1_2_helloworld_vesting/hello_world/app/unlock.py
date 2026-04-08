from dataclasses import dataclass
import json
import os
import sys

from dotenv import load_dotenv
from pycardano import (
    Address,
    BlockFrostChainContext,
    HDWallet,
    Network,
    PaymentExtendedSigningKey,
    PlutusData,
    PlutusV3Script,
    Redeemer,
    StakeExtendedSigningKey,
    TransactionBuilder,
    TransactionOutput,
    UTxO,
)
from pycardano.hash import ScriptHash, TransactionId, VerificationKeyHash


# Load biến môi trường từ file .env
load_dotenv()


# Redeemer sẽ được truyền vào khi tiêu UTxO đang nằm ở script
# Ở đây redeemer chỉ chứa 1 message bytes
@dataclass
class HelloWorldRedeemer(PlutusData):
    CONSTR_ID = 0
    msg: bytes


# Đọc validator từ file plutus.json đã build sẵn
# Hàm này trả về:
# - script bytes: dùng để attach script khi unlock
# - script hash: dùng để tạo contract address và tìm UTxO tại contract
def read_validator() -> dict:
    with open("../contract/plutus.json", "r", encoding="utf-8") as file:
        plutus_json = json.load(file)

    validator_data = plutus_json["validators"][0]

    script = PlutusV3Script(bytes.fromhex(validator_data["compiledCode"]))
    script_hash = ScriptHash(bytes.fromhex(validator_data["hash"]))

    return {
        "script": script,
        "script_hash": script_hash,
    }


# Từ mnemonic trong .env, derive ra:
# - payment signing key để ký giao dịch
# - stake key để tạo địa chỉ ví đầy đủ
# - wallet address để nhận tiền sau khi unlock
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


# Tìm đúng UTxO tại contract address dựa trên tx hash đã truyền vào
# Đây là UTxO trước đó đã được lock vào script
def find_script_utxo(
    context: BlockFrostChainContext,
    tx_hash: str,
    contract_address: Address,
) -> UTxO:
    for utxo in context.utxos(str(contract_address)):
        if str(utxo.input.transaction_id) == tx_hash:
            return utxo

    raise ValueError(f"UTxO not found for transaction {tx_hash}")


# Tạo và submit giao dịch unlock ADA từ contract
# Giao dịch này sẽ:
# - lấy 1 script UTxO làm input
# - đính kèm validator script và redeemer để tiêu UTxO đó
# - gửi ADA từ contract về lại ví người nhận
# - yêu cầu chữ ký của owner
def unlock(
    script_utxo: UTxO, 
    script: PlutusV3Script,
    redeemer: Redeemer,
    signing_key: PaymentExtendedSigningKey,
    owner_key_hash: VerificationKeyHash,
    receiver_address: Address,
    context: BlockFrostChainContext,
) -> TransactionId:
    # In ra các giá trị thực sự đang được dùng để unlock
    print("=== Unlock parameters ===")
    print(f"Script UTxO tx hash: {script_utxo.input.transaction_id}")
    print(f"Script UTxO index: {script_utxo.input.index}")
    print(f"Locked amount: {script_utxo.output.amount.coin}")
    print(f"Receiver address: {receiver_address}")
    print(f"Required signer: {owner_key_hash}")
    print(f"Redeemer CBOR: {redeemer.to_cbor_hex()}")

    # Khởi tạo transaction builder
    builder = TransactionBuilder(context=context)

    # Thêm script input để tiêu UTxO đang nằm ở contract
    builder.add_script_input(
        utxo=script_utxo,
        script=script,
        redeemer=redeemer,
    )

    # Thêm input thường từ ví người dùng để trả phí giao dịch
    builder.add_input_address(receiver_address)

    # Gửi số ADA đang khóa tại script về ví người nhận
    builder.add_output(
        TransactionOutput(
            address=receiver_address,
            amount=script_utxo.output.amount.coin,
        )
    )

    # Yêu cầu chữ ký của owner để validator có thể kiểm tra signer nếu cần
    builder.required_signers = [owner_key_hash]

    # Build giao dịch, tự trả tiền thừa về ví người nhận, rồi ký giao dịch
    signed_tx = builder.build_and_sign(
        signing_keys=[signing_key],
        change_address=receiver_address,
    )

    # Submit giao dịch lên mạng preview testnet
    context.submit_tx(signed_tx.to_cbor())
    return signed_tx.id


# Hàm main để gom toàn bộ luồng chạy chính:
# - đọc config từ env
# - đọc tx hash từ command line
# - tạo context kết nối Blockfrost
# - derive ví từ mnemonic
# - đọc validator
# - tìm UTxO tại contract
# - tạo redeemer
# - unlock ADA từ contract
def main() -> None:
    lock_tx_hash = "dea4f695d0ea2a4201bb9a736d14a7b718807f841388f3918414f041bd02fea9"
    blockfrost_project_id = os.environ["BLOCKFROST_PROJECT_ID"]
    mnemonic = os.environ["MNEMONIC"]

    # Kết nối tới Cardano Preview testnet thông qua Blockfrost
    context = BlockFrostChainContext(
        project_id=blockfrost_project_id,
        base_url="https://cardano-preview.blockfrost.io/api/",
    )

    # Lấy signing key và địa chỉ ví từ mnemonic
    signing_key, wallet_address = get_signing_key_and_address_from_mnemonic(mnemonic)

    # Đọc validator đã build từ contract
    validator = read_validator()

    # Tạo contract address từ script hash để tìm UTxO đang bị khóa
    contract_address = Address(
        payment_part=validator["script_hash"],
        network=Network.TESTNET,
    )

    # Tìm đúng UTxO tại contract từ tx hash của giao dịch lock trước đó
    script_utxo = find_script_utxo(
        context=context,
        tx_hash=lock_tx_hash,
        contract_address=contract_address,
    )

    # Owner là payment key hash của người ký giao dịch unlock
    owner_key_hash = signing_key.to_verification_key().hash()

    # Tạo redeemer để truyền vào validator khi unlock
    redeemer = Redeemer(data=HelloWorldRedeemer(msg=b"Hello, World!"))

    # In ra thông tin chính để tiện kiểm tra trước khi submit
    print("=== Script info ===")
    print(f"Contract address: {contract_address}")
    print(f"Script hash: {validator['script_hash']}")
    print(f"Owner PKH: {owner_key_hash}")

    # Unlock ADA từ contract
    tx_hash = unlock(
        script_utxo=script_utxo,
        script=validator["script"],
        redeemer=redeemer,
        signing_key=signing_key,
        owner_key_hash=owner_key_hash,
        receiver_address=wallet_address,
        context=context,
    )

    # In link tra cứu giao dịch sau khi submit thành công
    print("=== Success ===")
    print(f"https://preview.cexplorer.io/tx/{tx_hash}")


if __name__ == "__main__":
    main()