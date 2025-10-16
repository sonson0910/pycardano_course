/// DID Management Validator
/// Validates DID operations on Cardano blockchain
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

/// Validator function - processes DID operations
pub fn did_manager(datum: DIDDatum, action: Action, _ctx: Data) -> Bool {
  when action is {
    Register -> validate_register(datum)
    Update -> validate_update(datum)
    Verify -> validate_verify(datum)
    Revoke -> validate_revoke(datum)
  }
}

fn validate_register(datum: DIDDatum) -> Bool {
  datum.did != #"" && datum.face_ipfs_hash != #"" && datum.created_at > 0
}

fn validate_update(_datum: DIDDatum) -> Bool {
  True
}

fn validate_verify(datum: DIDDatum) -> Bool {
  datum.did != #"" && datum.face_ipfs_hash != #""
}

fn validate_revoke(datum: DIDDatum) -> Bool {
  datum.did != #""
}
