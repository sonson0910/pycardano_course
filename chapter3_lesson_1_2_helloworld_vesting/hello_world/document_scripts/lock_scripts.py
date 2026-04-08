# đầu tiên chúng ta sẽ tạo một thư mục app: sẽ là nơi chứa code offchain
# Và sẽ có 2 việc là lock và unlock, nên mình sẽ tạo 2 file lock.py và unlock.py
# Chúng ta sẽ xử lý lock trước
# Viết code python thì chúng ta đúng là chỉ cần viết từu trên xuống dưới là nó có thể chạy dược, 
# nhưng để code có cấu trúc hơn, dễ đọc hơn, hơn thì mình sẽ dùng và viết hàm main như một entry point, và sẽ gọi các hàm khác từ main

def main() -> None:
    # Ok thì mục đích của chúng ra sẽ là tạo ra 1 transaction để lock 1 ADA vào contract
    # Để khởi tạo 1 trasaction thì chúng ta sẽ có lệnh
    builder = TransactionBuilder(context=context)

    # Sau đó thì sẽ thêm những gì mà chúng ta muốn tạo ra trên cái transaction đó
    # Như mình đã nói về mặt lý thuyết trước đó là chũng ta sẽ tạo ra 1 cái UTxO trên cái mã hợp đồng, và UTxO này sẽ chứa số tiến muốn lock và datum
    builder.add_output(
        TransactionOutput(
            address=<Địa chỉ hợp đồng>, # Địa chỉ mà chúng ta muốn tạo ra UTxO trên đó, ở đây sẽ là địa chỉ của contract
            amount=<Số ADA muốn lock>,# Số ADA muốn lock vào contract
            datum=<datum gồm public key của mình>, # Datum muốn đính kèm vào UTxO đó
        )
    )

    # Phía trên nó là cái output mà chúng ta expect là sẽ tạo ra được đúng k
    # Và giờ chúng ra sẽ cần phải có input để trả phí cho giao dịch, và input này sẽ được lấy từ ví của chúng ta
    builder.add_input_address(<Địa chỉ ví của chúng ta>)

    # Sau khi đã có input và output rồi thì chúng ta sẽ build transaction và submit nó lên mạng lưới
    signed_tx = builder.build_and_sign(
        signing_keys=[<Khóa dùng để ký giao dịch>], # Khóa dùng để ký giao dịch, ở đây sẽ là khóa của ví chúng ta, nó như kiểu cai mật khẩu
        change_address=<Địa chỉ ví của chúng ta>, # Địa chỉ ví của chúng ta để nhận lại tiền thừa nếu có
    )

    # Và cuối cùng là submit giao dịch lên mạng lưới
    context.submit_tx(signed_tx.to_cbor()) # transaction phải được submit dưới dạng cbor, nên chúng ta sẽ convert nó sang cbor trước khi submit
    
    # Phía trên là các logic chính mà mình cần thực hiện để lock được tiền vào hợp đồng, căn bản nó chỉ chỉ có vậy thôi, cũng ko có gì khó đúng không
    # Việc chính chúng ta đã define ra được rồi, giờ chúng ta chỉ cần cung cấp đúng các tham số phía trên và chạy là ok

if __name__ == "__main__":
    main()

# Để dễ hơn thì mình sẽ gom cái logic chính kia vào 1 hàm riêng gọi là hàm lock đi
# đó thì mình sẽ chỉ truyền vào những param cần thiết thôi, còn việc các param đó lấy từ đâu ra thifminhf sẽ xử lý ở hàm main
def lock(
    amount: int,
    contract_address: Address,
    datum: PlutusData,
    signing_key: PaymentExtendedSigningKey,
    sender_address: Address,
    context: BlockFrostChainContext,
):
    builder = TransactionBuilder(context=context)
    builder.add_input_address(sender_address)
    builder.add_output(
        TransactionOutput(
            address=contract_address,
            amount=amount,
            datum=datum,
        )
    )

    signed_tx = builder.build_and_sign(
        signing_keys=[signing_key],
        change_address=sender_address,
    )
    context.submit_tx(signed_tx.to_cbor())
    return signed_tx.id # Ngoài ra mình trả về mã giao dịch ở đây để chúng ta có thể check trên blockchain sau khi chạy


