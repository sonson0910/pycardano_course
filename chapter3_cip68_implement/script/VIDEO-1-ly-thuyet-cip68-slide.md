Dưới đây là kịch bản (script) chi tiết dựa trên toàn bộ nội dung lời nói của bạn trong video thuyết trình về **Lý thuyết CIP-68**.

---

### 🎙️ SCRIPT CHI TIẾT: LÝ THUYẾT CIP-68 (DYNAMIC NFT)

Dưới đây là bản kịch bản (script) đầy đủ đã được hiệu chỉnh lỗi chính tả, các thuật ngữ chuyên môn (Cardano, CIP-68, UTxO...) và trình bày chuyên nghiệp, giữ đúng mốc thời gian như video của bạn.

---

**0:06 - 0:51 | Mở đầu**
Xin chào mọi người. Chào mừng mọi người đã quay trở lại với chuỗi video hướng dẫn lập trình **PyCardano** của chúng tôi. Ngày hôm nay, chúng ta sẽ tiếp tục với các bài học liên quan đến **Chương 3**. Đây sẽ là những bài học khá quan trọng và hữu ích, vì thế mọi người hãy chú ý theo dõi. 

Trong chương này, chúng ta sẽ đi sâu vào một chuỗi các bài giảng về chuẩn **CIP-68**, hay còn gọi là **Dynamic NFT (NFT động)**.

**0:51 - 1:25 | Nội dung video đầu tiên**
Trong video đầu tiên của chuỗi này, mình sẽ chia sẻ những nội dung lý thuyết cần thiết cũng như quy trình triển khai một ví dụ thực tế liên quan đến chuẩn CIP-68 Dynamic NFT. Cụ thể, mình sẽ trình bày phần lý thuyết cốt lõi và định hướng triển khai các tính năng: Mint (Đúc), Update (Cập nhật) và Burn (Đốt).

**1:25 - 2:23 | Vấn đề của chuẩn cũ CIP-25**
Đầu tiên, chúng ta vào Phần 1: Lý thuyết về CIP-68. Tại sao người ta lại sinh ra chuẩn CIP-68? Điều này xuất phát từ những hạn chế của chuẩn **CIP-25** hiện đang được sử dụng phổ biến. 

Với CIP-25, cơ chế là **Metadata** được ghi trực tiếp vào **Transaction Metadata** (nhãn 721) dưới dạng JSON. Hậu quả là nó gây ra sự **bất biến** về khả năng sửa đổi. Khi giao dịch đã được submit lên chuỗi, metadata không thể thay đổi được nữa do đặc tính của blockchain.

**2:23 - 3:39 | Những hạn chế về chi phí và lịch sử**
Thứ hai là vấn đề chi phí. Nếu muốn cập nhật thông tin — ví dụ như bạn lập trình game và nhân vật cần tăng level — bạn bắt buộc phải Mint lại NFT mới và Burn cái cũ. Công đoạn này vừa tốn thời gian, vừa tốn phí giao dịch. Ngoài ra, việc Mint lại làm mất đi tính liên tục và lịch sử của tài sản. 

Mọi người có thể nhìn sơ đồ bên phải: Metadata được đính kèm trong Block dưới dạng cấu trúc JSON chứa các giá trị thuộc tính, dính liền với giao dịch Mint ban đầu.


**3:39 - 5:35 | Ý tưởng cốt lõi của CIP-68: Tách biệt quyền sở hữu và dữ liệu**
Để giải quyết những hạn chế đó, chuẩn CIP-68 đã ra đời. Ý tưởng cốt lõi là **tách biệt quyền sở hữu và dữ liệu**. Nó tạo ra một cặp đôi token (Token Pair) gồm:
1. **User Token (Label 222):** Nằm trong ví người dùng, đại diện cho quyền sở hữu NFT. Nó có tiền tố (prefix) là 222.
2. **Reference Token (Label 100):** Token tham chiếu này nằm tại địa chỉ hợp đồng (Script Address). Đây mới chính là nơi chứa Metadata, cụ thể là được lưu trong **Datum** của UTxO chứa Reference Token.

Mối liên hệ giữa hai token này là chúng có cùng **Policy ID** và cùng **Asset Name** (phần tên sau prefix).

**5:35 - 6:51 | Cơ chế hoạt động của CIP-68**
Khi thực hiện Mint, hệ thống đồng thời tạo ra cả User Token và Reference Token. Reference Token sẽ nằm trên Smart Contract. Mỗi khi muốn cập nhật Metadata, chúng ta chỉ cần cập nhật Datum bằng cơ chế: Chi tiêu (spend) UTxO chứa Reference Token cũ và tạo ra một UTxO mới chứa Reference Token đó nhưng mang **Datum mới**, sau đó gửi lại địa chỉ hợp đồng.

**6:51 - 8:54 | Tại sao gọi là "Dynamic"?**
Chúng ta gọi là **Dynamic (Động)** vì thông tin có thể sửa đổi mà **không chạm vào User Token** trong ví người dùng. 

Mọi người có thể hình dung qua sơ đồ: Chủ sở hữu dùng Private Key ký xác thực để chi tiêu UTxO cũ (ví dụ đang ở Level 1) và tạo ra UTxO mới với trạng thái mới (ví dụ Level 99). Reference Token vẫn giữ nguyên, chỉ có dữ liệu trong Datum là thay đổi.

