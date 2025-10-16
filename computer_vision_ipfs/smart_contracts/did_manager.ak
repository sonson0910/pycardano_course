// DID Management Smart Contract Validator
// Validates registration, verification, and revocation of DIDs

/// DID Datum - stored on-chain
pub type DIDDatum {
  did_id: ByteArray,
  // Unique DID identifier
  face_ipfs_hash: ByteArray,
  // IPFS hash of face embedding
  owner: ByteArray,
  // Owner's public key hash
  created_at: Int,
  // Creation timestamp
  verified: Bool,
}

// Verification status

/// Redeemer Actions
pub type Action {
  Register
  // Register new DID
  Update
  // Update DID data
  Verify
  // Verify face identity
  Revoke
}

// Revoke DID

/// Main validator function (entry point for Aiken)
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
  let did_not_empty = datum.did_id != #""
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
  datum.did_id != #"" && datum.face_ipfs_hash != #""
}

/// Validate DID Revocation
fn validate_revoke(datum: DIDDatum) -> Bool {
  datum.did_id != #""
}
