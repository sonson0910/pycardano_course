# 🎯 Computer Vision + Blockchain DApp

**Decentralized identity management using real-time face tracking + Cardano blockchain**

> 📖 **Start here**: Check [INDEX.md](INDEX.md) for documentation guide

---

## ⚡ Quick Start (5 minutes)

### 1. Get Blockfrost API Key
```bash
# https://blockfrost.io/ → Sign up → Create project → Copy ID
```

### 2. Clone & Setup
```bash
# Backend
cd backend && pip install -r requirements.txt

# Frontend
cd frontend && npm install
```

### 3. Configure
Create `.env`:
```bash
BLOCKFROST_PROJECT_ID=preview_your_key_here
IPFS_GATEWAY_URL=http://localhost:5001
```

### 4. Run
```bash
# Terminal 1: Backend
cd backend && python main.py

# Terminal 2: Frontend
cd frontend && npm run dev

# Terminal 3 (Optional): IPFS
ipfs daemon
```

✅ **Open**: http://localhost:5173

---

## 📋 Features

✅ **Real-time Face Detection** - MediaPipe tracking  
✅ **Blockchain DIDs** - Cardano smart contracts  
✅ **Off-chain Storage** - IPFS + optional Pinata  
✅ **Web DApp** - React TypeScript interface  
✅ **100% Real APIs** - No mocks  

---

## 🏗️ Architecture

```
React Frontend (5173)
    ↓
FastAPI Backend (8000)
    ├─ Face Detection (MediaPipe)
    ├─ IPFS Client (5001)
    └─ Cardano Client (Blockfrost)
        ↓
    ├─ Cardano Preview Testnet
    └─ IPFS Network
```

---

## 🔌 API Endpoints

```
POST /api/v1/detect-faces      # Upload image → Get faces
POST /api/v1/register-did      # Register on blockchain
POST /api/v1/verify-face       # Verify identity
GET  /api/v1/did/{did_id}      # Get DID document
```

**Full docs**: http://localhost:8000/docs

---

## 📁 Structure

```
├── backend/          # FastAPI + Cardano + IPFS
├── frontend/         # React DApp
├── smart_contracts/  # Aiken validators
├── docs/             # Documentation
├── README.md         # This file
├── SETUP.md          # Installation guide
├── SECURITY.md       # Security notes
└── INDEX.md          # Documentation index
```

---

## ⚙️ Tech Stack

| Component | Tech |
|-----------|------|
| Frontend | React 18, TypeScript, Vite |
| Backend | Python 3.11, FastAPI |
| Blockchain | Cardano, Aiken, Plutus V3 |
| Storage | IPFS Kubo, Pinata (optional) |
| API | Blockfrost |

---

## 📖 Documentation

- **[INDEX.md](INDEX.md)** - Docs navigation
- **[SETUP.md](SETUP.md)** - Installation guide (detailed)
- **[SECURITY.md](SECURITY.md)** - Security best practices
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Project layout

---

## 🚀 Development

### Test API
```bash
cd backend && pytest tests/
```

### Build Smart Contracts
```bash
cd smart_contracts && aiken build
```

### Run with Docker
```bash
docker-compose up
```

---

## 🔐 Security

✅ Private keys stored locally  
✅ Transactions signed on-chain  
✅ Smart contracts validated  
✅ IPFS content hashed  

See [SECURITY.md](SECURITY.md)

---

## 🆘 Troubleshooting

**Backend error?** → See [SETUP.md](SETUP.md) Troubleshooting  
**IPFS failed?** → Run `ipfs daemon`  
**Blank frontend?** → Run `npm install && npm run dev`  

---

## 📄 License

MIT

---

**Author**: Sonson0910 @ Cardano Developer Course

**Status**: ✅ Production Ready (Real APIs, No Mocks)