# Ok bây giờ hàm main của chúng ta sẽ còn là kiểu ntn
def main() -> None:
    tx_hash = lock(
        amount=2_000_000,
        contract_address=contract_address,
        datum=datum,
        signing_key=signing_key,
        sender_address=wallet_address,
        context=context,
    )

# Bây giờ mình sẽ xử lý để lấy ra được các tham số truyền vào phía trên
def main() -> None:
    # Đầu tiên là context: nó là cái kết nối để chúng ta có thể tương tác với blockchain, 
    # ở chúng ta sẽ dùng API của Blockfrost để kết nối nên chúng ta sẽ lấy như sau
    context = BlockFrostChainContext(
        #Chúng ta sẽ cần truyên vào cái key của bloackfrost ở đây, chúng ta có thể lấy free 
        # Với cái key thì mình sẽ tạo 1 file .env để lưu trữ cái key này, thì với file env lay lát mình sẽ điền key của mình vào trc khi chạy
        # Ok thì file env của mình sé có dạng như sau các bạn có thể xem qua sample nha
        project_id= <>,

        # Đây là url của mạng preview testnet, chúng ta sẽ dùng mạng này để test, các bạn nhớ để ý để ko submit nhầm mạng
        base_url="https://cardano-preview.blockfrost.io/api/", 
    )

    # tiếp đến là signing_key và wallet_address 
    # Cái này nó chính là khóa và địa chỉ ví của chúng ta, thì chúng ta sẽ láy được nó từ cái mnemonic, Mnemonic ở đây chính là cụm từ khôi phục vílà chuỗi 12 từ hoặc 24 từ.
    # cái mnemonic này cũng sensitive nen mình cx sẽ để vào file .env luôn
    # Với cái này thì mình sẽ viết 1 hàm khác để đọc là extract ra đi, ko thì hàm main nó bị dài quá
    # chúng ta sẽ viết tên hàm ntn và cho truyền vào cái mnemonic từ env vào đó
    # Ý tưởng chung là: từ một mnemonic, mình có thể dựng lại cả ví, rồi từ ví đó derive ra các key cần thiết.
    # Bởi từ cái mnemonic mình có thể lấy ra cả signing_key và wallet_address luôn nên mình sẽ trả về cả 2 cái này
    signing_key, wallet_address = get_signing_key_and_address_from_mnemonic(mnemonic)


