#Ok chúng ta sẽ trở lại phần coding cho việc unlock ada
# Cũng concept nhưu phần lock mình sẽ build khung cho phần unlock 
# để các bạn tưởng tượng, ghi nhớ luôn đc phần logic mục đích chính chúng ta sẽ xây dựng
# Chúng ta sẽ start với hàm hàm main nha

def main() -> None:
    # Để khởi tạo 1 trasaction thì chúng ta sẽ có lệnh quen thuộc
    builder = TransactionBuilder(context=context)

    # Sau đó thì sẽ thêm những gì mà chúng ta muốn tạo ra trên cái transaction đó
    # Như mình đã nói về mặt lý thuyết trước đó là chũng ta sẽ tạo ra 1 cái UTxO trên địa chỉ ví của chúng ta, kèm theo số lượng ADA mà chúng ta muốn lấy từ contract
    builder.add_output(
        TransactionOutput(
            address=receiver_address,
            amount=script_utxo.output.amount.coin,
        )
    )

    # Và để adapt được với cái expected output phía trên ta sẽ phải cung cấp cho nó 2 cái input
    # Cái đầu tiên là tạo input từ cái UTxO đang nằm ở contract, và cái này chúng ta sẽ đính kèm luôn redeemer chứa thông điệp của chúng ta
    # Chú ý ở đây sẽ có 2 tham số là script_utxo và script nó là yêu cầu của cái hàm add_script_input, nên ta sẽ cần cấp cho nó cả 2 tham số này
    builder.add_script_input(
        utxo=script_utxo,
        script=script, 
        redeemer=redeemer,
    )

    # Cái thứ 2 là tạo input thường từ ví người dùng để trả phí giao dịch
    builder.add_input_address(receiver_address)

    # Sau khi đã có input và output rồi thì chúng ta sẽ build transaction và submit nó lên mạng lưới
    builder.required_signers = [owner_key_hash]  # trước khi submit chúng ta sẽ cần cung cấp thêm chữ ký của owner để validator có thể kiểm tra signer nếu cần
    signed_tx = builder.build_and_sign(
        signing_keys=[signing_key],
        change_address=receiver_address,
    )

    # Và cuối cùng là submit giao dịch lên mạng lưới
    context.submit_tx(signed_tx.to_cbor()) # transaction phải được submit dưới dạng cbor, nên chúng ta sẽ convert nó sang cbor trước khi submit

    # Như vậy là chúng ta đã define ra được logic chính cần thực hiện
    # Bây giờ mình sẽ thực hiện tách hàm và provide cho nó các tham số cần thiết

if __name__ == "__main__":
    main()

# Chúng ta sẽ tách ra cái hàm unlock tên là unlock và truyền vào các tham số cần thiết 
# Thì ở đây mình có tạo sẵn rồi ý tưởng của nó vẫn vậy vẫn là chúng ta gom cái logic vừa define ở trên vào trong hàm unlock, 
# và truyền vào các tham số cần thiết để nó có thể thực hiện được nhiệm vụ của mình
def unlock(
    script_utxo: UTxO, 
    script: PlutusV3Script,
    redeemer: Redeemer,
    signing_key: PaymentExtendedSigningKey,
    owner_key_hash: VerificationKeyHash,
    receiver_address: Address,
    context: BlockFrostChainContext,
) -> TransactionId:
    # Khởi tạo transaction builder
    builder = TransactionBuilder(context=context)

    builder.add_output(
        TransactionOutput(
            address=receiver_address,
            amount=script_utxo.output.amount.coin,
        )
    )

    builder.add_script_input(
        utxo=script_utxo,
        script=script,
        redeemer=redeemer,
    )
    builder.add_input_address(receiver_address)

    builder.required_signers = [owner_key_hash]
    signed_tx = builder.build_and_sign(
        signing_keys=[signing_key],
        change_address=receiver_address,
    )

    context.submit_tx(signed_tx.to_cbor())
    return signed_tx.id # Ngoài ra mình trả về mã giao dịch ở đây để chúng ta có thể check trên blockchain sau khi chạy

# Như vậy là hàm main chúng ta sẽ còn là 
def main() -> None:
    tx_hash = unlock(
        script_utxo=script_utxo,
        script=validator["script"],
        redeemer=redeemer,
        signing_key=signing_key,
        owner_key_hash=owner_key_hash,
        receiver_address=wallet_address,
        context=context,
    )

