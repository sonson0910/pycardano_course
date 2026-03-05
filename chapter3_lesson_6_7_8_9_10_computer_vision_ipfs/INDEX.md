# 📖 Documentation Index

Hướng dẫn nhanh để tìm những gì bạn cần.

---

## 🚀 Bắt Đầu Nhanh

👉 **Start Here**: [README.md](README.md) - Project overview (5 min read)

---

## 📋 Tài Liệu Chính

| File | Nội Dung | Thời Gian |
|------|---------|---------|
| **[SETUP.md](SETUP.md)** | Cài đặt đầy đủ: Blockfrost, Backend, Frontend, IPFS | 20 min |
| **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** | Cấu trúc project, layout files | 5 min |
| **[SECURITY.md](SECURITY.md)** | Bảo mật, private keys, best practices | 10 min |

---

## 🔗 Bên Ngoài

**Blockfrost:**
- Get API Key: https://blockfrost.io/
- Docs: https://docs.blockfrost.io/
- Status: https://status.blockfrost.io/

**IPFS (Kubo):**
- Install: https://docs.ipfs.tech/
- Docs: https://docs.ipfs.tech/

**Cardano:**
- Developers: https://developers.cardano.org/
- Testnet Faucet: https://docs.cardano.org/cardano-testnet/tools/faucet

**Aiken:**
- Aiken Lang: https://aiken-lang.org/
- Docs: https://docs.aiken-lang.org/

---

## 🎯 Quick Navigation

### "Tôi muốn..."

**...cài đặt toàn bộ hệ thống**
→ [SETUP.md](SETUP.md)

**...hiểu cấu trúc project**
→ [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

**...biết về bảo mật**
→ [SECURITY.md](SECURITY.md)

**...test API**
→ Backend running → http://localhost:8000/docs

**...xem code**
→ `backend/app/` hoặc `frontend/src/`

**...deploy smart contract**
→ `cd smart_contracts && aiken build`

---

## 📊 Project Overview

```
Frontend (React)     ← http://localhost:5173
    ↓ API calls
Backend (FastAPI)    ← http://localhost:8000
    ↓
Blockchain (Cardano Preview Testnet via Blockfrost)
Storage (IPFS local + optional Pinata)
```

---

## ✅ Status

- ✅ **Code**: Production-ready (no mocks)
- ✅ **Blockchain**: Real Blockfrost API
- ✅ **Storage**: Real IPFS + optional Pinata
- ✅ **Documentation**: Clean & organized
- ⏳ **Testing**: Ready for testnet

---

## 📞 Troubleshooting

**Backend won't start?**
- Check: `BLOCKFROST_PROJECT_ID` in `.env`
- See: [SETUP.md](SETUP.md) → Troubleshooting

**IPFS connection error?**
- Run: `ipfs daemon` in terminal
- See: [SETUP.md](SETUP.md) → IPFS Setup

**Frontend blank?**
- Run: `npm install` in frontend/
- Run: `npm run dev`

---

## 🔄 Development Workflow

1. Make code changes
2. Backend: `python main.py`
3. Frontend: `npm run dev`
4. Test at http://localhost:5173
5. API docs at http://localhost:8000/docs

---

## 📝 Adding New Docs

- Keep docs in `docs/` folder
- Add reference here
- Max one page per topic
- Use clear headers and examples

---

**Last Updated**: October 16, 2025
**Maintainer**: Sonson0910
