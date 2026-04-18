# Transcript bam sat video - Frontend + Backend CIP-68 (ASR cleaned)

- Goal: keep natural speaking style, fix ASR noise, normalize key technical terms.
- Note: Source has 4 videos, so subtitles are exported as 4 SRT files.

## Part 1 - Backend coding (no run yet)
- Video link: https://www.youtube.com/watch?v=BZ_EaiZyOY0

[00:00:14] Xin chào mọi người. Chào mừng mọi người đã đến với video tiếp theo trong khóa học lập trình Cardano của chúng tôi.
[00:00:22] Trong video này chúng ta sẽ tiếp tục triển khai ví dụ CIP-68.
[00:00:27] Thì tiếp tục với chuối video hướng dẫn triển khai ví dụ CIP-68 trong những
[00:00:35] trước đó thì trong video này ờ chúng tôi sẽ hướng dẫn mọi người triển khai full một app bao gồm các thành phần
[00:00:44] là frontend và backend để thực hiện các tính năng mint update metadata cũng
[00:00:50] là burn asset trực tiếp ngay trên giao diện thì công nghệ
[00:00:57] Ờ công công nghệ mình sử dụng cho frontend đó là Next.js.
[00:01:05] Còn backend thì vẫn là backend được viết bằng PyCardano.
[00:01:17] Thì đầu tiên cũng như là giống giống với những bài học trước đó thôi. Ờ
[00:01:25] vẫn sẽ nói lại cái quy trình
[00:01:32] mình vẫn sẽ thực hiện cái source code mà mình đã hướng dẫn trong
[00:01:40] bài học trước đó. Và trong bài học trước đó chúng ta đã triển khai xong phần ờ code hợp đồng thông minh và triển
[00:01:49] và thực hiện code phần code off-chain để thực hiện tương tác ừ trực tiếp
[00:01:56] hợp đồng thông minh bằng các cái script.
[00:02:00] Đấy và trong bài học tiếp theo này thì mình sẽ thực hiện tạo ra full một cái
[00:02:07] ứng dụng để có hai phần frontend và backend. Đấy thì đầu tiên vẫn là những bước quen thuộc
[00:02:16] Đầu tiên thì chúng ta vẫn phải khởi tạo môi trường ảo như những bài học trước đó. Vì là chúng ta đã cài đặt rồi
[00:02:24] chúng ta không chạy lại câu lệnh này. Chúng ta sẽ thực hiện kích hoạt môi trường ảo. Ok. Ờ sau khi kích hoạt môi
[00:02:33] ảo xong thì các cái setup ừ chúng ta cũng không cần phải install các cái thư viện trong những bài học trước đó để
[00:02:42] cái backend. Đấy vì là chúng ta vẫn dùng cái source cũ ấy nên không cần install lại thư viện.
[00:02:55] Sau khóa học này thì mình sẽ gọi là push tất cả code liên quan đến các video bài giảng lên GitHub của team. Mọi người có
[00:03:05] clone về và ừ đọc lại các cái nội dung code dự án mà
[00:03:13] mình đã triển khai trong các video mọi người nên mọi người cứ yên tâm.
[00:03:19] Đấy thì đầu tiên đó là chúng ta sẽ build một con con backend trước. Đấy
[00:03:29] trong thư mục script CIP-68 này chúng ta sẽ thực hiện tạo một cái folder backend để chúng ta code backend.
[00:03:38] Rồi đầu tiên thì chúng ta sẽ viết hàm main luôn.
[00:03:49] Đấy.
[00:03:52] Rồi trong hàm trong hàm main này chúng ta sẽ làm những
[00:03:59] Chúng ta sẽ xây một cái con backend API, sử dụng FastAPI của backend
[00:04:07] xử lý các yêu cầu của frontend. Đấy.
[00:04:20] Bao gồm các yêu cầu đó là mint asset này.
[00:04:25] Đấy, update metadata, burn asset và query các metadata của từng asset để
[00:04:34] thị lên giao dịch và list các asset trong ví. Đó.
[00:04:42] Ngoài ra thì còn có các dịch vụ như là ờ tạo các cái
[00:04:48] giao dịch mà chưa có chữ ký ờ để gửi lại frontend. frontend ký bằng wallet browser.
[00:04:58] Đấy thì mình sẽ nhắc lại một chút vì là Next.js ấy nó vẫn chưa có thư viện hỗ trợ.
[00:05:09] PyCardano để Next.js có thể code thư viện PyCardano ngay trên
[00:05:17] ngay trên giao diện người dùng. Chính vì thế mà chúng ta cần phải build cái con backend
[00:05:25] để khi mà chúng ta ờ gửi đến những cái ờ yêu cầu như là yêu cầu mint asset
[00:05:35] update metadata hoặc là burn asset từ frontend thì backend này nó sẽ phải xử lý được.
[00:05:42] Còn bình thường nếu như chúng ta dùng thư viện Lucid thì mọi người có thể code ngay được trên suộc của font luôn.
[00:05:53] Đấy thì ok về tổng quan thì mục tiêu trong cái phần backend này mục tiêu của nó là dùng
[00:06:02] code các cái API nhận các cái yêu cầu từ frontend và xử lý logic. Đấy thì các cái bước mình sẽ thực hiện xây dựng backend.
[00:06:15] Đầu tiên đó là chúng ta sẽ phải cài đặt FastAPI này.
[00:06:22] Đấy.
[00:06:26] Tiếp theo ừ gọi là mình sẽ nói luôn có tổng bao nhiêu bước nhá. Xong đó mình sẽ nhảy vào code từng bước luôn. Đấy. Đầu
[00:06:36] mình sẽ cài đặt thư viện FastAPI và Uvicorn để xây dựng backend API.
[00:06:44] Đấy. Tiếp theo là định nghĩa các mô hình dữ liệu với thư viện Pydantic Pydantic.
[00:06:53] Đấy, nó sẽ định nghĩa các yêu cầu và phản hồi API đến từ frontend. Tiếp theo
[00:07:00] là sử dụng async context manager để quản lý các vòng đời của ứng dụng ấy. Thiết lập tx context và các script.
[00:07:14] Đấy. Tiếp theo là tạo ứng dụng FastAPI với cấu hình cần thiết. Và bước thứ
[00:07:22] đó là định nghĩa các endpoint API để xử lý các yêu cầu từ frontend bao gồm các endpoint mình đã liệt kê này. Và thứ sáu và
[00:07:31] bước thứ sáu và bước thứ bảy chúng ta sẽ xử lý lỗi và trả về phản hồi cho từng endpoint. Và bước bảy là chạy ứng dụng.
[00:07:40] Đầu tiên thì chúng ta sẽ thực hiện khai báo các cái thư viện, import các thư viện như là OS, JSON này. Đấy,
[00:07:50] thư viện kiểu dữ liệu này, thư viện Time này. Đấy,
[00:07:57] Tiếp theo là import thư viện
[00:08:04] aiofiles đấy.
[00:08:10] async context manager để thực hiện quản lý vòng đời của ứng dụng này.
[00:08:17] Tiếp theo thì chúng ta sẽ ờ import các cái thư viện liên quan đến FastAPI.
[00:08:26] Đấy thì cái FastAPI này mình sẽ nói lại dùng để ờ xây các cái API này và xử lý
[00:08:36] cái yêu cầu http. Tiếp theo là import CORS middleware
[00:08:42] đấy để gọi là cho frontend có thể query đến backend.
[00:08:51] Rồi tiếp theo là thư viện Pydantic đấy.
[00:09:00] Để định nghĩa các mô hình dữ liệu ừ cho các request và response
[00:09:07] dotenv.
[00:09:11] Tiếp theo là import các cái thư viện của PyCardano.
[00:09:15] Rồi tiếp theo là import ừ một số các cái thư viện để chúng ta ờ xử lý witness set.
[00:09:26] Đấy thì cái witness set này tí nữa mình sẽ nhấn mạnh lại cho các bạn tại sao cần
[00:09:33] dùng nó. Tiếp theo là import các hàm tiện ích mà chúng ta đã xây dựng từ module offchain trong bài học trước đó. Đấy.
[00:09:43] Các cái hàm tiện ích đây này.
[00:09:46] Rồi vì là các cái video nó liên quan mật thiết
[00:09:53] với nhau nên mọi người chú ý là ờ xem gọi là khi học thì phải học
[00:10:00] video một và đúng thứ tự nhé. thì mới hiểu được bài học
[00:10:08] Tiếp đầu tiên chúng ta nhảy vào code này. Đầu tiên đấy là load môi trường khai báo một số cái biến toàn cục.
[00:10:21] Đấy, đầu tiên là tx context này. Tiếp theo là Blockfrost context này.
[00:10:29] Rồi tiếp theo là đường dẫn đến file plutus.json.
[00:10:36] Tiếp theo là network này. Đấy, cái này để xử lý liên quan đến blockfrost đấy. Tiếp theo là khai báo
[00:10:44] dữ liệu mint script này để đọc thông tin của hợp đồng thông minh này. Store script cũng vậy. policy ID này và store address. Đấy.
[00:10:59] Rồi sau khi chúng ta đã định nghĩa các cái biến toàn cục ừ để xử lý trong cái
[00:11:06] dụng thì chúng ta sẽ đầu tiên đó là bước đến định nghĩa các model.
[00:11:13] Đấy, định nghĩa các model để xác định cấu trúc dữ liệu cho các yêu
[00:11:19] và phản hồi đến từ frontend. Đấy chúng ta sẽ sử dụng ờ Pydantic model.
[00:11:33] Đấy. Đầu tiên thì chúng ta sẽ khai báo cái mint request.
[00:11:40] mint request này thì nó sẽ ờ là cái module để
[00:11:49] báo cái kiểu dữ liệu cho cái request mint đấy nó sẽ khai báo khai
[00:12:00] báo
[00:12:09] Kiểu dữ liệu
[00:12:19] yêu cầu mint asset này. Đấy, nó sẽ giúp xác định các trường cần thiết để
[00:12:27] một asset mới. Đấy, mẫu của nó là như vậy.
[00:12:36] Đây bao gồm các trường như là wallet,
[00:12:46] wallet, token name này.
[00:12:55] Đấy, description mô tả NFT. Đấy.
[00:13:02] Ok. Tiếp theo thì chúng ta sẽ khai báo cái module của cái update request.
[00:13:09] Đấy. Tiếp theo là model.
[00:13:18] Module của yêu cầu
[00:13:25] update metadata. Cái này nó sẽ dùng cho endpoint API update này. Đấy
[00:13:33] cái này khai báo class update request
[00:13:41] có các kiểu dữ liệu đó là wallet address nè, token name nè, new
[00:13:49] n tức là khi chúng ta gửi cái yêu cầu lên bao gồm các cái trường wallet, address nè, token name và new description.
[00:13:59] Đấy. Tiếp theo là module cho
[00:14:07] burn token yêu cầu burn asset đấy. Dùng cho
[00:14:16] API B này cần các trường như là đấy mình vừa code mình sẽ vừa chú thích luôn.
[00:14:27] Có gì không hiểu mọi người xem lại burn request nào base model cái thừa base
[00:14:34] này. Đấy cũng bao gồm các cái trường như là wallet address và token name.
[00:14:44] Tiếp theo đó là module transaction.
[00:14:56] Ừ
[00:15:06] này nó sẽ dùng cho các cái giao dịch như là mint API update. Đấy dùng cho các
[00:15:14] endpoint gọi đến là yêu cầu mint và yêu cầu update. Đấy, cái này là model phản hồi nhá. Phản hồi tức là response ấy,
[00:15:28] sẽ định nghĩa cấu trúc phản hồi khi một giao dịch được gửi tới. Đấy, bao gồm
[00:15:36] trạng thái thành công, thông điệp và mã giao dịch
[00:15:44] giao dịch là giao dịch chưa ký.
[00:15:52] các trường.
[00:15:57] Đấy, mình sẽ nhấn mạnh lại mọi người một chút nhá. Khi mà chúng ta
[00:16:04] mint hay là update hay là burn ấy thì có một điểm chung đó là chúng ta
[00:16:12] giao dịch thì phải ký bên frontend đúng không? Đấy,
[00:16:18] backend nó không có chế độ ký giao dịch. Chính vì thế mà khi người dùng gửi yêu cầu mint
[00:16:27] burn đấy thì người dùng sẽ gửi cái thông tin về tài sản muốn thực hiện này
[00:16:34] Đấy, thì lên backend, backend sẽ thực hiện
[00:16:40] giao dịch. Tuy nhiên là vì là chỉ có thể là ký hiệu ở frontend đúng không?
[00:16:47] Nên backend không có chữ ký nên phải backend chỉ có thể build giao dịch không có chữ ký và gửi cái giao dịch đó về frontend. Đấy,
[00:16:57] cái giao dịch không có chữ ký đó về frontend và frontend sẽ phải ký bằng ví ở trình duyệt của người dùng ấy. Xong
[00:17:07] lại, người dùng lại tiếp tục gửi lại cái giao dịch đã ký lên backend để backend xử lý ờ thêm cái chữ ký đó vào giao
[00:17:16] và submit. Đấy, mình đã nhắc khá nhiều lần về cái a ờ gì nhở? nguyên lý
[00:17:23] hoạt động của chúng ta. Rồi
[00:17:31] tiếp theo là chúng ta sẽ định nghĩa mô hình
[00:17:39] yêu cầu gửi giao dịch nha.
[00:17:52] Đấy, mình sẽ dùng cho endpoint.
[00:17:58] Đấy, mô hình này xác định các trường cần thiết này. Đấy, bao gồm các
[00:18:06] dịch này và witness set từ ví nà. Thứ hai là transaction object này.
[00:18:15] Đấy.
[00:18:23] Ứ mình cứ chú thích một hồi nhá.
[00:18:29] Xong đấy mình giải thích lại. Mình vừa giải thích xong rồi. Đây mình nhắc lại
[00:18:35] lần nữa này. Tức là khi người dùng gửi cái submit này, submit giao dịch lên
[00:18:45] ấy thì backend sẽ nhận được các cái thông tin bao gồm body và with
[00:18:52] set. Đấy. Đấy thì backend sẽ
[00:18:59] hiện hợp nhất cái witness set và cái transaction và submit lên on-chain.
[00:19:12] Ừ. Ok. Này có lẽ là hơi hơi hơi thiếu clear một chút thì mình sẽ clear lại.
[00:19:20] Ừ. Đầu tiên người dùng gửi những cái yêu cầu như là
[00:19:26] này, update này, burn đúng không? Thì
[00:19:33] là backend nó không thể có cái chế độ gọi đến ví ở bên backend đúng không?
[00:19:39] Trình duyệt nó chỉ hỗ trợ ví ở frontend thôi. Đấy nên backend nó không thể ký được bên backend được. Mọi
[00:19:48] hiểu chứ? Đấy, trình duyệt nó chỉ hỗ trợ kết nối ví và ký giao dịch ở bên Font
[00:19:57] Còn backend thì không hỗ trợ trực tiếp. Đấy, nên chúng ta mới phải xử lý
[00:20:03] vấn đề này. Đó là người dùng yêu cầu tạo giao dịch mint hoặc là update này
[00:20:11] là burn này. Đấy, người dùng sẽ yêu cầu đến backend. Đấy, backend sẽ thực hiện này build cái giao dịch đấy.
[00:20:24] Nhưng mà cái giao dịch đấy là cái giao dịch chưa ký đấy và gửi lại cái giao dịch chưa ký về với frontend. Đấy thì tại
[00:20:34] thì người dùng sẽ thực hiện ký cái giao dịch đấy bằng ví theo chuẩn CIP-30 đây
[00:20:40] Đấy sau đó sau khi ký xong sẽ gửi lại cái thông tin giao dịch kèm theo cái witness set
[00:20:50] đấy chứa chữ ký của người dùng về lại backend thì backend nhận được
[00:20:57] hợp nhất witness set này vào transaction gốc và submit lên on-chain. Đấy thì bình thường transaction sẽ
[00:21:06] gồm hai thành phần. Mọi người có thể nhìn thấy này. Body đấy. transaction body chứa các input, output này, mint
[00:21:14] một số các tham số khác. Ngoài ra còn chứa gọi là đối tượng witness set.
[00:21:21] Đấy gọi là transaction witness set chứa các thông tin như script này, redeem này, plus data chẳng hạn. Đấy mọi người ok chưa?
[00:21:31] Tức là frontend đóng vai trò connect wallet và ký giao dịch. Còn backend
[00:21:39] sẽ build giao dịch và trả về giao dịch chưa có chữ ký.
[00:21:48] backend không hỗ trợ trực tiếp việc connect ví hoặc ký giao
[00:21:56] ngay trên giao diện ấy. Đấy nên chúng ta phải xử lý như vậy. Ok. Tiếp
[00:22:04] là model submit request.
[00:22:17] Đấy, bao gồm các trường mình đã nói ở trên rồi nhá.
[00:22:24] Rồi tiếp theo là model phản hồi giao dịch,
[00:22:30] mô hình phản hồi giao dịch
[00:22:39] dùng cho API submit này.
[00:22:49] định nghĩa cấu trúc phản hồi khi một giao dịch được gửi lên blockchain. Đấy, bao gồm trạng thái thành công và submit response.
[00:23:02] Đấy.
[00:23:06] Ok. Tiếp theo là module phản hồi truy vấn metadata.
[00:23:11] Phản hồi truy vấn metadata.
[00:23:20] Đấy, mô hình dùng cho API rồi. Định nghĩa class là metadata response này.
[00:23:32] Đấy, các trường như là trường success này,
[00:23:38] này, metadata này. Tiếp theo là một mô hình
[00:23:45] model phản hồi thông tin ví,
[00:23:52] model phản hồi thông tin ví nhá.
[00:24:01] Phản hồi thông tin ví dung cho API.
[00:24:13] Tiếp theo là mô hình này định nghĩa cấu trúc phản hồi thông tin truy xuất ví này
[00:24:19] gồm các số dư này đấy.
[00:24:25] Khai báo model các cái trường cần.
[00:24:34] Ok.
[00:24:36] Như vậy thì chúng ta đã định nghĩa các cái kiểu dữ liệu cho các yêu cầu request và response ừ phản hồi đến từ các cái
[00:24:46] API. Đấy, tiếp theo thì chúng ta sẽ thực hiện khai báo cái
[00:24:56] đối tượng quản lý ờ vòng đời của ứng dụng
[00:25:05] thực hiện khai báo
[00:25:19] async context manager này xử lý vòng đời của ứng dụng này
[00:25:26] theo là định nghĩa async lifespan này
[00:25:33] các tham số với các biến global như tx context chúng ta đã khai báo ở trên để duy trì sử dụng trong
[00:25:43] bộ dự án đấy. Khởi tạo context này.
[00:25:49] Đấy tiếp theo là lấy Blockfrost API key này.
[00:26:00] Tiếp theo là lấy network ra.
[00:26:11] Tiếp theo là khởi tạo tx context.
[00:27:28] Chúng ta thiếu mất thứ viện Blockfrost API à.
[00:27:35] Ok. để bổ sung thêm thư viện đây.
[00:27:50] From Blockfrost này, import này. Ok rồi.
[00:28:02] Tiếp theo thì chúng ta sẽ ừ khai báo thiết lập đường dẫn đến file plutus.json đấy.
[00:28:14] chúng ta sẽ vẫn dùng đường dẫn giống như phần
[00:28:29] dẫn của file plutus.json hôm trước ấy. Đấy, tiếp theo là load Script.
[00:28:37] Nói chung là đến bước này thì chắc chắn là mọi người cũng đã hiểu rất là rõ các
[00:28:44] này rồi nên mình sẽ không không nói chi tiết những phần này.
[00:29:01] Rồi tiếp theo là load các cái script
[00:29:12] in ra policy ID này.
[00:29:21] Store address này.
[00:29:25] Tiếp theo là nếu như không có thì báo lỗi. Đấy và cuối cùng là in ra trạng thái connect.
[00:29:34] Context khởi tạo thành công rồi và xong.
[00:29:49] Ok. Như vậy chúng ta đã ừ thiết lập xong cái
[00:29:56] quản lý vòng đời cho cái ứng dụng của chúng ta. Đấy.
[00:30:03] Tiếp theo thì chúng ta sẽ khởi tạo ứng dụng FastAPI.
[00:30:13] Khởi tạo ứng dụng FastAPI để chạy ứng dụng.
[00:30:24] title và description này, version này và chạy cái quản lý vòng đời.
[00:30:34] Ok. Sau khi đã khởi tạo ứng dụng xong thì chúng ta sẽ khai báo
[00:30:41] CORS Middleware để cho phép frontend có thể truy cập vào endpoint của backend.
[00:30:49] Đấy. App.
[00:30:53] middleware này call middleware
[00:31:03] origin cái port của frontend vào.
[00:31:10] Tiếp theo đó là cho phép xác minh allow credential và cho phép tất cả các cái method.
[00:31:22] Rồi vào chính vào nội dung chính này chúng ta sẽ bắt đầu xử lý các cái API endpoint để xử lý các cái yêu cầu.
[00:31:33] Đầu tiên là khai báo phương thức get. Đấy,
[00:31:41] này thì lấy các cái thông số của ứng dụng bao gồm như là
[00:31:50] khỏe của là trả về các cái thông tin như status.
[00:32:01] Rồi tiếp theo là khai báo cái endpoint để chuyển đổi
[00:32:09] địa chỉ ví từ dạng hex sang dạng bech32. Đấy cái này là
[00:32:17] tên là API convert address đi với hàm là convert address này.
[00:32:25] Đấy.
[00:32:27] Ừ. Hex dạng bytes
[00:32:47] tiếp theo là chú thích nhé. Đấy. Try
[00:33:02] address dạng byte này. Sau đó thì chuyển về dạng
[00:33:11] bech32 return.
[00:33:19] Tiếp theo là try/except. Nếu như có lỗi rồi không thể chuyển đổi đây này.
[00:33:42] và except trả về full lỗi.
[00:33:53] Rồi tiếp theo thì là point lấy thông tin của hợp đồng thông minh.
[00:34:03] Đấy định nghĩa tên là get script info đấy. Định nghĩa hàm
[00:34:12] script info lấy thông tin của hợp đồng thông minh này.
[00:34:21] cái trường dữ liệu của hợp đồng thông minh mà chúng ta đã lấy ra. Đấy.
[00:34:28] Tiếp theo là API endpoint lấy thông tin từ ví.
[00:34:38] Lấy các thông tin từ ví ra đấy. Ừ. Định nghĩa endpoint là API wallet address. Đấy,
[00:34:50] là get wallet info rồi. Try.
[00:35:04] Tiếp theo thì chúng ta sẽ thực hiện convert address từ dạng ấy ra.
[00:35:14] Nếu như nó không phải dạng bech32 thì chúng ta sẽ phải convert.
[00:35:21] Tiếp theo là lấy UTxO và tổng hợp balance.
[00:35:32] Tiếp theo là truy vấn ừ thông tin của asset.
[00:35:39] Khởi tạo asset bằng rỗng này. Duyệt tất cả UTxO for UTxO in UTxO này. Duyệt tất cả
[00:35:47] cái multi-asset trong UTxO.
[00:35:55] Đấy.
[00:36:03] Xong. Duyệt tiếp từng cái asset trong multi-asset.
[00:36:12] lại tiếp tục duyệt các cái thông tin của asset
[00:36:21] add vào danh sách asset của chúng ta rồi
[00:36:30] wallet response và except lại.
[00:36:52] Tiếp theo thì đến với những endpoint đó là giao dịch mint token.
[00:37:01] gửi yêu cầu mint token với địa chỉ ví và các trường liên quan.
[00:37:07] Đấy, backend sẽ thực hiện tạo unsigned transaction và trả về CBOR.
[00:37:16] Và cái thông tin trả về sẽ bao gồm body, transaction và witness set.
[00:37:25] transaction đấy. Frontend ký transaction bằng ví và gửi
[00:37:32] set. Cái nữa thì tí nữa đến bước submit mình sẽ
[00:37:38] chú thích đó vào rồi định nghĩa API mint.
[00:37:47] Cái này sẽ là một response model trả về cho thằng frontend khi nó gửi cái yêu
[00:37:54] mint đấy.
[00:38:00] Create mint transaction này. Viết hàm mint transaction đầu vào là request.
[00:38:12] Ừ, tức là nó gửi lên thông tin của cái giao dịch mint. Đấy,
[00:38:19] trong cái bước này thì chúng ta sẽ thực hiện tạo cái giao dịch chưa ký.
[00:38:27] Đầu tiên vẫn là try/except này.
[00:38:31] Try và except.
[00:38:53] Rồi đầu tiên vẫn bước quen thuộc giống như phần trước đó thôi. Nhưng mà có thêm bước là
[00:39:02] như mint script hoặc là store script không có ấy thì sẽ ra cái lỗi.
[00:39:10] Đấy.
[00:39:13] Rồi vẫn là lấy địa chỉ của
[00:39:21] chiếu đối chiếu chữ ký ấy. Tiếp theo là lấy
[00:39:33] key của lấy UTxO của ví người dùng.
[00:39:44] Đấy. Tiếp theo là query rồi. Nếu không có thì race lỗi.
[00:40:18] Ray lỗi nà. Bước tiếp theo vẫn là tạo asset name. Đấy, từ cái
[00:40:27] name truyền vào request ấy, chúng ta lấy ra và chuyển nó về dạng buy
[00:40:35] nó đi và tạo refer asset name đính được prefix vào.
[00:40:45] Và tiếp theo là lấy policy ID, vẫn rất quen thuộc trong phần mint ở trong phần off-chain. Đấy. Tiếp theo là create datum.
[00:40:57] Rồi tiếp theo vẫn là tạo multi-asset asset.
[00:41:02] Ừ. Nói chung là phần này khá là giống với các bài trước nên mình sẽ làm nhanh nhá. Đấy.
[00:41:10] Rồi tiếp theo là tạo redeemer vẫn rất quen thuộc. Tiếp theo là tính value cho từng tài sản.
[00:41:21] Đấy cho cả multiac cho cả user reference token và
[00:41:28] token. Tiếp theo là tạo builder rồi builder add input này vẫn rất quen.
[00:41:41] Tính kèm thông tin giao dịch mint vào giao dịch mint này. Adminting script này.
[00:41:49] Rồi tiếp theo là add output.
[00:41:54] Phần này vẫn nói chung là giống y hệt phần build giao dịch lúc chúng ta code off-chain đấy.
[00:42:05] Đấy. Tiếp theo là ừ yêu cầu chữ ký này tương ứng với cái ờ public key hash của cái địa chỉ. Đấy.
[00:42:18] Tiếp theo là đây. Cái này thì hơi khác một chút.
[00:42:23] Đây bắt đầu khác rồi. Đấy.
[00:42:30] Thay vì cái cái kia kìa chúng ta ký giao dịch thì đến bước này thì chúng ta sẽ phải khởi tạo riêng cái trans body riêng. Đấy.
[00:42:42] Ứ. Tiếp theo là khởi tạo witness set này.
[00:42:56] Mình sẽ chú thích lại đây. transaction body có các thành phần đó là
[00:43:03] và witness set. Đấy, transaction body gồm các input, output, mint này.
[00:43:11] Còn witness set gồm chứa các cái script này. Đấy, để sau này chúng ta phải tách riêng hai cái thành phần này ra để xử lý chữ ký.
[00:43:23] Rồi tạo giao dịch từ hai cái đối tượng trên.
[00:43:29] Rồi tiếp theo là chuyển về STB.
[00:43:36] Và cuối cùng là trả lại cái giao dịch đã được build nhưng mà chưa có chữ ký về
[00:43:42] end. Đấy, xong cái bước gọi là
[00:43:50] định nghĩa ờ endpoint cho yêu cầu mint rồi.
[00:43:58] Đấy, thì kết quả của cái ừ yêu cầu mint thì chúng ta sẽ phải trả về
[00:44:06] frontend một cái cấu trúc dữ liệu ờ transaction dạng CP này. Đấy. Đấy. Thì
[00:44:14] cái transaction dạng CBOR này nó sẽ có hai thành phần là thành phần đó là transaction body và thành phần witness set
[00:44:22] Đấy. Thì ở bên frontend chúng ta sẽ ký và
[00:44:29] cái chữ ký vào witness set này và gửi lại bên backend. Đấy, tí nữa chúng ta sẽ xử lý phần đó.
[00:44:36] Đấy. Ok.
[00:44:41] Mọi người đã hiểu ý tưởng chưa? Tiếp theo nhá, chúng ta sẽ đến với Endpoint tạo giao dịch update Metat Metadata
[00:44:51] khai báo API update response module. Đấy, trang
[00:44:59] response sử dụng cái module ở trên kia nhờ.
[00:45:04] Đấy. Tiếp theo là khai báo cái hàm tạo update transaction này. Hàm này sẽ có
[00:45:13] số đầu vào là request update. Nó sẽ gửi cái request lên bao gồm cái thông số
[00:45:20] thông số mình đã khai báo trên model update request ở trên kia kìa. Đấy và
[00:45:28] ta sẽ nhận lại và build cái giao dịch unsigned đấy. Tạo giao dịch unsigned và gửi lại cái
[00:45:37] giao dịch để frontend ký. Đấy vẫn là try/catch, khá là quen thuộc.
[00:45:46] Thì phần này thì mình sẽ đi nhanh nhá.
[00:45:51] nhanh không không nói rồi
[00:46:03] là check xem có tồn tại script không đấy
[00:46:12] theo vẫn là lấy địa chỉ và lấy public key hash để
[00:46:19] khớp chữ ký này. Tiếp theo vẫn là lấy policy id ra tạo token name này.
[00:46:29] Đấy tạo reference asset name này.
[00:46:35] Đấy tiếp theo vẫn là tìm UTxO trong store address.
[00:46:40] Đấy thì phần này mình sẽ ấy nhanh giống phần code off-chain hôm trước thôi.
[00:46:46] Tiếp theo vẫn là xử lý datum xử lý datum
[00:46:55] lấy public key của các thông tin của datum để khởi tạo datum mới.
[00:47:03] Rồi tiếp theo là tạo datum mới này. Vẫn giống như phần viết code trên cho cái
[00:47:13] update metadata ấy. Đấy. Tiếp theo là tạo redeem
[00:47:20] build transaction và build add input address.
[00:47:30] Và tiếp theo là add input script.
[00:47:34] Rồi tiếp theo vẫn là ừ tạo value cho
[00:47:43] UTxO chứa ref token. Đấy.
[00:47:49] Rồi tiếp theo vẫn là build add output vẫn là yêu cầu chữ ký.
[00:48:01] Rồi bước này thì vẫn tương tự như phần mình vừa giải thích trong mint ấy. Thì tx
[00:48:09] chuyển cái transaction sang bên frontend để người ta ký ấy chúng ta sẽ có hai thành phần. Thành phần đầu tiên đó là TX
[00:48:18] và thành phần thứ hai đó là witness set. Đấy.
[00:48:24] Đấy. Thì chúng ta sẽ build ờ witness set nhưng mà không có chữ ký
[00:48:31] frontend nó gắn thêm cái chữ ký vào đấy. Và cuối cùng là tạo đối tượng transaction.
[00:48:41] Tiếp theo là chuyển về kiểu dữ liệu.
[00:48:47] Và cuối cùng là phản hồi trả về cho frontend.
[00:48:53] Kết quả ừ gọi là thông tin của transaction chưa có chữ ký. Đấy, tương tự như vậy
[00:49:01] ta cũng sẽ sang phần định nghĩa API endpoint cho cái burn token đấy.
[00:49:11] Nó sẽ response thì trả về các trường chúng ta đã
[00:49:18] báo trong phần mod trước đó ấy. Đấy, tạo hàm này.
[00:49:26] Request cũng nhận vào kiểu dữ liệu theo kiểu model chúng ta đã khai báo trước đó.
[00:49:36] Rồi vẫn rất giống với mint và update cũng try và except.
[00:49:55] Rồi vẫn là xử lý build giao dịch.
[00:50:01] Đầu tiên vẫn là kiểm tra xem store script có tồn tại hay không.
[00:50:13] Đấy. Tiếp đến đấy là lấy thông tin của public key hash tương ứng với địa chỉ và
[00:50:22] tên tài sản từ cái trường token name truyền vào.
[00:50:30] Tiếp theo là tạo refer và user token name để tạo multi asset trong bước tiếp
[00:50:37] Tiếp theo vẫn là query UTxO từ store address.
[00:50:44] Đấy.
[00:50:48] Tiếp theo vẫn là xử lý datum.
[00:50:55] Đấy,
[00:51:02] Datum thuộc kiểu CIP-68 datum thì chúng ta sẽ lấy ra cái thông tin
[00:51:09] public key của owner để sau này đối chiếu chữ ký. Ấy tiếp theo là
[00:51:16] những cái UTxO của
[00:51:24] trong địa chỉ của ví địa chỉ ví của user.
[00:51:28] Đấy những bước gọi là build giao dịch ấy nó tương tự trong phần code off-chain luôn
[00:51:37] trong phần này mình sẽ không giải thích nhiều về nguyên lý cả.
[00:51:42] Đấy, create redeemer này vẫn có hai phần ừ gọi là
[00:51:50] burn thì phải chi tiêu cái token trên store address. Đấy, và sau khi chi tiêu
[00:51:57] thì chúng ta phải hủy hủy bỏ cái token đó. Rồi tiếp theo là tạo builder add input address.
[00:52:11] add input script và lấy input từ user
[00:52:20] thực hiện đính kèm thông tin burn vào giao dịch burn đấy và add minting script
[00:52:31] yêu cầu chữ ký và vẫn là giống như là mint và burn thôi à
[00:52:42] và update ấy cũng build gọi là transaction body đấy sau đó thì build
[00:52:51] có chữ ký ấy và cuối cùng là tạo transaction chuyển về C và phản hồi lại frontend.
[00:53:04] Đấy rồi ok. Ờ mình sẽ tổng tổng kết lại một chút nhá.
[00:53:18] Trong cái ba cái API endpoint cho mint này,
[00:53:22] này, B này thì mục tiêu của nó là trả về cái thông tin transaction chưa
[00:53:32] chữ ký cho frontend. Đấy, để frontend thực hiện ký bằng ví trên trình duyệt,
[00:53:39] rồi submit lại giao dịch lên backend để backend hợp nhất chữ ký
[00:53:46] và submit on-chain. Đấy thì ba API endpoint này xử lý như vậy. Tiếp theo thì chúng ta sẽ thực hiện định nghĩa cái
[00:53:55] endpoint nhận giao dịch gửi lên backend sau khi đã được bổ sung chữ ký từ frontend. Đấy,
[00:54:09] định nghĩa API POST đấy.
[00:54:17] Tạo hàm này.
[00:54:21] Tiếp theo là có một chút chú thích.
[00:54:28] Đấy. Tiếp theo là try và except.
[00:54:37] Mình đang ghi theo note nên hơi nhanh.
[00:54:45] Rồi đầu tiên chúng ta sẽ thực hiện load lại transaction gốc từ CBOR chứa body và witness set nhé.
[00:54:58] Đấy.
[00:55:07] Load transaction góc từ CBOR đấy.
[00:55:13] Khai báo backtx này bằng transaction from CBOR.
[00:55:29] Đấy.
[00:55:32] Tiếp theo là lấy ra witness set
[00:55:45] witness set bằng transaction witness set from CBOR.
[00:55:55] từ frontend. Đấy.
[00:55:58] Rồi tiếp theo thì chúng ta sẽ hợp nhất hợp nhất cái
[00:56:07] ký vào witness set.
[00:56:25] backend_tx.witness_set này đây.
[00:56:34] ví có trả về chữ ký thì hãy thêm vào witness set
[00:56:42] nếu ví trả về key thì gộp vào.
[00:57:02] Ứ trong trường hợp này sẽ có hai trường hợp. Một là backend.
[00:57:11] Ừ.
[00:57:13] Nhiều lúc ấy nó có chế độ multisig đấy. Trong trường hợp đó backend có thể có thêm các chữ ký khác.
[00:57:23] Đấy nên chúng ta cũng cần phải quét thêm cái điều kiện này.
[00:57:29] Đấy trong trường hợp multi nhá. Multi
[00:57:36] Nếu như tồn tại
[00:57:44] chúng ta sẽ gộp vào
[00:57:57] Thực hiện gộp này.
[00:58:01] vkey này. Đấy, sync vkey cộng new key đấy.
[00:58:09] Chúng ta sẽ gộp vào. Còn nếu không thì chúng ta vẫn gộp bình thường thôi.
[00:58:17] Thì phổ biến thì đa số là backend sẽ không có chữ ký đâu. Đấy.
[00:58:29] Đấy.
[00:58:32] gán lại cái final witness set bằng cái chữ ký của wallet ấy. Và cuối cùng là gắn vào transaction.
[00:58:46] Gắn lại vào transaction.
[00:59:04] Rồi bước cuối cùng là submit.
[00:59:11] và tx context submit này kiểu dữ liệu
[00:59:18] phải là CBOR và cuối cùng là phản hồi lại.
[00:59:30] Rồi như vậy thì chúng ta đã xong những cái phần quan trọng của cái những cái yêu cầu đến từ frontend. Đấy,
[00:59:43] xin nhắc lại một lần nữa, mặc dù nó tốn thời gian nhưng mà mình nghĩ là điều này sẽ giúp cho mọi người hiểu hơn. Đấy,
[00:59:51] là frontend chưa thể dùng trực tiếp đầy đủ thư viện Cardano
[00:59:59] trên môi trường máy client. Đấy, chính vì thế
[01:00:04] khi code cái ví dụ này mình đã thiết kế backend để build giao dịch
[01:00:14] và trả về giao dịch chưa ký cho frontend.
[01:00:22] Frontend sẽ thực hiện ký transaction
[01:00:29] bằng ví được cài trên extension của trình duyệt. Đấy. Và
[01:00:39] gửi lại giao dịch đã có chữ ký về backend, backend sẽ xử lý chữ ký và submit giao dịch lên on-chain.
[01:00:48] Đấy, đấy là điểm khó nhất mà cái bài toán ừ triển khai một cái app ừ
[01:00:59] gọi là minh họa thực tế ngay trên giao diện về các tính năng của
[01:01:05] CIP-68 này. Mình thấy đây là điểm khúc mắc nhất.
[01:01:12] Nhưng mình cũng đã chia sẻ giải pháp đó rồi, tiếp theo chúng ta sẽ định nghĩa
[01:01:20] một số cái endpoint API cần thiết khác như là lấy metadata của các cái
[01:01:27] token đấy. Get metadata.
[01:01:38] Try.
[01:01:48] Và except.
[01:02:03] Đầu tiên đó là vẫn là phải kiểm tra xem store address có tồn tại hay không.
[01:02:12] Tiếp theo là tạo token name từ request gửi lên.
[01:02:22] Sau đó tạo reference asset name từ token name. Đấy,
[01:02:32] một số cái thông báo ra màn hình console.
[01:02:40] Tiếp theo đó là tìm UTxO. Đấy,
[01:02:49] các UTxO trong hợp đồng thông minh.
[01:02:52] Nếu có thì hiển thị xem có bao nhiêu cái rồi duyệt.
[01:02:59] Nếu không thì đóng lại.
[01:03:07] Nếu như UTxO có multi asset này thì lại tiếp tục duyệt trong multi asset các cái item.
[01:03:17] Đấy, xong in ra một số thông tin như là policy, asset name, số lượng.
[01:03:26] Tiếp theo là tiếp tục duyệt trong asset item
[01:03:33] và in ra các thông tin của asset.
[01:03:43] Sau đó xử lý thêm datum.
[01:04:05] Nếu datum thuộc kiểu dữ liệu phù hợp
[01:04:15] chúng ta sẽ chuyển nó về dạng datum CIP-68.
[01:04:37] Rồi tiếp theo nếu datum là kiểu dữ liệu có thể đọc được
[01:04:48] chúng ta sẽ thực hiện convert metadata đấy.
[01:04:58] duyệt các trường trong metadata.
[01:05:11] item trong metadata này.
[01:05:21] xử lý key và value.
[01:06:09] Else.
[01:06:30] Sau đó thì khởi tạo value metadata và in ra
[01:06:46] ra metadata.
[01:06:52] Rồi cuối cùng là return
[01:07:16] Nếu không thì không tìm thấy.
[01:07:46] Cuối cùng là return not found.
[01:07:55] Ok.
[01:07:57] Tiếp theo đó là chúng ta viết thêm một endpoint để liệt kê
[01:08:02] tất cả các token CIP-68
[01:08:10] trong hợp đồng thông minh tương ứng với
[01:08:18] địa chỉ store để list.
[01:08:29] này.
[01:08:55] Vẫn phải check tồn tại store hay không. Khởi tạo token bằng rỗng.
[01:09:05] Tiếp theo lấy các UTxO và duyệt.
[01:09:12] Duyệt các UTxO trong hợp đồng và lấy thông tin token.
[01:09:33] Rồi. Ok.
[01:09:39] Bước tiếp theo là chạy server, rồi khai báo khởi tạo thêm một file
[01:09:51] __init__ để import/export các file khi cần. Ok,
[01:10:05] ta thử chạy xem nào.
[01:10:10] Ừ. À để chạy được thì chúng ta sẽ phải có một cái file run server chứ. Run server, run backend.
[01:10:19] Hai dòng run backend như sau.
[01:10:27] Đầu tiên vẫn là import này. Thêm một số đường dẫn vào.
[01:10:36] Thêm đường dẫn của thư mục backend vào môi trường.
[01:10:43] Đấy, mục tiêu của việc này là giúp thêm đường dẫn, import các module
[01:10:53] trong dự án đấy để đảm bảo các module dễ dàng được gọi trong dự án.
[01:11:02] và chạy chạy thôi. Đấy rồi chúng ta thử chạy thử xem nào.
[01:11:13] python run_backend.py.
[01:11:28] Lỗi gì đây?
[01:11:41] tx context bằng none à
[01:11:55] tx context đây.
[01:12:16] context này.
[01:12:41] nhầm rồi mình lại thêm cái phím enter vào đây. Ok.
[01:12:56] đây?
[01:13:04] tx context này app
[01:13:23] nhầm nhầm blockfrost project đi. Ok rồi.
[01:13:36] Nào.

