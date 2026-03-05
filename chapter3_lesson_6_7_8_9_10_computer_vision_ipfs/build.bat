@echo off
REM Build script for Computer Vision + Blockchain DApp (Windows)

echo 🚀 Building Computer Vision + Blockchain DApp...
echo ================================================

REM Build Backend
echo.
echo 📦 Building Backend...
cd backend
pip install -r requirements.txt
cd ..

REM Build Frontend
echo.
echo 📦 Building Frontend...
cd frontend
call npm install
call npm run build
cd ..

REM Check if Aiken is installed
where aiken >nul 2>nul
if %errorlevel% equ 0 (
    echo.
    echo 📦 Building Smart Contracts...
    cd smart_contracts
    call aiken build
    cd ..
)

echo.
echo ✅ Build complete!
echo.
echo Next steps:
echo 1. Start backend: cd backend ^&^& python main.py
echo 2. Start frontend: cd frontend ^&^& npm run dev
echo 3. Open http://localhost:5173
