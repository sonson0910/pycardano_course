"""
Lesson 9 — FastAPI DApp Backend

Entry point cho REST API server.
Kết hợp Face Detection + IPFS + Blockchain.

Usage:
    python -m uvicorn app.main:app --reload --port 8000
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import did, face

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup & shutdown events"""
    logger.info("🚀 Starting DApp Backend...")
    yield
    logger.info("🛑 Shutting down...")


app = FastAPI(
    title="DID Face Tracking DApp",
    description="Computer Vision + Blockchain: Face Identity on Cardano",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — cho phép frontend kết nối
allowed_origins = [
    "http://localhost:5173",
    "http://localhost:3000",
]

# Thêm Vercel domain từ env (set khi deploy)
import os
vercel_url = os.getenv("FRONTEND_URL", "")
if vercel_url:
    allowed_origins.append(vercel_url)

# Cho phép tất cả *.vercel.app domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(face.router, prefix="/api/v1", tags=["Face Detection"])
app.include_router(did.router, prefix="/api/v1", tags=["DID Management"])


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "did-face-dapp"}
