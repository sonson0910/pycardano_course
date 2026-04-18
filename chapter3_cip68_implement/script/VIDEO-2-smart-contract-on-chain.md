# 🎥 VIDEO 1 — Hợp Đồng Thông Minh CIP-68 (On-chain với Aiken)

## Tổng quan Video
- **Thời lượng ước tính:** 45–60 phút  
- **Mục tiêu:** Người học viết hoàn chỉnh smart contract CIP-68 bằng Aiken, build ra `plutus.json`, sẵn sàng cho off-chain  
- **Điều kiện tiên quyết:** Đã cài Aiken CLI (v1.1.19+), có terminal  

---

## PHẦN 1: KHỞI TẠO DỰ ÁN AIKEN

### Bước 1.1 — Tạo project Aiken mới

**Mục tiêu:** Khởi tạo folder dự án Aiken từ con số 0.

**Hành động code:**
{owner}/{project}
```bash
aiken new pycardano_course/cip68_dynamic_asset
cd cip68_dynamic_asset
```

**Nội dung giảng:**
> "Bước đầu tiên, ta tạo một project Aiken mới. Lệnh `aiken new` sẽ sinh ra cấu trúc thư mục chuẩn gồm `aiken.toml`, thư mục `validators/`, và thư mục `lib/`. Tên project theo format `owner/project_name`."

**Giải thích CIP-68:**
> CIP-68 không quy định ngôn ngữ viết smart contract. Ở đây ta chọn Aiken vì nó là ngôn ngữ chuyên cho Cardano, compile ra Plutus V3 nhỏ gọn.

**Lỗi thường gặp:**
- Quên cài Aiken → chạy `aikup` trước để cài
- Tên project có ký tự đặc biệt → chỉ dùng chữ, số, dấu gạch dưới

---

### Bước 1.2 — Cấu hình `aiken.toml`

**Mục tiêu:** Thiết lập metadata dự án và version Plutus.

**Hành động code:** Mở file `aiken.toml` và xác nhận nội dung:
```toml
name = "pycardano_course/cip68_dynamic_asset"
version = "0.0.1"
compiler = "v1.1.19"
plutus = "v3"
license = "MIT"
description = "CIP-68 Dynamic Asset Smart Contract for PyCardano Course"

[repository]
user = "pycardano_course"
project = "cip68_dynamic_asset"
platform = "github"

[[dependencies]]
name = "aiken-lang/stdlib"
version = "v2.2.0"
source = "github"
```

**Nội dung giảng:**
> "File `aiken.toml` là cấu hình chính. Điểm quan trọng nhất: `plutus = "v3"` — ta dùng Plutus V3 vì nó hỗ trợ đầy đủ tính năng mới nhất. Dependency duy nhất là `aiken-lang/stdlib` — thư viện chuẩn của Aiken."

**Lỗi thường gặp:**
- Dùng `plutus = "v2"` cũng được nhưng code sẽ khác signature → nên dùng v3 cho nhất quán

---

### Bước 1.3 — Cài dependency

**Mục tiêu:** Download thư viện chuẩn Aiken.

**Hành động code:**
```bash
aiken packages
```

**Nội dung giảng:**
> "Lệnh `aiken packages` sẽ download `aiken-lang/stdlib` vào thư mục `build/packages/`. Thư viện này cung cấp các module xử lý `list`, `bytearray`, `assets`, `transaction` — tất cả những gì ta cần."

---

## PHẦN 2: ĐỊNH NGHĨA TYPES (Redeemer & Datum)

### Bước 2.1 — Tạo file validator và import thư viện

**Mục tiêu:** Tạo file chính chứa smart contract, khai báo imports.

**Hành động code:** Tạo file `validators/cip68.ak` với nội dung:
**Nội dung giảng:**
> "Ta tạo file `cip68.ak` trong thư mục `validators/`. Đây sẽ là nơi chứa toàn bộ logic smart contract. Import 4 module chính:
> - `list` — để duyệt danh sách inputs/outputs/signatories
> - `bytearray` — để nối prefix vào tên token
> - `assets` — để kiểm tra số lượng token trong mint/value
> - `transaction` — để truy cập thông tin transaction"

