# Development Setup Guide

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional)
- Git

## Backend Setup

### 1. Install Python Dependencies

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Setup Environment Variables

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Setup Local Services

#### IPFS Node (Kubo)
```bash
# Install from https://github.com/ipfs/kubo/releases
# Then run:
ipfs daemon
```

#### Cardano (Optional)
- Use testnet (no local node needed)
- Or setup local node with Docker

### 4. Run Backend

```bash
python main.py
```

Backend will be available at: `http://localhost:8000`

API Docs: `http://localhost:8000/docs`

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Run Development Server

```bash
npm run dev
```

Frontend will be available at: `http://localhost:5173`

## Docker Setup (Optional)

### Build and Run

```bash
docker-compose up
```

Services:
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- IPFS: http://localhost:8080
- API Docs: http://localhost:8000/docs

### Rebuild

```bash
docker-compose build --no-cache
docker-compose up
```

## Testing the API

### Health Check
```bash
curl http://localhost:8000/api/v1/health
```

### Upload Image for Face Detection
```bash
curl -X POST http://localhost:8000/api/v1/detect-faces \
  -F "file=@test_image.jpg"
```

### API Documentation
Visit: http://localhost:8000/docs

## Troubleshooting

### Port Already in Use
```bash
# Find process using port
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>  # Mac/Linux
taskkill /PID <PID> /F  # Windows
```

### IPFS Connection Error
```bash
# Ensure IPFS daemon is running
ipfs daemon

# Check IPFS connectivity
curl http://localhost:5001/api/v0/version
```

### Python Dependencies Issue
```bash
# Upgrade pip
pip install --upgrade pip

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Permission Denied (IPFS)
```bash
# Initialize IPFS (if not done)
ipfs init
ipfs daemon
```

## Development Workflow

1. **Backend Development**
   - Create features in `backend/app/`
   - Test with FastAPI docs at `http://localhost:8000/docs`
   - Run tests: `pytest backend/tests/`

2. **Frontend Development**
   - Create components in `frontend/src/components/`
   - Use hot reload: changes auto-update
   - Build for production: `npm run build`

3. **Smart Contracts**
   - Write Aiken contracts in `smart_contracts/`
   - Compile: `aiken build`
   - Deploy to testnet

## Next Steps

1. Setup local IPFS node
2. Configure `.env` with your settings
3. Run backend: `python main.py`
4. Run frontend: `npm run dev`
5. Test API endpoints
6. Deploy to production

## Resources

- [PyCardano Docs](https://pycardano.readthedocs.io/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [MediaPipe Docs](https://google.github.io/mediapipe/)
- [IPFS Docs](https://docs.ipfs.io/)
