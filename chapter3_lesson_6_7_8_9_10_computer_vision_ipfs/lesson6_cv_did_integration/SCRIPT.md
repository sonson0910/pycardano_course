# 🎬 SCRIPT BÀI GIẢNG — Lesson 6: Smart Contract DID Validator (Aiken + CKV)
# Thời lượng: ~18 phút
# Công cụ: Screen recording + Terminal + VS Code (mở Aiken project)

---

## [00:00 – 01:30] 🎯 Giới thiệu & Mục tiêu bài học

**Nói:**

> Xin chào các bạn! Chào mừng đến với **Lesson 6** — bài đầu tiên trong chuỗi 5 bài của Chapter 3.
>
> Trong chapter này, chúng ta sẽ xây dựng một **DApp hoàn chỉnh** tích hợp **Computer Vision** — cụ thể là nhận diện khuôn mặt — với **Cardano Blockchain** thông qua khái niệm **DID — Decentralized Identity**.
>
> Bài hôm nay, chúng ta sẽ tập trung vào phần **on-chain** — viết smart contract bằng **Aiken**. Đây là nền tảng cho toàn bộ pipeline.
>
> Cụ thể, sau bài này các bạn sẽ:
> - Hiểu khái niệm **DID** trên blockchain
> - Thiết kế **DIDDatum** — cấu trúc dữ liệu lưu on-chain
> - Viết validator sử dụng **CKV pattern** — kiểu "state machine" trên Cardano
> - Viết và chạy **16 unit tests** với Aiken
>
> OK, bắt đầu thôi!

---

## [01:30 – 04:00] 📚 Lý thuyết: DID là gì?

**Nói:**

> Trước khi code, hãy hiểu **DID** là gì.
>
> **DID — Decentralized Identity** — là khái niệm danh tính số **phi tập trung**.
>
> Hãy tưởng tượng thế này: CMND hoặc căn cước công dân của bạn là do **Bộ Công an** cấp — đó là danh tính **tập trung**. Họ có thể thu hồi, thay đổi, hoặc từ chối cấp cho bạn. Bạn không thực sự "sở hữu" danh tính đó.
>
> DID thì ngược lại. **Bạn tự tạo, tự sở hữu, tự kiểm soát** danh tính của mình. Nó được lưu trên blockchain — bất biến, minh bạch, và không ai có thể can thiệp.
>
> Trong project của chúng ta, DID sẽ gắn với **face embedding** — tức là "dấu vân tay số" của khuôn mặt bạn. Đây là cách chúng ta liên kết **AI** (Computer Vision) với **Blockchain**.

*(Hiện slide/diagram)*

```
Camera → AI (MediaPipe) → Face Embedding (vector 512D)
                                ↓
                          Upload IPFS → CID (content hash)
                                           ↓
                Smart Contract lưu DIDDatum { did_id, face_ipfs_hash: CID, owner, verified }
```

> Ý tưởng cốt lõi: **face embedding** quá lớn để lưu trực tiếp on-chain — nên ta lưu nó trên **IPFS** (Lesson 7), và chỉ lưu **CID** — tức hash tham chiếu — on-chain trong DIDDatum.

---

## [04:00 – 06:30] 📐 Thiết kế DIDDatum & Action

*(Mở file `types.ak` trong VS Code)*

**Nói:**

> Bây giờ hãy nhìn vào **cấu trúc dữ liệu on-chain** — `types.ak`.
>
> Đầu tiên là `DIDDatum`:

```aiken
pub type DIDDatum {
  did_id: ByteArray,         // ID duy nhất, ví dụ "did:cardano:abc123"
  face_ipfs_hash: ByteArray, // IPFS CID chứa face embedding
  owner: ByteArray,          // Public key hash (28 bytes)
  created_at: Int,           // POSIX timestamp (milliseconds)
  verified: Int,             // 0 = chưa, 1 = đã xác minh
}
```

