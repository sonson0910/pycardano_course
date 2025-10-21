"""
Main entry point for Computer Vision + Blockchain DApp Backend
Face Tracking with DIDs and IPFS Integration
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import router

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    logger.info("🚀 Starting Computer Vision + Blockchain Backend")
    logger.info("Vision Processing Server initialized")
    yield
    logger.info("🛑 Shutting down server")


# Create FastAPI app
app = FastAPI(
    title="Computer Vision + Blockchain DApp",
    description="Face Tracking with DIDs and IPFS Integration",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(router, prefix="/api/v1", tags=["vision-blockchain"])

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Computer Vision + Blockchain Backend",
        "version": "0.1.0",
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Computer Vision + Blockchain DApp Backend",
        "docs": "/docs",
        "openapi": "/openapi.json",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
