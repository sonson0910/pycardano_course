use cardano/transaction.{OutputReference, Transaction}
// Test validator - ALWAYS SUCCEEDS
use computer_vision_dapp/types.{
  Action, DIDDatum, Register, Revoke, Update, Verify,
}

validator test_did {
  spend(
    datum: Option<DIDDatum>,
    action: Action,
    _own_ref: OutputReference,
    _self: Transaction,
  ) {
    // ALWAYS TRUE for testing
    True
  }

  else(_) {
    fail
  }
}
