use aiken/collection/list
use cardano/transaction.{InlineDatum, OutputReference, Transaction}

/// DID Manager Validator — Real CKV (Continuing output Validation)
///
/// Logic thực tế kiểm soát state transition:
///   Register → datum valid + verified=0 + continuing output ✅
///   Update   → same did_id + diff ipfs_hash + continuing output + owner sign ✅
///   Verify   → verified 0→1 + same fields + continuing output ✅
///   Revoke   → owner sign + NO continuing output (burn DID) ✅

use did_contract/types.{Action, DIDDatum, Register, Revoke, Update, Verify}
use did_contract/validation

validator did_manager {
  spend(
    datum_opt: Option<DIDDatum>,
    action: Action,
    own_ref: OutputReference,
    self: Transaction,
  ) {
    // Datum phải tồn tại (inline datum required)
    expect Some(datum) = datum_opt

    // Tính script address từ own UTxO
    expect Some(own_input) =
      list.find(self.inputs, fn(input) { input.output_reference == own_ref })
    let script_address = own_input.output.address

    // Tìm continuing outputs (outputs quay lại cùng script address)
    let continuing_outputs =
      list.filter(self.outputs, fn(output) { output.address == script_address })

    // Kiểm tra chữ ký owner
    let is_signed_by_owner =
      list.has(self.extra_signatories, datum.owner)

    when action is {
      // ─── Register ───
      // Đăng ký DID mới: lock datum + owner ký
      // Phải có continuing output với cùng datum (verified=0)
      Register -> {
        expect [cont_output] = continuing_outputs
        expect InlineDatum(cont_datum_raw) = cont_output.datum
        expect cont_datum: DIDDatum = cont_datum_raw
        // Datum hợp lệ + verified=0 + output giống input
        validation.validate_register(cont_datum) && is_signed_by_owner && cont_datum == datum
      }

      // ─── Update ───
      // Cập nhật DID (thay đổi ipfs_hash): owner ký
      // Phải có continuing output với did_id giống, ipfs_hash khác
      Update -> {
        expect [cont_output] = continuing_outputs
        expect InlineDatum(cont_datum_raw) = cont_output.datum
        expect cont_datum: DIDDatum = cont_datum_raw
        validation.validate_update(datum, cont_datum) && is_signed_by_owner
      }

      // ─── Verify ───
      // Xác minh danh tính: verified 0 → 1
      // Ai cũng có thể verify (không cần owner sign)
      // Phải có continuing output với verified=1
      Verify -> {
        expect [cont_output] = continuing_outputs
        expect InlineDatum(cont_datum_raw) = cont_output.datum
        expect cont_datum: DIDDatum = cont_datum_raw
        validation.validate_verify(datum, cont_datum)
      }

      // ─── Revoke ───
      // Thu hồi DID vĩnh viễn: owner ký + KHÔNG có output quay lại script
      // ADA được trả về ví owner
      Revoke -> {
        let no_continuing_output = list.is_empty(continuing_outputs)
        validation.validate_revoke(datum) && is_signed_by_owner && no_continuing_output
      }
    }
  }

  else(_) {
    fail
  }
}
