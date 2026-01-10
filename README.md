# 🚚 LICS - Logistics Intelligence & Command System

> **"AI Suggests, Humans Decide, Customers Stay Informed"**

A Human-in-the-Loop logistics decision support system that combines AI intelligence with human oversight for transparent, accountable delivery management.

---

## 🎯 What is LICS?

LICS is an intelligent logistics system with **FOUR USER ROLES**:

1. **Seller** → Creates shipment
2. **AI System** → Analyzes & recommends (NO final decision)
3. **Manager** → Reviews & decides (FINAL authority)
4. **Customer** → Tracks & stays informed

### 🔑 Golden Rule
```
❌ AI NEVER decides alone
✅ Humans ALWAYS have final control
```

---

## 📚 Documentation

All setup guides, philosophy docs, and references are in the **[README/](./README/)** folder:

### Quick Links:
- 🚀 **[Setup Guide](./README/SETUP_GUIDE.md)** - Start here for installation
- 🎯 **[Core Philosophy](./README/SYSTEM_CORE_PHILOSOPHY.md)** - Understand the system
- 💻 **[Developer Reference](./README/DEVELOPER_QUICK_REFERENCE.md)** - Code patterns
- 📁 **[Project Structure](./README/PROJECT_STRUCTURE.md)** - Directory guide
- ⚡ **[Quick Reference](./README/PHASE_0_SUMMARY.md)** - Command shortcuts

---

## 🚀 Quick Start

### 1. Activate Virtual Environment
```powershell
.venv\Scripts\activate
```

### 2. Start Backend API
```powershell
cd backend
uvicorn main:app --reload
```
Access: http://localhost:8000/docs

### 3. Start Frontend Dashboard
```powershell
cd frontend
streamlit run dashboard/control_tower.py
```
Access: http://localhost:8501

---

## 📁 Project Structure

```
LICS/
├── backend/          # FastAPI + backend services
├── frontend/         # Streamlit user interface
├── intelligence/     # AI decision modules (11 engines)
├── realtime/         # WebSocket (Phase 2)
├── tests/            # All test files (200+ tests)
├── docs/             # Technical documentation
├── README/           # Setup guides & philosophy ⭐
├── data/             # CSV datasets
├── logs/             # System logs
├── configs/          # Configuration files
└── database/         # MongoDB (Phase 1)
```

---

## ✅ Current Status

| Component | Status | Details |
|-----------|--------|---------|
| **Backend API** | ✅ Operational | 23 REST endpoints |
| **Intelligence Modules** | ✅ Complete | 11 AI engines |
| **Testing Suite** | ✅ Complete | 200+ tests passing |
| **Documentation** | ✅ Complete | Comprehensive guides |
| **Database** | ⏳ Phase 1 | MongoDB integration |
| **Authentication** | ⏳ Phase 1 | JWT + RBAC |
| **Frontend Redesign** | ⏳ Phase 2 | Multi-page app |

---

## 🎯 Core Features

### Intelligence Modules (11 Engines)
1. **Risk Engine** - 9-parameter scoring (0-100)
2. **Address Intelligence** - NLP-based parsing
3. **Weather Impact** - 3 API provider integration
4. **Pre-Dispatch Gate** - DISPATCH/DELAY/RESCHEDULE logic
5. **Vehicle Selector** - Hyper-local feasibility
6. **CO₂ Calculator** - Emission vs speed tradeoff
7. **Human Override** - Manager authority with logging
8. **Customer Notifier** - Proactive communication
9. **Delivery Simulator** - Live tracking
10. **End-of-Day Logger** - Analytics & insights
11. **Learning Loop** - Continuous improvement

### Key Differentiator
✨ **Pre-dispatch delay notifications** - Customers are informed BEFORE dispatch, not after failed delivery

---

## 🔄 System Flow

```
Seller Creates → AI Analyzes → Manager Decides → Customer Informed → System Learns
```

---

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python 3.14
- **Frontend**: Streamlit (redesign planned)
- **Database**: MongoDB (Phase 1), CSV (current)
- **AI/ML**: Custom risk engine, NLP
- **APIs**: Weather APIs (3 providers)
- **Testing**: pytest, 200+ tests
- **Auth**: JWT + RBAC (Phase 1)
- **Real-time**: WebSocket (Phase 2)

---

## 📊 Success Metrics

- ✅ 200+ tests, 100% passing
- ✅ 11 intelligence modules operational
- ✅ 23 REST API endpoints
- ✅ Complete documentation
- ✅ Human-in-the-loop philosophy

---

## 📖 Full Documentation

Visit the **[README folder](./README/)** for complete guides:
- Setup & installation
- System philosophy
- Developer guidelines
- Project structure
- Quick references

Technical documentation: **[docs/](./docs/)** folder

---

## 🚀 Roadmap

- ✅ **Phase 0**: Environment & project setup (COMPLETE)
- ⏳ **Phase 1**: MongoDB + Authentication (IN PROGRESS)
- 📅 **Phase 2**: Frontend redesign (Planned)
- 📅 **Phase 3**: Real-time features (Planned)
- 📅 **Phase 4**: Production deployment (Planned)

---

## 🤝 Contributing

Before contributing, please read:
1. [SYSTEM_CORE_PHILOSOPHY.md](./README/SYSTEM_CORE_PHILOSOPHY.md) - Core concepts
2. [DEVELOPER_QUICK_REFERENCE.md](./README/DEVELOPER_QUICK_REFERENCE.md) - Code patterns

Every feature must follow the principle: **"AI suggests, humans decide"**

---

## 📞 Support

- Setup issues? → [SETUP_GUIDE.md](./README/SETUP_GUIDE.md)
- Understand system? → [SYSTEM_CORE_PHILOSOPHY.md](./README/SYSTEM_CORE_PHILOSOPHY.md)
- Code patterns? → [DEVELOPER_QUICK_REFERENCE.md](./README/DEVELOPER_QUICK_REFERENCE.md)

---

## 📄 License

[Your License Here]

---

## 👥 Team

**Owner**: IleshDevX  
**Repository**: [07-Logistics-Intelligence---Command-System--LICS-](https://github.com/IleshDevX/07-Logistics-Intelligence---Command-System--LICS-)

---

**Built with the philosophy**: *AI is the advisor, Manager is the authority, Customer is informed* 💪