**Lỗi thường gặp:**
- Import thiếu `InlineDatum` → sẽ lỗi khi parse datum ở phần update metadata
```aiken
use aiken/collection/list
use aiken/primitive/bytearray
use cardano/assets.{PolicyId}
use cardano/transaction.{InlineDatum, OutputReference, Transaction}
```

---

### Bước 2.2 — Thêm comment mô tả kiến trúc CIP-68

**Mục tiêu:** Ghi chú rõ ràng CIP-68 dùng 2 token và prefix tương ứng.

**Hành động code:** Thêm ngay sau imports:
```aiken
// ============================================================================
// CIP-68 DYNAMIC ASSET - SMART CONTRACT (SIMPLIFIED)
// ============================================================================
// Smart contract đơn giản cho CIP-68 Dynamic NFT
// Không có parameterized scripts - dễ sử dụng và portable
// 
// CIP-68 sử dụng 2 tokens:
// - Reference Token (100): Lưu trữ metadata trên-chain, luôn ở script address
// - User Token (222): Token mà người dùng sở hữu
// ============================================================================

// CIP-68 Asset Label Prefixes
// Reference Token: (100) - 0x000643b0
// User Token: (222) - 0x000de140
```

**Nội dung giảng:**
> "Trước khi code, hãy hiểu rõ kiến trúc CIP-68. Chuẩn này quy định mỗi NFT phải có 2 token cùng policy ID:
> 
> **Reference Token (label 100)**: Prefix `000643b0`. Token này luôn nằm ở script address, chứa datum = metadata. Nó KHÔNG BAO GIỜ rời khỏi script.
> 
> **User Token (label 222)**: Prefix `000de140`. Token này nằm trong ví người dùng, chứng minh quyền sở hữu.
> 
> Bất kỳ ai đọc reference token trên chain đều lấy được metadata — đây là tính 'readable' của CIP-68."

**Giải thích CIP-68:**
> Prefix `000643b0` và `000de140` là kết quả encode theo CIP-67 Asset Label. Số 100 encode thành 000643b0, số 222 encode thành 000de140. Đây là quy ước chuẩn, KHÔNG được thay đổi.

---

### Bước 2.3 — Định nghĩa `MintRedeemer`

**Mục tiêu:** Tạo kiểu redeemer cho minting policy — phân biệt hành động Mint vs Burn.

**Hành động code:** Thêm tiếp:
```aiken
/// Redeemer cho minting policy
pub type MintRedeemer {
  /// Mint mới reference token và user token
  MintToken { token_name: ByteArray }
  /// Burn reference token và user token
  BurnToken { token_name: ByteArray }
}
```

**Nội dung giảng:**
> "Redeemer là dữ liệu mà off-chain code gửi kèm transaction để 'ra lệnh' cho smart contract. Ở đây ta có 2 variant:
> - `MintToken { token_name }` — khi muốn mint NFT mới, truyền tên token
> - `BurnToken { token_name }` — khi muốn burn, cũng truyền tên token
> 
> Cả hai đều cần `token_name` vì từ tên này, contract sẽ tính ra asset name đầy đủ bằng cách nối prefix."

**Giải thích CIP-68:**
> `token_name` ở đây là phần tên gốc, CHƯA có prefix. Ví dụ: token_name = `"MyNFT"`. Khi mint, contract tự nối thành `000643b0 ++ MyNFT` (ref) và `000de140 ++ MyNFT` (user).

**Lỗi thường gặp:**
- Truyền nguyên asset name đã có prefix → contract sẽ nối thêm lần nữa → sai

---

### Bước 2.4 — Định nghĩa `SpendRedeemer`

**Mục tiêu:** Tạo kiểu redeemer cho spending validator — phân biệt Update vs Burn.

**Hành động code:**
```aiken
/// Redeemer cho spending validator (dùng để update metadata)
pub type SpendRedeemer {
  /// Update metadata của reference token
  UpdateMetadata
  /// Burn reference token
  BurnReference
}
```

