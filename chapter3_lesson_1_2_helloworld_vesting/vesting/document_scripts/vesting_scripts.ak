// Bây giờ chúng ta sẽ cùng đến với phần coding 
// Ở đây mình có tạo sẵn môi trưởng ảo venv và activate nó để tiết kiệm thời gian, các bạn không nhớ cú pháp có thể xem lại hướng dẫn trước đó của mình nha
// Chúng ta sẽ bắt đầu ta sẽ xử lý phần hợp đồng thông minh trước
// Mình sẽ cần tạo dự án Aiken mới bằng câu lệnh quen thuộc
// aiken new aiken-lang/contract

// Và như mình có đề cập thì ở trong bài hôm nay chúng ta sẽ dùng thư viện vodka để hỗ trợ viết hợp đồng thông minh,
// vì vậy chúng ta sẽ cần cài đặt thư viện này vào dự án Aiken của mình
// Bằng cách thêm thư viện vào file toml bằng cách thêm đoạn code sau
[[dependencies]]
name = "sidan-lab/vodka"
version = "0.1.1-beta"
source = "github"
// Như vậy là chúng ta đã thêm thư viện vodka vào dự án Aiken của mình rồi,
// bây giờ chúng ta sẽ bắt đầu viết hợp đồng thông minh

// Ok thì như thường lệ chúng ta vẫn sẽ viết code trong cái file validator này nhé
// Đổi tên thành vesting.ak cho nó dễ nhìn

// Đầu tiên mình vẫn sẽ note lại những gì hợp đồng vesting này cần làm:
// 1. Loại hợp đồng là spend
// 2. Owner có thể lấy lại tiền bất cứ lúc nào
// 3. Beneficiary chỉ được lấy tiền sau thời điểm lock_until

// Trước hết, vì đây là hợp đồng dạng spend nên ta sẽ định nghĩa validator
// và override lại hàm spend đúng theo entrypoint mà Aiken cung cấp.
// Và chúng ta cũng sẽ phải định nghĩa ra kiểu của Datum 

// Datum sẽ chứa toàn bộ thông tin cần kiểm tra:
// + lock_until: thời điểm mở khóa -> kiểu int mình muốn lưu nó dưới dạng timestamp
// + owner: public key hash của người lock -> kiểu VerificationKeyHash
// + beneficiary: public key hash của người được ủy quyền -> kiểu VerificationKeyHash
pub type VestingDatum {
  lock_until: Int,
  owner: VerificationKeyHash,
  beneficiary: VerificationKeyHash,
}

// Redeemer thì ở đây mình không cần dùng đến nên mình sẽ để nó là kiểu Data cho nó linh hoạt. 
// Và biến nào xác định là không dùng thì mình sẽ đặt tên với dấu _ để thể hiện điều đó nhé, 
// ở đây ta ko cần dùng đến output reference luôn nên mình cx sẽ đặt tên với dấu _ luôn nhé
// còn tx ở đây chứa các thông tin giao dịch và mình có thể dùng đẻ truy vấn các thông tin liên quan đến người kí, .. dể so sanh 
validator vesting {
  spend(
    datum_opt: Option<VestingDatum>,
    _redeemer: Data,
    _input: OutputReference,
    tx: Transaction,
  ) {

    // Vì datum trong spend có kiểu Option, nên trước tiên ta cần ép nó
    // phải tồn tại và đúng format VestingDatum thì mới lấy dữ liệu ra để check tiếp.
    // Cái này thì cũng khá giống bên hello world r nhỉ, 
    // bên hello world mình sẽ extract thằng owner ra luôn còn ở đay mình sẽ lấy cả obj của nso ra rồi truy vấn , tùy nha chúng ta có thể xử lý theo các cách khác nhau
    expect Some(datum) = datum_opt

    // Sau dòng này ta sẽ có:
    // + datum.lock_until
    // + datum.owner
    // + datum.beneficiary

    // Bây giờ đến phần logic chính 
    // Logic của contract này gồm 2 nhánh hợp lệ:
    // 1. Owner ký giao dịch -> được lấy lại tiền bất cứ lúc nào
    // 2. Beneficiary ký giao dịch và giao dịch diễn ra sau lock_until -> được nhận tiền
    // Chúng ta sẽ or block và and block của aiken để thực hiện điều này
    or {
      // Nhánh 1: owner ký
      // Hàm này dùng để kiểm tra: một public key hash nào đó có nằm trong danh sách người ký giao dịch không.
      // Chúng ta có thể thấy với ví dụ hello world thì chúng ta có thể dùng hàm list.has để so sánh cũng đc nha
      key_signed(tx.extra_signatories, datum.owner),

      // Nhánh 2: beneficiary ký và đã qua thời gian khóa
      and {
        key_signed(tx.extra_signatories, datum.beneficiary),
        valid_after(tx.validity_range, datum.lock_until), 
        // validity_range cho biết là giao dịch này chỉ có hiệu lực sau một thời điểm nào đó,
        // valid_after: nó sẽ kieeurm tra xem cái thời điểm validity_range báo là hợp lệ nó có lớn hơn lock_until hay không, 
        //nếu lớn hơn thì có nghĩa là giao dịch này diễn ra sau lock_until và sẽ được phép thực hiện
        // Nhiều bạn chắc nhàm tưởng validity_range là thời gian các bạn submit giao dịch nhưng ko phải nha,
        // nó chỉ là một ràng buộc để đảm bảo giao dịch này chỉ có hiệu lực sau một thời điểm nào đó thôi,
      },
    }
  }
}



// OK bây giwof chúng ta sẽ import những thư viện cần dùng
use cardano/transaction.{OutputReference, Transaction}
use vodka_extra_signatories.{key_signed}
use vodka_validity_range.{valid_after}
use aiken/crypto.{VerificationKeyHash}

// Chúng ta sẽ chạy lệnh aiken build để check 
// Ok như vậy là chúng ta đã build xong phần hợp đồng, bây giwof chúng ta sẽ chuyển sang phàn tích hợp bên code offchain