# Bây giờ mình sẽ xử lý để lấy ra được các tham số truyền vào phía trên
def main() -> None:
    # Đầu tiên là context chúng ta vẫn sẽ lấy nó từ blockfrost thôi
    context = BlockFrostChainContext(
        project_id=blockfrost_project_id, # Tham số này ta sẽ lấy từ file .env như phần lock
        base_url="https://cardano-preview.blockfrost.io/api/",
    )

     # Lấy signing key và địa chỉ ví từ mnemonic
     # Cũng giống như phần lock thôi nên mình sẽ cop cái hàm của nó sang đây nhé
     # Thật ra để chuẩn chỉ thì những logic có thể tái sử dụng cta sẽ nên viết nó ra 1 file riêng để các phàn dùng tới inport vào sẽ tránh được việc duplicate code
     # Tuy nhiên để đơn giản và phù hợp với mục đích truyền đạt thì mình sẽ copy trực tiêp cái hàm này sang đây luôn
    signing_key, wallet_address = get_signing_key_and_address_from_mnemonic(mnemonic)
    #(Copy hàm xang)

    # Tiếp théo chúng ta cũng sẽ đọc validator, ở đây nó chỉ khác một chút là mình sẽ lấy ra thêm thằng script nữa nên sẽ điều chỉnh một chút
    validator = read_validator()

    # Build ra đối tượng địa chỉ hợp đồng cũng vậy 
    contract_address = Address(
        payment_part=validator["script_hash"],
        network=Network.TESTNET,
    )

    # Ok ở đây có một thằng nữa chúng ta cần để ý là script_utxo
    # Để lấy được cái script_utxo này thì chúng ta sẽ cần lấy ra được chính xác cái UTxO muốn tạo input
    # Chúng ta sẽ viết riêng cái hàm này ra đi, và chúng ta sẽ tìm chính xác cái UTxO này qua mã giao dịch nhé
    script_utxo = find_script_utxo(
        context=context,
        tx_hash=lock_tx_hash,
        contract_address=contract_address,
    )

# Về cái hàm này thì mình expect những tham số truyền vòa như trên 
def find_script_utxo(
    context: BlockFrostChainContext,
    tx_hash: str,
    contract_address: Address,
) -> UTxO:
    for utxo in context.utxos(str(contract_address)): # duyệt các utxos có trong contract và lấy ra cái utxo có transaction id trùng với tx hash của giao dịch lock trước đó,
        if str(utxo.input.transaction_id) == tx_hash:
            return utxo

    raise ValueError(f"UTxO not found for transaction {tx_hash}") # nếu ko tồn tại ta tạm trả ra lỗi ntn

# Vây là cơ bản chúng ta đã có được tham số script_utxo

def main() -> None:
    ...
    # tiếp đến chúng ta sẽ xử lý tham số owner_key_hash
    # Thì khá đơn giản vì chúng ta đã lấy được signing key rồi thì chúng ta có thể lấy được verification key hash từ signing key này luôn
    owner_key_hash = signing_key.to_verification_key().hash()

    # Còn tham số redeemer thì chúng ta sẽ tạo ra một redeemer mới có chứa thông điệp muốn gửi kèm input
    redeemer = HelloWorldRedeemer(message="Hello from unlock script!")


#Với cái redeemer này chúng ta cũng sẽ tạo 1 class  là HelloWorldRedeemer 
# THoogn điệp truyền ddi ta vẫn sẽ để dạng bytes và CONSTR_ID = 0
@dataclass    
class HelloWorldRedeemer(PlutusData):
    CONSTR_ID = 0
    msg: bytes 

def main() -> None:
    ...
    # Như vậy là chúng ta đã có đủ các tham số cần thiết để gọi hàm unlock rồi

     # Bây giờ trước khi gọi hàm chúng ta có thể print ra 1 chút để kiểm tra
     
    # Ok và mình muốn sau khi unlock thành công thì sẽ trả ra cho 1 một cái mã giao dịch để mình kiểm tra trên blockchain
    print(f"https://preview.cexplorer.io/tx/{tx_hash}")