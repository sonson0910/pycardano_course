/// Test suite cho DID Validator — CKV Logic
/// Tests cho pure validation functions

use did_contract/types.{DIDDatum}
use did_contract/validation

/// Helper: tạo DIDDatum mẫu hợp lệ
fn sample_did() -> DIDDatum {
  DIDDatum {
    did_id: #"6469643a63617264616e6f3a746573743031",
    face_ipfs_hash: #"516d5465737448617368313233",
    owner: #"aabbccddee00112233445566778899aabbccddee00112233445566",
    created_at: 1700000000,
    verified: 0,
  }
}

// ═══════════════════════════════════════════════
// REGISTER TESTS
// ═══════════════════════════════════════════════

test register_valid_did() {
  validation.validate_register(sample_did())
}

test register_empty_did_fails() fail {
  let datum = DIDDatum { ..sample_did(), did_id: #"" }
  validation.validate_register(datum)
}

test register_empty_hash_fails() fail {
  let datum = DIDDatum { ..sample_did(), face_ipfs_hash: #"" }
  validation.validate_register(datum)
}

test register_already_verified_fails() fail {
  let datum = DIDDatum { ..sample_did(), verified: 1 }
  validation.validate_register(datum)
}

test register_invalid_timestamp_fails() fail {
  let datum = DIDDatum { ..sample_did(), created_at: 0 }
  validation.validate_register(datum)
}

// ═══════════════════════════════════════════════
// UPDATE TESTS
// ═══════════════════════════════════════════════

test update_valid() {
  let input = sample_did()
  let output = DIDDatum { ..input, face_ipfs_hash: #"516d4e657748617368343536" }
  validation.validate_update(input, output)
}

test update_same_hash_fails() fail {
  let input = sample_did()
  // ipfs_hash không thay đổi → fail
  validation.validate_update(input, input)
}

test update_diff_did_id_fails() fail {
  let input = sample_did()
  let output =
    DIDDatum {
      ..input,
      did_id: #"6469643a6f74686572",
      face_ipfs_hash: #"516d4e657748617368343536",
    }
  validation.validate_update(input, output)
}

test update_diff_owner_fails() fail {
  let input = sample_did()
  let output =
    DIDDatum {
      ..input,
      owner: #"112233445566778899aabbccddee00112233445566778899aabbcc",
      face_ipfs_hash: #"516d4e657748617368343536",
    }
  validation.validate_update(input, output)
}

// ═══════════════════════════════════════════════
// VERIFY TESTS
// ═══════════════════════════════════════════════

test verify_valid() {
  let input = sample_did()
  let output = DIDDatum { ..input, verified: 1 }
  validation.validate_verify(input, output)
}

test verify_already_verified_fails() fail {
  let input = DIDDatum { ..sample_did(), verified: 1 }
  let output = DIDDatum { ..input, verified: 1 }
  validation.validate_verify(input, output)
}

test verify_wrong_direction_fails() fail {
  let input = DIDDatum { ..sample_did(), verified: 1 }
  let output = DIDDatum { ..input, verified: 0 }
  validation.validate_verify(input, output)
}

test verify_diff_did_id_fails() fail {
  let input = sample_did()
  let output =
    DIDDatum { ..input, verified: 1, did_id: #"6469643a6f74686572" }
  validation.validate_verify(input, output)
}

test verify_diff_ipfs_hash_fails() fail {
  let input = sample_did()
  let output =
    DIDDatum { ..input, verified: 1, face_ipfs_hash: #"516d4e657748617368" }
  validation.validate_verify(input, output)
}

// ═══════════════════════════════════════════════
// REVOKE TESTS
// ═══════════════════════════════════════════════

test revoke_valid() {
  validation.validate_revoke(sample_did())
}

test revoke_empty_did_fails() fail {
  let datum = DIDDatum { ..sample_did(), did_id: #"" }
  validation.validate_revoke(datum)
}
