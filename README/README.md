# 📚 LICS - Documentation Index

Welcome to the LICS (Logistics Intelligence & Command System) documentation hub. This folder contains all instructional guides, setup documentation, and reference materials.

---

## 📖 Quick Navigation

### 🚀 Getting Started

1. **[SETUP_GUIDE.md](./SETUP_GUIDE.md)** ⭐ START HERE
   - Complete Phase 0 setup instructions
   - Installation steps
   - How to run the system
   - Troubleshooting guide
   - Next steps roadmap

2. **[PHASE_0_SUMMARY.md](./PHASE_0_SUMMARY.md)**
   - Quick reference card
   - Phase 0 checklist
   - Command shortcuts
   - Project status overview

---

### 🎯 Core Concepts

3. **[SYSTEM_CORE_PHILOSOPHY.md](./SYSTEM_CORE_PHILOSOPHY.md)** ⭐ MUST READ
   - The 4 users (Seller, AI, Manager, Customer)
   - Golden rule: "AI NEVER decides alone"
   - Complete end-to-end flow
   - Design principles
   - Success metrics

4. **[DEVELOPER_QUICK_REFERENCE.md](./DEVELOPER_QUICK_REFERENCE.md)** ⭐ FOR DEVELOPERS
   - Code patterns (WRONG vs CORRECT)
   - API endpoint examples
   - Database schema guidelines
   - UI/UX patterns
   - Testing checklist
   - Common mistakes to avoid

---

### 📁 Project Organization

5. **[PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md)**
   - Complete directory structure
   - Folder purposes
   - Dependencies installed
   - Run commands
   - Project status

---

## 🎓 Reading Order (Recommended)

### For New Team Members:
1. Read **SYSTEM_CORE_PHILOSOPHY.md** first (understand what we're building)
2. Then **SETUP_GUIDE.md** (set up your environment)
3. Keep **DEVELOPER_QUICK_REFERENCE.md** open while coding
4. Reference **PROJECT_STRUCTURE.md** when navigating codebase

### For Project Reviewers:
1. **PHASE_0_SUMMARY.md** - Quick overview
2. **SYSTEM_CORE_PHILOSOPHY.md** - Core concepts
3. **PROJECT_STRUCTURE.md** - Technical details

---

## 🔑 Key Concepts (TL;DR)

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   LICS: "AI Suggests, Humans Decide, Customers Informed"   │
│                                                             │
│   4 Users:  Seller → AI → Manager → Customer               │
│   Golden Rule: AI NEVER decides alone                      │
│   Philosophy: Human-in-the-loop decision support           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Documentation Status

| Document | Status | Purpose | Audience |
|----------|--------|---------|----------|
| SETUP_GUIDE.md | ✅ Complete | Setup & installation | Everyone |
| SYSTEM_CORE_PHILOSOPHY.md | ✅ Complete | Core concepts | Everyone |
| DEVELOPER_QUICK_REFERENCE.md | ✅ Complete | Code guidelines | Developers |
| PROJECT_STRUCTURE.md | ✅ Complete | Directory map | Developers |
| PHASE_0_SUMMARY.md | ✅ Complete | Quick reference | Everyone |

---

## 🗂️ Other Documentation

### Technical Documentation
Located in `../docs/` folder:
- System architecture
- API documentation
- Data schemas
- Decision logic
- Test cases
- Future roadmap

### Review Package
Located in `../docs/review_package/`:
- Complete project review documents
- Problem statement
- System architecture
- Process flowcharts
- Test cases
- Future scope

---

## 🚀 Quick Start Commands

### Activate Environment
```powershell
.venv\Scripts\activate
```

### Start Backend
```powershell
cd backend
uvicorn main:app --reload
```

### Start Frontend
```powershell
cd frontend
streamlit run dashboard/control_tower.py
```

### Run Tests
```powershell
cd tests\testing
python test_fastapi_backend.py
```

---

## 💡 Philosophy Reminder

Before writing ANY code, ask yourself:

1. ✅ **Transparency**: Does AI explain WHY?
2. ✅ **Control**: Can manager override?
3. ✅ **Communication**: Is customer informed?
4. ✅ **Accountability**: Is it logged?
5. ✅ **Learning**: Does system improve?

If ANY answer is NO → Redesign the feature!

---

## 📞 Need Help?

- **Setup issues?** → Read SETUP_GUIDE.md troubleshooting section
- **Understanding system?** → Read SYSTEM_CORE_PHILOSOPHY.md
- **Code patterns?** → Check DEVELOPER_QUICK_REFERENCE.md
- **Project structure?** → See PROJECT_STRUCTURE.md

---

## 📅 Last Updated

- **Date**: January 10, 2026
- **Phase**: Phase 0 Complete ✅
- **Next**: Phase 1 - MongoDB + Authentication

---

**Remember**: This system is built on the principle that AI assists, but humans decide. Every line of code must reflect this philosophy! 💪