**Nội dung giảng:**
> "Spending validator quản lý reference token ở script address. Hai hành động có thể xảy ra:
> - `UpdateMetadata` — lấy reference token ra, thay datum mới, trả lại script
> - `BurnReference` — cho phép burn reference token (phối hợp với minting policy burn)
> 
> Lưu ý `UpdateMetadata` và `BurnReference` không cần truyền token_name vì thông tin đã có sẵn trong datum."

---

### Bước 2.5 — Định nghĩa `CIP68Datum`

**Mục tiêu:** Tạo cấu trúc datum chứa metadata on-chain — trái tim của CIP-68.

**Hành động code:**
```aiken
/// Datum chứa metadata của CIP-68 NFT
/// Bao gồm thông tin để xác định chính xác token
pub type CIP68Datum {
  /// Policy ID của token - để verify đúng token
  policy_id: ByteArray,
  /// Asset name (không có prefix) - để phân biệt các token
  asset_name: ByteArray,
  /// Owner public key hash - người có quyền update/burn
  owner: ByteArray,
  /// Metadata fields theo CIP-68 standard
  metadata: Data,
  /// Version của metadata
  version: Int,
}
```

**Nội dung giảng:**
> "Datum là dữ liệu gắn kèm UTxO tại script address. Trong CIP-68, datum chứa metadata của NFT. Cấu trúc gồm 5 fields:
> 
> 1. `policy_id` — 28 bytes, dùng để verify đúng token
> 2. `asset_name` — tên gốc không prefix, phân biệt các NFT cùng policy
> 3. `owner` — public key hash 28 bytes, ai có quyền update/burn
> 4. `metadata` — kiểu `Data` generic, chứa key-value pairs (tên, mô tả, hình ảnh...)
> 5. `version` — số nguyên, tăng mỗi lần update
> 
> Điểm đặc biệt: `metadata` dùng kiểu `Data` (generic) — cho phép lưu bất kỳ cấu trúc Plutus data nào, rất linh hoạt."

**Giải thích CIP-68:**
> CIP-68 gốc chỉ yêu cầu: metadata (map), version (integer), và optional extra. Ở đây ta thêm `policy_id`, `asset_name`, `owner` vào datum để contract có thể tự verify mà không cần parameterize script.

**Lỗi thường gặp:**
- Nhầm `owner` = địa chỉ ví → PHẢI là public key hash (28 bytes), không phải toàn bộ Address
- Quên field `version` → không thể tracking update history

---

## PHẦN 3: MINTING POLICY VALIDATOR

### Bước 3.1 — Khai báo validator `cip68_mint` và destructure transaction

**Mục tiêu:** Bắt đầu viết minting policy, truy cập mint field từ transaction.

**Hành động code:**
```aiken
// ============================================================================
// VALIDATORS
// ============================================================================

/// Minting Policy cho CIP-68 tokens
/// Chỉ check format và số lượng - ai cũng có thể mint
/// Ownership được quản lý bởi spending validator
validator cip68_mint {
  mint(redeemer: MintRedeemer, policy_id: PolicyId, tx: Transaction) {
    let Transaction { mint, .. } = tx
    // ... logic tiếp theo
  }

  else(_) {
    fail
  }
}
```

**Nội dung giảng:**
> "Validator `cip68_mint` là minting policy — quyết định khi nào được phép mint/burn token. Hàm `mint` nhận 3 tham số:
> - `redeemer` — lệnh từ off-chain (MintToken hoặc BurnToken)
> - `policy_id` — Aiken tự inject policy ID (hash của chính script này)
> - `tx` — toàn bộ transaction
> 
> Dòng `let Transaction { mint, .. } = tx` destructure để lấy ra `mint` field — chứa thông tin tất cả tokens đang mint/burn.
> 
> Khối `else(_) { fail }` là catch-all: nếu ai gọi contract với mục đích khác (ví dụ spend) → luôn fail."

**Giải thích CIP-68:**
> Minting policy này KHÔNG giới hạn ai được mint — bất kỳ ai cũng có thể. Quyền sở hữu được quản lý bởi datum (field `owner`). Đây là thiết kế đơn giản — trong production có thể thêm điều kiện chặt hơn.

