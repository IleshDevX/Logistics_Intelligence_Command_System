# Process Flowcharts

## 1. End-to-End Delivery Decision Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    SHIPMENT ARRIVES                          │
│               (from Seller/Warehouse)                        │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│              STEP 1: DATA INGESTION                          │
│  • Load shipment details                                     │
│  • Validate schema (priority, weight, dimensions)            │
│  • Check data quality (missing fields, invalid values)       │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│         STEP 2: ADDRESS INTELLIGENCE (NLP)                   │
│  • Parse delivery address                                    │
│  • Extract landmarks (16 types)                              │
│  • Calculate confidence score (0-100)                        │
│  • Result: HIGH (>75) / MEDIUM (50-75) / LOW (<50)           │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│           STEP 3: WEATHER IMPACT ANALYSIS                    │
│  • Fetch weather forecast (3 providers)                      │
│  • Analyze: rain, wind, fog, temperature                     │
│  • Calculate risk multiplier (1.0 - 2.5)                     │
│  • Add ETA buffer if needed (15-60 min)                      │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│             STEP 4: RISK ENGINE (7 Factors)                  │
│  1. Address confidence                                       │
│  2. Weather conditions                                       │
│  3. Priority level                                           │
│  4. Package value                                            │
│  5. Fragility                                                │
│  6. Time urgency (promised vs current time)                  │
│  7. Historical delivery success rate                         │
│                                                               │
│  OUTPUT: Risk Score (0-100)                                  │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│          STEP 5: PRE-DISPATCH GATE (Decision)                │
│                                                               │
│  Risk < 40?  ──YES──► DISPATCH                               │
│      │                                                        │
│      NO                                                       │
│      ↓                                                        │
│  Risk 40-60? ──YES──► DELAY (inform customer)                │
│      │                                                        │
│      NO                                                       │
│      ↓                                                        │
│  Risk > 60?  ──YES──► RESCHEDULE (clarify address)           │
│                                                               │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
         ┌─────────────┴─────────────┐
         ↓                           ↓
┌──────────────────┐       ┌──────────────────┐
│   IF DISPATCH    │       │ IF DELAY/RESCHED │
└────────┬─────────┘       └────────┬─────────┘
         ↓                           ↓
┌─────────────────────────┐  ┌─────────────────────────┐
│ STEP 6: VEHICLE SELECTOR│  │ STEP 6: CUSTOMER NOTIFY │
│ • Check capacity         │  │ • Generate message      │
│ • Match requirements     │  │ • Send via WhatsApp/SMS │
│ • CO₂ trade-off analysis │  │ • Capture response      │
│ • Assign best vehicle    │  │ • Present options       │
└────────┬────────────────┘  └────────┬────────────────┘
         ↓                             ↓
┌─────────────────────────┐  ┌─────────────────────────┐
│ STEP 7: DISPATCH        │  │ WAIT FOR RESPONSE       │
│ • Generate route        │  │ • Customer chooses:     │
│ • Notify driver         │  │   1. Deliver tomorrow   │
│ • Track shipment        │  │   2. Evening slot       │
│ • Update status         │  │   3. Custom date        │
└────────┬────────────────┘  │   4. Provide details    │
         ↓                   └────────┬────────────────┘
┌─────────────────────────┐           ↓
│ STEP 8: DELIVERY        │  ┌─────────────────────────┐
│ • Real-time tracking    │  │ RE-ENTER FLOW           │
│ • POD capture           │  │ (with updated info)     │
│ • Customer feedback     │  └─────────────────────────┘
└────────┬────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│         STEP 9: END-OF-DAY LOGGING & LEARNING                │
│  • Log all decisions                                         │
│  • Calculate success rate                                    │
│  • Update risk weights                                       │
│  • Feed into learning loop                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Human Override Process

```
┌─────────────────────────────────────────────────────────────┐
│         AI MAKES DECISION (DISPATCH/DELAY/RESCHEDULE)        │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
              ┌────────────────┐
              │ Manager Reviews│
              │   Decision?    │
              └────────┬───────┘
                       ↓
              ┌────────┴────────┐
              ↓                 ↓
         ┌─────────┐      ┌──────────┐
         │  AGREE  │      │ DISAGREE │
         └────┬────┘      └─────┬────┘
              ↓                 ↓
     ┌────────────────┐  ┌──────────────────────────────┐
     │ PROCEED WITH   │  │   INITIATE OVERRIDE          │
     │ AI DECISION    │  │                              │
     └────────────────┘  │ 1. Select OVERRIDE action    │
                         │ 2. Provide mandatory reason  │
                         │ 3. Confirm authority level   │
                         └──────────┬───────────────────┘
                                    ↓
                         ┌──────────────────────────────┐
                         │   SYSTEM ACTIONS:            │
                         │ • Execute override decision  │
                         │ • Log: who, when, why        │
                         │ • Set manual_lock = True     │
                         │ • Prevent AI re-evaluation   │
                         │ • Update shipment status     │
                         └──────────┬───────────────────┘
                                    ↓
                         ┌──────────────────────────────┐
                         │  ACCOUNTABILITY TRAIL        │
                         │ • Store in override_log.csv  │
                         │ • Visible in dashboard       │
                         │ • Audit trail maintained     │
                         └──────────────────────────────┘
```

