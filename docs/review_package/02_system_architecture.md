# System Architecture

## Layered Architecture

The system follows a **layered architecture** separating data ingestion, decision intelligence, execution control, and learning feedback to ensure scalability and explainability.

```
┌─────────────────────────────────────────────────────────────┐
│             USER / SELLER / OPS MANAGER                      │
│  (Web Dashboard, Mobile App, External System Integration)   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    API LAYER (FastAPI)                       │
│  • 23 REST Endpoints                                         │
│  • Auto-generated docs (Swagger/ReDoc)                       │
│  • CORS middleware                                           │
│  • Request validation (Pydantic schemas)                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│           DECISION INTELLIGENCE LAYER                        │
│  ┌─────────────┬─────────────┬─────────────┬──────────────┐│
│  │ Risk Engine │ Address NLP │Weather Impact│ Vehicle      ││
│  │ (7 factors) │ (16 lndmrks)│ (3 providers)│ Selector     ││
│  │ Score 0-100 │ Conf. 0-100 │ ETA buffer   │ Feasibility  ││
│  └─────────────┴─────────────┴─────────────┴──────────────┘│
│  ┌─────────────────────────────────────────────────────────┐│
│  │              CO₂ Trade-off Calculator                    ││
│  │  (ESG-aware vehicle recommendations)                     ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│          DECISION GATES + HUMAN OVERRIDE                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Pre-Dispatch Gate:                                   │  │
│  │  • Risk < 40 → DISPATCH                               │  │
│  │  • Risk 40-60 → DELAY (notify customer)               │  │
│  │  • Risk > 60 → RESCHEDULE (clarification)             │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Human Override:                                      │  │
│  │  • Manager/Supervisor authority                       │  │
│  │  • Reason mandatory                                   │  │
│  │  • Manual lock (prevent AI re-evaluation)             │  │
│  │  • Accountability trail (who, when, why)              │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              EXECUTION & TRACKING                            │
│  • 10 delivery statuses (DISPATCH → DELIVERED)               │
│  • Real-time status updates                                  │
│  • Customer notification (WhatsApp/SMS/Email/App)            │
│  • Tracking history                                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   EOD LOGGING                                │
│  • Prediction vs Reality comparison                          │
│  • Mismatch detection (AI wrong rate)                        │
│  • Override success measurement                              │
│  • 16 fields per log entry                                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  LEARNING LOOP                               │
│  • Daily weight adjustments (±5/day, 5-30 range)             │
│  • Address confidence improvement                            │
│  • Override effectiveness analysis                           │
│  • Complete audit trail (learning_history.csv)               │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Data Ingestion Layer
**Purpose**: Load and validate shipment data

**Components**:
- CSV-based data loading (50K shipments)
- Schema validation
- Data quality checks

**Files**: `models/data_loader.py`

### 2. Decision Intelligence Layer
**Purpose**: Analyze shipments and quantify risks

**Components**:

#### Risk Engine
- **Input**: Weight, payment type, area type, road accessibility, address confidence, weather, priority
- **Output**: Risk score (0-100), Risk bucket (Low/Medium/High)
- **Logic**: Explainable, rule-based, tunable
- **Files**: `models/risk_engine.py`

#### Address Intelligence (NLP)
- **Input**: Delivery address string
- **Output**: Confidence score (0-100), Nearby landmarks, Area classification
- **Logic**: Keyword extraction, 16 landmark types, pattern matching
- **Files**: `models/address_intelligence.py`

#### Weather Impact
- **Input**: City, date
- **Output**: Weather severity (Low/Medium/High), Impact score (0-100), ETA buffer (1.0× to 2.0×)
- **Logic**: Real-time API integration (3 providers), Flood zone detection
- **Files**: `models/weather_engine.py`

#### Vehicle Selector
- **Input**: Weight, volume, area type, road width, address confidence
- **Output**: Selected vehicle, Feasibility flag, Alternative recommendations
- **Logic**: Weight capacity, Narrow lane detection, Split delivery option
- **Files**: `models/vehicle_selector.py`

#### CO₂ Calculator
- **Input**: Vehicle type, distance
- **Output**: Carbon footprint (kg CO₂), ESG score
- **Logic**: Vehicle emission factors, Distance-based calculation
- **Files**: `models/carbon_calculator.py`

### 3. Decision Gate Layer
**Purpose**: Make dispatch decisions based on intelligence

**Components**:

#### Pre-Dispatch Gate
- **Decision Logic**:
  ```
  IF risk_score < 40: DISPATCH
  ELIF risk_score < 60: DELAY (notify customer, buffer ETA)
  ELSE: RESCHEDULE (request clarification)
  ```
- **Files**: `models/decision_gate.py`

#### Human Override
- **Authority Levels**: Manager (all overrides), Supervisor (risk < 70), Operator (no override)
- **Requirements**: Reason mandatory, Manual lock applied
- **Logging**: Who, when, why, outcome
- **Files**: `override/human_override.py`

### 4. Execution Layer
**Purpose**: Track delivery lifecycle

**Components**:
- Status updates (10 statuses)
- Customer notifications (4 channels)
- Tracking history
- **Files**: `execution/delivery_simulator.py`, `notifications/customer_notifier.py`

### 5. Analytics Layer
**Purpose**: Measure prediction accuracy

**Components**:
- EOD logging (16 fields)
- Mismatch detection
- Override success rate
- **Files**: `analytics/end_of_day_logger.py`

### 6. Learning Layer
**Purpose**: Continuous improvement

**Components**:
- Daily learning cycle
- Risk weight adjustments (±5/day, 5-30 range)
- Address confidence improvement
- Override effectiveness analysis
- **Files**: `learning/learning_loop.py`

### 7. API Layer
**Purpose**: External system integration

**Components**:
- 23 REST endpoints
- Auto-generated docs (Swagger UI at `/docs`)
- Pydantic schemas (20+ schemas)
- **Files**: `api/main.py`, `api/routes.py`, `api/schemas.py`

### 8. Dashboard Layer
**Purpose**: Real-time operations monitoring

**Components**:
- 10 dashboard panels
- Risk distribution charts
- Active shipments tracking
- Override monitoring
- Learning statistics
- **Files**: `dashboard/control_tower.py`

## Design Principles

### 1. **Explainability First**
- All decisions are rule-based and explainable
- No black-box ML models
- Clear reasoning for every decision

### 2. **Human-in-the-Loop**
- AI suggests, humans decide
- Manager override capability
- Accountability trail

### 3. **Pre-Dispatch Intelligence**
- Detect risks BEFORE dispatch
- Proactive customer communication
- Prevent failures, not react to them

### 4. **Continuous Learning**
- Daily learning loop
- Controlled adjustments (±5/day)
- Evidence-based weight tuning

### 5. **Scalability**
- Microservices-ready (FastAPI)
- Stateless API design
- CSV → Database migration path clear

## Data Flow

```
1. Shipment Arrives
   ↓
