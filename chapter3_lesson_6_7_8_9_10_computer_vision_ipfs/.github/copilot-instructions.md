# Computer Vision + Blockchain DApp - Project Guidelines

## Project Overview
This project integrates Computer Vision with Blockchain technology:
- **Face Tracking Model**: Real-time face detection and tracking using OpenCV/MediaPipe
- **DIDs (Decentralized Identifiers)**: Identity management using Cardano blockchain
- **IPFS Integration**: Off-chain storage for face embeddings and metadata
- **Smart Contracts**: Aiken/Plutus contracts for on-chain DID management
- **Backend**: Python FastAPI server for vision processing
- **Frontend**: React/Vue DApp interface

## Tech Stack
- **Backend**: Python 3.11+, FastAPI, OpenCV, MediaPipe, PyCardano
- **Blockchain**: Cardano (Smart Contracts in Aiken)
- **Storage**: IPFS (via Kubo API or Pinata)
- **Frontend**: React/TypeScript
- **Database**: SQLite/PostgreSQL (optional)

## Project Structure
```
computer_vision_ipfs/
├── backend/              # Python FastAPI backend
│   ├── app/
│   │   ├── models/      # Face detection/tracking models
│   │   ├── api/         # API endpoints
│   │   ├── ipfs/        # IPFS client integration
│   │   └── blockchain/  # Cardano/DID integration
│   ├── requirements.txt
│   └── main.py
├── smart_contracts/      # Aiken smart contracts
│   ├── validators/
│   └── lib.ak
├── frontend/            # React DApp interface
│   ├── src/
│   ├── public/
│   └── package.json
├── docs/                # Project documentation
├── README.md
└── docker-compose.yml   # Local development setup
```

## Key Features to Implement
1. Face detection and tracking using MediaPipe
2. Generate face embeddings and store on IPFS
3. Create DIDs on Cardano blockchain
4. Link face data to DIDs on-chain
5. Verify face identity against stored DIDs
6. DApp frontend for user interaction

## Development Workflow
1. Start with backend face detection models
2. Setup IPFS integration
3. Create smart contracts for DID management
4. Build API endpoints connecting vision + blockchain
5. Develop frontend DApp
6. Docker setup for deployment