## Part 2 - Backend run
- Video link: https://www.youtube.com/watch?v=_4NE9cFxmhU

[00:00:04] Vẫn lỗi nhở. Xem nào. Main nà.
[00:00:13] Network network token mismatch không đúng network à?
[00:00:27] Xem nào. Network network bằng pre
[00:00:34] à. Ok hiểu rồi.
[00:00:40] Do cái này nó được gán bằng network.testnet rồi chứ không phải preprod. Đấy chúng ta phải sửa cái này
[00:00:48] Ok rồi. Ok.
[00:00:56] Như vậy backend của chúng ta đã chạy thành công rồi này. Đấy đã tìm thấy file plutus này đã
[00:01:05] được cái plutus script thành ID rồi đã có address của store rồi. Ok.

## Part 3 - Frontend coding (no demo yet)
- Video link: https://www.youtube.com/watch?v=5k7Esch4UQE

[00:00:03] Ok, sau khi backend đã code và chạy thành công rồi, bây giờ thì chúng ta sẽ thực hiện code frontend.
[00:00:12] Đấy thì như mình đã giới thiệu thì frontend
[00:00:18] ta sẽ dùng thư viện Next.js và sử dụng chuẩn CIP-30 để thực hiện
[00:00:27] các thao tác với ví như ký giao dịch và kết nối ví trên trình duyệt.
[00:00:37] Đấy, chúng ta sẽ tạo một cái terminal mới để cái con backend nó vẫn chạy đấy.
[00:00:42] Ừ. CD vào CIP-68 rồi
[00:00:58] thì mình sẽ bắt đầu vì là
[00:01:06] trình code frontend nếu như chúng ta thực hiện code cả giao diện ấy nó khá là tốn thời gian. Chính vì thế mà mình đã
[00:01:14] chuẩn bị một cái template giao diện frontend phục vụ cho phần này. Đấy,
[00:01:21] template này chưa có code logic,
[00:01:24] chưa có các dịch vụ như build giao dịch hay viết hàm
[00:01:34] xử lý thu thập dữ liệu. Đấy, chính vì thế mà mình đã tạo sẵn một template có giao diện rồi và chúng ta
[00:01:42] chỉ việc vào đó và code thôi. Mọi người có thể lấy link này và clone template về nhé.
[00:01:52] Git clone rồi clone về.
[00:01:59] Khi clone về chúng ta vào CD template frontend và chạy
[00:02:10] câu lệnh npm install để cài các thư viện cho frontend.
[00:02:23] Thì trong cái file package.json này này mình đã khai báo khá là đầy đủ những cái thư viện cần thiết.
[00:02:33] Đấy mọi người chỉ việc chạy cái file chạy cái câu lệnh npm install sẽ tự động
[00:02:40] các cái thư viện trong của dự án về đấy. Đấy.
[00:03:18] Ok, như vậy là chúng ta đã cài xong các cái thư viện rồi. Bây giờ chúng ta sẽ chạy thử dự án và kiểm tra trên trình duyệt xem nào.
[00:03:29] Dùng câu lệnh npm run dev.
[00:03:52] Rồi xem trên duyệt xem có chưa. Ah.
[00:04:35] Ok, chúng ta đã có giao diện rồi. Ờ tuy nhiên thì giao diện này thì mới chỉ là giao diện tĩnh thôi. Nó chỉ là một cái
[00:04:42] template thôi. Đấy. Ờ để có giao diện hoàn chỉnh thì chúng ta sẽ phải viết thêm logic. Ví dụ như là tích hợp
[00:04:52] ví này. Sau khi tích hợp ví và connect ví xong sẽ cho ra một cái giao diện cho người dùng, giao diện client
[00:04:59] người dùng. Đấy, còn đây là giao diện dành cho những cái đối tượng chưa connect ví. Đấy, bây giờ chúng ta sẽ quay lại source code của dự án này.
[00:05:22] Chúng ta sẽ xem lại cái giao diện nó có những cái gì nào.
[00:05:26] Đấy. Đấy, có các thư mục như là thư mục application này. Đấy, trong đấy có các định nghĩa layout.
[00:05:35] Đấy, có page đấy, có home content.
[00:05:41] Đấy, thì trong cái template này thì mình cũng đã soạn sẵn những cái
[00:05:49] to do để mọi người có thể hiểu được những cái bước mình sẽ thực hiện code logic. Đấy.
[00:06:00] Đấy. Layout này. Component thì có các modal để burn, mint form, và modal kế thừa đến các modal nhỏ.
[00:06:14] Đấy, list các NFT này, các cái provider đấy.
[00:06:20] transaction status để hiển thị thông tin giao dịch có thành công hay không.
[00:06:27] form gọi là để update metadata này.
[00:06:31] Trong đây thì cũng có các cái chú thích to do để hướng dẫn viết logic code này.
[00:06:38] Ừ đã có component wallet connect để thực hiện tích hợp wallet integration với ứng dụng.
[00:06:47] và context để thực hiện truyền dữ liệu của wallet trong cả ứng dụng này.
[00:06:55] Đấy, đây là đây là định nghĩa wallet API theo chuẩn CIP-30 dùng cho các dự án này.
[00:07:07] Đấy, bây giờ thì mình sẽ đi sâu vào code luôn.
[00:07:14] Đấy, bước đầu tiên chúng ta sẽ thực hiện bước wallet integration.
[00:07:21] Đầu tiên đó là vào file wallet context.
[00:07:25] Chúng ta sẽ vào hoàn thiện cái wallet context để thực hiện truyền cái các cái thông tin liên quan đến wallet trong
[00:07:34] bộ các cái trang của ừ giao diện của người dùng. Đấy thì ở đây thì mình cũng đã khởi tạo sẵn những cái state.
[00:07:46] Đấy. Tuy nhiên thì những cái logic như là lấy các cái thông tin như là kiểm tra
[00:07:53] trình duyệt có cái ví đã cài extension ví trên trình duyệt
[00:08:01] chưa này. Thứ hai đó là get cái address của wallet.
[00:08:07] Đấy thì đầu tiên thì chúng ta sẽ thực hiện hoàn thành cái todo 1 này.
[00:08:13] Đấy, mục tiêu của nó là kiểm tra các cái ví của Cardano đã được cài đặt trên trình duyệt hay chưa. Đấy, chúng ta sẽ khai
[00:08:23] const nhé. Đây đã có hàm sẵn rồi, viết vào đây.
[00:08:32] const useMemo trả về info này.
[00:08:39] typeof window === "undefined"
[00:08:46] hoặc window.cardano thì return rỗng này.
[00:08:59] Rồi tiếp theo là ừ
[00:09:07] supportedWallets này.
[00:09:19] Ừ mình thấy là cũng khá là tiện ấy. Xong tiếp theo là lọc này. wallet.available. Ok.
[00:09:30] xong phần kiểm tra xem trình duyệt đã cài các cái extension của các cái ví của Cardano hay chưa đấy. Đấy. Tiếp theo.
[00:09:47] Tiếp theo thì chúng ta sẽ thực hiện query address
[00:09:54] từ wallet.
[00:10:02] Đây đã có hàm này, get wallet address. Mình giải thích khá là chi tiết rồi.
[00:10:09] Đây const addressWallet const
[00:10:25] bằng API.
[00:10:30] used address nè. Khá là tiện. If address
[00:10:39] tại address
[00:10:47] address.Length > 0 nhé
[00:10:53] tại vị trí 0 và const unused address này.
[00:11:05] Get address này.
[00:11:09] If unused address.Length thì return này. Đấy.
[00:11:17] return. Ok.
[00:11:25] Thì
[00:11:42] sẽ giải thích một chút nhá. Theo chuẩn CIP-30 thì nó có ba loại address. Loại đầu tiên là used address.
[00:11:54] Đấy, theo chuẩn CIP mình giải thích một chút nhé.
[00:12:05] Giải thích một chút. Ừ.
[00:12:16] chuẩn CIP-30
[00:12:21] thì có ba loại address
[00:12:30] ba loại address này, đầu tiên là used address
[00:12:38] là đã từng giao dịch, thứ hai là unused address chưa từng giao dịch và thứ ba là
[00:12:46] reward address là nhận tiền thừa. Đấy thì mỗi wallet thì nó sẽ trả lại một cái format khác nhau.
[00:12:58] Đấy thì address của CIP-30 này sẽ trả về dạng hex.
[00:13:06] và backend sẽ phải convert cái này về
[00:13:12] thông qua API endpoint convert sang bech32. Đấy. Đấy.
[00:13:27] Tiếp theo thì chúng ta sẽ tiếp tục code phần connect wallet. Đấy. Thì ở đây cũng khá là chi tiết mình hướng dẫn từng bước
[00:13:35] Đầu tiên là check này xem có tồn tại hay không. Nếu như có thì lấy ID.
[00:13:42] Nếu không tồn tại thì trả về và set trạng thái chưa connect.
[00:13:46] Và tiếp theo là set các cái ừ các cái gì nhờ?
[00:13:55] Ừ state để dùng cho để dùng cho toàn bộ dự án. Đấy, triển khai thôi.
[00:14:07] Ừ, đầu tiên đó là connect wallet này. useCallback này. Đấy.
[00:14:17] if có wallet id thì kiểm tra tiếp.
[00:14:23] nếu không tồn tại wallet thì chúng ta sẽ báo ra.
[00:14:33] Đấy. Còn nếu nếu tồn tại thì chúng ta sẽ thực hiện gán cái wallet
[00:14:41] cái wallet này.
[00:14:54] Rồi nếu như wallet tồn tại thì chúng ta sẽ lấy cái wallet list đầu tiên này này.
[00:15:01] Nếu không tồn tại thì lại báo tiếp
[00:15:08] set connecting error bằng null. Rồi tiếp theo là
[00:15:20] const selected wallet
[00:15:26] Const address kiểu hex này.
[00:15:32] Rồi tiếp theo là set các cái state.
[00:15:41] Rồi tiếp theo là lưu wallet ID vào bộ nhớ local của trình
[00:15:50] local storage của trình duyệt
[00:15:59] thông báo ra đấy.
[00:16:06] Finally, set connecting bằng false. Ok,
[00:16:11] thực hiện xong cái connect wallet nhá. Hàm connect wallet. Tiếp theo disconnect wallet này.
[00:16:27] Disconnect wallet thì cũng tương tự. Viết tiếp vào đây mình đã
[00:16:33] ghi khá là chi tiết rồi. Sử dụng reset các state về rỗng hoặc null. Đấy.
[00:16:46] Rồi set error bằng null và localStorage remove xóa đi.
[00:16:55] Rồi tiếp theo thì chúng ta sẽ triển khai
[00:17:05] ờ cái ờ cái gì nhở? Hàm gọi là ký giao dịch.
[00:17:16] Đấy. Ứ chúng ta lại phải nhắc lại đấy. Thằng
[00:17:25] backend đấy. Nó sẽ trả về cái giao dịch trả về cái thông tin giao dịch đã build
[00:17:34] cho frontend và frontend nó sẽ ký cái giao dịch đấy. Đấy.
[00:17:45] Đây chúng ta sẽ triển khai vào đây. Đầu tiên là if wallet API.
[00:17:58] Rồi kiểm tra xem đã kết nối wallet chưa.
[00:18:14] xong return wallet API.
[00:18:26] Đấy, thì thông báo lỗi.
[00:18:38] bỏ cái true này đi.
[00:18:43] trong trong hàm catch đã bắt lỗi rồi.
[00:18:55] Rồi ở đây nhá mình sẽ giải thích lại một chút.
[00:19:04] Ờ cái function ký trans này này thì đầu vào nó chính là cái TX ở dạng đã được
[00:19:15] về sau khi người dùng gửi cái yêu cầu mint hay là update hay là burn ấy. Đấy
[00:19:22] cái TX này nó là cái transaction chưa có chữ ký đấy.
[00:19:34] Và khi nó thực hiện cái hàm này nó sẽ
[00:19:40] ra một chữ ký
[00:19:50] tạo ra một cái witness set đấy. chứa chữ ký đấy.
[00:20:23] chữ ký xong và gửi lại bên backend để xử lý hợp nhất chữ ký.
[00:21:13] Tiếp theo nhá, chúng ta sẽ viết thêm một cái hàm nữa là hàm auto reconnect.
[00:21:22] Đấy, thêm vào cuối này bằng useEffect.
[00:21:34] Reconnect useEffect, đọc saved wallet, lấy id.
[00:21:41] Nếu có wallet đã lưu thì chúng ta connect lại wallet đó.
[00:21:57] Điều này sẽ làm cho mỗi lần chúng ta ừ mở lại ứng dụng trên web ấy thì nó sẽ tự
[00:22:05] connect lại nếu như trong trình duyệt vẫn còn lưu wallet từ những lần kết nối trước đó.
[00:22:14] Ok. Sau khi chúng ta đã xử lý cái Wallet context rồi thì chúng ta sẽ đến với bước tiếp theo
[00:22:24] là code cái nút connect wallet.
[00:22:35] Ừ. để thực hiện thao tác
[00:22:43] bấm nút kết nối ví. Đấy thì chúng ta sẽ vào component connect và viết vào đây.
[00:22:54] Ừ connect wallet này. Đấy set drop down.
[00:23:03] Kết nối xong thì drop down bằng false. Đấy.
[00:23:12] Rồi rồi chúng ta sau khi set dropdown xong nhá.
[00:23:36] Rồi bây giờ chúng ta set dropdown xong chúng ta sẽ quay lại trình duyệt xem có gì khác không nhá. Tức là chúng ta đã thực hiện gọi đến cái gì nhở?
[00:23:49] hàm connect wallet ở trong cái context rồi đấy. Và đã gắn cái component
[00:23:57] cái giao diện người dùng rồi. Bây giờ chúng ta sẽ vào thử xem đã thực hiện được kết nối Wallet chưa.
[00:24:11] Đây kết nối ví này mình đang có ví đấy. chọn
[00:24:17] Ok. Giao diện đã có này. Đấy. Có thông tin của cái form để mint này rồi nhá. Đấy.
[00:24:28] Rồi chưa có NFT nào. Ngắt kết nối.
[00:24:35] Kết nối lại. Click. Rồi làm mới này. Không có gì. Ok chưa?
[00:24:43] Rồi chúng ta sẽ đến với bước tiếp theo.
[00:25:02] Bước tiếp theo của chúng ta đó là thực hiện cái xử lý các cái hành động
[00:25:10] giao dịch mint, update và burn. Đấy, đầu tiên vào mint trước đây. Thì đầu tiên thì
[00:25:18] ta sẽ phải thực hiện xây dựng
[00:25:24] quy trình xử lý phần mint bao gồm các phần như thu
[00:25:34] thông tin này, gửi cái yêu cầu mint lên backend và backend sẽ xử lý.
[00:25:46] xử lý trả về data này. Đấy. Thì bước đầu tiên
[00:25:53] ta sẽ thực hiện code phần kiểm tra.
[00:26:01] Kiểm tra xem đã connect wallet hay chưa. Đấy. Nếu connect wallet rồi thì
[00:26:09] báo kết nối wallet. Đấy, xong bắt đầu vào rồi. Try này.
[00:26:23] try/catch/finally đấy.
[00:26:31] Bước đầu tiên thì chúng ta sẽ test loading.
[00:26:39] Đấy, khi nhấn cái nút mint ấy nó sẽ mở một cái
[00:26:47] loading quay tạo hiệu ứng và set status để thông báo
[00:26:54] màn hình này. Đầu tiên là build transaction này.
[00:26:59] Đấy, response. Chúng ta sẽ định nghĩa một response và fetch cái
[00:27:05] API đây.
[00:27:15] Sẽ gọi đến endpoint API mint này là đúng chưa? API mint này.
[00:27:22] Đấy cái này method là post đấy. Method là
[00:27:33] là content type và application/json
[00:27:40] thì có kiểu là json.
[00:27:46] body này. Đấy,
[00:27:55] file thì thu thập các cái trường để gửi lên backend bao gồm wallet address
[00:28:02] token name là description này. Các trường này đã được thu thập thông qua các state này, token name, description này.
[00:28:11] Ok chưa? Rồi tiếp theo là đóng cái hàm này lại đã có respond.
[00:28:18] Tiếp theo thì lấy cái data từ cái phản hồi rồi.
[00:28:27] await response.json() này.
[00:28:47] không có gì thì thông báo lỗi này.
[00:28:53] Đấy bạn này thì hơi hơi ấy một chút nhá.
[00:28:57] Mình định nghĩa lại kiểu component mint này. Đấy,
[00:29:09] định nghĩa lại kiểu dữ liệu.
[00:30:14] Thôi cái đấy tí fix sau vậy. Bước thứ hai là bước ký giao dịch này.
[00:30:22] Ký giao dịch thì set status này.
[00:30:27] Đấy và thực hiện ký
[00:30:39] bước ba là submit giao dịch lại backend. Đấy lại tiếp tục set nè.
[00:30:47] Đấy lại tiếp tục submit response method.
[00:31:07] Và cuối cùng là in cái thông tin ra ngoài màn hình.
[00:31:13] Đấy. Tiếp theo là xét cái form rỗng
[00:31:21] thành công rồi.
[00:31:41] Rồi do mình thiếu dấu ngoặc đấy. Xong rồi nhá.
[00:31:50] Mình sẽ nói lại đoạn này một chút.
[00:31:53] Ừ. Đầu tiên thì chúng ta nói chung là mấy cái này là mấy cái hiển thị thôi. Đấy hiển thị nên
[00:32:01] sẽ không nói mấy cái này. Đầu tiên thì chúng ta sẽ gửi một cái request lên cái backend. Đấy, backend
[00:32:11] với yêu cầu gửi các thông tin như wallet, token và yêu cầu mint. Đấy, thằng API endpoint mint nhận
[00:32:20] request này và nó xử lý nó sẽ build transaction trong backend như lúc chúng ta đã
[00:32:29] lý lúc nãy đấy. Đấy. Và nó trả về trả về cái transaction unsigned. Đấy. Đây này. Trả về transaction unsigned.
[00:32:41] Đấy. Khi trả về transaction thì chúng ta sẽ gọi cái hàm sign TX này mà chúng
[00:32:48] đã xây dựng trong cái wallet context ấy. Đấy. Đây này. Wallet context đây này.
[00:32:57] Đây.
[00:32:59] Thì cái hàm này sẽ thực hiện ký giao dịch này.
[00:33:08] Đấy và nó chủ động cập nhật cái witness set trong cái tx này này.
[00:33:17] Đấy.
[00:33:21] Và sau khi chúng ta ký xong, tức là cái giao dịch đã có chữ ký rồi thì chúng ta
[00:33:28] lại gửi lại cái đã có witness set đấy.
[00:33:36] Lên cái gì nhở?
[00:33:39] cái backend để backend thực hiện merge chữ ký và submit lên on-chain. Đấy mình nhắc lại một lần nữa nhá.
[00:33:50] Đầu tiên frontend gửi yêu cầu mint này bao gồm thông tin token và description này. Sau đó thì
[00:33:59] sẽ trả về cái ờ cấu trúc ừ response bao gồm các cái trường như là TX Body đấy.
[00:34:10] Ờ TX body này ờ TX witness set này được gói
[00:34:17] tx đấy. Witness set này sẽ thực hiện ký vào đấy.
[00:34:26] Đấy.
[00:34:29] Ký vào và nó tiếp tục nó gửi lại cái witness set CBOR cho backend.
[00:34:40] witness set nó sẽ xử lý chữ ký bên backend ấy. Nó sẽ ừ lấy cái chữ ký của
[00:34:47] wallet đã ký ấy trong cái witness set và nó gộp vào transaction và nó thực hiện submit lên giao dịch.
[00:35:08] Đây chúng ta có thể xem lại cái hàm ký này.
[00:35:16] Đấy.
[00:35:20] Đây là của cái API CIP-30
[00:35:33] Đấy. Đấy.
[00:35:41] Mình sẽ nhắc lại một lần nữa. Dự án này khó ở phần xử lý tách giao dịch. Đấy.
[00:35:52] Làm sao để khi gửi về frontend chúng ta sẽ có thể ký được ký được cái giao dịch đó và chuyển về
[00:35:59] rồi chuyển về backend. Backend sẽ lấy chữ ký, gộp vào giao dịch và submit lên on-chain.
[00:36:08] Ok, như vậy là chúng ta đã xong phần triển khai logic mint.
[00:36:31] Triển khai xong cái logic mint này rồi nhá.
[00:36:34] Chúng ta sẽ tiếp theo là chúng ta sẽ đến phần
[00:36:45] Thì tương tự như vậy, chúng ta vào update modal này và tiếp tục triển khai logic.
[00:36:55] Đầu tiên vẫn là try catch.
[00:37:26] Đầu tiên vẫn là xét các cái hiệu ứng đấy.
[00:37:39] Rồi gửi request AP này API P này.
[00:37:54] Chúng ta sẽ gửi lên token name và wallet address.
[00:38:00] À đâu cái này là burn chứ mình nhầm mình nhầm.
[00:38:09] Update đây. Update đây. Update đây.
[00:38:17] Bằng update. Đấy.
[00:38:25] Rồi lấy data lại tiếp tục xử lý chữ ký thôi.
[00:38:35] Rồi tiếp tục.
[00:38:47] Tiếp tục lấy ra chữ ký này và thực hiện ký.
[00:39:07] Ừ, mình sẽ nhắc lại một lần nữa thì cái tx ấy nó sẽ có hai thành phần. Thành
[00:39:17] đầu tiên đó là TX body và witness set. Đấy. Thì cái hàm hàm sign TX này
[00:39:26] Đấy. Cái hàm sign TX này nó sẽ tự xử lý
[00:39:34] cái ký cho chúng ta đấy. Tự xử lý ký cho
[00:39:40] ta vào cái tx trả về đây này. Và nó sẽ trả ra cái witness set đã bao gồm
[00:39:49] ký của wallet. Đấy, mình sẽ nhắc lại một lần nữa để mọi người nắm bắt chi tiết hơn.
[00:39:57] Vì nãy trong phần mint ấy mình cảm thấy là mình nói chưa thực sự clear. Đấy, tức
[00:40:04] cái hàm sign TX này đấy, đầu vào tham số của nó là cái transaction,
[00:40:14] là full cái transaction ở dạng JSON mà chúng ta đã xử lý bên backend đấy.
[00:40:22] Thì nó sẽ nhận vào là cái transaction dạng CBOR nó sẽ chủ động xử lý ký và trả
[00:40:30] cái witness set. Đấy, thì sau khi hàm này nó chạy xong rồi này, chúng ta không cần quan tâm nó xử lý như thế nào nhá.
[00:40:40] Đấy, chúng ta chỉ quan tâm là chúng ta cho nó vào đầu vào của nó là transaction
[00:40:46] ở dạng đã được xử lý bên backend. Đấy, đầu vào là transaction là dạng CBOR đã xử lý bên backend.
[00:40:56] Và nó kết quả của nó cho ra witness set đã có chữ ký của wallet. Đấy mọi người chỉ cần hiểu thế thôi.
[00:41:06] Sau đó sau khi có witness set rồi nhá.
[00:41:12] Tiếp theo bước tiếp theo này. Đấy chúng ta sẽ lại submit một lần nữa cái
[00:41:22] transaction CBOR này quay lại backend.
[00:41:25] cái witness set CBOR đấy. Tức là cái cái này này nó sẽ tự xử
[00:41:33] cho chúng ta để cho ra một cái đối tượng gọi là witness set. Đấy để chúng ta chuyển lại trong cái đối tượng
[00:41:42] set đấy. Nó sẽ có chữ ký của wallet.
[00:41:48] Mọi người chưa? Có cần mình mở lại code backend để nói lại không? Ok. Mở lại code backend để nói lại một chút nhá.
[00:41:58] Đây đâu nhở? Xử lý chữ ký nhận về cái
[00:42:07] cầu submit đâu nhỉ? Đây nhá. Nói lại cái đoạn này đây nhá. transaction CBOR này này. Nó là cái transaction có hai thành phần body và witness set. Đấy.
[00:42:19] Đấy. Thì quay lại đây thì nó sẽ trả về
[00:42:26] trả về cái gì nhờ? Đây cái response này nó sẽ trả về cái tx chính là cái thằng này.
[00:42:39] Đấy đã được chuyển sang CBOR.
[00:42:42] Thì trong cái thằng này nó sẽ có hai cái đối tượng là TX body và witness set.
[00:42:48] Đấy thì khi thằng này nó xử lý cái hàm sign này này, nó xử lý cái kiểu dữ liệu
[00:42:54] CBOR này, nó sẽ tự xử lý và trả ra cho chúng ta cái kiểu dữ liệu witness set đã có cái vkey.
[00:43:05] Chúng ta không cần quan tâm nó xử lý như thế nào đâu. Đây là thư viện người ta làm, thư viện người ta thực hiện. Chúng ta không cần quan tâm, chúng ta chỉ cần
[00:43:14] tâm cái hàm sign này nó nhận vào là một đối tượng transaction ở dạng CBOR
[00:43:22] nó trả ra cho chúng ta đối tượng witness set. Đấy, witness set này nó sẽ có vkey của wallet đã được ký. Đấy, ok.
[00:43:32] Đấy. Thì cái hàm sau khi chúng ta ký xong nhá là chúng ta submit lại này.
[00:43:40] Đấy, submit lại.
[00:43:44] Ký xong chúng ta submit lại. Đây, submit lại đây. Đúng không? Request này cái này thì
[00:43:52] TX là full các cái TX. Đấy, thì chúng ta gắn nhá. Còn cái wallet witness
[00:43:59] đấy thì nó sẽ lấy cái current witness này và nó gán vào cái wallet witness set này.
[00:44:08] Đấy thì trong cái wallet witness này sẽ nó sẽ có cái vkey chúng ta đã ký đấy. Đấy
[00:44:25] Xong cái a tx này bởi vì nó được cấu tạo bởi hai
[00:44:33] phần đúng không? transaction body và transaction witness set. Đấy thì sau khi chúng ta đã gộp cái chữ ký từ
[00:44:40] wallet người dùng gửi lên rồi thì nó sẽ gộp vào đây. Nó thay thế cái witness set ban đầu kia kìa.
[00:44:51] Đấy mình nói khá là chi tiết như vậy cũng mong là cũng mọi người sẽ hiểu rõ
[00:44:59] Đấy. Ok. Tiếp theo là submit data.
[00:45:06] Submit data này kiểm tra xem có success hay không.
[00:45:12] Đấy nhá.
[00:45:19] success không? Nếu success thì chúng ta sẽ thực hiện close bỏ cái
[00:45:28] đó đi rồi và phát bỏ.
[00:45:42] Ok. Ừ.
[00:45:51] Ok, đã xong phần update nhá.
[00:45:58] Đã xong logic phần update. Tiếp theo thì chúng ta sẽ vào phần logic B. Thì cũng
[00:46:05] khác gì mấy trong phần logic B này thì vẫn là gửi cái yêu cầu burn lên bao
[00:46:12] những cái thông tin như là token muốn burn chẳng hạn.
[00:46:19] Đầu tiên vẫn phải thêm các bước loading cho giao diện có trải nghiệm mượt mà. Ok. Gửi request.
[00:46:32] Ừ. burn này gửi endpoint là burn API burn này tham số yêu cầu là token này tiếp
[00:46:42] là nhận về data phản hồi
[00:46:50] tiếp theo là nếu data success
[00:46:58] hiển thị.
[00:47:03] Còn nếu không thì vẫn lấy
[00:47:12] set ra và thực hiện ký và trả về witness set đã có chữ ký đấy. Gọi lại
[00:47:19] lại giao dịch đây. Submit lại tx
[00:47:26] để gán lại cái transaction và witness set
[00:47:30] để gộp cái chữ ký vào tx sau đó rồi lấy ra cái thông tin kết quả.
[00:47:43] Và bây giờ là thông báo và thoát form.
[00:47:53] Ok.
[00:47:58] Rồi sau khi chúng ta đã viết sang viết xong một số các cái logic của cái
[00:48:06] phần logic mint và update ấy thì chúng ta sẽ có thêm một
[00:48:15] bổ trợ cho cái giao diện của chúng ta như là hiển thị các cái asset theo chuẩn CIP-68 trong ví của chúng ta.
[00:48:24] Đấy, chúng ta sẽ thực hiện đây nào. Đây triển khai ở đây.
[00:48:32] Rồi đầu tiên sẽ loading này. Đấy, try/catch.
[00:48:50] Rồi đầu tiên đó là gửi request lên
[00:48:57] nhận lại response
[00:49:05] này. Endpoint là API wallet, địa chỉ wallet này.
[00:49:16] Đấy.
[00:49:17] Rồi tiếp theo đó là nhận lại data và nếu như không thành công thì return rỗng.
[00:49:29] Còn tiếp theo là xử lý prefix này. Đấy,
[00:49:35] những cái asset có prefix là user token prefix
[00:49:44] decode ra dạng
[00:49:52] thể đọc token name đấy.
[00:50:06] Rồi tức là tên thì lấy là tên asset nhưng mà hiển thị là hiển thị cho dễ đọc nhá.
[00:50:15] Đấy. Sau đấy thì set state rồi tiếp theo là load thôi.
[00:50:27] Rồi chúng ta đã lấy xong.
[00:50:34] Rồi tiếp theo có một số các cái phần như là cần phải load metadata
[00:50:42] từng cái token một chúng ta cũng phải viết. Đấy.
[00:50:49] Đây try/catch.
[00:51:06] Đầu tiên thì chúng ta cũng phải query từ backend những cái metadata theo token name.
[00:51:16] Đấy.
[00:51:19] Tiếp theo là parse ra.
[00:51:27] Và nếu như thành công thì description sau đó thì xử lý metadata.
[00:51:40] Nếu metadata có trường description
[00:51:52] metadata
[00:52:07] nếu không phải thì để mặc định.
[00:52:12] Rồi tiếp theo là xét danh sách Đ
[00:52:45] Ok.
[00:53:00] Tiếp theo thì chúng ta sẽ code thêm một cái hàm gọi là hàm auto refresh khi mà
[00:53:07] NFT thay đổi. Khi asset thay đổi thì gọi hàm effect.
[00:53:15] Đấy.
[00:53:18] Rồi. Ok. Sau khi chúng ta đã hoàn thành xong các cái component rồi bao gồm các
[00:53:26] component để phục vụ cho quá trình mint này.
[00:53:32] update này và burn
[00:53:38] list các cái asset và
[00:53:44] các cái metadata, hiển thị metadata thì chúng ta sẽ tiếp theo đó là thực hiện
[00:53:53] convert địa chỉ và
[00:54:03] cái địa chỉ vào backend. Đấy, vì là theo chuẩn CIP-30 ấy, địa chỉ nó là địa chỉ dạng hex.
[00:54:13] Đấy, nên chúng ta cũng phải chuyển nó thành dạng.
[00:54:18] Rồi chúng ta sẽ vào file Home Context này và thực hiện chuyển.
[00:54:26] Đầu tiên thì chúng ta sẽ phải check.
[00:54:52] Ừ. Gửi request lên yêu cầu convert đấy.
[00:55:03] Return này. Return này hình như trong ít đúng không? Ok.
[00:55:09] Rồi tiếp theo là lấy ra data. Đấy.
[00:55:16] Và nếu data success thì
[00:55:25] Ok. Tiếp theo thì có một số các cái
[00:55:32] tính năng như lấy thông tin script từ backend như policy ID và store address.
[00:55:45] Chúng ta sẽ thực hiện luôn.
[00:55:54] Vẫn là try. Try này.
[00:56:03] Backend. Đấy,
[00:56:11] là gửi request này.
[00:56:14] Đấy, lấy data và set script info.
[00:56:33] Rồi script info đã khai báo chưa?
[00:56:56] info này.
[00:57:33] Sao cái này lại không dùng được add script info đ Ah
[00:58:09] address này.
[00:58:22] Rồi mình thừa một giống ngoặc. Ok, xong rồi.
[00:58:34] Như vậy là chúng ta đã code xong phần
[00:58:41] giao diện. Mình sẽ tổng kết lại một chút phần code
[00:58:47] đầu tiên. Đấy. Ừ. chúng ta đã vào thiết lập
[00:58:55] các cái hàm trong phần Wallet Context để sử dụng trong toàn bộ ứng dụng bao gồm như là
[00:59:03] kiểm tra xem trình duyệt đã cài đặt các cái extension cho các ví của Cardano
[00:59:11] chưa. Đấy. Thứ hai đó là lấy address
[00:59:18] CIP-30 trả về dạng hex, dạng bytes. Đấy. Đấy. Tiếp theo đấy là
[00:59:28] ta sẽ thực hiện viết hàm connect wallet.
[00:59:37] Và disconnect wallet, rồi viết hàm ký giao dịch.
[00:59:46] Đấy, ký giao dịch thì đầu vào của nó là transaction ở dạng CBOR và nó sẽ trả về cái witness set. Đấy,
[01:00:01] từ cái witness set đấy, chúng ta sẽ gửi lại backend để backend thực hiện gộp cái witness set vào cái witness set trong transaction.
[01:00:13] Đấy để cái submit giao dịch.
[01:00:18] Đấy sau đó chúng ta cũng đã gọi hàm connect wallet trong component connect wallet.
[01:00:33] Đấy. Rồi tiếp theo thì chúng ta cũng đã viết logic phần mint.
[01:00:41] Đấy, phần mint thì lộ trình của nó đấy là gửi yêu cầu lên là mint 1 asset theo
[01:00:49] CIP-68 ở bên backend với các tham số là token name và description
[01:00:56] và nhận về data phản hồi. Đấy, phản hồi này chứa transaction dạng CBOR chưa có chữ ký.
[01:01:06] sau đó dùng hàm sign TX để ký và trả về
[01:01:14] cái witness set. Đấy, witness set tiếp tục được submit lại trên backend
[01:01:21] với cái transaction CBOR này. Và bên backend sẽ thực hiện gộp cái witness set
[01:01:28] có cái chữ ký của ví vào transaction CBOR và submit lên on-chain. Đấy,
[01:01:36] với update cũng như vậy,
[01:01:43] tương tự và burn cũng tương tự.
[01:01:47] Rồi sau khi chúng ta đã xong thì chúng ta có thêm một bước xử lý nhỏ nữa đó là
[01:01:53] các cái asset của người dùng đấy theo chuẩn CIP-68.
[01:02:05] xử lý hiển thị metadata.
[01:02:12] Rồi như vậy đã xong
[01:02:21] xong phần code đấy. Đấy.
[01:02:48] Chúng ta đã xong phần code frontend rồi.

