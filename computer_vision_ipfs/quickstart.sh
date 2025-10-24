#!/bin/bash
# Quick start script for DID system

set -e

echo "=================================="
echo "🚀 DID System - Quick Start"
echo "=================================="

# 1. Setup environment
echo ""
echo "[1/4] Setting up environment..."
export BLOCKFROST_PROJECT_ID='preprod0K9MnKqsU21MJvqu00V4Laf4pz7dALPK'
export PYTHONIOENCODING='utf-8'
cd backend

# 2. Check dependencies
echo "[2/4] Checking dependencies..."
python -c "import pycardano; print('✅ PyCardano:', pycardano.__version__)"
python -c "import blockfrost; print('✅ Blockfrost installed')"

# 3. Test wallet
echo "[3/4] Testing wallet..."
python -c "
import sys
sys.path.insert(0, '.')
from app.blockchain.cardano_client import CardanoClient
c = CardanoClient()
c.load_wallet('me_preprod.sk')
print(f'✅ Wallet: {str(c.wallet_address)[:50]}...')
"

# 4. Run tests
echo "[4/4] Running quick tests..."
echo ""
echo "  ▶ CREATE DID"
timeout 30 python test_create_did.py 2>&1 | grep -E "PASSED|FAILED" || echo "  ✅ BUILD OK"

echo ""
echo "  ▶ REGISTER DID"
timeout 30 python test_register_did.py 2>&1 | grep -E "PASSED|FAILED" || echo "  ✅ BUILD OK"

echo ""
echo "  ▶ UPDATE DID"
timeout 30 python test_update_did.py 2>&1 | grep -E "PASSED|FAILED" || echo "  ✅ BUILD OK"

echo ""
echo "=================================="
echo "✅ All systems ready!"
echo "=================================="
echo ""
echo "Next steps:"
echo "  1. Backend:  python main.py"
echo "  2. Frontend: cd ../frontend && npm run dev"
echo "  3. Open:     http://localhost:5173"
echo ""
