# Engine Decomposition & Contracts
## Logistics Intelligence & Command System (LICS)

---

## 1. Purpose of Engine Decomposition

The system is built using multiple **independent decision engines**.
Each engine:
- Has a single responsibility
- Does not overlap with others
- Can be tested independently
- Does not make final decisions

This prevents:
- Logic entanglement
- Hidden automation
- Untraceable outcomes

---

## 2. Engine Execution Order (Locked)

The engines execute in the following fixed order:

1. Input & Validation Engine  
2. Area-Based Last-Mile Feasibility Engine  
3. Weather Impact Advisory Engine  
4. Hyper-Local Vehicle Feasibility Engine  
5. Shipment Priority Classification Engine  
6. Pre-Dispatch Risk Scoring Engine  
7. Delivery Delay Explanation Engine  
8. Manager Decision Engine  
9. Supervisor Analytics Engine  

No engine may be skipped or reordered.

---

## 3. Engine 1 — Input & Validation Engine

### Responsibility
Ensure all shipment inputs are complete, valid, and normalized.

### Inputs
- Raw seller input (form / CSV upload)

### Outputs
- Clean, validated shipment object
- Validation errors (if any)

### Explicit Restrictions
- No risk scoring
- No feasibility decisions

---

## 4. Engine 2 — Area-Based Last-Mile Feasibility Engine

### Responsibility
Evaluate locality-level feasibility based on static constraints.

### Inputs
- Validated shipment data
- Area feasibility CSV

### Outputs
- Feasibility flag (ALLOW / WARN / BLOCK)
- Reason codes

### Explicit Restrictions
- No vehicle selection
- No risk scoring

---

## 5. Engine 3 — Weather Impact Advisory Engine

### Responsibility
Assess weather-related delivery risk.

### Inputs
- Destination city
- Delivery date
- Weather API response

### Outputs
- Weather risk adjustment score
- Weather explanation

### Explicit Restrictions
- Cannot block shipments
- Cannot approve shipments

---

## 6. Engine 4 — Hyper-Local Vehicle Feasibility Engine

### Responsibility
Validate vehicle suitability for last-mile delivery.

### Inputs
- Shipment dimensions & weight
- Address type
- Area type
- Vehicle master CSV

### Outputs
- Vehicle decision (ACCEPT / WARN / REJECT)
- Suggested alternative (if any)

### Explicit Restrictions
- No shipment approval
- No risk scoring

---

## 7. Engine 5 — Shipment Priority Classification Engine

### Responsibility
Classify shipment importance from a business perspective.

### Inputs
- Shipment attributes
- Pretrained ML model

### Outputs
- Priority level (HIGH / MEDIUM / LOW)

### Explicit Restrictions
- No risk scoring
- No feasibility logic

---

## 8. Engine 6 — Pre-Dispatch Risk Scoring Engine

### Responsibility
Estimate overall risk of delivery delay.

### Inputs
- Distance
- Area feasibility output
- Weather risk output
- Vehicle feasibility output
- Priority level

### Outputs
- Risk score (0–100)
- Risk category (LOW / MEDIUM / HIGH)
- AI recommendation

### Explicit Restrictions
- Cannot approve or reject shipments

---

## 9. Engine 7 — Delivery Delay Explanation Engine

### Responsibility
Explain why a shipment is risky.

### Inputs
- Risk score
- Feature contributions
- Engine outputs

### Outputs
- Human-readable explanation
- Ranked risk reasons

### Explicit Restrictions
- No scoring
- No decision authority

---

## 10. Engine 8 — Manager Decision Engine

### Responsibility
Allow human decision-making with accountability.

### Inputs
- All previous engine outputs
- Manager action

### Outputs
- Final decision (ACCEPT / HOLD / OVERRIDE)
- Override reason (if applicable)

### Explicit Restrictions
- No rule changes
- No data mutation beyond logging

---

## 11. Engine 9 — Supervisor Analytics Engine

### Responsibility
Provide governance and performance visibility.

### Inputs
- Historical decisions
- Delivery outcomes

### Outputs
- KPIs
- Trend analysis
- AI vs human comparison

### Explicit Restrictions
- No operational decisions

---

## 12. Independent Testability Guarantee

Each engine:
- Can be tested with mock inputs
- Can be executed without UI
- Produces deterministic outputs

This is mandatory for system reliability.

---

End of document.