---

### Bước 3.2 — Logic xử lý `MintToken`

**Mục tiêu:** Check mint đúng 1 reference token + 1 user token.

**Hành động code:** Thay comment `// ... logic tiếp theo` bằng:
```aiken
    when redeemer is {
      MintToken { token_name } -> {
        // Tạo asset names theo CIP-68 standard
        let ref_token_name = #"000643b0" |> bytearray.concat(token_name)
        let user_token_name = #"000de140" |> bytearray.concat(token_name)
        // Kiểm tra mint đúng số lượng tokens
        let ref_qty = assets.quantity_of(mint, policy_id, ref_token_name)
        let user_qty = assets.quantity_of(mint, policy_id, user_token_name)
        // Phải mint đúng 1 reference token và 1 user token
        ref_qty == 1 && user_qty == 1
      }
      // ... BurnToken case sẽ thêm sau
    }
```

**Nội dung giảng:**
> "Khi redeemer là `MintToken`, ta thực hiện 3 bước:
> 
> **Bước 1:** Tính asset name đầy đủ bằng cách nối prefix. Toán tử `|>` pipe forward: lấy prefix byte, nối (`concat`) với token_name.
> - `#"000643b0"` — hex literal cho prefix reference (100)
> - `#"000de140"` — hex literal cho prefix user (222)
> 
> **Bước 2:** Dùng `assets.quantity_of` kiểm tra trong `mint` field có đúng token với policy_id, asset_name đó không, và số lượng bao nhiêu.
> 
> **Bước 3:** Điều kiện cuối: ref_qty PHẢI bằng 1, user_qty PHẢI bằng 1. Nếu ai cố mint 2 hoặc 0 → fail.
> 
> Đây là ràng buộc CIP-68: LUÔN LUÔN mint theo cặp."

**Lỗi thường gặp:**
- Nối sai thứ tự: `bytearray.concat(token_name, prefix)` → prefix phải ĐẦU TIÊN
- Quên kiểm tra cả 2 token → vi phạm CIP-68

---

### Bước 3.3 — Logic xử lý `BurnToken`

**Mục tiêu:** Check burn đúng -1 reference token + -1 user token.

**Hành động code:** Thêm case `BurnToken` vào block `when`:
```aiken
      BurnToken { token_name } -> {
        let ref_token_name = #"000643b0" |> bytearray.concat(token_name)
        let user_token_name = #"000de140" |> bytearray.concat(token_name)
        // Kiểm tra burn đúng số lượng
        let ref_qty = assets.quantity_of(mint, policy_id, ref_token_name)
        let user_qty = assets.quantity_of(mint, policy_id, user_token_name)
        // Phải burn cả reference token (-1) và user token (-1)
        ref_qty == -1 && user_qty == -1
      }
```

**Nội dung giảng:**
> "Logic burn gần giống mint, chỉ khác số lượng: phải là -1 thay vì 1. Trong Cardano, burn = mint với số lượng âm. Check cả 2 token: ref = -1 VÀ user = -1. Nếu chỉ burn 1 token → fail. CIP-68 yêu cầu burn theo cặp, không thể burn riêng lẻ."

**Lỗi thường gặp:**
- Chỉ burn user token mà quên ref token → vi phạm CIP-68
- Check `ref_qty == 1` thay vì `-1` → burn không thành công

---

## PHẦN 4: SPENDING VALIDATOR (Reference Token Store)

### Bước 4.1 — Khai báo `cip68_store` và extract datum

**Mục tiêu:** Viết spending validator quản lý reference token, parse datum.

