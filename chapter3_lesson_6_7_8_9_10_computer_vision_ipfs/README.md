# 🎯 Chapter 3 — Computer Vision + Blockchain (Lessons 6-10)

**Tích hợp Computer Vision với Blockchain: Face Tracking sử dụng DIDs trên Cardano**

---

## 📋 Danh sách bài học

| Bài | Chủ đề | Thư mục |
|-----|--------|---------|
| **Lesson 6** | CV + DID Integration (Smart Contract, Aiken) | `lesson6_cv_did_integration/` |
| **Lesson 7** | Setup AI Model (Face Tracking) + IPFS | `lesson7_face_tracking_ipfs/` |
| **Lesson 8** | Off-chain Code: AI Logic + On-chain TX | `lesson8_offchain_code/` |
| **Lesson 9** | Deploy DApp hoàn chỉnh lên Testnet | `lesson9_deploy_dapp/` |
| **Lesson 10** | Demo DApp | `lesson10_demo_dapp/` |

## 🏗️ Kiến trúc tổng quan

```
User (Browser)
     ↓
React Frontend (:5173)          [Lesson 10]
     ↓ HTTP API
FastAPI Backend (:8000)          [Lesson 9]
     ├─ MediaPipe (Face Detection) [Lesson 7]
     ├─ Pinata IPFS (Off-chain)    [Lesson 7]
     └─ PyCardano + Blockfrost     [Lesson 8]
            ↓
     Aiken Smart Contract           [Lesson 6]
     (DID Validator, Plutus V3)
```

## ⚙️ Yêu cầu chung

- Python 3.9+
- Node.js 18+ (Lesson 10)
- Aiken v1.1.21 (Lesson 6)
- Tài khoản [Blockfrost](https://blockfrost.io) — Project ID cho **Preprod**
- Tài khoản [Pinata](https://pinata.cloud) — JWT token (miễn phí)
- Ví Cardano có seed phrase + ít nhất **5 tADA** trên Preprod

## 🔧 Cài đặt

### 1. Tạo môi trường ảo

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
```

### 2. Cấu hình biến môi trường

```bash
cp .env.example .env
# Điền: BLOCKFROST_PROJECT_ID, PINATA_JWT, MNEMONIC
```

### 3. Bắt đầu từ Lesson 6

```bash
cd lesson6_cv_did_integration/did_contract
aiken build && aiken check
```

## 🔗 Tài liệu tham khảo

- [Aiken Language](https://aiken-lang.org/)
- [PyCardano Documentation](https://pycardano.readthedocs.io/)
- [Blockfrost API](https://docs.blockfrost.io/)
- [MediaPipe Face Detection](https://ai.google.dev/edge/mediapipe/solutions/vision/face_detector)
- [Pinata IPFS](https://docs.pinata.cloud/)

---

**Author**: Sonson0910 @ Cardano Developer Course