---

## 3. Learning Loop Process

```
┌─────────────────────────────────────────────────────────────┐
│                 DELIVERY COMPLETED                           │
│           (Success / Failed / Returned)                      │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│              CAPTURE OUTCOME DATA                            │
│  • Actual delivery result                                    │
│  • AI predicted risk score                                   │
│  • AI decision (DISPATCH/DELAY/RESCHEDULE)                   │
│  • Was there human override?                                 │
│  • Actual vs predicted ETA                                   │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│           CALCULATE ACCURACY METRICS                         │
│  • Success rate by risk bucket (LOW/MEDIUM/HIGH)             │
│  • False positive rate (predicted fail, actually success)    │
│  • False negative rate (predicted success, actually fail)    │
│  • Override accuracy (were human overrides correct?)         │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│            ADJUST RISK WEIGHTS                               │
│  IF success_rate < 80% in bucket:                            │
│    → Increase weights for contributing factors               │
│  IF false_positive_rate > 15%:                               │
│    → Decrease weights (model too conservative)               │
│  IF override_accuracy > AI_accuracy:                         │
│    → Learn from human decisions                              │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│         UPDATE RISK ENGINE CONFIGURATION                     │
│  • Save new weights to configs/risk_weights.json             │
│  • Log changes to logs/learning_history.csv                  │
│  • Apply in next decision cycle                              │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│              CONTINUOUS IMPROVEMENT                          │
│  System learns from every delivery, every override,          │
│  every success, and every failure.                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Customer Notification Flow

```
┌─────────────────────────────────────────────────────────────┐
│      PRE-DISPATCH GATE DECIDES: DELAY or RESCHEDULE          │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│           GENERATE PERSONALIZED MESSAGE                      │
│  • Shipment ID + Customer name                               │
│  • Explain reason (weather, address unclear, etc.)           │
│  • Provide reassurance                                       │
│  • Present actionable options                                │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
         ┌─────────────┴─────────────┐
         ↓                           ↓
┌──────────────────┐       ┌──────────────────┐
│   IF DELAY       │       │ IF RESCHEDULE    │
└────────┬─────────┘       └────────┬─────────┘
         ↓                           ↓
┌─────────────────────────┐  ┌─────────────────────────┐
│ MESSAGE:                │  │ MESSAGE:                 │
│ "Slight delay expected  │  │ "Need clarification      │
│  due to [reason].       │  │  to ensure successful    │
│  New ETA: [time+buffer] │  │  delivery."              │
│  We'll keep you updated"│  │                          │
└────────┬────────────────┘  │ OPTIONS:                 │
         ↓                   │ 1. Deliver tomorrow      │
┌─────────────────────────┐  │ 2. Evening slot (6-9 PM) │
│ SEND NOTIFICATION       │  │ 3. Choose custom date    │
│ • WhatsApp (primary)    │  │ 4. Provide address info  │
│ • SMS (fallback)        │  └────────┬────────────────┘
│ • Email (backup)        │           ↓
└────────┬────────────────┘  ┌─────────────────────────┐
         ↓                   │ SEND NOTIFICATION        │
┌─────────────────────────┐  │ • WhatsApp (primary)     │
│ CUSTOMER INFORMED       │  │ • SMS (fallback)         │
│ No action needed        │  │ • Email (backup)         │
└─────────────────────────┘  └────────┬────────────────┘
                                      ↓
                             ┌─────────────────────────┐
                             │ WAIT FOR RESPONSE       │
                             │ (24-hour window)        │
                             └────────┬────────────────┘
                                      ↓
                             ┌─────────────────────────┐
                             │ CAPTURE CUSTOMER CHOICE │
                             │ • Log response          │
                             │ • Update shipment data  │
                             │ • Re-enter decision flow│
                             └─────────────────────────┘
