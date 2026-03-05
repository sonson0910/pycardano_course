"""
Cardano Testnet Configuration
Run local services for development
"""

import subprocess
import sys
import time
import os
from pathlib import Path


def run_command(cmd, description):
    """Run shell command"""
    print(f"\n🚀 {description}...")
    subprocess.Popen(cmd, shell=True)
    time.sleep(2)


def setup_local_environment():
    """Setup local Cardano testnet environment"""

    print("=" * 60)
    print("Computer Vision + Blockchain DApp - Local Setup")
    print("=" * 60)

    # Check Python
    print(f"\n✅ Python {sys.version.split()[0]}")

    # Check npm
    result = subprocess.run("npm --version", shell=True, capture_output=True)
    if result.returncode == 0:
        print(f"✅ npm {result.stdout.decode().strip()}")

    # Check Docker
    result = subprocess.run("docker --version", shell=True, capture_output=True)
    if result.returncode == 0:
        print(f"✅ Docker {result.stdout.decode().strip()}")

    # Create .env if not exists
    env_path = Path(".env")
    if not env_path.exists():
        print("\n📝 Creating .env from .env.example...")
        with open(".env.example") as f:
            content = f.read()
        with open(".env", "w") as f:
            f.write(content)
        print("✅ .env created")

    print("\n" + "=" * 60)
    print("Setup Instructions:")
    print("=" * 60)

    print(
        """
1. 💾 Start IPFS Node:
   ipfs daemon

2. 🐍 Start Backend (in another terminal):
   cd backend
   python -m venv venv
   venv\\Scripts\\activate  # Windows
   source venv/bin/activate  # Mac/Linux
   python main.py

3. ⚛️  Start Frontend (in another terminal):
   cd frontend
   npm install
   npm run dev

4. 🌐 Open http://localhost:5173 in your browser

5. 📚 API Docs: http://localhost:8000/docs
    """
    )

    print("\n" + "=" * 60)
    print("Or use Docker:")
    print("=" * 60)
    print(
        """
docker-compose up
    """
    )


if __name__ == "__main__":
    setup_local_environment()
