use aiken/collection/list
use aiken/crypto.{VerificationKeyHash}
use cardano/script_context.{ScriptContext}
use cardano/transaction.{OutputReference, Transaction}

// Mình comment lại vào đây những gì cta cần xây dựng trong hợp đồng hello_world.ak 
// để cta có thể đối chiếu được các bước cần thực hiện
// 1. Loại hợp đồng spend
// 2. Người lock và người unlock phải là 1 người
// 3. Phải truyền đúng thông điệp "Hello, World!"


// Đầu tiên Loại hợp đồng spend
// Với hợp đồng thông minh trong aiken thì trước hết ta cần phải định nghĩa khối validator bằng cái từ khóa validator, 
// sau đó là tên của nó, ở đây mình sẽ để tên nó là hello_world
// Thì bên trong cái khối validator này chúng ta có thể xây dựng các hợp đồng 
// như mint, spend, withdraw vân vân thì chú ý ở đây là mình muốn xây dựng loại nào là phải dùng đúng cái hàm mà aiken họ định nghĩa ra: 
// cái này họ cũng có định nghĩa rõ trong validator có những hàm nào, và các hàm có những tham số nào: các bạn có thể xem ở đây
// Và mình sẽ như kiểu overide lại cái của người ta sau đó viết logic của mình phía trong

// Ở đây cta cần spend thì sta sẽ cần overide lại cái hàm spend của aiken kiểu như thế này:
 spend(datum: Option<MyDatum>, redeemer: MySpendRedeemer, utxo: OutputReference, self: Transaction) {
    todo @"spend logic goes here"
  }
// Ở đây nó có cái kiểu MyDatum và  MySpendRedeemer mình sẽ phải định nghĩa lại nó để nó phù hợp với logic của mình,
// thì ở đây mình sẽ định nghĩa lại nó như sau (mình muốn cái datum này nó sẽ chứa thông tin của người lock,
// còn redeemer sẽ chứa thông điệp mà mình muốn truyền vào khi unlock)
pub type Datum {
  owner: VerificationKeyHash,
}
 
pub type Redeemer {
  msg: ByteArray,
}

validator hello_world {
  spend(
    datum: Option<Datum>,
    redeemer: Redeemer,
    _own_ref: OutputReference,
    self: Transaction,
  ) {
    // Chúng ta sẽ xử lý cái logic "Người lock và người unlock phải là 1 người"
    // Thì câu hỏi đặt ra là chũng ta sẽ lấy data của người lock và người unlock ở đâu trong phạm phi của cái hợp đồng này
    // Thì đối với data của người lock: 
    // + thì khi lock bản chất là ta sẽ tạo ra 1 cái UTxO cho cái hợp đồng này, thì lúc đấy mình sẽ đính kèm theo 1 cái datum trong đó
    // + Và ở trong cái hàm spend nó có cung cấp cho ta 1 tham số để lấy ra cái datum đó là cái datum này, thì ta đã có data của người lock nhé
    // Tuy nhiên thì như bạn thấy thì cái datum này mình vẫn chưa định nghĩa kiểu cho nó thì mình sẽ define nó trước gồm ownwer, 
    // kiểu VerificationKeyHash nghãi là cái public key của người lock, mình sẽ dùng public key để so sánh
    
    // Còn đối với data của người unlock:
    // + thì khi unlock bản chất là ta sẽ tạo ra 1 cái giao dịch để chi tiêu cái UTxO mà ta đã lock ở trên 
    //  thì thực hiện giao dịch thì ta sẽ láy đượng thông tin người kí giao dịch đó ở trong cái transaction, 
    // thì ở trong cái hàm spend nó cũng có cung cấp cho ta 1 tham số để lấy ra cái transaction đó là cái self này, thì ta đã có public key của người unlock nhé
    
    // Ok ý tưởng nó là nt như vậy, thì bây giờ mình sẽ đi vào code để thực hiện nó nhé
    // Đầu tiên mình sẽ lấy data của người lock ra từ cái datum này, thì
    // Trong Aiken, tham số datum của spend không phải lúc nào cũng có nên bạn để ý họ để cái Option, 
    // vì trên Cardano ai gửi tiền đến địa chỉ hợp đồng cũng có thể không đính kèm datum.
    // Nhưng mình yêu cầu UTxO này bắt buộc phải có datum, và datum phải đúng format Datum, rồi mới lấy thông tin người lock ra
    // Nên ta sẽ có lện sau: lệnh này sẽ expect là datum phải có kiểu như kia, nếu có nó cũng sẽ giải nén ra được owner, nếu không thì sẽ trả về false luôn
    expect Some(Datum { owner }) = datum

    //Sau khi lấy được owner từ datum, mình sẽ check người ký transaction có đúng owner không → đảm bảo người unlock phải là người lock.
    //cái self này cho phép ta lấy ra được các chữ ký của giao dịch, thì ta sẽ check xem trong cái self này có chữ ký của owner không bằng cash dùng cái hàm list.has(..)
    let must_be_signed = list.has(self.extra_signatories, owner)

    // Ok vừa rồi cta vừa check người unlock có phải là người lock không, vừa rồi cta cũng check xem thông điệp có phải là "Hello, World!" không
    // Đơn giản thôi như mình đã nói khi unlock thì mình sẽ tạo ra 1 cái redeemer để truyền vào,Và ở đây spend cũng cung cấp 1 tham số để lấy ra cái redeemer đó là cái redeemer này, 
    // thì ta chỉ cần so sánh 
    let must_say_hello = redeemer.msg == "Hello, World!"
    
    must_say_hello && must_be_signed
    // Ok logic căn bản nó là như vậy nhưng trước đó ta nên định nghĩa 
    // cái Datum và Redeemer chỉ chứa các tham số mà chũng ta muốn check
  }
}