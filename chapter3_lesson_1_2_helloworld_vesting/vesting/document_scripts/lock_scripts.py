# Chúng ta sẽ đến với phần code offchain nha
# Tạo file lock.py, unlock.py 
# env
# Chúng ta sẽ bắt đầu với action lock nha
# Lock thì nó vẫn là logic thêm UTxO trên địa chỉ hợp đồng, kèm datum nên căn bản nó không có gì khác so với vD hello world cả
# Điểm khác biệt ở đây là chúng ta sẽ phải tạo ra datum với đúng format mà hợp đồng yêu cầu,
# Vì nó khá tương tự nên ta sẽ copy code bên hello world qua và sửa một chút đoạn datum nha

# Đầu tiên mình sẽ xem qua hàm lock, nó vẫn sẽ bao gồm những tham số , logic code như vậy nhé
# Ở đây như mình có nói là chỉ có đoạn datum ta sẽ xư lý lại
# Thì mình sẽ update datum cũ một chút, 
# đổi tên, thêm 1 trường beneficiary để lưu public key của người được ủy quyên và lock  ultil để lưu thời điểm được phép
# Quay lại hàm main 
def main() -> None:
    ...
    # ở đây có 2 mnemonic là của owner và beneficiary, nên mình sẽ đổi tên cái biến này lại cho dễ đọc nhé
    owner_mnemonic = os.environ["OWNER_MNEMONIC"]
    beneficiary_mnemonic = os.environ["BENEFICIARY_MNEMONIC"]
    # Các bạn nhớ là để test đc thì ta sẽ cần 1 ví nữa để là BENEFICIARY_MNEMONIC lưu trong file env
    ...
    # Sau đó ngời lấy các thông tin key address của owner thì mình cũng sẽ lấy cho beneficiary luôn nhé
    beneficiary_signing_key, beneficiary_address = (
        get_signing_key_and_address_from_mnemonic(beneficiary_mnemonic)
    )
    # ĐỔi lại tên biên các phàn liên quan

    # Lấy ra luôn public key hash của benificiary ở đây luôn, để lát mình lưu vào datum
    beneficiary = beneficiary_signing_key.to_verification_key().hash()

    # Và với tham số lock_until của datum thì ta sẽ set nó là 1 phút kể từ thời điểm chạy script. Tức là mình muốn lát mình unlock nó sẽ đượt luôn nên mình sẽ đặt một thời điểm sớm 
    # sau này khi chạy thực tế thì mình sẽ set lock_until là 1 timestamp cụ thể nào đó trong tương lai mà mình muốn
    lock_until = int(
        (datetime.now(timezone.utc) + timedelta(minutes=1)).timestamp() * 1000
    )

    # đã đủ các thông tin thì ta sẽ có datum như sau:
    datum = VestingDatum(
        lock_until=lock_until,
        owner=owner.to_primitive(), #to_primitive() sẽ trả về dạng bytes để phù hợp với kiểu dữ liệu trên blockchain đã được định nghĩa
        beneficiary=beneficiary.to_primitive(),
    )

    # Mình sẽ đổi sang lock 3 ADA đi cho mới

    # Ok như vậy có vẻ như đã đủ thông tin để chạy rồi bây giờ để mình nhìn qu một lượt xem còn vấn đề gì k nhé
    # Như vậy có vẻ ổn rồi, bây giwof mình sẽ chạy lệnh để test nhé