# Bây giwof mình sẽ viết cái hàm này 
def get_signing_key_and_address_from_mnemonic(mnemonic: str):
    # Mình lấy mnemonic và tạo ra một HD wallet. HD wallet có thể hiểu đơn giản là một ví dạng cây.\
    # Từ một gốc duy nhất là mnemonic, mình có thể đi theo nhiều nhánh khác nhau để lấy ra các key khác nhau.
    #Nói dễ hiểu hơn:
    # mnemonic là hạt giống
    # wallet là cái cây mọc lên từ hạt đó
    # lát nữa mình sẽ đi vào từng nhánh của cây để lấy đúng key mình cần
    wallet = HDWallet.from_mnemonic(mnemonic)

    # Tiếp theo mình derive ra nhánh payment "m/1852'/1815'/0'/0/0" Lúc mới nhìn thì nó khó hiểu, nhưng cứ hiểu đơn giản đây là đường dẫn để đi tới đúng key.
    # Mục đích của lênh này là  Từ ví gốc, hãy đi tới payment key đầu tiên của account đầu tiên.
    payment_wallet = wallet.derive_from_path("m/1852'/1815'/0'/0/0")

    # Sau khi đã có nhánh payment rồi, mình chuyển nó thành payment signing key
    # Signing key ở đây là private key.
    # Đây là thứ mình dùng để ký giao dịch, tức là chứng minh mình có quyền tiêu UTxO thuộc ví này.
    payment_signing_key = PaymentExtendedSigningKey.from_hdwallet(payment_wallet)

    # Bây giờ từ private key, mình tạo ra public key tương ứng.
    # Trong Cardano hay trong crypto nói chung:signing key là private key, verification key là public key
    # Private key thì dùng để ký, Public key thì dùng để xác minh chữ ký, hoặc tạo ra address.
    # Ở đây mình cần public key vì lát nữa mình sẽ lấy hash của nó để build địa chỉ ví.
    payment_verification_key = payment_signing_key.to_verification_key()

    # Tiếp theo là phần stake key.
    # Cũng derive từ cùng ví gốc, nhưng lần này path khác một chút "m/1852'/1815'/0'/2/0" Điểm khác quan trọng nhất là con số 2
    # Nghĩa là thay vì lấy payment key, mình đang lấy stake key đầu tiên của account đầu tiên.
    stake_wallet = wallet.derive_from_path("m/1852'/1815'/0'/2/0")

    # tạo stake signing key và verification key
    # Phần này gần như y chang payment key.
    # Đầu tiên mình tạo ra stake signing key, tức là private key cho phần stake.
    # Sau đó từ nó tạo ra stake verification key, tức là public key.
    # Trong hàm này, stake signing key không được return ra ngoài, vì mục tiêu chính của mình hiện tại chỉ là:
    # cần payment signing key để ký giao dịch
    # cần stake verification key để gắn vào địa chỉ ví
    # Nói cách khác, ở đây mình dùng stake key chủ yếu để build ra địa chỉ chuẩn Cardano có cả phần staking
    stake_signing_key = StakeExtendedSigningKey.from_hdwallet(stake_wallet)
    stake_verification_key = stake_signing_key.to_verification_key()

    # Cuối cùng là tạo địa chỉ ví.
    # Một địa chỉ Cardano thường gồm: phần payment và phần staking.
    # Ở đây mình không nhét trực tiếp public key vào address, mà lấy hash của public key
    wallet_address = Address(
        payment_part=payment_verification_key.hash(),
        staking_part=stake_verification_key.hash(),
        network=Network.TESTNET,
    )

    return payment_signing_key, wallet_address

# OK Như vậy là chũng ta đã lấy được các thông tham số liên quan đến signing_key và wallet_address rồi
# Quy trở lại với hàm main
def main() -> None:
    ...
    # Chúng ta sẽ lấy ra 1 tham số nữa là contract_address
    # Cái này như mình có nói từ trước là khi chúng ta buil hợp đồng sẽ có 1 file plutus.json được tọa ra
    # chúng tra sẽ extract thông tin từ file này ra để sử dụng, thì đúng vậy ở đây mình sẽ dùng nó để lấy ra được cái địa chỉ hợp đồng nha
    # Nó sẽ đơn giản là hàm chũng ta đọc file và lấy data thôi nên mình sẽ paste luôn vào sau đó giai thích qua cho ác bạn nhé
    # Ở đây chúng ta nên tách cái logic đọc file ra 1 hàm, ta sẽ lấy được cái script_hash từ file plutus.json, và từ cái script_hash này ta mới buil ra được địa chỉ hợp đồng
    script_hash = read_script_hash()

    # Và để lấy ra cái đối tượng Address để truyền vòa hàm lock ta sẽ cần
    contract_address = Address(
        payment_part=script_hash,
        network=Network.TESTNET,
    )

    # OK bnaya giờ mình sẽ xử lý cái hmaf read_script_hash nhé

