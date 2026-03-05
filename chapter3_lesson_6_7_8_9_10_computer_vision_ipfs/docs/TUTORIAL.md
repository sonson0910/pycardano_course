# PyCardano Course - Computer Vision + Blockchain DApp

## Project Overview

This is a comprehensive learning project for the PyCardano course that integrates:
- **Computer Vision** (Face tracking using MediaPipe)
- **Blockchain** (Cardano with PyCardano)
- **Decentralized Storage** (IPFS)
- **DIDs** (Decentralized Identifiers for identity management)

## Learning Objectives

1. Learn PyCardano for blockchain transactions
2. Understand Cardano wallet management
3. Build smart contracts (Aiken)
4. Integrate face tracking with blockchain
5. Store data on IPFS
6. Create a full-stack DApp

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (optional, for local Cardano node)
- Basic understanding of blockchain concepts

## Installation

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
```

## Running the Project

### Development

```bash
# Terminal 1: Start backend
cd backend
python main.py

# Terminal 2: Start frontend
cd frontend
npm run dev
```

### With Docker

```bash
docker-compose up
```

## Project Structure Details

### Backend

```
backend/
├── app/
│   ├── models/           # Face tracking models
│   │   ├── face_tracker.py    # MediaPipe face detection
│   │   └── __init__.py
│   ├── api/              # FastAPI routes
│   │   ├── routes.py     # API endpoints
│   │   └── __init__.py
│   ├── ipfs/             # IPFS integration
│   │   ├── ipfs_client.py     # IPFS upload/download
│   │   └── __init__.py
│   ├── blockchain/       # Cardano integration
│   │   ├── cardano_client.py  # PyCardano wrapper
│   │   ├── did_manager.py     # DID operations
│   │   └── __init__.py
│   └── __init__.py
├── main.py               # FastAPI app entry
└── requirements.txt      # Python dependencies
```

### Smart Contracts

```
smart_contracts/
├── validators/           # Aiken validators
├── lib.ak               # Main contract library
└── aiken.toml           # Aiken project config
```

### Frontend

```
frontend/
├── src/
│   ├── components/      # React components
│   ├── pages/          # Page components
│   ├── hooks/          # Custom React hooks
│   ├── utils/          # Utility functions
│   └── App.tsx
├── public/
└── package.json
```

## Key Concepts

### 1. Face Tracking
- Real-time face detection using MediaPipe
- Facial landmarks extraction
- Face embedding generation

### 2. DIDs (Decentralized Identifiers)
- Create unique identifiers for faces
- Link to IPFS hash of embeddings
- Store verification metadata on-chain

### 3. Cardano Integration
- Connect to testnet/mainnet
- Query wallet balance
- Build and submit transactions
- Interact with smart contracts

### 4. IPFS Storage
- Upload face embeddings and metadata
- Retrieve data using content hash
- Pin important data for persistence

## API Examples

### Health Check
```bash
curl http://localhost:8000/api/v1/health
```

### Upload Image for Face Detection
```bash
curl -X POST http://localhost:8000/api/v1/detect-faces \
  -F "file=@photo.jpg"
```

### Create DID
```bash
curl -X POST http://localhost:8000/api/v1/create-did \
  -H "Content-Type: application/json" \
  -d '{
    "face_id": "face_001",
    "metadata": {
      "name": "Alice",
      "created_at": "2025-01-01T00:00:00Z"
    }
  }'
```

## Configuration

Create `.env` file in backend directory:

```env
# Cardano
CARDANO_NETWORK=testnet
CARDANO_MNEMONIC=your_12_word_mnemonic_here

# IPFS
IPFS_GATEWAY_URL=http://localhost:5001
PINATA_JWT=optional_pinata_jwt

# API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
```

## Step-by-Step Tutorial

### Step 1: Setup PyCardano
1. Install PyCardano: `pip install pycardano`
2. Connect to testnet
3. Load wallet from mnemonic

### Step 2: Face Detection
1. Install MediaPipe
2. Create FaceTracker class
3. Test with sample images

### Step 3: IPFS Integration
1. Setup local IPFS node (Kubo)
2. Upload embeddings
3. Retrieve data by hash

### Step 4: DID Management
1. Create DIDs linked to faces
2. Register on-chain
3. Verify identity

### Step 5: Frontend
1. Create React components
2. Connect wallet
3. Upload images
4. Display results

## Testing

Run tests:
```bash
pytest backend/tests/
```

## Deployment

### Local Testing
- Use Cardano testnet
- Local IPFS node

### Production
- Use Cardano mainnet
- Pinata or other IPFS pinning service
- Deploy frontend to Vercel/Netlify

## Troubleshooting

### IPFS Connection Error
- Ensure Kubo daemon is running: `ipfs daemon`

### Cardano Connection Error
- Check testnet RPC endpoint
- Verify wallet has sufficient funds (tADA)

### Face Detection Not Working
- Install MediaPipe: `pip install mediapipe`
- Ensure camera permissions are granted

## Additional Resources

- [PyCardano GitHub](https://github.com/dcspark/pycardano)
- [Cardano Developers](https://developers.cardano.org/)
- [MediaPipe Tutorials](https://google.github.io/mediapipe/)
- [IPFS Docs](https://docs.ipfs.io/)

## Contributing

Feel free to submit issues and enhancement requests!

## Support

For questions, create an issue in the repository.