> Chú ý trường `verified` — mình dùng **Int** (0 hoặc 1) chứ **không dùng Bool**. Tại sao?
>
> Vì sau này khi viết off-chain code bằng Python (Lesson 8), kiểu `Bool` trong Aiken khi encode sang CBOR sẽ **không tương thích** trực tiếp với `bool` Python. Dùng `Int` thì việc serialize/deserialize giữa on-chain và off-chain luôn nhất quán. Đây là kinh nghiệm thực tế rất quan trọng.
>
> Tiếp theo là `Action` — kiểu enum cho redeemer:

```aiken
pub type Action {
  Register    // CONSTR_ID = 0
  Update      // CONSTR_ID = 1
  Verify      // CONSTR_ID = 2
  Revoke      // CONSTR_ID = 3
}
```

> Mỗi variant là một action mà user có thể thực hiện trên DID. Thứ tự quan trọng — nó quyết định **CONSTR_ID** trong CBOR, off-chain phải khớp chính xác.

---

## [06:30 – 10:00] 🔄 CKV Pattern — State Machine trên Cardano

**Nói:**

> Bây giờ đến phần quan trọng nhất — **CKV pattern**.
>
> CKV — **Continuing Key Validation** — hay "continuing output validation". Đây là pattern cốt lõi trong Cardano smart contracts khi bạn muốn tạo **state machine**.
>
> Bình thường trên Cardano, mỗi UTxO chỉ **spend một lần**. Không có concept "state" được lưu lâu dài như Ethereum. Vậy làm sao tạo state machine?
>
> Câu trả lời: **continuing output**.

*(Vẽ diagram)*

> Khi bạn spend 1 UTxO tại script address, validator yêu cầu bạn phải tạo **1 output mới quay lại đúng script address đó**, với datum mới thể hiện **state transition**.
>
> Giống như vầy:

```
UTxO #1 (verified=0) ──spend──→ UTxO #2 (verified=0)   [Register: giữ nguyên]
                                     │
UTxO #2 (verified=0) ──spend──→ UTxO #3 (verified=1)   [Verify: 0→1]
                                     │
UTxO #3 (verified=1) ──spend──→ KHÔNG output            [Revoke: burn DID]
```

> Mỗi lần spend, validator kiểm tra:
> 1. **Có đúng 1 continuing output** quay lại script? (trừ Revoke)
> 2. **Datum mới** có tuân thủ state transition rules?
> 3. **Chữ ký owner** có hợp lệ? (cho những action cần owner auth)
>
> Revoke là trường hợp đặc biệt — **KHÔNG có continuing output**. ADA được trả về ví owner, DID bị **burn vĩnh viễn**. Giống như `break` trong vòng lặp.

*(Mở file `did_manager.ak`)*

> Hãy nhìn vào validator chính — `did_manager.ak`:

```aiken
validator did_manager {
  spend(datum_opt, action, own_ref, self) {
    expect Some(datum) = datum_opt

    // Tìm script address từ own UTxO
    let script_address = own_input.output.address

    // Tìm continuing outputs
    let continuing_outputs =
      list.filter(self.outputs, fn(output) { output.address == script_address })
```

> Đoạn này tìm tất cả các output **quay lại cùng script address**. Đây chính là "continuing outputs".
>
> Sau đó, mỗi action sẽ kiểm tra khác nhau:

---

## [10:00 – 13:30] 📝 Validation Logic chi tiết

*(Mở file `validation.ak`)*

**Nói:**

> Mình tách validation logic ra file riêng `validation.ak` — clean code, dễ test.
>
> **Register:**

```aiken
pub fn validate_register(datum: DIDDatum) -> Bool {
  validate_datum_fields(datum) && datum.verified == 0
}
```

> Register yêu cầu datum hợp lệ (did_id, ipfs_hash non-empty, timestamp > 0) **VÀ** `verified` phải bằng 0 — tức chưa xác minh. Logic! Vừa tạo mà đã verified thì vô lý.
>
> Trong validator, Register còn kiểm tra:
> - Phải có **đúng 1** continuing output (`expect [cont_output] = continuing_outputs`)
> - Datum của output phải **giống hệt** input datum (`cont_datum == datum`)
> - Phải có **chữ ký owner**
>
> **Update:**

