use cardano/transaction.{OutputReference, Transaction}
// validators/did_manager.ak
// DID Manager Validator
// Main validator for DID operations on-chain

use computer_vision_dapp/types.{Action, DIDDatum}

validator did_manager {
  spend(
    _datum: Option<DIDDatum>,
    _action: Action,
    _own_ref: OutputReference,
    _self: Transaction,
  ) {
    True
  }

  else(_) {
    fail
  }
}
