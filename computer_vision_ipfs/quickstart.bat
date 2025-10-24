@echo off
REM Computer Vision + Blockchain DApp - Windows Quick Start
REM This script starts both backend and frontend servers

echo.
echo ========================================
echo  🚀 Computer Vision + Blockchain DApp
echo  Face Tracking with DIDs on Cardano
echo ========================================
echo.

REM Check if backend is running
echo Checking dependencies...

python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Install from https://www.python.org/
    exit /b 1
)

node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found. Install from https://nodejs.org/
    exit /b 1
)

echo ✅ Python and Node.js found
echo.

REM Set environment variables
set BLOCKFROST_PROJECT_ID=preprod0K9MnKqsU21MJvqu00V4Laf4pz7dALPK
set PYTHONUNBUFFERED=1

echo.
echo ========================================
echo 📋 Step 1: Starting Backend (PyTorch Vision + FastAPI)
echo ========================================
echo.
echo Opening backend server on http://localhost:8000
echo.

cd backend
start cmd /k "python main.py"

REM Wait for backend to start
timeout /t 5 /nobreak

echo.
echo ========================================
echo 📋 Step 2: Starting Frontend (React DApp)
echo ========================================
echo.
echo Opening frontend on http://localhost:5173
echo.

cd ..\frontend
npm install >nul 2>&1
start cmd /k "npm run dev"

echo.
echo ========================================
echo ✅ SERVICES STARTED!
echo ========================================
echo.
echo 🌐 Frontend:  http://localhost:5173
echo 📡 Backend:   http://localhost:8000
echo 📚 API Docs:  http://localhost:8000/docs
echo.
echo 📝 WORKFLOW:
echo   1. Upload face image
echo   2. Auto-create DID
echo   3. Register/Update/Verify/Revoke DIDs
echo.
echo Press any key to continue monitoring...
pause
