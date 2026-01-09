# LICS Web Application

## 🚚 Logistics Intelligence & Command System

A human-in-the-loop logistics platform where AI predicts delivery risks before dispatch, managers make transparent decisions, and customers are proactively informed.

---

## 🎯 Core Philosophy

✅ **AI suggests, humans decide**  
✅ **Customers forgive delays, not silence**  
✅ **Transparent, explainable decisions**  
✅ **Continuous learning from outcomes**

---

## 🏗️ Architecture

### Technology Stack
- **Frontend**: Streamlit (Python-based multi-page app)
- **Backend**: FastAPI (existing, 23 REST endpoints)
- **AI Modules**: Custom intelligence engines (risk, address, weather, decision)
- **Authentication**: Session-based (demo-safe)
- **Data**: CSV-based (development), MongoDB-ready

### User Roles
1. **Seller** - Create shipments, view AI analysis
2. **Manager** - Review decisions, apply overrides, manage risk
3. **Supervisor** - Analytics view only
4. **Customer** - Public tracking (no login)

---

## 📁 Project Structure

```
webapp/
├── app.py                          # Main entry point
├── .streamlit/
│   └── config.toml                 # Streamlit configuration
├── pages/
│   ├── 1_📦_Seller_Portal.py      # Shipment creation with AI analysis
│   ├── 2_🧭_Control_Tower.py      # Manager dashboard (TODO)
│   ├── 3_📊_Analytics.py           # Analytics dashboard (TODO)
│   └── 4_📍_Customer_Tracking.py   # Public tracking page (TODO)
├── components/
│   ├── auth.py                     # Authentication & session management
│   ├── shipment_form.py            # (Future) Modular form component
│   ├── risk_heatmap.py             # (Future) Risk visualization
│   └── override_form.py            # (Future) Manager override UI
├── utils/
│   ├── session_manager.py          # Session state management
│   ├── styling.py                  # Custom CSS and themes
│   └── notifications.py            # (Future) Notification utilities
└── README.md                       # This file
```

---

## 🚀 How to Run

### Prerequisites
- Python 3.11+
- All backend modules installed (see parent `requirements.txt`)

### Installation

1. **Install Streamlit** (if not already installed):
```bash
pip install streamlit
```

2. **Navigate to webapp directory**:
```bash
cd webapp
```

3. **Run the application**:
```bash
streamlit run app.py
```

4. **Access the app**:
Open your browser to `http://localhost:8501`

---

## 🔐 Demo Credentials

### Sellers
- **Username**: `seller1` | **Password**: `seller123`
- **Username**: `seller2` | **Password**: `seller123`

### Managers
- **Username**: `manager1` | **Password**: `manager123`
- **Username**: `manager2` | **Password**: `manager123`

### Supervisor
- **Username**: `supervisor1` | **Password**: `super123`

---

## ✨ Features Implemented

### ✅ Phase 1 (Current)
- [x] Authentication system with role-based access
- [x] Seller Portal with shipment creation form
- [x] Real-time AI analysis integration:
  - [x] Address Intelligence (NLP + landmarks)
  - [x] Weather Impact Analysis
  - [x] Risk Scoring (7-factor engine)
  - [x] Pre-Dispatch Decision Gate
  - [x] Vehicle Feasibility Check
  - [x] CO₂ Trade-off Analysis
- [x] Clean, responsive UI with custom styling
- [x] Role-based dashboards (Seller/Manager/Supervisor)
- [x] Session management

### 🚧 Phase 2 (Coming Next)
- [ ] Manager Control Tower
  - [ ] Risk heatmap visualization
  - [ ] Shipment review interface
  - [ ] Human override form with mandatory reasons
  - [ ] Real-time filters (city, risk, status)
- [ ] Analytics Dashboard
  - [ ] Prediction accuracy metrics
  - [ ] Override rate analysis
  - [ ] Learning loop insights
  - [ ] Performance charts
- [ ] Customer Tracking Page
  - [ ] Public shipment tracking
  - [ ] Status timeline
  - [ ] Delay notifications
  - [ ] Reschedule options

### 🔮 Phase 3 (Future Enhancements)
- [ ] Database migration (CSV → MongoDB)
- [ ] Real-time updates (WebSocket)
- [ ] Mobile responsiveness improvements
- [ ] Advanced analytics with Plotly charts
- [ ] Notification system (SMS/Email integration)
- [ ] Multi-tenant support

---

## 🧠 AI Intelligence Modules (Backend)

All AI modules are **already implemented** in parent directory:

1. **Risk Engine** (`models/risk_engine.py`)
   - 7-factor explainable scoring
   - Output: 0-100 score + Low/Medium/High bucket

2. **Address Intelligence** (`features/address_intelligence.py`)
   - NLP-based landmark extraction
   - 16 landmark types for Indian addresses
   - Confidence scoring

3. **Weather Impact** (`features/weather_impact.py`)
   - Multi-API integration (3 providers)
   - Severity analysis + ETA buffering