```

---

## 5. CO₂ Trade-off Decision Flow

```
┌─────────────────────────────────────────────────────────────┐
│         VEHICLE SELECTOR FINDS FEASIBLE VEHICLES             │
│              (Based on capacity, constraints)                │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│          CALCULATE CO₂ FOR EACH VEHICLE                      │
│  • Diesel Truck: 0.8 kg/km                                   │
│  • EV Truck: 0.3 kg/km                                       │
│  • Bike: 0.05 kg/km                                          │
│  • Total CO₂ = emission_rate × distance                      │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│          RANK VEHICLES BY PREFERENCE                         │
│  1. Feasibility (can it carry the load?)                     │
│  2. Speed (can it meet ETA?)                                 │
│  3. Carbon impact (lowest CO₂)                               │
│  4. Cost (operational cost)                                  │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│         PRESENT TRADE-OFF TO OPS MANAGER                     │
│                                                               │
│  Option A: EV Truck    → CO₂: 6 kg   (ECO-FRIENDLY)          │
│  Option B: Diesel Truck→ CO₂: 16 kg  (FASTER, RELIABLE)      │
│  Option C: Bike        → CO₂: 1 kg   (LOW COST, SLOW)        │
│                                                               │
│  Recommendation: EV Truck (balances speed + carbon)          │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
              ┌────────┴────────┐
              ↓                 ↓
      ┌───────────────┐  ┌──────────────┐
      │ AUTO-SELECT   │  │ HUMAN CHOOSES│
      │ RECOMMENDED   │  │ ALTERNATIVE  │
      └───────┬───────┘  └──────┬───────┘
              ↓                 ↓
      ┌─────────────────────────────────┐
      │    LOG DECISION + RATIONALE     │
      │  • Selected vehicle             │
      │  • CO₂ impact                   │
      │  • ESG compliance               │
      └─────────────────────────────────┘
```

---

## 6. Dashboard Control Tower Flow

```
┌─────────────────────────────────────────────────────────────┐
│              USER OPENS CONTROL TOWER DASHBOARD              │
│                  (Streamlit Interface)                       │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                 LOAD SHIPMENT DATA                           │
│  • All pending shipments                                     │
│  • Filtered by status (PENDING/DISPATCH/DELAY/RESCHEDULE)   │
│  • Real-time risk scores                                     │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│              DISPLAY SHIPMENTS TABLE                         │
│  Columns: ID | Priority | Risk | Status | Decision | Action  │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
              ┌────────┴────────┐
              ↓                 ↓
      ┌───────────────┐  ┌──────────────────┐
      │ VIEW DETAILS  │  │ INITIATE OVERRIDE│
      └───────┬───────┘  └──────┬───────────┘
              ↓                 ↓
┌──────────────────────┐ ┌──────────────────────────────┐
│ SHOW:                │ │ OVERRIDE FORM:               │
│ • Risk breakdown     │ │ 1. Select new decision       │
│ • Address confidence │ │ 2. Enter reason (mandatory)  │
│ • Weather impact     │ │ 3. Authority level           │
│ • Vehicle options    │ │ 4. Confirm                   │
│ • CO₂ comparison     │ └──────┬───────────────────────┘
└──────────────────────┘        ↓
                       ┌─────────────────────────────┐
                       │ EXECUTE OVERRIDE            │
                       │ • Update shipment           │
                       │ • Log in override_log.csv   │
                       │ • Refresh dashboard         │
                       └─────────────────────────────┘
```

---

## Key Process Characteristics

### 1. **Fail-Safe Design**
- Every decision has a fallback
- Low-confidence addresses → clarification before dispatch
- Weather risk → ETA buffer added
- System errors → human escalation

### 2. **Transparency**
- Every decision shows reasoning
- Risk score breakdown visible
- Override reasons logged
- Customer always informed

### 3. **Learning Integration**
- Every delivery outcome captured
- Accuracy metrics calculated daily
- Risk weights auto-adjusted
- Human override patterns analyzed

### 4. **Human-in-the-Loop**
- Manager can override any AI decision
- Mandatory reason enforces accountability
- Manual lock prevents AI re-evaluation
- Audit trail maintained

### 5. **Customer-Centric**
- Proactive communication (DELAY/RESCHEDULE)
- Actionable options presented
- Response captured and acted upon
- "Forgive delay, NOT silence" philosophy

---

## Integration Points

| Process | Input | Output | Next Step |
|---------|-------|--------|-----------|
| Data Ingestion | Raw CSV/API data | Validated shipment records | Address Intelligence |
| Address Intelligence | Shipment address | Confidence score, landmarks | Weather Impact |
| Weather Impact | Location, time | Risk multiplier, ETA buffer | Risk Engine |
| Risk Engine | 7 risk factors | Risk score (0-100) | Pre-Dispatch Gate |
| Pre-Dispatch Gate | Risk score | DISPATCH/DELAY/RESCHEDULE | Vehicle Selector / Customer Notification |
| Vehicle Selector | Shipment specs | Feasible vehicles, CO₂ | Dispatch |
| Customer Notification | Decision + reason | Message sent, response | Re-entry or completion |
| Human Override | AI decision | Override decision + reason | Execution |
| Learning Loop | Delivery outcome | Updated risk weights | Next decision cycle |

---

This flowchart documentation provides a complete visual and textual guide to how data flows through the LICS system from shipment arrival to delivery completion and continuous learning.