**Hành động code:**
```aiken
/// Spending Validator cho Reference Token
/// Cho phép update metadata hoặc burn reference token
/// Chỉ owner (từ datum) mới có quyền thực hiện
/// Verify policy_id và asset_name để đảm bảo đúng token
validator cip68_store {
  spend(
    datum: Option<CIP68Datum>,
    redeemer: SpendRedeemer,
    own_ref: OutputReference,
    tx: Transaction,
  ) {
    // Phải có datum
    expect Some(current_datum) = datum
    // Lấy thông tin từ datum
    let owner_pkh = current_datum.owner
    let datum_policy_id = current_datum.policy_id
    let datum_asset_name = current_datum.asset_name
    // Kiểm tra chữ ký của owner
    let must_be_signed = list.has(tx.extra_signatories, owner_pkh)
    // ... xử lý redeemer tiếp theo
  }

  else(_) {
    fail
  }
}
```

**Nội dung giảng:**
> "Validator `cip68_store` quản lý UTxO chứa reference token tại script address. Hàm `spend` nhận 4 tham số:
> - `datum: Option<CIP68Datum>` — datum gắn với UTxO, là `Option` vì có thể None
> - `redeemer: SpendRedeemer` — lệnh UpdateMetadata hoặc BurnReference
> - `own_ref: OutputReference` — tham chiếu đến chính UTxO đang bị spend
> - `tx: Transaction` — toàn bộ transaction
> 
> Đầu tiên, `expect Some(current_datum) = datum` — bắt buộc phải có datum, nếu None → fail.
> 
> Sau đó extract 3 thông tin key: `owner_pkh`, `datum_policy_id`, `datum_asset_name` — đây là identity của NFT.
> 
> Cuối cùng check chữ ký: `list.has(tx.extra_signatories, owner_pkh)` — owner PHẢI ký transaction. Nếu không ký → không được update/burn."

**Giải thích CIP-68:**
> Đây là cơ chế authorization: ai là owner (ghi trong datum) thì mới được thao tác. Không cần parameterize script với owner address — owner nằm ngay trong datum, portable giữa các thiết bị.

**Lỗi thường gặp:**
- Quên `expect` trước `Some` → compiler warning, không handle None case
- Nhầm `tx.signatories` và `tx.extra_signatories` → trong Plutus V3 dùng `extra_signatories`

---

### Bước 4.2 — Logic `UpdateMetadata` (Phần 1: tìm input & kiểm tra ref token)

**Mục tiêu:** Xác minh UTxO input chứa đúng reference token.

**Hành động code:** Thêm bên trong `when redeemer is`:
```aiken
    when redeemer is {
      UpdateMetadata -> {
        // Tìm input của script
        expect Some(own_input) =
          list.find(tx.inputs, fn(input) { input.output_reference == own_ref })
        let script_address = own_input.output.address
        // Tạo expected reference token name
        let ref_token_name = #"000643b0" |> bytearray.concat(datum_asset_name)
        // Kiểm tra input có chứa reference token với đúng policy_id và asset_name
        let input_has_ref_token =
          assets.quantity_of(
            own_input.output.value,
            datum_policy_id,
            ref_token_name,
          ) == 1
        // ... phần kiểm tra output tiếp theo
      }
      // ... BurnReference case
    }
```

**Nội dung giảng:**
> "Update metadata là thao tác phức tạp nhất. Ta cần:
> 
> **1. Tìm đúng input** đang bị spend: dùng `list.find` tìm input có `output_reference` trùng với `own_ref`. Từ đó lấy `script_address` — địa chỉ script.
> 
> **2. Tính reference token name** đầy đủ: nối prefix `000643b0` với `datum_asset_name` (lưu trong datum).
> 
> **3. Verify input** chứa đúng 1 reference token: dùng `assets.quantity_of` kiểm tra value của input."

---

### Bước 4.3 — Logic `UpdateMetadata` (Phần 2: validate output)

**Mục tiêu:** Kiểm tra output trả reference token về đúng script, datum mới hợp lệ.