## Part 4 - Frontend demo
- Video link: https://www.youtube.com/watch?v=SJJrgRPWdu0

[00:00:00] Ok.
[00:00:04] Sau khi chúng ta đã code xong frontend rồi thì mình sẽ thực hiện demo ngay trên giao diện luôn.
[00:00:12] Đầu tiên thì chúng ta sẽ test thử tính năng mint xem nào.
[00:00:17] Demo demo mint ờ 1102 này.
[00:00:26] Demo minấy mint submit giao dịch.
[00:00:38] Ok. Đợi ký giao dịch. Confirm.
[00:00:46] Confirm.
[00:00:49] Đấy, giao dịch đã được mint thành công rồi. Chúng ta sẽ đợi để nó submit lên blockchain và nó sẽ cập nhật lại danh
[00:00:58] cái cái các cái CIP-68 NFT của chúng ta. Chúng ta sẽ đợi.
[00:01:07] Đấy,
[00:01:09] diện cũng mình cũng chỉ thiết kế cái giao diện làm sao đủ dùng thôi.
[00:01:36] Ok.
[00:01:37] Ờ như vậy là ừ giao diện của chúng ta đã cập nhật thêm cái
[00:01:45] mới rồi này. Mọi người có thể nhìn thấy nhá. Demo mint này version 1 nhá.
[00:01:51] Đấy. Bây giờ chúng ta sẽ thử tính năng update metadata xem nào. Update metadata đấy.
[00:01:59] Thử V2 đi. Cập nhật.
[00:02:14] Confirm cái giao dịch. Confirm.
[00:02:21] Ok. Xem nào. Thành công. Metadata đã được cập nhật. Chúng ta sẽ đợi để nó cập nhật xem nào.
[00:02:58] Check trên Cardanoscan xem vẫn chưa có
[00:03:25] chúng ta làm mới lại xem nào.
[00:03:28] chuyển sang Version 2. Ok chưa? Rồi bây giờ chúng ta sẽ test tính năng burn
[00:03:35] B đây. Tôi đồng ý muốn xóa này. Xóa NFT này. Đợi và ký giao dịch thôi.
[00:03:57] Rồi xem nào.
[00:04:00] NFT đã được burn. Ok. Chúng ta sẽ đợi một lúc. để giao dịch được submit lên on-chain
[00:04:24] đợi thì mình sẽ mở lại cái slide để Ừ,
[00:04:35] lại cái slide để trình bày lại cho mọi người tổng kết lại cái bài học về chuẩn CIP-68 của chúng ta.
[00:04:46] Đấy, làm mới xem nào. Ok,
[00:04:57] burn thành công rồi. Chúng ta xem lại trên Cardanoscan xem.
[00:05:04] Ok, như vậy là giao dịch đã được burn thành công là số lượng đã thành -1 này.
[00:05:11] Đấy. Rồi bây giờ mình sẽ
[00:05:18] tổng kết lại một chút về cái bài học của chúng ta trong cái chuỗi ờ ví dụ thực tế
[00:05:28] triển khai toàn bộ một quy trình chuẩn CIP-68 Dynamic Asset
[00:05:37] NFT trên Cardano nó như thế nào rồi như vậy thì trong Cái chuỗi video mà mình
[00:05:44] hướng dẫn về cái CIP-68 này thì mọi người cũng đã hiểu được về cơ chế
[00:05:50] động của CIP-68. Đấy, mục đích của nó sinh ra là giải quyết cái vấn đề
[00:05:57] là nếu như chúng ta gắn metadata kèm theo cái transaction khi chúng ta thực
[00:06:04] giao dịch mint các cái token hoặc là asset trên hệ sinh thái thì nó sẽ tạo
[00:06:11] một cái hạn chế đó là metadata đấy không thể cập nhật được. Đấy, cái CIP-68 nó được sinh ra nhằm khắc phục cái
[00:06:20] đề đó. Đấy giúp chúng ta có thể update metadata một cách dễ dàng hơn thông qua cái cơ chế đó là mint một cặp
[00:06:29] đấy một token là user token được
[00:06:38] về ví của chúng ta còn một token gọi là reference token ứ token đó sẽ
[00:06:44] metadata được lưu trong datum đấy và chúng ta có thể cập nhật metadata
[00:06:52] qua cách cập nhật datum và ờ cập nhật datum trong UTxO chứa ref token
[00:06:59] đấy và trong cái chuỗi video hướng dẫn thì mình cũng đã ừ mô tả khá
[00:07:09] chi tiết về quy trình triển khai một cái ví dụ thực tế bao gồm đầu tiên đó là triển khai hợp đồng thông minh
[00:07:18] này đấy mình cũng đã ờ chia sẻ khá là chi tiết trong cái logic thiết kế hợp đồng thông minh như
[00:07:27] nào, thiết kế datum hay là thiết kế redeemer như thế nào. Rồi thứ hai đó là thực hiện code off-chain để tương tác với
[00:07:36] đồng thông minh bao gồm các tính năng như mint này, update metadata và burn.
[00:07:41] Đấy và cuối cùng là video lần này video khá là dài đó là xây dựng một ứng dụng
[00:07:49] stack dApp đấy có giao diện đấy mọi người có thể mint update và burn cái
[00:07:57] CIP-68 này trên giao diện đấy như vậy thì trong chuỗi video vừa rồi thì mình cũng đã chia sẻ cho các bạn khá
[00:08:05] chi tiết mong rằng cái những cái hiểu biết những cái thực hành về cái chuẩn
[00:08:13] CIP-68 này nó sẽ mang lại cho các bạn nhiều kiến thức bổ ích. Sau này các bạn ờ sẽ bước vào quy trình xây dựng các ứng
[00:08:21] thực tế trên Cardano và áp dụng các cái chuẩn CIP-68 này. Thì mình rất
[00:08:29] ơn mọi người đã theo dõi các video giảng dạy của bọn mình.
[00:08:34] Về thời lượng thì nó khá là dài rồi nên mình cũng xin phép kết thúc video tại đây. Mình xin cảm ơn mọi người và mình xin chào mọi người.



