**8:54 - 11:42 | Ứng dụng thực tế**
Tính chất này rất hữu ích trong thực tế:
* **Blockchain Game:** Cập nhật chỉ số vũ khí, cấp độ nhân vật, độ bền trang bị (ví dụ sửa chữa xe đua).
* **RWA (Tài sản thực):** NFT nhà đất cập nhật giá cả, tình trạng quy hoạch, trạng thái thuê/bán khi đổi chủ.
* **Supply Chain:** Cập nhật vị trí lô hàng theo thời gian thực (từ nhà máy, cảng biển đến kho hàng).
* **Định danh & Thương mại:** NFT bằng tốt nghiệp có thể cập nhật thêm chứng chỉ mới; thẻ thành viên tự động đổi cấp độ khi tích lũy đủ điểm.

**11:42 - 13:57 | Hướng dẫn triển khai kỹ thuật**
Tiếp theo, mình sẽ hướng dẫn cách triển khai một ví dụ xây dựng hợp đồng bao gồm: Mint, Update và Burn. 
Ý tưởng là dùng logic Smart Contract (Plutus/Aiken) để tạo **Minting Policy** và một **Store Script** để lưu trữ UTxO có Datum. 

Thiết kế Datum sẽ bao gồm các trường: `policy_id`, `asset_name` (để định danh), `owner` (lưu Hash ví người dùng - đây là chìa khóa xác thực quyền update), `metadata` và `version`.

**13:57 - 15:52 | Minting Policy Script**
Khác với các bài học trước dùng Native Script đơn giản, lần này chúng ta dùng **Minting Policy Script** dựa trên logic hợp đồng thông minh để đảm bảo tính toàn vẹn:
1. **Khi Mint:** Bắt buộc tạo ra đồng thời đúng 1 User Token và 1 Reference Token.
2. **Khi Burn:** Bắt buộc phải đốt cả cặp token này (số lượng thay đổi là -1).
Hệ thống sẽ tự động tính toán prefix (100 và 222) dựa trên tên token người dùng nhập vào.

**15:52 - 17:25 | Store Script và Logic cập nhật**
**Store Script** là nơi trú ngụ của Reference Token. Logic của nó gồm:
* **Kiểm tra (Checker):** Chỉ cho phép chi tiêu UTxO nếu giao dịch có chữ ký của đúng chủ sở hữu được ghi trong Datum.
* **Bổ sung:** Output mới phải giữ nguyên các trường định danh của token, chỉ cho phép thay đổi Metadata và Version.

**17:25 - 19:25 | Cơ chế hoạt động Off-chain**
Về phần Off-chain (mã xử lý bên ngoài), chúng ta cần code cho cả 3 quy trình:
1. **Quy trình Mint:** Tính prefix, tạo Metadata/Datum, build giao dịch gửi User Token về ví và Ref Token lên Script.
2. **Quy trình Update:** Tìm UTxO chứa Ref Token trên hợp đồng, kiểm tra quyền, tạo Datum mới, spend UTxO cũ và tạo UTxO mới.
3. **Quy trình Burn:** Tìm cả hai token, gom chúng lại và thực hiện giao dịch đốt.

**19:25 - 21:58 | Kiến trúc Fullstack (Assembly Pattern)**
Phần phức tạp nhất là xây dựng ứng dụng Fullstack (có giao diện, backend và hợp đồng). Thông thường chúng ta dùng Lucid hoặc MeshJS trên Frontend. Tuy nhiên, hiện tại Frontend chưa có thư viện hỗ trợ đầy đủ cho **PyCardano**.

Giải pháp của mình là xây dựng **Backend bằng Python (FastAPI)** sử dụng thư viện PyCardano để xử lý logic và build giao dịch. **Frontend (NextJS)** sẽ thu thập thông tin người dùng (như nhập tên NFT, sửa metadata) và thực hiện ký giao dịch.

**21:58 - 24:44 | Tại sao cần Backend?**
Mô hình này gọi là **Assembly Pattern**: 
1. Frontend gửi yêu cầu (Request).
2. Backend build giao dịch chưa ký (Unsigned Tx) dưới dạng **CBOR** và trả về.
3. Frontend dùng chuẩn **CIP-30** để yêu cầu ví người dùng ký, thu về **Witness**.
4. Frontend gửi Witness về Backend. Backend ghép chữ ký vào giao dịch và thực hiện **Submit** lên mạng lưới.


**24:44 - Kết thúc | Tổng kết và Video sau**
Vừa rồi mình đã chia sẻ để mọi người hiểu về cơ chế hoạt động của chuẩn CIP-68 Dynamic NFT và quy trình triển khai thực tế. 

Trong các video tiếp theo, mình sẽ thực hiện chi tiết từng bước: từ triển khai Smart Contract, viết code Off-chain tương tác, cho đến xây dựng ứng dụng DApp hoàn chỉnh. Phần này mới chỉ là lý thuyết, phần thực hành sẽ có trong các video tới. Mong các bạn tiếp tục đón xem. Xin chào và hẹn gặp lại!
