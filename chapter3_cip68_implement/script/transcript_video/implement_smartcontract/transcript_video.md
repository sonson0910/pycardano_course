# Transcript bám sát video (đã sửa chính tả nhẹ)

[00:04] Xin chào mọi người. Chào mừng mọi người đã đến với video tiếp theo trong chuỗi video khóa học dạy lập trình của chúng tôi.
[00:11] Trong video này chúng ta sẽ bắt đầu triển khai ví dụ CIP-68.
[00:19] ờ mà mình đã chia sẻ khá là chi tiết trong phần lý thuyết trước đó. Thì trong các video tiếp theo chúng ta sẽ chỉ thực hiện code.
[00:31] Thì trong video này mình sẽ trực tiếp hướng dẫn các bạn từng bước ờ code triển
[00:38] khai hợp đồng thông minh. Đấy thì mặc định khi các bạn đã học đến video này
[00:45] thì mình cũng mặc định là các bạn đã biết cách tạo ra một thư mục
[00:52] Aiken trong source code của các bạn rồi nên mình sẽ không hướng dẫn lại các bạn cài Aiken như thế nào. Đấy đầu tiên thì chúng ta sẽ vào tạo thư mục luôn. Đấy.
[01:06] Ok. Chúng ta đã tạo xong thư mục Aiken dùng để code hợp đồng thông minh. Trong thư mục này nó sẽ bao gồm các cái thư mục và
[01:15] các file cần thiết để thực hiện biên dịch hợp đồng mã nguồn. Thì mình đang sử
[01:22] dụng phiên bản gọi là Aiken V1.1.19 và biên dịch sang Plutus V3. Mọi
[01:30] người chú ý để không bị lệch cú pháp so với hướng dẫn của mình nhé. Đầu tiên thì
[01:37] chúng ta sẽ vào project.
[01:44] Ok xong rồi. Chúng ta sẽ đi vào code luôn.
[01:51] Thêm một file `cip68.ak` để code hợp đồng.
[02:03] Xóa bỏ cái file có sẵn đi.
[02:06] Rồi ok thì mình sẽ tóm tắt lại một chút về các công
[02:15] việc mình sẽ thực hiện trong cái việc viết hợp đồng này thì chúng ta sẽ có hai cái hợp đồng chính mà chúng ta sẽ
[02:24] viết. Hợp đồng thứ nhất là hợp đồng dùng để mint. Tức là hợp đồng mint này nó
[02:32] sẽ tạo ra một cái minting policy script dùng để mint hoặc burn NFT,
[02:41] token theo chuẩn CIP-68 này này. Đấy thì đây chính là cách mint ra một cái
[02:50] token hay là một cái NFT trên hệ sinh thái Cardano. Đấy, trong những bài học trước đó mình cũng đã giới thiệu sơ qua
[02:59] về một số cách mint, cách đơn giản nhất là dùng native script. Đấy, thì trong bài học
[03:08] này thì chúng ta sẽ thực hiện mint theo kiểu Plutus script. Đấy.
[03:19] Và cái hợp đồng thứ hai đó là cái hợp đồng dùng để lưu trữ các UTxO chứa
[03:27] reference token mà chúng ta đã thảo luận khá là chi tiết trong phần lý
[03:35] thuyết. Đấy. Rồi. Ok. Sau khi nói xong lý thuyết rồi, chúng ta sẽ nhảy vào code. Đấy,
[03:43] đầu tiên đó là chúng ta sẽ import cái thư viện đầu tiên đó là thư viện list này. Đấy, để thực
[03:52] hiện ờ các cái công việc liên quan đến duyệt qua danh sách, các cái input hoặc
[03:59] là output. Đấy. Thứ hai là thư viện là bytearray để xử lý
[04:06] liên quan đến bytearray. Và tiếp theo là Policy ID này. Tiếp theo là thư viện liên quan đến transaction để truy cập thông tin giao dịch.
[04:18] Ok.
[04:21] Sau khi chúng ta đã import xong các cái thư viện cần thiết rồi thì mình sẽ đi vào code luôn. Trước khi code mình sẽ
[04:28] nói một chút vì đây là một khóa học mang tính chất giảng dạy.
[04:35] Chính vì thế mà chúng mình cũng cố gắng cung cấp những nội dung cốt lõi nhất để mọi người hiểu và hình dung,
[04:44] nắm được nguyên lý hoạt động của nó. Từ đó sau này khi mọi người ứng
[04:52] dụng và thực tế mọi người sẽ tạo ra những cái bài toán nó phức tạp hơn nhưng lõi của nó vẫn phải tuân theo những nguyên lý mà chúng ta chia sẻ. Chính vì
[05:02] thế mà hợp đồng thông minh của chúng ta sẽ chỉ là hợp đồng đơn giản thôi. Đấy.
[05:09] Và cái CIP-68 sẽ luôn sử dụng hai cái token mà chúng ta đã chia sẻ đó là reference token.
[05:21] Nó sẽ được lưu trữ ở cái hợp đồng store.
[05:25] Đấy. Còn cái user token là cái token mà mọi người sở hữu và user token sẽ được
[05:31] liên kết với cái reference token thông qua cái policy ID và asset name ấy. Đấy.
[05:40] Rồi ok.
[05:44] Đấy, mình cũng cung cấp thêm prefix của ref token là
[05:53] chuỗi bytes `000643b0`. Còn user token là chuỗi
[06:00] `000de140`. Đấy, rồi bắt đầu vào code rồi.
[06:13] Reference token nằm trong script
[06:20] để chứa datum.
[06:25] Còn user token nằm trong ví của người dùng để thể hiện
[06:35] quyền sở hữu
[06:43] đối với tài sản.
[06:53] Đây vẫn chỉ là những cái nội dung mình đã chia sẻ khá là chi tiết trong bài học trước đó. Đấy, không có gì mới mẻ cả.
[07:04] Rồi tiếp theo là chúng ta sẽ đầu tiên có một số kiểu dữ liệu mà chúng
[07:11] ta sẽ phải định nghĩa. Đầu tiên đó là redeemer cho hợp đồng mint và redeemer
[07:19] cho cái hợp đồng store tức là hợp đồng để chứa cái reference token đấy. Đấy và cái datum.
[07:27] Đấy đầu tiên thì chúng ta sẽ định nghĩa redeemer cho mint trước, thì chúng ta sẽ khai báo là
[07:36] MintRedeemer này. Đấy nó sẽ có hai hành động,
[07:46] hành động mint và hành động burn. Đấy.
[07:55] Tiếp theo thì redeemer mint này sẽ nhận vào tham số là token name. Đấy, tức là nó sẽ
[08:03] thực hiện mint ra một cái token với token name truyền vào.
[08:11] Còn tiếp theo là chúng ta sẽ định nghĩa redeemer cho
[08:19] hợp đồng store, tức là `SpendRedeemer`.
[08:34] Redeemer của hợp đồng store thì nó sẽ có hai hành động:
[08:41] `UpdateMetadata` hoặc `BurnReference`.
[08:49] khi burn thì chúng ta sẽ thực hiện chi tiêu UTxO,
[08:56] đấy nên chúng ta phải có cái hành động gửi lên hợp đồng thông minh để biết được đó là hành động chi tiêu đúng không?
[09:05] Đấy, chi tiêu UTxO sẽ khác với burn token nhé.
[09:13] Chi tiêu UTxO tức là mọi người chi tiêu UTxO khỏi hợp đồng. Đấy, còn burn
[09:23] token là làm nó hủy bỏ cái token trên toàn bộ chuỗi.
[09:30] Đấy, mọi người hiểu như thế. Tức là khi burn nó sẽ bao gồm hai quá trình. Quá
[09:36] trình đầu tiên đó là chi tiêu bỏ cái UTxO chứa cái reference token trên hợp đồng
[09:42] store đấy. Và hành động thứ hai là hành động chính là hủy bỏ cái token đó trên
[09:49] chuỗi. Đấy nó gồm có hai cái quá trình như vậy. Ok.
[09:57] Sau khi định nghĩa được hai cái redeemer cho hai hợp đồng rồi, chúng ta sẽ thực hiện định nghĩa datum. Đấy, đây chính là
[10:06] phần quyết định cái CIP-68 có thể cập nhật Datum được hay không này. Đấy, thì nó sẽ có một cái một số trường sau. Đầu tiên đó là Policy ID. Đấy,
[10:19] policy_id dùng để định danh token và ràng buộc đúng tài sản.
[10:29] Thứ hai là asset_name.
[10:41] Đấy.
[10:44] Policy ID và asset name
[10:54] là thông tin
[11:05] để xác định token.
[11:11] Rồi tiếp theo là một cái trường gọi là trường owner đi. Đây chính là cái public key hash của người dùng đấy.
[11:27] Tức là thêm cái này để thêm cái logic là khi người dùng ký giao dịch thì phải ký
[11:34] bằng cái ví tương ứng với public key hash được lưu trong datum này thì
[11:41] giao dịch nó mới thành công được. Tiếp theo chính là cái trường metadata. Chúng ta sẽ cập nhật cái trường này.
[11:52] Đây, metadata chính là cái kiểu như là một đối tượng để lưu trữ dữ liệu của chúng ta. Chúng ta sẽ cập nhật cái
[12:00] trường metadata này. Và cái trường version này cũng cập nhật cái này. Ok.
[12:07] Sau khi chúng ta đã khởi tạo xong, khai báo xong ba cái kiểu dữ liệu phục vụ cho
[12:14] việc viết hợp đồng thì chúng ta sẽ đi vào viết từng hợp đồng một. Thì đầu tiên
[12:21] thì chúng ta sẽ viết hợp đồng minting policy script. Đấy, chúng ta sẽ khai báo
[12:30] vẫn là dùng để tạo ra minting policy script để
[12:39] đính vào giao dịch mint thôi. Và phục vụ sau này cho burn nữa. Đấy, thì hành động này là hành động mint.
[12:49] hành động mint này với các tham số truyền vào là redeemer và transaction.
[12:58] Tiếp theo đó là lấy ra thông tin của giao dịch mint.
[13:09] Nếu như không phải hành động mint thì fail.
[13:15] Rồi trong hàm mint này mình sẽ kiểm tra theo redeemer.
[13:32] Tiếp theo kiểm tra redeemer.
[13:36] `when redeemer is`
[13:48] thì chúng ta sẽ có hai hành động,
[13:57] một là `MintToken`, hai là `BurnToken`. Nếu là `MintToken` thì
[14:03] sao? `MintToken` với tham số là token name.
[14:16] token name này.
[14:34] tham số token name.
[14:36] Đầu tiên là chúng ta sẽ phải tạo ra asset name theo chuẩn CIP-68
[14:44] thì chúng ta sẽ tạo asset name cho cái reference token.
[14:49] Đấy thì hàm `bytearray.concat` này
[14:56] chính là nối cái prefix vào cái token name để
[15:02] để định nghĩa đó là reference token. Đấy tương tự chúng ta
[15:11] sẽ tạo user token nối thêm cái prefix vào. Rồi sau khi đã
[15:19] tạo xong rồi nhá thì chúng ta sẽ thực hiện kiểm tra mint đúng số lượng token
[15:26] rồi chúng ta sẽ lấy ra
[15:31] số lượng mint
[15:42] bằng cách dùng hàm
[15:48] `assets.quantity_of`. Hàm này dùng để
[15:56] lấy ra số lượng reference token theo policy ID và reference token name
[16:05] là bao nhiêu trong giao dịch mint.
[16:12] Tiếp theo là lấy cái user amount.
[16:19] Rồi tiếp theo thì chúng ta sẽ kiểm tra giao dịch mint này phải mint đúng số lượng.
[16:30] Đấy. Ok. Mình xin nhắc lại một lần nữa nhé.
[16:39] Nếu như redeemer là hành động `MintToken` truyền vào tham số token name,
[16:46] thì chúng ta sẽ phải thực hiện xây dựng reference token name và user token name
[16:53] đấy bằng cách nối thêm các cái prefix tương ứng với từng loại token.
[17:01] Đấy, sau khi tạo token name xong, chúng ta sẽ lấy ra số lượng của hành động mint cho
[17:11] token với cái policy ID và cái reference token name tương ứng. Đấy. Và kiểm tra
[17:18] điều kiện là chỉ được phép mint đúng một ref token và một user token thôi. Đấy. Ok.
[17:28] Bước tiếp theo chúng ta sẽ viết logic cho Burn.
[17:36] Burn token cũng tương tự như vậy và cũng nhận tham số token name.
[17:47] Cũng xử lý ờ cái token name dưới dạng CIP-68 chuẩn sau đó cũng lấy ra số
[17:55] lượng và kiểm tra. Tuy nhiên khác ở burn là nó phải là -1. Ok chưa?
[18:02] Ok. Chúng ta bước sang bước tiếp theo.
[18:08] Rồi về cơ bản thì phần mint
[18:15] chỉ có logic như vậy thôi, không quá phức tạp. Đấy,
[18:29] về cơ bản phần mint thì không phức tạp như mọi người nghĩ. Nó chỉ là một
[18:35] cái hợp đồng có cái logic để tạo ra một cái policy script. Đấy,
[18:46] ok, đã xong phần hợp đồng mint nhé.
[18:51] Tiếp theo thì chúng ta sẽ vào code hợp đồng store để chứa
[18:58] các UTxO chứa reference token.
[19:08] Và thực hiện các logic update hoặc burn, thì chúng ta nhảy vào code luôn.
[19:18] Đầu tiên đó là khai báo
[19:25] đây. Khai báo validator `cip68_store` với hành động `spend`.
[19:35] `spend` này có tham số đầu tiên là datum, dùng để lấy thông tin redeemer và dữ liệu hiện tại.
[19:47] Để xem hành động là update hay burn.
[19:55] rồi lấy thông tin tham chiếu đến cái UTxO đang được spend đấy.
[20:06] Chú thích ở đây là tham chiếu đến UTxO
[20:13] đang được chi tiêu, tức là spend.
[20:23] Đấy, tiếp theo đó là transaction nhé.
[20:29] Rồi đầu tiên thì chúng ta sẽ lấy ra thông tin liên quan đến datum này.
[20:38] Lấy datum ra từ UTxO đang spend.
[20:52] Ừ, đầu tiên là lấy thông tin datum.
[21:00] Rồi đầu tiên là `expect` này.
[21:07] Tiếp theo là lấy thông tin từ datum ra.
[21:12] Tiếp theo là lấy thông tin để kiểm tra chữ ký, rồi lấy policy ID của tài sản.
[21:24] Rồi tiếp theo là lấy asset name.
[21:30] Rồi thì cái hợp đồng này,
[21:39] tức là hợp đồng store,
[21:45] được thiết kế để với action update sẽ có các điều kiện bắt buộc.
[21:55] Điều kiện thứ nhất là phải được ký bởi owner.
[22:04] Điều kiện thứ hai là input khi chi tiêu phải có reference token.
[22:14] Điều kiện thứ ba là output trả lại hợp đồng
[22:23] phải có reference token và datum mới hợp lệ.
[22:33] Đấy.
[22:40] Output trả lại đúng hợp đồng,
[22:47] có token và có datum mới.
[22:53] Datum mới thì
[23:02] chỉ được cập nhật metadata và version,
[23:07] còn policy_id, asset_name, owner phải giữ nguyên. Rồi nhé, đầu tiên thì
[23:17] chúng ta sẽ viết logic kiểm tra chữ ký trước.
[23:23] Logic kiểm tra chữ ký này khá đơn giản.
[23:27] Rồi ok, kết thúc kiểm tra chữ ký.
[23:39] Ok, xong phần này rồi nhé. Tiếp theo chúng ta viết `when redeemer is`.
[23:47] Lúc nãy có đoạn thừa thì mình xóa đi.
[23:57] Rồi viết lại từ đầu.
[24:05] `when redeemer is`
[24:12] đầu tiên là `UpdateMetadata`.
[24:18] Với `UpdateMetadata` thì đầu tiên là
[24:24] input khi chi tiêu phải có reference token, nên chúng ta phải tìm input của script.
[24:35] Tìm own input của script.
[24:42] Đầu tiên là kiểm tra input này có chứa reference token hay không.
[24:55] Rồi sau đấy thì chúng ta sẽ lấy ra
[25:05] địa chỉ của hợp đồng thông minh.
[25:19] Đấy, lấy địa chỉ của hợp đồng từ
[25:27] own input này.
[25:35] Tiếp theo thì chúng ta sẽ tạo reference token name bằng cách nối prefix vào
[25:44] `datum.asset_name`.
[25:51] Rồi tiếp theo thì chúng ta kiểm tra input có chứa ref token name hay không.
[26:02] Rồi.
[26:15] `let input_has_ref_token = assets.quantity_of(...) == 1`
[26:37] Trong `own_input.output.value`,
[26:47] theo đúng policy ID
[26:55] và reference token name, rồi kiểm tra bằng 1.
[27:06] Hàm này mục đích là kiểm tra input
[27:15] có chứa reference token name hay không.
[27:20] Rồi ok xong rồi.
[27:25] Xong phần kiểm tra input.
[27:39] Input phải chứa ref token name. Tiếp theo là kiểm tra
[27:53] output gửi lại script phải chứa
[27:59] reference token và datum mới có các trường
[28:09] được cập nhật đúng,
[28:19] còn các trường identity thì không được thay đổi.
[28:27] Đấy, chúng ta sẽ viết ra `has_valid_output` này
[28:37] bằng `list.any(tx.outputs, ...)`.
[28:49] Với từng output
[29:03] thì kiểm tra datum,
[29:14] `when output.datum is`
[29:27] `InlineDatum(data)`
[29:43] rồi `expect new_datum: CIP68Datum = data`.
[29:56] Tiếp theo kiểm tra
[30:07] output hợp lệ.
[30:22] Output phải có
[30:30] `assets.quantity_of(...) == 1`.
[30:47] Đấy. Tức là luồng của đoạn này là:
[30:55] Đầu tiên kiểm tra output gửi lên hợp đồng
[31:03] mới có chứa UTxO,
[31:08] mà UTxO mới phải chứa reference token.
[31:18] Để tránh trường hợp UTxO gửi lên hợp đồng không chứa ref token
[31:28] thì user token sẽ không liên kết đúng.
[31:35] Đấy, bước này là logic ràng buộc quan trọng.
[31:48] Ok.
[31:50] Rồi tiếp theo
[32:02] sẽ có thêm các điều kiện kiểm tra thông tin sau update.
[32:11] Một là
[32:21] output phải
[32:29] có địa chỉ output đúng địa chỉ hợp đồng store.
[32:35] Tiếp theo là output phải có ref token.
[32:44] Đấy.
[32:45] Tiếp theo là new datum.
[32:49] Policy ID phải giữ nguyên, asset name cũng phải giữ nguyên, không được thay đổi.
[33:00] Và nếu không thỏa thì fail.
[33:24] Tiếp theo là điều kiện `must_be_signed`, phải được ký bởi user tương ứng.
[33:38] Ngoài ra input phải chứa reference token và output cũng phải chứa reference token.
[33:46] Kết hợp tất cả các điều kiện này.
[33:58] Đó, đôi khi thiếu ngoặc thì sẽ lỗi.
[34:09] Đây, đúng không?
[34:16] Rồi tiếp theo là đến phần burn. Phần update xong rồi.
[34:24] Xong rồi nhé, `BurnReference`.
[34:36] Thì chúng ta chỉ cần điều kiện là phải được ký bởi owner.
[34:46] Tức là phải được ký bởi ví tương ứng với public key hash trong datum.
[34:58] Rồi đã code xong hợp đồng, giờ chúng ta check thử xem nào.
[35:07] Một lỗi. Lỗi ở đâu đây?
[35:11] Expect new datum nà. À rồi cái này là hai chấm chứ không phải bằng đâu.
[35:19] Cái này lại thiếu mất dấu ngoặc nào rồi.
[35:24] `when` mất cái ngoặc này đúng không?
[35:36] Rồi những này thừa không? Rồi đấy.
[35:58] Đâu nhỉ? `expect new_datum` này.
[36:04] Thiếu khai báo nên vẫn sai nhiều lỗi quá.
[37:03] Rồi nên bây giờ mới đúng này. Mình xin lỗi các bạn, mình hơi chủ quan trong việc
[37:13] xử lý cú pháp address.
[37:22] `script_address`
[37:33] ở output.
[37:49] rồi `expect Some(own_input)`
[37:58] input này đấy.
[38:10] `quantity_of` này.
[38:21] owner, input, output sao lại không có nhỉ?
[38:31] `list.find(tx.inputs, fn(input) { ... })`
[38:41] `input.output_reference` này.
[38:52] Rồi, script_address lấy từ own input.
[39:00] và đối chiếu với output.address.
[39:07] `input_has_ref_token` dùng `assets.quantity_of`.
[39:19] Input này với datum này có khác gì đâu nhỉ?
[39:37] `has_valid_output = list.any(...)`.
[40:11] Output này
[40:28] output này phải thỏa điều kiện.
[41:31] Rồi check lại, giờ ổn rồi.
[41:45] (đoạn nói không rõ)
[42:04] Mình vừa thêm một dấu rồi. Ok, như vậy đã check thành công.
[42:13] Rồi. Mình xin lỗi các bạn một chút về một số sự cố trong cú pháp. Mong các bạn
[42:19] thông cảm. Đấy, sau khi chúng ta sửa xong nó cũng đã check thành công rồi.
[42:25] Đấy, mình sẽ điểm lại một chút về cái hợp đồng của chúng ta. Thì chúng ta sẽ có hai cái hợp đồng chính. Hợp đồng đầu
[42:34] tiên đó là hợp đồng dùng để tạo ra minting policy script, mục đích là dùng để mint và burn token.
[42:44] Và cái hợp đồng thứ hai là hợp đồng store, tức là dùng để chứa các UTxO.
[42:53] Đấy, trong UTxO sẽ chứa những cái datum để chúng ta update. Đấy, và trong nó sẽ có cái reference token.
[43:05] Đấy.
[43:08] Đấy, hợp đồng update thì chúng ta sẽ có các hành động là update metadata hoặc burn. Đấy,
[43:21] đối với update thì nó sẽ có ba điều kiện. Điều kiện đầu tiên khi thực hiện
[43:28] ký giao dịch thì nó phải được ký đúng với cái khóa tương ứng với cái khóa được lưu trữ trong datum. Đấy, điều kiện
[43:36] thứ hai đó là cái input khi được chi tiêu nó phải chứa cái reference token.
[43:44] Và điều kiện thứ ba đó là cái output được tạo ra gửi lên hợp đồng
[43:51] thì nó phải gửi đúng hợp đồng này. Thứ hai là nó phải chứa reference token. Và
[43:59] tiếp theo là các cái trường thông tin thì nó không được thay đổi ngoài cái trường metadata và version. Đấy.
[44:06] Đấy như vậy thì mình cũng đã hướng dẫn các bạn khá là chi tiết về cái quy trình mình code hợp đồng thông minh cũng như
[44:15] là triển khai nó để tạo ra cái ờ gì nhở?
[44:23] Một bản hợp đồng gọi là đơn giản hóa nhất có thể, giúp mọi người hiểu
[44:30] được một cái quy trình, những cái logic cần phải có trong cái hợp đồng thông
[44:37] minh của một cái dự án theo chuẩn CIP-68 nó bao gồm những thành phần nào. Đấy,
[44:44] tiếp theo thì vì đã check thành công rồi thì chúng ta sẽ thực hiện build giao dịch
[44:51] để nó biên dịch cái file hợp đồng của chúng ta thành cái file plutus.json phục vụ mục đích để xử lý như là code
[45:00] off-chain hoặc backend trong các bài học tiếp theo. Đấy, chúng ta sẽ thực hiện câu lệnh aiken build.
[45:09] Rồi trong source code thư mục hợp đồng thông minh của chúng ta sẽ có thêm một file.
[45:17] Đây là file mà hệ thống đã biên dịch cho chúng ta. Đấy. Ok.
[45:24] Như vậy thì mình đã chia sẻ hướng dẫn khá là chi tiết trong
[45:32] cái phần hướng dẫn code hợp đồng thông minh theo chuẩn CIP-68. Mong rằng nó sẽ giúp mọi người hiểu được nguyên lý
[45:42] hoạt động để sau này có thể code ra những cái
[45:49] ứng dụng thực tế áp dụng CIP-68. Hơn nữa phục vụ mục đích đời sống hàng ngày
[45:55] của mọi người. Và đến đây thì mình xin phép kết thúc video tại đây. Xin chào mọi người.
