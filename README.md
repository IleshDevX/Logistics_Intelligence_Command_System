# Logistics Intelligence & Command System (LICS)

## Overview
LICS is an **AI-assisted, human-in-the-loop logistics decision support system**.  
It focuses on **pre-dispatch risk awareness**, not blind automation.

**Version 2.0** features a completely redesigned **professional light-theme control tower UI** optimized for calm, informed decision-making.

## Key Principles
- ✅ AI advises, humans decide
- 🎯 Risk awareness over speed
- 💡 Explainability over black-box accuracy
- 🇮🇳 Designed for Indian logistics realities
- 🎨 Professional, light-theme interface
- ⚖️ Governance transparency and audit trails

## Core Capabilities
- **Input Validation** – Comprehensive shipment data validation
- **Area Feasibility** – Last-mile delivery complexity assessment
- **Weather Impact** – Real-time weather risk analysis
- **Vehicle Feasibility** – Smart vehicle recommendation
- **Priority Classification** – ML-powered urgency detection
- **Risk Scoring** – Multi-factor delivery risk calculation
- **Explainable AI** – Plain English risk explanations
- **Manager Decisions** – Accept/Hold/Override with mandatory justification
- **Supervisor Analytics** – Governance dashboard with override tracking
- **Audit Trail** – Complete decision logging for compliance

## UI/UX Design Philosophy

### Light Theme Professional Design
- **Calm & Clean**: Off-white backgrounds, subtle shadows
- **Soft Risk Colors**: Pastel green/amber/red (no harsh alarms)
- **Explanation-First**: Plain English before technical details
- **Progressive Disclosure**: Technical data hidden in expanders
- **Audit-Friendly**: All decisions logged and traceable

### Three Role-Based Views
1. **📦 Seller View** – Shipment input + AI risk intelligence
2. **🧑‍💼 Manager View** – Decision dashboard with override controls
3. **📊 Supervisor View** – Governance metrics and compliance monitoring

## Technology Stack
- **Framework**: Python + Streamlit
- **Data Processing**: Pandas, NumPy
- **Machine Learning**: Scikit-learn (Decision Tree Classifier)
- **Weather API**: WeatherAPI.com (live data)
- **Architecture**: Hybrid rule-based + ML engines
- **Storage**: CSV-based (stateless, audit-friendly)

## Project Structure
```
├── app.py                          # Unified control tower UI
├── config.py                       # Configuration settings
├── requirements.txt                # Python dependencies
├── train_priority_model.py         # ML model training script
├── data/                           # CSV data files
│   ├── area_feasibility_master.csv
│   ├── manager_decisions.csv
│   ├── shipments_input.csv
│   ├── traffic_profile.csv
│   ├── vehicle_master.csv
│   └── weather_risk_rules.csv
├── engines/                        # Decision engines
│   ├── input_validation_engine.py
│   ├── area_feasibility_engine.py
│   ├── weather_impact_engine.py
│   ├── vehicle_feasibility_engine.py
│   ├── priority_classification_engine.py
│   ├── risk_scoring_engine.py
│   ├── delay_explanation_engine.py
│   ├── manager_decision_engine.py
│   └── supervisor_analytics_engine.py
├── utils/
│   └── id_generator.py             # Parcel ID generation
└── docs/                           # Comprehensive documentation
    ├── 01_problem_statement.md
    ├── 02_roles_and_decision_boundaries.md
    ├── 03_system_architecture.md
    ├── 04_engine_contracts.md
    ├── 05_data_strategy_and_csv_contracts.md
    ├── 06_assumptions_limits_ethics.md
    ├── 07_ui_design_documentation.md
    └── 08_ui_style_guide.md
```

## How to Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Train Priority Classification Model (First Time Only)
```bash
python train_priority_model.py
```

### 3. Launch Control Tower
```bash
streamlit run app.py
# or
python -m streamlit run app.py
```

The application will open in your browser at `http://localhost:8501` (or 8502)

## User Guide

### Seller Workflow
1. Navigate to **📦 Seller View**
2. Enter shipment details (weight, dimensions, route, urgency)
3. Click **"🚀 Run Pre-Dispatch Analysis"**
4. Review AI risk assessment and explanations
5. Optionally expand technical details
6. Proceed to Manager View for decision

### Manager Workflow
1. Navigate to **🧑‍💼 Manager View**
2. Review shipment snapshot (Parcel ID, route, risk band)
3. Read AI risk assessment and explanation
4. Select decision:
   - **ACCEPT** – Proceed with dispatch
   - **HOLD** – Delay for review
   - **OVERRIDE** – Proceed against AI (requires justification)
5. Submit decision (logged to CSV)

### Supervisor Workflow
1. Navigate to **📊 Supervisor View**
2. Review governance metrics (override rate, high-risk accepts)
3. Analyze decision analytics charts
4. Examine overridden shipments table
5. Review model transparency information
6. Use insights for compliance and training

## Key Features

### AI-Powered Risk Intelligence
- Multi-engine analysis (area, weather, vehicle, priority)
- Composite risk scoring (0-100 scale)
- Risk bands: 🟢 LOW, 🟡 MEDIUM, 🔴 HIGH
- Plain English explanations

### Human-in-the-Loop Decision Making
- Managers review AI recommendations
- Accept, hold, or override with justification
- Mandatory audit trail for overrides
- Balance automation with human judgment

### Governance & Compliance
- Real-time override tracking
- High-risk acceptance monitoring
- AI vs. human disagreement metrics
- Complete decision audit trail
- Model transparency documentation

### Professional Light-Theme UI
- Calm, focused decision environment
- Soft risk color coding
- Progressive disclosure of complexity
- Mobile-ready responsive design
- Industry-grade aesthetics

## Design Principles

### Transparency Over Black-Box
- All AI decisions are explainable
- Risk factors clearly communicated
- Model information readily available

### Human Authority Over Automation
- Managers can override AI recommendations
- Justification required for overrides
- Human judgment valued and preserved

### Risk Awareness Over Speed
- Comprehensive risk analysis before dispatch
- Multiple risk dimensions considered
- Safety and reliability prioritized

### Governance Over Convenience
- All decisions logged and traceable
- Override visibility for supervisors
- Compliance-ready audit trails

## Documentation

Comprehensive documentation available in `/docs`:

1. **Problem Statement** – Business context and objectives
2. **Roles & Decision Boundaries** – User roles and responsibilities
3. **System Architecture** – Technical design overview
4. **Engine Contracts** – API specifications for each engine
5. **Data Strategy** – CSV schemas and data governance
6. **Assumptions & Ethics** – System limitations and ethical considerations
7. **UI Design Documentation** – Complete UI/UX design guide
8. **UI Style Guide** – Visual design reference (colors, typography, components)

---

## Version History

### v2.0 (January 2026)
- ✨ Complete UI/UX redesign (light theme)
- 🎨 Professional control tower interface
- 📊 Enhanced supervisor analytics
- 📝 Comprehensive documentation
- ♿ Improved accessibility

### v1.0 (Initial Release)
- ✅ Core engine implementations
- 🤖 ML-powered priority classification
- 🌤️ Weather API integration
- 📋 CSV-based data strategy
- 🧑‍💼 Manager decision workflow

---

**Built with care for real-world logistics operations.**  
*AI-Assisted. Human-Controlled. Risk-Aware.*
