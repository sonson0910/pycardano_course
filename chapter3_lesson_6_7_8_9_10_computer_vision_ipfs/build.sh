#!/bin/bash

# Build script for Computer Vision + Blockchain DApp

echo "🚀 Building Computer Vision + Blockchain DApp..."
echo "================================================"

# Build Backend
echo ""
echo "📦 Building Backend..."
cd backend
pip install -r requirements.txt
cd ..

# Build Frontend
echo ""
echo "📦 Building Frontend..."
cd frontend
npm install
npm run build
cd ..

# Build Smart Contracts (if Aiken is installed)
if command -v aiken &> /dev/null; then
    echo ""
    echo "📦 Building Smart Contracts..."
    cd smart_contracts
    aiken build
    cd ..
fi

echo ""
echo "✅ Build complete!"
echo ""
echo "Next steps:"
echo "1. Start backend: cd backend && python main.py"
echo "2. Start frontend: cd frontend && npm run dev"
echo "3. Open http://localhost:5173"
