# ─── DID Face DApp Backend ───
# FastAPI + MediaPipe + PyCardano
# Build context: chapter3_lesson_6_7_8_9_10_computer_vision_ipfs/ (root)
#
# Build: docker build -t did-face-dapp .
# Run:   docker run -p 8000:8000 --env-file .env did-face-dapp

FROM python:3.11-slim

# System deps for OpenCV headless + mediapipe
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-dev \
    libglu1-mesa \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first (Docker layer cache)
COPY lesson9_deploy_dapp/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy smart contract blueprint
COPY lesson6_cv_did_integration/did_contract/plutus.json /app/plutus.json

# Copy backend source
COPY lesson9_deploy_dapp/app /app/app/
COPY lesson9_deploy_dapp/models /app/models/

# Download MediaPipe model at build time
RUN mkdir -p /app/models && python -c "\
import urllib.request; \
urllib.request.urlretrieve( \
    'https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite', \
    '/app/models/blaze_face_short_range.tflite' \
)"

# Environment
ENV PLUTUS_JSON_PATH=/app/plutus.json
ENV MODEL_DIR=/app/models

# Expose port
EXPOSE 8000

# Production server
CMD ["gunicorn", "app.main:app", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "1", \
     "--timeout", "120"]