```aiken
pub fn validate_update(input: DIDDatum, output: DIDDatum) -> Bool {
  input.did_id == output.did_id &&          // did_id giữ nguyên
  input.owner == output.owner &&            // owner giữ nguyên
  input.face_ipfs_hash != output.face_ipfs_hash &&  // ipfs_hash phải KHÁC
  validate_datum_fields(output)             // output vẫn valid
}
```

> Update cho phép thay đổi face embedding (khi user chụp ảnh mới), nhưng bắt buộc `did_id` và `owner` phải giữ nguyên. Hợp lý — bạn cập nhật khuôn mặt, không phải tạo DID mới.
>
> **Verify:**

```aiken
pub fn validate_verify(input: DIDDatum, output: DIDDatum) -> Bool {
  input.verified == 0 && output.verified == 1 &&  // 0 → 1
  input.did_id == output.did_id &&
  input.face_ipfs_hash == output.face_ipfs_hash &&
  input.owner == output.owner
}
```

> Verify chuyển `verified` từ 0 sang 1. Tất cả các trường khác phải giữ nguyên. Và chú ý — Verify **không cần chữ ký owner**. Ai cũng có thể verify nếu chứng minh được khuôn mặt khớp (phần này xử lý off-chain ở Lesson 9).
>
> **Revoke:**

```aiken
pub fn validate_revoke(datum: DIDDatum) -> Bool {
  datum.did_id != #""
}
```

> Revoke đơn giản nhất — chỉ cần did_id non-empty. Nhưng trong validator, nó kiểm tra thêm:
> - **Chữ ký owner** — chỉ owner mới được revoke
> - `list.is_empty(continuing_outputs)` — **KHÔNG có output quay lại script** → DID bị burn

---

## [13:30 – 16:00] 🧪 Unit Tests

*(Chạy terminal: `aiken check`)*

**Nói:**

> Aiken có hệ thống test tích hợp. Mình viết **16 tests** cover toàn bộ logic.
>
> Mỗi action có cả test **positive** (valid case) và **negative** (invalid case):

```
┍━ did_contract ━━━━━━━━━━━━━━━━━━━━━━
│ PASS test_register_valid
│ PASS test_register_no_continuing_output     ← phải fail
│ PASS test_register_datum_mismatch           ← phải fail
│ PASS test_update_valid
│ PASS test_update_same_hash                  ← phải fail
│ PASS test_verify_valid_transition
│ PASS test_verify_already_verified           ← phải fail
│ PASS test_revoke_valid
│ PASS test_revoke_has_continuing_output      ← phải fail
│ ... (16 tests total)
┕━━━━━━━━━━━━━━━━━━━━━━ 16 tests | 16 passed | 0 failed
```

> Các test negative rất quan trọng — chúng đảm bảo validator **từ chối** những trường hợp không hợp lệ. Ví dụ: Register mà không có continuing output → phải fail. Revoke mà CÓ continuing output → phải fail.

*(Chạy `aiken build`)*

> Sau khi test pass, chạy `aiken build` sẽ tạo file `plutus.json` — đây là **blueprint** chứa compiled CBOR hex của validator. File này sẽ được dùng trong Lesson 8 để build transactions từ Python.

---

## [16:00 – 18:00] 🔑 Tổng kết & Preview

**Nói:**

> OK, tổng kết Lesson 6:
>
> 1. **DIDDatum** — cấu trúc lưu danh tính on-chain, liên kết face embedding qua IPFS CID
> 2. **CKV Pattern** — state machine trên Cardano: mỗi action tạo continuing output với datum mới
> 3. **4 Actions**: Register (tạo mới), Update (đổi face), Verify (xác minh 0→1), Revoke (burn DID)
> 4. **Security**: Owner authorization qua `extra_signatories`, trừ Verify (ai cũng verify)
> 5. **16 tests** đảm bảo validator chặt chẽ
>
> File `plutus.json` sau khi build chính là "cầu nối" giữa on-chain (Aiken) và off-chain (Python).
>
> Bài tiếp theo — **Lesson 7** — chúng ta sẽ setup **AI model** (MediaPipe) để detect khuôn mặt và upload embedding lên **IPFS**. Đó chính là phần Computer Vision trong pipeline!
>
> Hẹn gặp lại ở Lesson 7!

---

*Kết thúc Lesson 6 — ~18 phút*