# Chúng ta hiểu đơn giản là nó lấy ra cái thằng "hash" của validator đầu tiên thôi, group nó obj ScriptHash để Pycardano có thể hiểu được, và trả về cái ScriptHash đó để chúng ta dùng sau này 
def read_script_hash() -> ScriptHash:
    with open("../contract/plutus.json", "r", encoding="utf-8") as file:
        plutus_json = json.load(file)

    validator_data = plutus_json["validators"][0]
    return ScriptHash(bytes.fromhex(validator_data["hash"]))

# Như vậy là chúng ta đã có được địa chỉ hợp đồng rồi, tiếp theo là datum
# Datum như ta đã thống nhất từ trước với nhau nó sẽ chỉ bao gồm public key hash của người lock, tức là owner
# như vậy thì ta sẽ tạo class model cho thằng datum này trước
# đây là datum dùng cho contract Hello World: class này kế thừa từ PlutusData (các bạn chú ý kế thừa thằng này để PyCardano có thể serialize thành Plutus datum để đưa lên chain)

@dataclass
class HelloWorldDatum(PlutusData):
    # CONSTR_ID dùng để cho PyCardano biết object này khi encode sang Plutus Data
    # sẽ mang constructor nào.
    # Trong smart contract, một kiểu dữ liệu có thể có một hoặc nhiều constructor.
    # pub type Datum {
        # Owner { owner: VerificationKeyHash }
        # Admin { admin: VerificationKeyHash }
    # }
    #Lúc này Datum không còn chỉ có 1 shape nữa, mà có 2 shape khác nhau:
    # một dạng là Owner
    # một dạng là Admin
    # Thì khi encode sang Plutus Data, mỗi constructor sẽ có một id riêng, thường là:
    # Owner → 0
    # Admin → 1
    # Mỗi constructor sẽ được đánh số từ 0, 1, 2, ...
    # Ở ví dụ này, datum của chúng ta chỉ có đúng một dạng duy nhất,
    # tức là chỉ có một constructor, nên constructor đó sẽ mang id là 0.
    CONSTR_ID = 0
    owner: bytes # Ở đây mình để owner là bytes, Kiểu của nó là bytes, vì public key hash thực chất là một dãy bytes

# QUay lại với hàm main, cúng ta sẽ build được datum như sau
def main() -> None:
    ...
    # Build datum với owner là payment key hash của chúng ta
    owner = signing_key.to_verification_key().hash() # Lấy payment key hash để làm owner, vì contract sẽ check owner này khi unlock
    datum = HelloWorldDatum(owner=owner.to_primitive()), # to_primitive() sẽ trả về dạng bytes để phù hợp với kiểu dữ liệu trên chuỗi

    # Ok còn số lượng ADA mình muốn lock ở đây mình muốn là 2ADA, thì mình sẽ truyền vào 2_000_000 (vì đơn vị của Cardano là lovelace, 1 ADA = 1_000_000 lovelace)
    # Như vậy là chúng ta đã có đủ các tham số cần thiết để gọi hàm lock rồi

    # Bây giờ trước khi gọi hàm chúng ta có thể print ra 1 chút để kiểm tra
    ...
    # Ok và mình muốn sau khi lock thành công thì sẽ trả ra cho 1 một cái mã giao dịch để mình kiểm tra trên blockchain
       print(f"https://preview.cexplorer.io/tx/{tx_hash}")
       
    # CHúng ta có thể kiểm tra, như vậy là với giao dịch này thì mình đã lock thành công 2ADA vào cái địa chỉ này, như các bạn thấy nó nhiwuwf hơn 2ADA 12 chút vì mình  cần chi trả thêm cho phí giao dịch nữa
    
# Như vậy là chúng ta đã hoàn thành phần lock rồi, phần unlock sẽ khó hơn một chút vì nó sẽ có thêm phần redeemer vào để truyền vào khi spend, nhưng về logic thì cũng tương tự thôi, chúng ta sẽ cùng nhau xử lý phần unlock ở file unlock.py nhé 

