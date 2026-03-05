# Project Structure Overview

## 📁 Directory Layout

```
computer_vision_ipfs/
│
├── 📘 README.md                 # Main project documentation
├── 📘 SECURITY.md              # Security guidelines
├── 🔧 setup.py                 # Setup script
├── 🔧 build.sh                 # Build script (Linux/Mac)
├── 🔧 build.bat                # Build script (Windows)
│
├── 🐍 backend/                 # Python FastAPI Backend
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Configuration management
│   ├── requirements.txt        # Python dependencies
│   ├── Dockerfile              # Docker config
│   ├── examples.py             # Usage examples
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── utils.py            # Utility functions
│   │   │
│   │   ├── models/             # Face tracking models
│   │   │   ├── __init__.py
│   │   │   ├── face_tracker.py # MediaPipe face detection/tracking
│   │   │
│   │   ├── api/                # FastAPI routes
│   │   │   ├── __init__.py
│   │   │   ├── routes.py       # API endpoints
│   │   │
│   │   ├── ipfs/               # IPFS integration
│   │   │   ├── __init__.py
│   │   │   ├── ipfs_client.py  # IPFS upload/download operations
│   │   │
│   │   └── blockchain/         # Cardano blockchain
│   │       ├── __init__.py
│   │       ├── cardano_client.py  # PyCardano wrapper
│   │       └── did_manager.py     # DID operations
│   │
│   └── tests/                  # Unit tests
│       ├── __init__.py
│       ├── conftest.py         # Pytest configuration
│       ├── test_models.py      # Face tracker tests
│       └── test_blockchain.py  # Blockchain tests
│
├── ⚛️  frontend/                # React TypeScript DApp
│   ├── src/
│   │   ├── main.tsx            # Entry point
│   │   ├── App.tsx             # Main app component
│   │   ├── index.css           # Global styles
│   │   ├── api.ts              # API client functions
│   │   │
│   │   └── components/         # React components
│   │       └── FaceDetector.tsx # Face detection UI
│   │
│   ├── public/                 # Static assets
│   ├── index.html              # HTML template
│   ├── package.json            # Node.js dependencies
│   ├── vite.config.ts          # Vite configuration
│   ├── tsconfig.json           # TypeScript config
│   ├── tsconfig.node.json      # TypeScript config (Node)
│   ├── .eslintrc.cjs           # ESLint config
│   └── Dockerfile              # Docker config
│
├── 📋 smart_contracts/         # Aiken Smart Contracts
│   ├── README.md               # Smart contract docs
│   ├── aiken.toml              # Aiken project config
│   ├── lib.ak                  # Main contract library
│   └── validators/             # Contract validators
│
├── 📚 docs/                    # Documentation
│   ├── SETUP.md                # Development setup guide
│   ├── TUTORIAL.md             # Project tutorial
│   └── PYCARDANO_GUIDE.md      # PyCardano integration guide
│
├── 🐳 docker-compose.yml       # Docker composition
├── .env.example                # Example environment variables
└── .gitignore                  # Git ignore rules
```

## 🔑 Key Files Explained

### Backend
- **main.py** - FastAPI application entry point, initializes routes and middleware
- **config.py** - Centralized configuration management from environment variables
- **models/face_tracker.py** - MediaPipe-based face detection and tracking implementation
- **blockchain/cardano_client.py** - PyCardano wrapper for blockchain operations
- **blockchain/did_manager.py** - DID creation, management, and verification logic
- **ipfs/ipfs_client.py** - IPFS integration for off-chain data storage
- **api/routes.py** - FastAPI endpoints for face detection, DID operations

### Frontend
- **App.tsx** - Main React component with health check and routing
- **api.ts** - HTTP client functions for backend API communication
- **components/FaceDetector.tsx** - Face detection UI component
- **index.css** - Global styling and layout

### Smart Contracts
- **lib.ak** - Aiken smart contract library for DID management

### Configuration
- **.env.example** - Template for environment variables
- **docker-compose.yml** - Docker services orchestration
- **requirements.txt** - Python package dependencies
- **package.json** - Node.js package dependencies
- **vite.config.ts** - Frontend build configuration

## 📊 Component Interaction Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                            │
│                      http://localhost:5173                          │
└────────────────────────────┬────────────────────────────────────────┘
                             │ HTTP Requests
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                              │
│                     http://localhost:8000                           │
├──────────────┬──────────────┬──────────────┬───────────────────────┤
│              │              │              │                       │
▼              ▼              ▼              ▼                       ▼
┌────────┐  ┌─────────┐  ┌──────────┐  ┌──────────┐          ┌───────────┐
│ Models │  │ IPFS    │  │Blockchain│  │Database  │          │ Logging   │
│(Vision)│  │(Storage)│  │(Cardano) │  │(Optional)│          │           │
└────┬───┘  └────┬────┘  └────┬─────┘  └──────────┘          └───────────┘
     │           │            │
     │      ┌────▼────┐       │
     │      │ IPFS    │       │
     │      │ Node    │       │
     │      │ (5001)  │       │
     │      └─────────┘       │
     │                        │
     │                   ┌────▼────────┐
     │                   │  Cardano    │
     │                   │  Blockchain │
     │                   │  (Testnet)  │
     │                   └─────────────┘
     │
     └─ Face Detection (MediaPipe)
        - Embedding Generation
        - Landmark Extraction
```

## 🔄 Data Flow

1. **Face Detection Flow**
   - User uploads image to frontend
   - Frontend sends to backend API
   - Backend processes with MediaPipe
   - Returns detected faces with IDs

2. **DID Creation Flow**
   - Face embedding uploaded to IPFS
   - IPFS returns content hash
   - Backend creates DID linked to hash
   - Optional: Register DID on-chain

3. **Face Verification Flow**
   - User uploads face image
   - Backend generates embedding
   - Compares with stored DID hash
   - Returns verification result

## 🚀 Getting Started

1. Install dependencies: `pip install -r backend/requirements.txt`
2. Setup IPFS: `ipfs daemon`
3. Configure `.env`
4. Run backend: `python backend/main.py`
5. Run frontend: `cd frontend && npm run dev`
6. Open http://localhost:5173

## 📝 Environment Configuration

Key environment variables in `.env`:

```env
# Cardano
CARDANO_NETWORK=testnet
CARDANO_KUPO_URL=http://localhost:1442
CARDANO_OGMIOS_URL=http://localhost:1337

# IPFS
IPFS_GATEWAY_URL=http://localhost:5001
PINATA_JWT=your_jwt_here

# API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
```

## 🧪 Testing

- **Unit Tests**: `pytest backend/tests/`
- **API Docs**: http://localhost:8000/docs
- **Health Check**: curl http://localhost:8000/api/v1/health

## 📦 Dependencies

### Backend
- FastAPI - Web framework
- PyCardano - Blockchain integration
- MediaPipe - Face detection
- OpenCV - Computer vision
- requests - HTTP client

### Frontend
- React 18+ - UI framework
- TypeScript - Type safety
- Vite - Build tool
- Axios - HTTP client

## 🔐 Security Considerations

- Keep `.env` files out of version control
- Use environment variables for sensitive data
- Test on testnet before mainnet deployment
- Implement proper error handling
- Validate all user inputs
- Use HTTPS in production

---

Last Updated: 2025-01-01
