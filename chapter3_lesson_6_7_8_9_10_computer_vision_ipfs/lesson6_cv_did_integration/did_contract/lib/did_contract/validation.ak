/// DID Validation Logic — Real State Machine
///
/// Pure validation + output checking functions.
/// Validator sử dụng CKV (Continuing output Validation)
/// để kiểm soát state transition thực sự.

use did_contract/types.{DIDDatum}

// ═══════════════════════════════════════════════
// PURE DATUM VALIDATION
// ═══════════════════════════════════════════════

/// Validate basic datum fields (non-empty, positive timestamp)
pub fn validate_datum_fields(datum: DIDDatum) -> Bool {
  datum.did_id != #"" && datum.face_ipfs_hash != #"" && datum.created_at > 0
}

// ═══════════════════════════════════════════════
// STATE TRANSITION RULES
// ═══════════════════════════════════════════════

/// Register: datum fields valid + verified phải = 0 (chưa xác minh)
pub fn validate_register(datum: DIDDatum) -> Bool {
  validate_datum_fields(datum) && datum.verified == 0
}

/// Update: output did_id phải giống input, ipfs_hash phải khác
pub fn validate_update(input: DIDDatum, output: DIDDatum) -> Bool {
  // Giữ nguyên did_id + owner
  input.did_id == output.did_id && input.owner == output.owner &&
  // ipfs_hash phải thay đổi (update mới)
  input.face_ipfs_hash != output.face_ipfs_hash &&
  // output datum fields vẫn phải valid
  validate_datum_fields(output)
}

/// Verify: chuyển verified từ 0 → 1, giữ nguyên các trường khác
pub fn validate_verify(input: DIDDatum, output: DIDDatum) -> Bool {
  // Input chưa verify (verified=0), Output đã verify (verified=1)
  input.verified == 0 && output.verified == 1 &&
  // Giữ nguyên did_id, ipfs_hash, owner
  input.did_id == output.did_id && input.face_ipfs_hash == output.face_ipfs_hash && input.owner == output.owner
}

/// Revoke: chỉ cần datum fields valid (owner auth do validator xử lý)
/// Revoke = burn DID → KHÔNG có output quay lại script
pub fn validate_revoke(datum: DIDDatum) -> Bool {
  datum.did_id != #""
}
