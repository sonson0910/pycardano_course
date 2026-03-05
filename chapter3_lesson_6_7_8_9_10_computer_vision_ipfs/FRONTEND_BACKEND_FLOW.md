"""
Complete Frontend-Backend Integration Flow Documentation

Flow Diagram:
┌──────────────────────────────────────────────────────────────┐
│                   FRONTEND (React)                           │
│              http://localhost:5173/                          │
└──────────────────────────────────────────────────────────────┘
           ↓ (Upload Image)
┌──────────────────────────────────────────────────────────────┐
│           POST /api/v1/detect-faces                          │
│                                                              │
│   FaceDetector Component                                     │
│   ├─ User uploads image                                      │
│   ├─ Frontend sends to /detect-faces                         │
│   ├─ Backend:                                                │
│   │  ├─ Decode image with OpenCV                           │
│   │  ├─ Run MediaPipe FaceDetection                         │
│   │  ├─ Extract 468 landmarks per face                      │
│   │  ├─ Calculate embedding (512-dim)                       │
│   │  ├─ Upload embedding to IPFS (auto)                     │
│   │  ├─ Upload image to IPFS (optional)                     │
│   │  └─ Return: {faces_detected, embedding_ipfs_hash}       │
│   │                                                          │
│   └─ Frontend displays:                                      │
│      ├─ Number of faces detected                            │
│      ├─ Confidence scores per face                          │
│      ├─ IPFS hash of embedding                              │
│      └─ "🔗 Create DID" button                              │
└──────────────────────────────────────────────────────────────┘
           ↓ (Click "Create DID")
┌──────────────────────────────────────────────────────────────┐
│           POST /api/v1/did/create                            │
│                                                              │
│   DIDAuto-Generation                                         │
│   ├─ Frontend passes: {face_embedding: "QmXxx..."}          │
│   ├─ Backend:                                                │
│   │  ├─ Auto-generate DID ID (did:cardano:abc123)          │
│   │  ├─ Check if embedding already uploaded                 │
│   │  ├─ If needed, upload to IPFS again                     │
│   │  ├─ Create DID Datum                                    │
│   │  ├─ Build Cardano TX with datum                         │
│   │  ├─ Sign with wallet private key                        │
│   │  ├─ Submit to blockchain                                │
│   │  └─ Return: {did, ipfs_hash, tx_hash}                  │
│   │                                                          │
│   └─ Frontend:                                               │
│      ├─ Auto-fill DIDAManagement form                       │
│      ├─ Show alert with DID + TX hash                       │
│      └─ Switch to "Manage DIDs" tab                         │
└──────────────────────────────────────────────────────────────┘
           ↓ (View & Manage DIDs)
┌──────────────────────────────────────────────────────────────┐
│           DIDAManagement Component                           │
│                                                              │
│   GET /api/v1/dids                                           │
│   ├─ Fetch all created DIDs                                  │
│   ├─ Display in list with status badges                      │
│   └─ Allow user to select for actions                        │
│                                                              │
│   Available Actions:                                         │
│   ├─ Register (created → registered)                         │
│   ├─ Update (change face embedding)                          │
│   ├─ Verify (confirm identity)                              │
│   ├─ Revoke (permanently disable)                           │
│   └─ Each triggers corresponding smart contract action       │
└──────────────────────────────────────────────────────────────┘

DETAILED ENDPOINT REFERENCE:
════════════════════════════════════════════════════════════════

1️⃣ Face Detection Endpoint
───────────────────────────────────────────────────────────────
   POST /api/v1/detect-faces

   Request:
   - file: Binary image file (JPG/PNG)

   Response:
   {
     "status": "success",
     "faces_detected": 1,
     "faces": [
       {
         "face_id": 0,
         "bbox": [x, y, w, h],
         "confidence": 0.98
       }
     ],
     "embedding_ipfs_hash": "QmExample123...",
     "face_image_ipfs_hash": "QmImageHash..."
   }

2️⃣ Create DID Endpoint
───────────────────────────────────────────────────────────────
   POST /api/v1/did/create

   Request:
   {
     "face_embedding": "QmIpfsHash" or "raw_embedding_data",
     "did_id": "optional_custom_id"  // Auto-generated if omitted
   }

   Response:
   {
     "status": "success",
     "did": "did:cardano:abc123def456",
     "ipfs_hash": "QmEmbedding...",
     "tx_hash": "4374fa5c...",
     "message": "DID created and locked to script..."
   }

3️⃣ Get DID Document
───────────────────────────────────────────────────────────────
   GET /api/v1/did/{did_id}

   Response:
   {
     "did": "did:cardano:abc123def456",
     "status": "created",
     "face_hash": "QmEmbedding...",
     "owner": "addr_test1...",
     "created_at": 1697000000,
     "verified": false
   }

4️⃣ Register DID
───────────────────────────────────────────────────────────────
   POST /api/v1/did/{did_id}/register

   Response:
   {
     "status": "success",
     "did": "did:cardano:abc123def456",
     "action": "register",
     "tx_hash": "txhash123..."
   }

5️⃣ Update DID (New Face Embedding)
───────────────────────────────────────────────────────────────
   POST /api/v1/did/{did_id}/update

   Request:
   {
     "new_face_embedding": "QmNewHash..."
   }

   Response:
   {
     "status": "success",
     "did": "did:cardano:abc123def456",
     "action": "update",
     "tx_hash": "txhash123..."
   }

6️⃣ Verify DID
───────────────────────────────────────────────────────────────
   POST /api/v1/did/{did_id}/verify

   Response:
   {
     "status": "success",
     "did": "did:cardano:abc123def456",
     "action": "verify",
     "verified": true,
     "tx_hash": "txhash123..."
   }

7️⃣ Revoke DID
───────────────────────────────────────────────────────────────
   POST /api/v1/did/{did_id}/revoke

   Response:
   {
     "status": "success",
     "did": "did:cardano:abc123def456",
     "action": "revoke",
     "tx_hash": "txhash123...",
     "message": "DID revoked permanently"
   }

8️⃣ List All DIDs
───────────────────────────────────────────────────────────────
   GET /api/v1/dids

   Response:
   {
     "dids": [
       {
         "id": "uuid1",
         "did": "did:cardano:abc123",
         "status": "verified",
         "faceHash": "QmHash1",
         "createdAt": "2025-10-22T10:00:00Z",
         "lastUpdated": "2025-10-22T10:15:00Z",
         "txHistory": [...]
       }
     ]
   }

9️⃣ Get DID Status
───────────────────────────────────────────────────────────────
   GET /api/v1/did/{did_id}/status

   Response:
   {
     "did": "did:cardano:abc123",
     "status": "registered",
     "txHistory": [
       {
         "action": "create",
         "txHash": "tx1...",
         "timestamp": "2025-10-22T10:00:00Z",
         "confirmed": true
       }
     ]
   }

🔟 Health Check
───────────────────────────────────────────────────────────────
   GET /api/v1/health

   Response:
   {
     "status": "healthy",
     "blockchain": "connected",
     "ipfs": "ready"
   }

USER WORKFLOW CHECKLIST:
════════════════════════════════════════════════════════════════

✅ Step 1: Upload Image
   - App: http://localhost:5173
   - Tab: "📸 1. Detect Face"
   - Action: Select image file

✅ Step 2: Detect Faces
   - Click "Detect Faces" button
   - Backend processes with MediaPipe
   - Shows: # of faces, confidence, IPFS hash

✅ Step 3: Create DID
   - Click "🔗 Create DID"
   - Backend auto-generates DID ID
   - Blockchain confirms TX
   - Alert shows: DID + TX hash

✅ Step 4: View DIDs
   - Auto-switch to "🆔 2. Manage DIDs" tab
   - See newly created DID in list
   - Status: "created"

✅ Step 5: Manage DID
   - Click on DID to select
   - Choose action:
     - Register: Activate DID on chain
     - Update: Change face embedding
     - Verify: Confirm identity
     - Revoke: Disable DID

✅ Step 6: Verify Identity
   - Use Register DID first
   - Then Verify action
   - Backend compares face embeddings
   - Confirms identity match


KEY IMPROVEMENTS MADE:
════════════════════════════════════════════════════════════════

1. Auto-Generation:
   ✅ DID ID auto-generated from embedding hash
   ✅ IPFS upload automatic during detection
   ✅ No manual hash entry required

2. Smart UI Flow:
   ✅ Tab navigation (Detect ↔ Manage)
   ✅ Auto-fill form from detection
   ✅ Success alerts with TX hash
   ✅ DID status indicators

3. Backend Enhancements:
   ✅ /detect-faces uploads to IPFS automatically
   ✅ /create-did accepts auto-generated DID ID
   ✅ IPFS client supports raw bytes upload
   ✅ Comprehensive error handling & logging

4. User Experience:
   ✅ Minimal user input (just upload image)
   ✅ Clear feedback at each step
   ✅ Visual status indicators
   ✅ One-click DID creation


TESTING GUIDE:
════════════════════════════════════════════════════════════════

Test Scenario 1: Happy Path (No Errors)
───────────────────────────────────────
1. Start backend: python main.py
2. Start frontend: npm run dev
3. Open http://localhost:5173
4. Upload face image → ✅ Detect → ✅ Create DID
5. Switch to Manage tab → View DID
6. Register DID → ✅

Test Scenario 2: Invalid Image
───────────────────────────────
1. Upload corrupted/invalid file
2. Backend returns: "Invalid image"
3. Frontend shows error message

Test Scenario 3: No Faces Detected
───────────────────────────────────
1. Upload image with no faces
2. Backend returns: faces_detected = 0
3. "Create DID" button disabled

Test Scenario 4: Multiple Faces
───────────────────────────────
1. Upload image with 3+ faces
2. Backend detects all, uses first for embedding
3. DID created with primary face


DATABASE SCHEMA (For Future):
════════════════════════════════════════════════════════════════

DIDs Table:
  id (UUID)
  did_id (String) - "did:cardano:xxx"
  ipfs_hash (String) - IPFS embedding hash
  status (Enum) - created|registered|verified|revoked
  owner_address (String) - Cardano address
  created_at (Timestamp)
  updated_at (Timestamp)
  tx_history (JSON) - Array of transactions

Transactions Table:
  id (UUID)
  did_id (FK)
  tx_hash (String) - Blockchain TX
  action (Enum) - create|register|update|verify|revoke
  status (Enum) - pending|confirmed|failed
  block_number (Int) - Cardano block
  timestamp (Timestamp)


ERROR HANDLING:
════════════════════════════════════════════════════════════════

Frontend Errors:
  ❌ Backend disconnected → Show connection banner
  ❌ Invalid image → Show alert
  ❌ Face detection failed → Show error message
  ❌ IPFS upload failed → Retry button
  ❌ Blockchain TX failed → Show error with details

Backend Errors:
  ❌ NumPy segfault → Use Docker or precompiled wheels
  ❌ IPFS timeout → Retry with exponential backoff
  ❌ Insufficient balance → Show balance check
  ❌ Invalid redeemer → Check action enum