2. Load Data (data_loader.py)
   ↓
3. Calculate Risk (risk_engine.py) → Risk Score 0-100
   ↓
4. Analyze Address (address_intelligence.py) → Confidence 0-100
   ↓
5. Check Weather (weather_engine.py) → Impact 0-100
   ↓
6. Make Decision (decision_gate.py) → DISPATCH/DELAY/RESCHEDULE
   ↓
7. [Optional] Human Override (human_override.py)
   ↓
8. Select Vehicle (vehicle_selector.py) → Vehicle + Feasibility
   ↓
9. Notify Customer (customer_notifier.py) → WhatsApp/SMS/Email
   ↓
10. Execute Delivery (delivery_simulator.py) → Status Updates
   ↓
11. Log EOD (end_of_day_logger.py) → Prediction vs Reality
   ↓
12. Learning Loop (learning_loop.py) → Adjust Weights
```

## Technology Stack

| Layer | Technology | Justification |
|-------|------------|---------------|
| Backend | Python 3.10+ | Rich ML/data ecosystem |
| API | FastAPI | Modern, async, auto-docs |
| Data | Pandas | Data manipulation |
| Dashboard | Streamlit | Rapid UI development |
| Config | JSON | Human-readable, version-controllable |
| Logging | CSV | Simple, queryable, audit trail |
| Testing | pytest | Industry standard |

## Scalability Considerations

### Current (MVP):
- Single-machine deployment
- CSV-based data storage
- In-memory processing

### Production Path:
1. **Database Migration**: CSV → PostgreSQL/MongoDB
2. **Message Queue**: Add RabbitMQ/Kafka for async processing
3. **Containerization**: Docker + Kubernetes deployment
4. **Caching**: Redis for hot data (weather, risk scores)
5. **Load Balancing**: Nginx/HAProxy for API scaling
6. **Monitoring**: Prometheus + Grafana for observability

---

**This architecture is production-ready with a clear scaling path.**
