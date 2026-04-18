Dưới đây là kịch bản (script) chi tiết dựa trên toàn bộ nội dung lời nói của bạn trong video thuyết trình về **Lý thuyết CIP-68**.

---

### 🎙️ SCRIPT CHI TIẾT: LÝ THUYẾT CIP-68 (DYNAMIC NFT)

#### 1. Mở đầu và Giới thiệu
* **[[00:15]]** Chào mừng các bạn đã quay trở lại với khóa học lập trình Cardano sử dụng thư viện PyCardano. Tôi là thành viên của Venera Lab.
* **[[00:30]]** Trong chương 3 này, chúng ta sẽ cùng nhau tìm hiểu về một tiêu chuẩn rất quan trọng và đang là xu hướng hiện nay trên Cardano: **Chuẩn CIP-68 (Dynamic NFT)**.
* **[[01:18]]** Nội dung chính của buổi hôm nay gồm 2 phần:
    1.  Lý thuyết cốt lõi về CIP-68.
    2.  Triển khai ví dụ thực tế (Mint, Update, Burn).

---

#### 2. Vấn đề của chuẩn cũ CIP-25
* **[[01:26]]** Trước khi nói về CIP-68, chúng ta hãy nhìn lại chuẩn cũ **CIP-25**. Đây là chuẩn NFT đời đầu, nơi mà metadata được lưu trữ trực tiếp trong phần Transaction Metadata của giao dịch đúc (Mint).
* **[[01:45]]** **Hệ quả của CIP-25:**
    * **Bất biến:** Một khi đã lên chuỗi, metadata không thể sửa đổi.
    * **Tốn kém:** Nếu muốn nâng cấp NFT (ví dụ nhân vật game lên level), bạn phải đốt NFT cũ và đúc lại cái mới hoàn toàn.
    * **Mất lịch sử:** Việc đúc lại làm đứt gãy tính liên tục của tài sản trên blockchain.

---

#### 3. Giải pháp CIP-68 (Dynamic NFT)
* **[[03:39]]** **Ý tưởng cốt lõi:** CIP-68 tách biệt hoàn toàn giữa **"Quyền sở hữu"** và **"Dữ liệu"**. Để làm được điều này, nó sử dụng một **cặp đôi Token (Token Pair)**:
    1.  **User Token (Prefix 222):** Nằm trong ví người dùng, đại diện cho quyền sở hữu NFT.
    2.  **Reference Token (Prefix 100):** Luôn nằm tại địa chỉ hợp đồng (Script Address). Đây là "hộp chứa dữ liệu" (Datum) chứa Metadata thực sự.
* **[[05:33]]** Hai token này được liên kết với nhau thông qua cùng một Policy ID và cùng Asset Name, chỉ khác tiền tố (Prefix).

---

#### 4. Cơ chế cập nhật Metadata (Update)
* **[[06:53]]** Tại sao gọi là Dynamic? Vì chúng ta có thể thay đổi Metadata mà **không chạm vào User Token** trong ví người dùng.
* **[[08:11]]** **Quy trình Update:**
    1.  Gửi một giao dịch để tiêu thụ (Spend) UTxO chứa Reference Token tại Script Address.
    2.  Xác thực quyền cập nhật (thường thông qua chữ ký của Owner được lưu trong Datum).
    3.  Tạo ra một UTxO mới cũng chứa Reference Token đó nhưng mang Datum mới (dữ liệu đã được cập nhật).

---

#### 5. Ứng dụng thực tế
* **[[08:54]]** **Gaming:** Vật phẩm tiến hóa, tăng chỉ số damage hoặc độ bền sau mỗi trận đấu.
* **[[10:15]]** **RWA (Tài sản thực):** NFT nhà đất có thể cập nhật lịch sử giá, trạng thái quy hoạch.
* **[[10:54]]** **Định danh & Thành viên:** Bằng cấp tích hợp thêm chứng chỉ mới, hoặc thẻ thành viên tự động đổi màu khi đủ điểm tích lũy.

---

#### 6. Triển khai kỹ thuật (Technical Implementation)
* **[[12:51]]** **Thiết kế Datum:** Cấu trúc Datum bao gồm Policy ID, Asset Name, Metadata, Version và **Owner** (mã hash ví người dùng để kiểm soát quyền sửa đổi).
* **[[13:57]]** **Minting Policy Script:** Đảm bảo tính toàn vẹn bằng cách bắt buộc đúc theo cặp (+1 User Token và +1 Ref Token). Không bao giờ được đúc lẻ.
* **[[15:52]]** **Store Script:** Nơi "trú ngụ" của Reference Token. Hợp đồng này kiểm tra xem giao dịch có chữ ký của người chủ thực sự (owner_pkh) trước khi cho phép thay đổi dữ liệu.

---

#### 7. Kiến trúc DApp (Full-stack Architecture)
* **[[19:25]]** Chúng ta sử dụng mô hình **Assembly Pattern** với NextJS (Frontend) và FastAPI (Backend).
* **[[23:21]]** **Quy trình:**
    1.  Frontend gửi yêu cầu đúc/cập nhật NFT.
    2.  Backend (Python/PyCardano) xây dựng giao dịch chưa ký (Unsigned Tx) và trả về CBOR.
    3.  Frontend yêu cầu người dùng ký qua ví (CIP-30).
    4.  Backend nhận chữ ký, ghép vào giao dịch và nộp lên chuỗi (Submit).

---

#### 8. Tổng kết và Kết thúc
* **[[24:44]]** Chúng ta đã nắm được cơ chế hoạt động của CIP-68 và kiến trúc triển khai thực tế.
* **[[26:16]]** Trong video tiếp theo, chúng ta sẽ thực hành một ứng dụng thực tế tích hợp cả **AI và Blockchain** sử dụng thư viện PyCardano. Cảm ơn các bạn đã theo dõi!

---