**Hành động code:** Thêm tiếp sau `input_has_ref_token`:
```aiken
        // Kiểm tra có output trả về cùng script address với:
        // - Đúng reference token
        // - Datum mới phải giữ nguyên owner, policy_id, asset_name
        let has_valid_output =
          list.any(
            tx.outputs,
            fn(output) {
              when output.datum is {
                InlineDatum(data) -> {
                  expect new_datum: CIP68Datum = data
                  // Kiểm tra output có reference token
                  let output_has_ref_token =
                    assets.quantity_of(
                      output.value,
                      datum_policy_id,
                      ref_token_name,
                    ) == 1
                  // Phải cùng script address, giữ nguyên identity fields
                  output.address == script_address && output_has_ref_token && new_datum.policy_id == datum_policy_id && new_datum.asset_name == datum_asset_name && new_datum.owner == owner_pkh
                }
                _ -> False
              }
            },
          )
        must_be_signed && input_has_ref_token && has_valid_output
```

**Nội dung giảng:**
> "Phần quan trọng nhất — validate output. Dùng `list.any` duyệt tất cả outputs, tìm output thỏa mãn:
> 
> **1. Datum phải inline:** `InlineDatum(data)` — CIP-68 yêu cầu datum inline để ai cũng đọc được trực tiếp.
> 
> **2. Parse datum mới:** `expect new_datum: CIP68Datum = data` — cast generic Data thành CIP68Datum.
> 
> **3. Output chứa ref token:** kiểm tra value có đúng 1 reference token.
> 
> **4. Validate identity fields:** 5 điều kiện AND:
>    - `output.address == script_address` — trả về ĐÚNG script address (không gửi đi chỗ khác)
>    - `output_has_ref_token` — có reference token
>    - `new_datum.policy_id == datum_policy_id` — KHÔNG được đổi policy_id
>    - `new_datum.asset_name == datum_asset_name` — KHÔNG được đổi asset_name
>    - `new_datum.owner == owner_pkh` — KHÔNG được đổi owner
> 
> Chỉ `metadata` và `version` là được thay đổi. Ba trường identity: policy_id, asset_name, owner — bất biến.
> 
> Kết quả cuối: `must_be_signed && input_has_ref_token && has_valid_output` — tất cả đều phải True."

**Giải thích CIP-68:**
> Đây là phần "dynamic" của CIP-68 Dynamic NFT: metadata CÓ THỂ thay đổi nhưng identity KHÔNG đổi. Bất kỳ dApp nào đọc reference token đều lấy metadata mới nhất — không cần re-mint.

**Lỗi thường gặp:**
- Quên check `output.address == script_address` → attacker có thể steal reference token
- Không check `new_datum.owner == owner_pkh` → attacker có thể chiếm quyền owner
- Dùng DatumHash thay vì InlineDatum → vi phạm CIP-68 (metadata phải readable on-chain)

---

### Bước 4.4 — Logic `BurnReference`

**Mục tiêu:** Cho phép burn reference token khi owner ký.

**Hành động code:** Thêm case `BurnReference`:
```aiken
      BurnReference ->
        // Chỉ cần owner ký để cho phép burn
        must_be_signed
    }
```

**Nội dung giảng:**
> "Burn reference token đơn giản hơn nhiều: chỉ cần owner ký là đủ. Không cần check output vì token sẽ bị destroy. Logic burn hoàn chỉnh cần CẢ HAI validators:
> - `cip68_store` (spending): cho phép spend reference token UTxO → check BurnReference + owner ký
> - `cip68_mint` (minting): cho phép burn tokens → check BurnToken + số lượng -1"

---

## PHẦN 5: KIỂM TRA VÀ BUILD

### Bước 5.1 — Review toàn bộ file `cip68.ak`

**Mục tiêu:** Kiểm tra lại code hoàn chỉnh trước khi build.

**Hành động code:** Xem lại toàn bộ file `validators/cip68.ak`. File hoàn chỉnh khoảng 160 dòng code.

**Nội dung giảng:**
> "Hãy review lại toàn bộ. Smart contract CIP-68 của ta gồm:
> - 3 types: `MintRedeemer`, `SpendRedeemer`, `CIP68Datum`  
> - 2 validators: `cip68_mint` (minting policy), `cip68_store` (spending validator)
> - Logic chính: mint/burn theo cặp, update metadata giữ identity, owner authorization"

---

### Bước 5.2 — Check compile

**Mục tiêu:** Check syntax và type errors.

**Hành động code:**
```bash
aiken check
```

