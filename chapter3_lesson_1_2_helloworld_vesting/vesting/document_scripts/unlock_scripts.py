# bây giờ chúng ta sẽ đến với action unlock hợp đồng nha
# Ở đây sẽ có 2 đối tượng có thể unlock là owner - người lock tiền vào hợp đồng
# người được ủy quyền - người được nhận tiền sau khi lock_until qua đi

# Mình vẫn sẽ draff một bản unlock để các bạn hình dung ra main flow nha
def main() -> None:
    # CHúng ta vẫn sẽ tạo ra 1 đối tượng TransactionBuilder quyen thuộc
    builder = TransactionBuilder(context=context)

    # Sau đó là add 1 cái output vào địa chỉ ví của người muốn nhận tiền
    # Ở đây có thể là 1 tỏng 2 người, nên mình sẽ để nó là 1 biến chung receiver_address
    builder.add_output(
        TransactionOutput(
            address=receiver_address,
            amount=script_utxo.output.amount.coin,
        )
    )

    # Bây giwof chúng ra sẽ add những input cần thiết 
    # Nó vẫn sẽ là tiêu UTxO từ ví người kí và đị chỉ hợp đồng giống hellowrorl thôi
    # Từ hợp đồng thì
    builder.add_script_input(
        utxo=script_utxo,
        script=script,
        redeemer=Redeemer(data=Unit()), # ở đây ta ko cần redeemer nên ta cứ gán nó cho 1 giá trị mặc định nha
    )
    # Thêm input thường từ ví người dùng để trả phí giao dịch
    builder.add_input_address(receiver_address)

    # Yêu cầu chữ ký của signer đúng với datum để validator kiểm tra
    builder.required_signers = [required_signer]

    # Đến đây thông thường như ví dụ trước ta có thể buil và submit giao dịch được rồi
    # Tuy nhiên ở đây có một điểm khác biệt nhỏ là nếu người unlock là beneficiary 
    # thì giao dịch sẽ chỉ có hiệu lực sau thời điểm lock_until
    # Nên nếu unlocker là beneficiary thì ta sẽ set validity_start 
    # Nó chính là cái giá trị min của cái khoảng validity_range ta set trong hợp đồng đó
    # validity_range = [validity_start, ...] nó sẽ kiểu ntn nha
    # Chúng ta sẽ cần cấp cho transaction thông tin này vì rõ ràng trong hợp đồng mình có ràng buộc này
    # Tuy nhiên là chỉ khi unlocker là beneficiary thôi nha, nên lát mình sẽ cần 1 cách check role hay làm thê snaof đấy mà chỉ B gửi thì mới thêm  
    builder.validity_start = validity_start

    # Sau đó thì như thường thôi, ta sẽ build và sign giao dịch, rồi submit lên mạng thôi
    signed_tx = builder.build_and_sign(
        signing_keys=[signing_key],
        change_address=receiver_address,
    )
    context.submit_tx(signed_tx.to_cbor())


# Ok bây giwof mình sẽ tach nó ra 1 cái hàm riêng nhé
def unlock(
    script_utxo: UTxO,
    script: PlutusV3Script,
    signing_key: PaymentExtendedSigningKey,
    required_signer: VerificationKeyHash,
    receiver_address: Address,
    context: BlockFrostChainContext,
    validity_start: int | None = None, # ở đây mình sẽ cho truyền thẳng validity_start vào  
) -> TransactionId:
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
        redeemer=Redeemer(data=Unit()),
    )

    builder.add_input_address(receiver_address)

    if validity_start is not None: # dưới này các bạn có thể thấy là validity_start none nghia là nó là owner nhé
        builder.validity_start = validity_start

    builder.required_signers = [required_signer]

    signed_tx = builder.build_and_sign(
        signing_keys=[signing_key],
        change_address=receiver_address,
    )

    context.submit_tx(signed_tx.to_cbor())
    return signed_tx.id

# Sau đó trong hàm main ta sẽ gọi hàm unlocl
def main() -> None:
    tx_hash = unlock(
        script_utxo=script_utxo,
        script=validator["script"],
        signing_key=signing_key,
        required_signer=required_signer,
        receiver_address=receiver_address,
        context=context,
        validity_start=validity_start,
    )

