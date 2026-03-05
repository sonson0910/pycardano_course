# 📖 Setup Guide

**Complete installation and configuration guide for Computer Vision + Blockchain DApp**

---

## 🔧 Prerequisites

- **Python**: 3.11+
- **Node.js**: 16+
- **Git**: Latest version
- **Blockfrost**: Free account (blockfrost.io)
- **IPFS** (optional): Kubo daemon

---

## 1️⃣ Blockfrost Setup (5 min)

### Get Your Free API Key

1. Go to: https://blockfrost.io/
2. Click **Sign Up**
3. Create account and verify email
4. Go to **Dashboard → Projects**
5. Click **Create Project**
6. Select network: **Preview** (testnet)
7. Copy **Project ID** (looks like: `preview_xxx...`)

Save this key - you'll need it!

---

## 2️⃣ Backend Setup (5 min)

### Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**What gets installed:**
- `pycardano` - Cardano blockchain API
- `fastapi` - Web framework
- `opencv-python` - Face detection
- `python-dotenv` - Environment config

### Create Environment File

```bash
# In root directory, create .env
BLOCKFROST_PROJECT_ID=preview_your_key_from_step_1
IPFS_GATEWAY_URL=http://localhost:5001
PINATA_JWT=  # leave empty for now
```

### Test Backend

```bash
cd backend
python -c "
import os
os.environ['BLOCKFROST_PROJECT_ID'] = 'test'
from app.blockchain.cardano_client import CardanoClient
print('✅ Backend imports OK!')
"
```

**If you see ✅**, backend is configured correctly!

**Note**: Full initialization requires BLOCKFROST_PROJECT_ID to be set. That's tested when you run `python main.py`.

---

## 3️⃣ Frontend Setup (3 min)

### Install Node Dependencies

```bash
cd frontend
npm install
```

**What gets installed:**
- React 18 with TypeScript
- Vite (build tool)
- UI libraries

---

## 4️⃣ IPFS Setup (Optional but Recommended) (5 min)

### Install Kubo

**Windows:**
```bash
# Download from: https://docs.ipfs.tech/install/command-line/
# Or use Chocolatey:
choco install go-ipfs
```

**macOS:**
```bash
brew install ipfs
```

**Linux:**
```bash
sudo apt install ipfs
```

### Initialize IPFS

```bash
# First time only
ipfs init

# Output:
# initializing IPFS node at /home/user/.ipfs
# ✅ Done!
```

### Test IPFS Connection

```bash
# Start daemon
ipfs daemon

# In another terminal:
curl http://localhost:5001/api/v0/version
# Should get: {"Version":"0.xx.x", ...}
```

---

## 5️⃣ Smart Contracts (Optional) (5 min)

### Install Aiken

```bash
# https://aiken-lang.org/installation
# Windows: Download installer
# macOS: brew install aiken-lang/aiken/aiken
# Linux: curl ... | bash
```

### Build Validator

```bash
cd smart_contracts
aiken build

# Output:
# ✓ Building lib/computer_vision_dapp
# ✓ Generating Plutus script
# ✓ Wrote plutus.json
```

**Important:** This creates `plutus.json` needed by backend!

---

## 6️⃣ Run Everything

### Terminal 1: IPFS (Optional)

```bash
ipfs daemon
# Leaves running: Kubo HTTP API at http://127.0.0.1:5001
```

### Terminal 2: Backend

```bash
cd backend
python main.py

# Output:
# ✅ Connected to Cardano Preview Testnet via Blockfrost
# INFO: Uvicorn running on http://0.0.0.0:8000
```

### Terminal 3: Frontend

```bash
cd frontend
npm run dev

# Output:
# ➜ Local: http://localhost:5173/
```

---

## ✅ Verification

### Check Backend

```bash
# Open in browser:
http://localhost:8000/docs

# Should see: FastAPI Swagger UI with endpoints
```

### Check Frontend

```bash
# Open in browser:
http://localhost:5173

# Should see: React app loaded
```

### Check Blockchain Connection

```bash
# In Python:
python -c "
from app.blockchain.cardano_client import CardanoClient
client = CardanoClient()
print('✅ Connected to Blockfrost!')
"
```

### Check IPFS Connection (if running)

```bash
# In terminal:
curl http://localhost:5001/api/v0/version

# Should return JSON with version
```

---

## 🚀 First Test Run

### 1. Get Test ADA

Go to: https://docs.cardano.org/cardano-testnet/tools/faucet

- Select: **Preview Testnet**
- Paste any address
- Get 10 tADA (test ADA)

### 2. Create Wallet

```bash
python -c "
from pycardano import PaymentSigningKey, PaymentVerificationKey, Address, Network
sk = PaymentSigningKey.generate()
sk.save('me.sk')
vk = PaymentVerificationKey.from_signing_key(sk)
addr = Address(payment_part=vk.hash(), network=Network.TESTNET)
with open('me.addr', 'w') as f:
    f.write(str(addr))
print('Address:', addr)
"
```

Save the address and paste in faucet!

### 3. Check Balance

```python
from app.blockchain.cardano_client import CardanoClient
from pycardano import Address

client = CardanoClient()
wallet_addr = Address.from_primitive("addr_test1...")  # Your address
balance = client.get_balance(wallet_addr)
print(f"Balance: {balance/1_000_000:.2f} ADA")
```

---

## 🛑 Troubleshooting

### "BLOCKFROST_PROJECT_ID not set"
```bash
# Verify .env exists and has:
echo $BLOCKFROST_PROJECT_ID
# Should show your key

# If empty, set it:
$env:BLOCKFROST_PROJECT_ID = "preview_xxx..."
```

### "Cannot connect to Blockfrost"
- Check internet connection
- Verify Project ID is correct
- Check Blockfrost status: https://status.blockfrost.io/

### "IPFS connection refused"
- Start daemon: `ipfs daemon`
- Check port 5001 is open: `netstat -an | grep 5001`

### "No module named 'pycardano'"
```bash
cd backend
pip install pycardano
```

### Frontend shows blank page
```bash
cd frontend
npm install
npm run dev
```

---

## 🐳 Docker Setup (Alternative)

```bash
# Build and start all services
docker-compose up

# Access:
# Frontend: http://localhost:5173
# Backend: http://localhost:8000
# IPFS: http://localhost:5001
```

---

## ✨ Next Steps

1. ✅ **Setup complete!**
2. 📖 Read **ARCHITECTURE.md** - understand the system
3. 🔌 Read **API.md** - learn available endpoints
4. 🚀 Deploy to testnet

---

## 📞 Support

- Issues? Check the docs/
- Blockfrost help: https://docs.blockfrost.io/
- IPFS help: https://docs.ipfs.tech/
- Cardano help: https://developers.cardano.org/
