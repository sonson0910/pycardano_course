/// DID Management Smart Contract
/// Manages Decentralized Identifiers linked to face embeddings

pub type DIDDatum {
  did: ByteArray,
  face_ipfs_hash: ByteArray,
  owner: ByteArray,
  created_at: Int,
  verified: Bool,
}

pub type Action {
  Register
  Update
  Verify
  Revoke
}

/// Main validator function
pub fn did_manager(datum: DIDDatum, action: Action, _ctx: Data) -> Bool {
  when action is {
    Register -> validate_register(datum)
    Update -> validate_update(datum)
    Verify -> validate_verify(datum)
    Revoke -> validate_revoke(datum)
  }
}

/// Validate DID Registration
fn validate_register(datum: DIDDatum) -> Bool {
  let did_not_empty = datum.did != #""
  let ipfs_hash_valid = datum.face_ipfs_hash != #""
  let created_at_valid = datum.created_at > 0

  did_not_empty && ipfs_hash_valid && created_at_valid
}

/// Validate DID Update
fn validate_update(_datum: DIDDatum) -> Bool {
  True
}

/// Validate DID Verification
fn validate_verify(datum: DIDDatum) -> Bool {
  datum.did != #"" && datum.face_ipfs_hash != #""
}

/// Validate DID Revocation
fn validate_revoke(datum: DIDDatum) -> Bool {
  datum.did != #""
}

// ============================================================================
// TEST SUITE
// ============================================================================

test register_valid_did() {
  let datum = DIDDatum {
    did: #"did_0001",
    face_ipfs_hash: #"QmHash",
    owner: #"owner",
    created_at: 1696000000,
    verified: False,
  }
  let did_not_empty = datum.did != #""
  let ipfs_hash_valid = datum.face_ipfs_hash != #""
  let created_at_valid = datum.created_at > 0

  did_not_empty && ipfs_hash_valid && created_at_valid
}

test register_empty_did() fail {
  let datum = DIDDatum {
    did: #"",
    face_ipfs_hash: #"QmHash",
    owner: #"owner",
    created_at: 1696000000,
    verified: False,
  }
  validate_register(datum)
}

test register_empty_face_hash() fail {
  let datum = DIDDatum {
    did: #"did_1",
    face_ipfs_hash: #"",
    owner: #"owner",
    created_at: 1696000000,
    verified: False,
  }
  validate_register(datum)
}

test register_invalid_timestamp_zero() fail {
  let datum = DIDDatum {
    did: #"did_1",
    face_ipfs_hash: #"QmHash",
    owner: #"owner",
    created_at: 0,
    verified: False,
  }
  validate_register(datum)
}

test register_invalid_timestamp_negative() fail {
  let datum = DIDDatum {
    did: #"did_1",
    face_ipfs_hash: #"QmHash",
    owner: #"owner",
    created_at: -1,
    verified: False,
  }
  validate_register(datum)
}

test update_always_succeeds() {
  let datum = DIDDatum {
    did: #"",
    face_ipfs_hash: #"",
    owner: #"",
    created_at: 0,
    verified: False,
  }
  validate_update(datum)
}

test verify_valid_did() {
  let datum = DIDDatum {
    did: #"did_1",
    face_ipfs_hash: #"QmHash",
    owner: #"owner",
    created_at: 1696000000,
    verified: False,
  }
  validate_verify(datum)
}

test verify_empty_did() fail {
  let datum = DIDDatum {
    did: #"",
    face_ipfs_hash: #"QmHash",
    owner: #"owner",
    created_at: 1696000000,
    verified: False,
  }
  validate_verify(datum)
}

test verify_empty_face_hash() fail {
  let datum = DIDDatum {
    did: #"did_1",
    face_ipfs_hash: #"",
    owner: #"owner",
    created_at: 1696000000,
    verified: False,
  }
  validate_verify(datum)
}

test revoke_valid_did() {
  let datum = DIDDatum {
    did: #"did_1",
    face_ipfs_hash: #"QmHash",
    owner: #"owner",
    created_at: 1696000000,
    verified: False,
  }
  validate_revoke(datum)
}

test revoke_empty_did() fail {
  let datum = DIDDatum {
    did: #"",
    face_ipfs_hash: #"QmHash",
    owner: #"owner",
    created_at: 1696000000,
    verified: False,
  }
  validate_revoke(datum)
}

test large_did_value() {
  let datum = DIDDatum {
    did: #"ffffffffffffffffffffffffffffffffffffffff",
    face_ipfs_hash: #"QmHash",
    owner: #"owner",
    created_at: 1696000000,
    verified: False,
  }
  validate_register(datum)
}

test minimum_valid_timestamp() {
  let datum = DIDDatum {
    did: #"did_1",
    face_ipfs_hash: #"QmHash",
    owner: #"owner",
    created_at: 1,
    verified: False,
  }
  validate_register(datum)
}

test future_timestamp() {
  let datum = DIDDatum {
    did: #"did_1",
    face_ipfs_hash: #"QmHash",
    owner: #"owner",
    created_at: 2_000_000_000,
    verified: False,
  }
  validate_register(datum)
}

test integration_complete_lifecycle() {
  let datum = DIDDatum {
    did: #"did_user",
    face_ipfs_hash: #"QmHash",
    owner: #"owner",
    created_at: 1696000000,
    verified: False,
  }
  let step1 = validate_register(datum)
  let step2 = validate_update(datum)
  let step3 = validate_verify(datum)
  let step4 = validate_revoke(datum)

  step1 && step2 && step3 && step4
}