# Bay giwof thì chúng ta sẽ lấy ra các tham số cần thiết để gọi hàm unlock này 
# Trước hết thì chúng ta cũng sẽ load ra các tham số quyen thuộc tuef env
# và một biến chứa mã hợp đồng để lát chúng ta lấy ra Utxo từ nó
def main() -> None:
    lock_tx_hash = "9acde4632c110ddd4dd7545fd0995fa34a0b553fb8d5af6cb37a272a3ce59c1a"
    # Ngoài ra ta sẽ scos thêm 1 biến dùng để chỉ định người kí unlock nha nó sẽ có 2 giá trị là owner hoặc beneficiary,
    # lát ta sẽ dùng biến này để chọn tham số phù hợp cho hàm
    unlocker = "beneficiary" 

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

      # Đọc validator đã build từ contract
    validator = read_validator()

    # Tạo contract address từ script hash để tìm UTxO đang bị khóa
    contract_address = Address(
        payment_part=validator["script_hash"],
        network=Network.TESTNET,
    )

    # Tìm đúng UTxO tại contract từ tx hash của giao dịch lock trước đó
    # Hàm này ở ví dụ trước mình đã giải thích rồi nên ở đay mình sẽ cop sang dùng luôn nha
    # Giải thích lại một chút là nó sẽ tìm ra UTxO tại địa chỉ hợp đồng có tx hash trùng với giao dịch lock trước đó,
    script_utxo = find_script_utxo(
        context=context,
        tx_hash=lock_tx_hash,
        contract_address=contract_address,
    )

    # Decode datum vesting để lấy lock_until, owner, beneficiary, mục đích vẫn là lấy ra tham số để truyền vào trong hàm unlock nha
    datum = VestingDatum.from_cbor(script_utxo.output.datum.cbor)
    owner_key_hash = VerificationKeyHash(datum.owner)
    beneficiary_key_hash = VerificationKeyHash(datum.beneficiary)

    # Đến đây thì ta sec kiểm tra unlocker
    # nếu là owner thì các biến như signing_key, receiver_address, required_signer sẽ là của owner
    if unlocker == "owner":
        signing_key = owner_signing_key
        receiver_address = owner_address
        required_signer = owner_key_hash
        validity_start = None # Ở đây nếu là owner thì ta sẽ ko set validity_start vì owner có thể unlock bất cứ lúc nào mà ko cần quan tâm đến thời gian
    else:
        signing_key = beneficiary_signing_key
        receiver_address = beneficiary_address
        required_signer = beneficiary_key_hash
        # Tuy nhiên với beneficiary thì ta sẽ cần set validity_start để đảm bảo giao dịch này chỉ có hiệu lực sau lock_until
        # mình sẽ viết 1 hàm để tính toán được ta con số theo định dạng chuẩn của blockchain để có thể trueyenf vào
        validity_start = estimate_validity_start_from_unix_time(
            datum.lock_until,
            context,
        )

# Ở đay mình co viết sẵn, nó chỉ là việc quy đổi sang thời gian slot của lockchain sao cho hợp lệ
# nên mình sẽ cop và giai thích qua nhé
# contract lưu lock_until dưới dạng thời gian
# nhưng transaction lại cần validity_start theo slot
# nên hàm này lấy:
# - slot hiện tại
# - thời gian hiện tại
# - độ dài mỗi slot
# rồi ước lượng xem lock_until tương ứng với slot nào
def estimate_validity_start_from_unix_time(
    unix_time_ms: int,
    context: BlockFrostChainContext,
) -> int:
    current_slot = context.last_block_slot
    current_time_ms = int(time.time() * 1000)
    slot_length_ms = context.genesis_param.slot_length * 1000

    # Nếu lock_until đã qua rồi thì ta trả về slot hiện tại để giao dịch luôn
    if unix_time_ms <= current_time_ms:
        return current_slot

    # nếu không ta sẽ lại cần tính còn bao nhiêu ms -> đổi số đó ra slot rồi cộng vào current_slot
    remaining_ms = unix_time_ms - current_time_ms
    remaining_slots = math.ceil(remaining_ms / slot_length_ms)
    return current_slot + remaining_slots

# Đó thì như vậy là ta có thể uy đổi ra một mức thời gian hợp lệ để trueyefn vào

#quay lại vơi shamf main có vẻ đã đủ tham số rồi, để mình kiểm tra lại 1 lần nữa
# Ok mainhf sẽ in ra nếu success cái mã giao dịch
# Mình sẽ chỉ test với người được ủy quyền unlock nhé, do là với owner thì cũng giống ví dụ hello world rồi
# Mình có thể kiểm tra tiền trong ví của 2 thằng trước khi unlock nha
# Ok giwof chúng ta có thể chạy unlock
# Kiểm tra mã giao dịch + kiểm tra ví sau unlock