**Nội dung giảng:**
> "Lệnh `aiken check` kiểm tra syntax, types, imports. Nếu thấy `0 errors, 0 warnings` nghĩa là code hợp lệ. Nếu có lỗi, đọc message cẩn thận — Aiken thường chỉ rõ dòng và nguyên nhân."

**Lỗi thường gặp:**
- `Unknown module` → check lại tên import
- `Type mismatch` → check kiểu dữ liệu parameter

---

### Bước 5.3 — Build thành `plutus.json`

**Mục tiêu:** Biên dịch smart contract thành Plutus Core, xuất ra blueprint.

**Hành động code:**
```bash
aiken build
```

**Nội dung giảng:**
> "Lệnh `aiken build` biên dịch Aiken code thành Plutus Core bytecode và xuất ra file `plutus.json`. File này là blueprint — chứa:
> - `compiledCode` — bytecode hex của mỗi validator
> - `hash` — script hash (chính là policy ID cho minting policy, và script hash cho spending validator)
> - `definitions` — schema của datum/redeemer
> 
> File `plutus.json` là 'cầu nối' giữa on-chain và off-chain. Off-chain code (PyCardano) sẽ đọc file này để biết bytecode gửi lên blockchain."

---

### Bước 5.4 — Xác minh `plutus.json`

**Mục tiêu:** Kiểm tra output, ghi nhận Policy ID và Script Hash.

**Hành động code:** Mở file `plutus.json` và kiểm tra:
```bash
# Xem policy_id (hash của cip68_mint)
# Xem store_hash (hash của cip68_store)
```

**Nội dung giảng:**
> "Mở `plutus.json`, ta thấy 4 validators (mỗi cái có .mint/.else hoặc .spend/.else):
> 
> - `cip68.cip68_mint.mint` → hash = `9a97fb...` → đây là **Policy ID**
> - `cip68.cip68_store.spend` → hash = `2d7d22...` → đây là **Store Script Hash**
> 
> Hai hash này CỐ ĐỊNH vì contract không parameterized. Ghi lại chúng — off-chain code sẽ dùng."

**Giải thích CIP-68:**
> Trong thiết kế này, Policy ID cố định nghĩa là BẤT KỲ AI cũng biết tokens nào thuộc dự án này. Đây là trade-off: đơn giản nhưng không private. Production có thể dùng parameterized script để mỗi user/collection có policy riêng.

---

## PHẦN 6: TÓM TẮT & CHUẨN BỊ CHO VIDEO 2

### Bước 6.1 — Tổng kết

**Nội dung giảng:**
> "Chúng ta đã hoàn thành smart contract CIP-68 với Aiken. Tổng kết:
> 
> **Minting Policy (`cip68_mint`):**
> - MintToken: check mint đúng 1 ref + 1 user token
> - BurnToken: check burn đúng -1 ref + -1 user token
> 
> **Spending Validator (`cip68_store`):**
> - UpdateMetadata: owner ký + ref token có trong input + output hợp lệ (cùng address, giữ identity)
> - BurnReference: owner ký
> 
> Kết quả: file `plutus.json` sẵn sàng cho off-chain code.
> 
> Video tiếp theo: Viết Python scripts dùng PyCardano để mint, update, burn NFT trên Preprod testnet."

---

## FILE HOÀN CHỈNH: `validators/cip68.ak`