4. **Pre-Dispatch Gate** (`rules/pre_dispatch_gate.py`)
   - Decision logic: DISPATCH / DELAY / RESCHEDULE
   - Threshold-based rules

5. **Vehicle Selector** (`rules/vehicle_selector.py`)
   - Hyper-local feasibility
   - Narrow lane detection

6. **CO₂ Trade-off** (`features/carbon_tradeoff_engine.py`)
   - Fast vs Green route comparison
   - ESG metrics

7. **Human Override** (`rules/human_override.py`)
   - Accountability logging
   - Learning from decisions

8. **Customer Notifications** (`notifications/customer_notifier.py`)
   - Pre-dispatch alerts
   - Multi-channel support

9. **Learning Loop** (`learning/learning_loop.py`)
   - Daily weight adjustments
   - Prediction accuracy improvement

---

## 🎨 UI/UX Principles

### Risk-First Design
- Visual indicators (🟢🟡🔴) for quick risk assessment
- Color-coded decision badges
- Prominent display of AI reasoning

### Transparency
- Show **why** decisions happen
- Display all risk factors
- Expose AI confidence levels

### Human Control
- Clear override options for managers
- Mandatory reason input for accountability
- No blind automation

### Mobile-Friendly
- Responsive layouts
- Touch-friendly buttons
- Optimized for tablets/phones

---

## 📊 System Workflow

### Seller Flow
1. Login → Seller Portal
2. Fill shipment details
3. Submit for AI analysis
4. Review AI decision (DISPATCH/DELAY/RESCHEDULE)
5. Accept or wait for manager review
6. Track shipment status

### Manager Flow
1. Login → Control Tower
2. View risk heatmap
3. Review AI recommendations
4. Apply overrides with reasons
5. Trigger customer notifications
6. Monitor analytics

### Customer Flow (No Login)
1. Access tracking link
2. View shipment status
3. See delay reasons (if any)
4. Request reschedule
5. Contact support

---

## 🔧 Configuration

### Streamlit Config (`.streamlit/config.toml`)
- Theme: Custom orange primary color (#FF6B35)
- Server: Port 8501, CORS disabled
- Browser: Auto-open disabled

### Authentication
- Demo mode: In-memory user database
- Production: Replace with MongoDB + JWT

### Data Sources
- Development: CSV files in `data/` directory
- Production: MongoDB connection required

---

## 🧪 Testing

### Run Backend Tests
```bash
cd ..
python testing/test_risk_engine.py
python testing/test_address_intelligence.py
python testing/test_pre_dispatch_gate.py
# ... (20+ test files available)
```

### Test Web Application
1. Login with different roles
2. Create test shipments
3. Verify AI analysis outputs
4. Check role-based access control

---

## 📝 Developer Notes

### Adding New Pages
1. Create file in `pages/` with naming pattern: `N_Icon_Name.py`
2. Import authentication: `require_auth(allowed_roles=["Role"])`
3. Apply styling: `apply_custom_css()`
4. Build page content

### Custom Components
Place reusable UI components in `components/` directory:
- `shipment_form.py` - Modular form builder
- `risk_heatmap.py` - Risk visualization
- `charts.py` - Analytics charts

### Session Management
Use `session_manager.py` utilities:
- `init_session_state()` - Initialize on page load
- `get_session_value(key)` - Retrieve session data
- `set_session_value(key, value)` - Store session data
- `add_notification(msg, type)` - Queue notifications

---

## 🐛 Known Issues

1. **Streamlit Rerun** - Form submissions trigger page rerun
2. **CSV Data** - Not suitable for production scale
3. **No Real-time Updates** - Requires WebSocket implementation
4. **Mobile Layout** - Some components need optimization

---

## 🚀 Deployment

### Streamlit Cloud (Recommended for Demo)
1. Push code to GitHub
2. Connect Streamlit Cloud account
3. Deploy from repository
4. Share public URL

### Docker (Production)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "webapp/app.py", "--server.port=8501"]
```

### Cloud Platforms
- **AWS**: EC2 + Elastic Beanstalk
- **GCP**: Cloud Run
- **Azure**: App Service

---

## 📚 Additional Resources

- [Project Analysis](../docs/PROJECT_ANALYSIS.md)
- [System Architecture](../docs/PROJECT_REDESIGN.md)
- [Implementation Guide](../docs/QUICK_WIN_IMPLEMENTATION.md)
- [Visual Summary](../docs/VISUAL_SUMMARY.md)

---

## 👥 Team & Support

**Developer**: Senior Full-Stack Engineer  
**Project**: Final Year / Innovation Challenge  
**Tech Stack**: Python, FastAPI, Streamlit, Custom AI Modules  

---

## 📄 License

This project is developed for academic and demonstration purposes.

---

**Built with 💡 by the LICS Team**  
*AI suggests, humans decide, customers stay informed* 🚚
