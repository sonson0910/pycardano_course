#!/usr/bin/env python3
"""
Computer Vision + Blockchain DApp - How It Works
"""

print(
    """
╔════════════════════════════════════════════════════════════════════════════╗
║         COMPUTER VISION + BLOCKCHAIN DApp - ARCHITECTURE & FLOW           ║
╚════════════════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. SYSTEM OVERVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌─────────────────────────────────────────────────────────────────┐
│                     REACT FRONTEND (DApp)                       │
│  - User uploads face photo                                      │
│  - Connect wallet (MetaMask/Nami)                               │
│  - Create/Update/Verify DID                                     │
│  - View on-chain DID status                                     │
└────────────────────┬────────────────────────────────────────────┘
                     │ HTTP API calls
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│              FASTAPI BACKEND (Python)                           │
│  - Receives face image from frontend                            │
│  - Processes with computer vision (MediaPipe)                   │
│  - Extracts face embeddings                                     │
│  - Uploads embeddings to IPFS                                   │
│  - Creates blockchain transactions                              │
│  - Manages wallet & keys                                        │
└────────────────────┬────────────────────────────────────────────┘
         ┌───────────┴──────────────┐
         │                          │
         ▼                          ▼
  ┌────────────────┐      ┌──────────────────┐
  │   IPFS Node    │      │ CARDANO BLOCKCHAIN │
  │ (Kubo/Pinata)  │      │    (Preprod)       │
  │                │      │                    │
  │ Stores:        │      │ Stores:            │
  │ - Face         │      │ - DIDs             │
  │   embeddings   │      │ - Smart contracts  │
  │ - Metadata     │      │ - Verification     │
  └────────────────┘      │   status           │
                          └──────────────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │ Smart Contracts  │
                        │   (Aiken)        │
                        │                  │
                        │ Validator Logic: │
                        │ - Register DID   │
                        │ - Update data    │
                        │ - Verify face    │
                        │ - Revoke DID     │
                        └──────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2. COMPLETE WORKFLOW - CREATE & VERIFY DID
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STEP 1: User Creates Account
┌─────────────────────────────────────────┐
│ Frontend: Upload face photo             │
│ ↓                                       │
│ Backend receives image                  │
└─────────────────────────────────────────┘

STEP 2: Face Recognition & Processing
┌─────────────────────────────────────────┐
│ Backend (MediaPipe/OpenCV):             │
│ 1. Detect face in image                 │
│ 2. Extract face landmarks               │
│ 3. Generate embedding (512D vector)     │
│ 4. Hash embedding                       │
│                                         │
│ Result: face_embedding = [0.1, 0.2...] │
└─────────────────────────────────────────┘

STEP 3: Store on IPFS
┌─────────────────────────────────────────┐
│ Backend → IPFS (Kubo):                  │
│ POST /api/v0/add {face_embedding}       │
│                                         │
│ Response:                               │
│ {                                       │
│   "hash": "QmExample...ABC123"          │
│ }                                       │
│                                         │
│ Result: ipfs_hash = "QmExample...ABC123"│
└─────────────────────────────────────────┘

STEP 4: Create DID & Lock to Smart Contract
┌──────────────────────────────────────────┐
│ Backend → Cardano Blockchain:            │
│                                          │
│ Create Transaction:                      │
│ {                                        │
│   Input: Wallet UTxO (2 ADA)             │
│   Output: Script Address (3 ADA)         │
│     datum = {                            │
│       did_id: "did:cardano:user123"      │
│       face_ipfs_hash: "QmExample...ABC123"
│       owner: <pub_key_hash>              │
│       created_at: 1697000000             │
│       verified: false                    │
│     }                                    │
│     script: <PlutusV3Script>             │
│ }                                        │
│                                          │
│ Sign & Submit TX                         │
│ TX ID: 4374fa5c17abeb977e00...          │
│ Status: CONFIRMED on chain               │
└──────────────────────────────────────────┘

STEP 5: Verify DID (Unlock from Script)
┌──────────────────────────────────────────┐
│ Backend → Cardano Blockchain:            │
│                                          │
│ Create Spending Transaction:             │
│ {                                        │
│   Input: UTxO locked by script (3 ADA)   │
│   Redeemer: Register() [enum variant]    │
│   Script: <PlutusV3Script>               │
│   Datum: (from locked UTxO)              │
│ }                                        │
│                                          │
│ Validator executes:                      │
│ ✓ Checks did_id != empty                 │
│ ✓ Checks face_ipfs_hash != empty         │
│ ✓ Checks created_at > 0                  │
│ ✓ Returns True → TX VALID                │
│                                          │
│ Output: Return funds to wallet (2.8 ADA) │
│ TX ID: 1519bf1bf1ef5a38ccdf46...        │
│ Status: CONFIRMED on chain               │
└──────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
3. DATA FLOW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

On-Chain (Blockchain):
┌─────────────────────────────────────────┐
│ Smart Contract State                    │
│                                         │
│ DID Record = {                          │
│   ✓ did_id (unique identifier)          │
│   ✓ face_ipfs_hash (link to face data)  │
│   ✓ owner (who owns the DID)            │
│   ✓ created_at (timestamp)              │
│   ✓ verified (true/false)               │
│   ✓ locked_by: smart_contract_address   │
│ }                                       │
│                                         │
│ Can only be:                            │
│ - Created (Register redeemer)           │
│ - Updated (Update redeemer)             │
│ - Verified (Verify redeemer)            │
│ - Revoked (Revoke redeemer)             │
│                                         │
│ Immutable, transparent, tamper-proof    │
└─────────────────────────────────────────┘

Off-Chain (IPFS):
┌─────────────────────────────────────────┐
│ Face Embedding Storage                  │
│                                         │
│ {                                       │
│   "embedding": [0.123, 0.456, ...],     │
│   "metadata": {                         │
│     "did_id": "did:cardano:user123",    │
│     "captured_at": 1697000000,          │
│     "image_hash": "sha256:abcd1234..."  │
│   }                                     │
│ }                                       │
│                                         │
│ Stored at: QmExample...ABC123           │
│ Can be pinned/unpinned                  │
│ Distributed P2P network                 │
└─────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
4. SECURITY MODEL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Cryptographic Security:
├─ Wallet: Ed25519 key pair
│  └─ Private key: Held by user/backend
│  └─ Public key: Derived in transactions
│
├─ DID: Decentralized Identifier
│  └─ Format: did:cardano:<unique_id>
│  └─ Resolvable on-chain
│  └─ Linked to verification key
│
├─ Face Embedding: Neural Network Output
│  └─ 512-dimensional vector
│  └─ Unique to each face
│  └─ Hashed before storage
│  └─ IPFS hash links to on-chain record
│
├─ Smart Contract: Aiken Validator
│  └─ Compiled to Plutus bytecode
│  └─ Locked with UTxO
│  └─ Can only unlock with valid redeemer
│  └─ Validator logic enforced by consensus
│
└─ Blockchain: Cardano UTxO Model
   └─ All tx immutable
   └─ Consensus-validated
   └─ Can't be reversed (unless governance)
   └─ All history publicly auditable

Verification Flow:
1. User provides face photo
2. Backend generates embedding
3. Embedding + metadata → IPFS hash
4. Hash + DID → locked on blockchain
5. Anyone can verify:
   a) DID exists on-chain
   b) Face hash matches IPFS
   c) Data not tampered with
   d) Owner is legitimate

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
5. KEY COMPONENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Frontend (React/TypeScript):
├─ DAppUI Component
│  ├─ Connect wallet (CIP-30)
│  ├─ Upload face image
│  ├─ Display DID info
│  └─ Show verification status
│
└─ API Integration
   ├─ POST /api/dids/create
   ├─ GET /api/dids/<did_id>
   ├─ POST /api/dids/<did_id>/verify
   └─ DELETE /api/dids/<did_id>/revoke

Backend (Python FastAPI):
├─ Computer Vision
│  ├─ Face detection (MediaPipe)
│  ├─ Landmark extraction
│  ├─ Embedding generation
│  └─ Face verification
│
├─ Blockchain Integration
│  ├─ PyCardano client
│  ├─ Transaction builder
│  ├─ Key management
│  └─ UTxO selection
│
├─ IPFS Integration
│  ├─ Kubo API client
│  ├─ File upload
│  ├─ Content addressing
│  └─ Pinning management
│
└─ API Endpoints
   ├─ POST /api/dids - Create DID
   ├─ GET /api/dids/<id> - Get DID
   ├─ POST /api/dids/<id>/verify - Verify
   └─ DELETE /api/dids/<id> - Revoke

Smart Contract (Aiken):
├─ DIDDatum (on-chain state)
│  ├─ did_id: ByteArray
│  ├─ face_ipfs_hash: ByteArray
│  ├─ owner: ByteArray
│  ├─ created_at: Int
│  └─ verified: Bool
│
└─ Validators (redeemers)
   ├─ Register: Initial creation
   ├─ Update: Modify data
   ├─ Verify: Mark as verified
   └─ Revoke: Disable DID

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
6. EXAMPLE TRANSACTION FLOW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CREATE DID TRANSACTION:
TX Hash: 4374fa5c17abeb977e008d0568cf1cdf458ce66025ef92871dcbfe2685242149

Input:
  Wallet UTxO: 9.98 ADA
  Script Address: (locked to validator)

Processing:
  1. Extract face from image
  2. Generate embedding [512 values]
  3. Upload to IPFS → hash: QmExample...
  4. Create datum:
     {
       did_id: "did:cardano:sonson0910",
       face_ipfs_hash: "QmExample123456789abcdef",
       owner: 4d17ab606e5375bddf2554ef865b6a87bf1867a4b...,
       created_at: 1697440465,
       verified: false
     }
  5. Encode as CBOR PlutusData
  6. Lock with validator script

Output:
  Script Address: 3.0 ADA (locked with datum + validator)
  Wallet Change: 6.98 ADA - 0.17 ADA (fees) = 6.81 ADA

Status: CONFIRMED
Block: 4015634
Slot: 104930502

UNLOCK TRANSACTION (Register):
TX Hash: 1519bf1bf1ef5a38ccdf46cba4089e7210288f44dfa1f9d27c294bfa906dd952

Input:
  Script UTxO: 3.0 ADA (with datum)
  Redeemer: Register() [enum variant, CONSTR_ID=0]
  Script: PlutusV3Script (validator bytecode)

Validation:
  Validator checks:
  ✓ did_id != "" (not empty)
  ✓ face_ipfs_hash != "" (not empty)
  ✓ created_at > 0 (valid timestamp)
  ✓ All checks pass → return True

Output:
  Wallet: 2.8 ADA (3.0 - 0.2 fees)

Status: CONFIRMED
Block: 4015634
Slot: 104930502

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
7. WHY THIS ARCHITECTURE?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Computer Vision (Face Recognition):
  ✓ Extract unique identity from biometric data
  ✓ Generate verifiable embeddings
  ✓ Run locally (privacy-preserving)
  ✓ MediaPipe: lightweight, fast, accurate

IPFS (Distributed Storage):
  ✓ Store large embeddings off-chain
  ✓ Content-addressed (hash-based)
  ✓ No central authority
  ✓ Redundancy & persistence
  ✓ Links to on-chain references

Blockchain (Cardano/Plutus):
  ✓ Immutable record of DID ownership
  ✓ Smart contract enforces rules
  ✓ Transparent & auditable
  ✓ Decentralized consensus
  ✓ Scriptable validation logic
  ✓ UTxO model = natural state machine

Combined Benefits:
  ✓ DECENTRALIZED: No single point of failure
  ✓ VERIFIABLE: Cryptographic proofs
  ✓ PRIVATE: Face data not on-chain
  ✓ SCALABLE: Blockchain for identity, IPFS for data
  ✓ COMPOSABLE: Smart contracts can interact
  ✓ AUDITABLE: All history transparent

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
8. CURRENT STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ WORKING:
  ✓ DID creation & locking to smart contract
  ✓ Smart contract execution (validator)
  ✓ DID unlocking with valid redeemer
  ✓ Transaction confirmation on-chain
  ✓ PyCardano integration
  ✓ IPFS integration
  ✓ Face detection & embedding
  ✓ Proper type encoding (Plutus)

🔄 IN PROGRESS:
  - Update/Verify/Revoke redeemers
  - Full lifecycle testing
  - Backend API endpoints
  - Frontend React component

⏳ TODO:
  - Integration testing
  - Security audit
  - Performance optimization
  - Documentation
  - Deployment to mainnet

"""
)