```aiken
use aiken/collection/list
use aiken/primitive/bytearray
use cardano/assets.{PolicyId}
use cardano/transaction.{InlineDatum, OutputReference, Transaction}

// ============================================================================
// CIP-68 DYNAMIC ASSET - SMART CONTRACT (SIMPLIFIED)
// ============================================================================
// Smart contract đơn giản cho CIP-68 Dynamic NFT
// Không có parameterized scripts - dễ sử dụng và portable
// 
// CIP-68 sử dụng 2 tokens:
// - Reference Token (100): Lưu trữ metadata trên-chain, luôn ở script address
// - User Token (222): Token mà người dùng sở hữu
// ============================================================================

// CIP-68 Asset Label Prefixes
// Reference Token: (100) - 0x000643b0
// User Token: (222) - 0x000de140

/// Redeemer cho minting policy
pub type MintRedeemer {
  /// Mint mới reference token và user token
  MintToken { token_name: ByteArray }
  /// Burn reference token và user token
  BurnToken { token_name: ByteArray }
}

/// Redeemer cho spending validator (dùng để update metadata)
pub type SpendRedeemer {
  /// Update metadata của reference token
  UpdateMetadata
  /// Burn reference token
  BurnReference
}

/// Datum chứa metadata của CIP-68 NFT
/// Bao gồm thông tin để xác định chính xác token
pub type CIP68Datum {
  /// Policy ID của token - để verify đúng token
  policy_id: ByteArray,
  /// Asset name (không có prefix) - để phân biệt các token
  asset_name: ByteArray,
  /// Owner public key hash - người có quyền update/burn
  owner: ByteArray,
  /// Metadata fields theo CIP-68 standard
  metadata: Data,
  /// Version của metadata
  version: Int,
}

// ============================================================================
// VALIDATORS
// ============================================================================

/// Minting Policy cho CIP-68 tokens
/// Chỉ check format và số lượng - ai cũng có thể mint
/// Ownership được quản lý bởi spending validator
validator cip68_mint {
  mint(redeemer: MintRedeemer, policy_id: PolicyId, tx: Transaction) {
    let Transaction { mint, .. } = tx
    when redeemer is {
      MintToken { token_name } -> {
        let ref_token_name = #"000643b0" |> bytearray.concat(token_name)
        let user_token_name = #"000de140" |> bytearray.concat(token_name)
        let ref_qty = assets.quantity_of(mint, policy_id, ref_token_name)
        let user_qty = assets.quantity_of(mint, policy_id, user_token_name)
        ref_qty == 1 && user_qty == 1
      }
      BurnToken { token_name } -> {
        let ref_token_name = #"000643b0" |> bytearray.concat(token_name)
        let user_token_name = #"000de140" |> bytearray.concat(token_name)
        let ref_qty = assets.quantity_of(mint, policy_id, ref_token_name)
        let user_qty = assets.quantity_of(mint, policy_id, user_token_name)
        ref_qty == -1 && user_qty == -1
      }
    }
  }

  else(_) {
    fail
  }
}

/// Spending Validator cho Reference Token
/// Cho phép update metadata hoặc burn reference token
/// Chỉ owner (từ datum) mới có quyền thực hiện
validator cip68_store {
  spend(
    datum: Option<CIP68Datum>,
    redeemer: SpendRedeemer,
    own_ref: OutputReference,
    tx: Transaction,
  ) {
    expect Some(current_datum) = datum
    let owner_pkh = current_datum.owner
    let datum_policy_id = current_datum.policy_id
    let datum_asset_name = current_datum.asset_name
    let must_be_signed = list.has(tx.extra_signatories, owner_pkh)
    when redeemer is {
      UpdateMetadata -> {
        expect Some(own_input) =
          list.find(tx.inputs, fn(input) { input.output_reference == own_ref })
        let script_address = own_input.output.address
        let ref_token_name = #"000643b0" |> bytearray.concat(datum_asset_name)
        let input_has_ref_token =
          assets.quantity_of(
            own_input.output.value,
            datum_policy_id,
            ref_token_name,
          ) == 1
        let has_valid_output =
          list.any(
            tx.outputs,
            fn(output) {
              when output.datum is {
                InlineDatum(data) -> {
                  expect new_datum: CIP68Datum = data
                  let output_has_ref_token =
                    assets.quantity_of(
                      output.value,
                      datum_policy_id,
                      ref_token_name,
                    ) == 1
                  output.address == script_address && output_has_ref_token && new_datum.policy_id == datum_policy_id && new_datum.asset_name == datum_asset_name && new_datum.owner == owner_pkh
                }
                _ -> False
              }
            },
          )
        must_be_signed && input_has_ref_token && has_valid_output
      }
      BurnReference ->
        must_be_signed
    }
  }

  else(_) {
    fail
  }
}
```
