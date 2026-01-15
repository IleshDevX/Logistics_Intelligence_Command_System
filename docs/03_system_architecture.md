# End-to-End System Architecture
## Logistics Intelligence & Command System (LICS)

---

## 1. Architectural Goal

The system is designed as a **Logistics Control Tower**, not a CRUD application.

Key characteristics:
- Stateless execution
- Engine-driven decisions
- Human-in-the-loop control
- Explainability at every step

---

## 2. Stateless Architecture Definition

This system does NOT maintain server-side state.

Design rules:
- No database
- No long-lived sessions
- Every decision is derived from:
  - CSV data
  - API responses
  - User input at runtime

Benefits:
- Predictable behavior
- Easy auditability
- Simple deployment
- No hidden system memory

---

## 3. Data Boundaries (CSV & API)

### 3.1 CSV-Based Inputs (Static & Semi-Static)

CSV files provide:
- Shipment inputs
- Area feasibility rules
- Vehicle constraints
- Traffic profiles
- Historical patterns (synthetic)

CSV files are:
- Read-only during execution
- Treated as source-of-truth inputs

---

### 3.2 API-Based Inputs (Dynamic)

External APIs are used only for:
- Weather intelligence

API rules:
- APIs provide advisory signals
- API data never directly approves or rejects shipments
- API failures degrade gracefully (system still works)

---

## 4. Engine-Oriented Design

The system is composed of **independent engines**.
Each engine:
- Has a single responsibility
- Accepts structured input
- Produces explainable output

No engine:
- Directly calls another engine
- Makes irreversible decisions

---

## 5. Engine Orchestration Flow

Execution order is fixed and transparent:

1. Input & Validation Engine  
2. Area-Based Feasibility Engine  
3. Weather Impact Engine  
4. Vehicle Feasibility Engine  
5. Shipment Priority Engine  
6. Pre-Dispatch Risk Engine  
7. Delay Explanation Engine  
8. Manager Decision Engine  
9. Supervisor Analytics Engine  

Each engine adds context, not authority.

---

## 6. Where AI Sits in the Architecture

AI components are embedded in:
- Risk scoring
- Priority classification
- Pattern recognition

AI characteristics:
- Advisory only
- Probabilistic, not deterministic
- Always accompanied by explanations

AI is explicitly blocked from:
- Auto-approval
- Auto-rejection
- Direct dispatch actions

---

## 7. Human-in-the-Loop Control Points

Human checkpoints exist at:
- Shipment acceptance
- Risk override
- Vehicle override

At each checkpoint:
- AI provides reasoning
- Human makes the final call
- Decision is logged

---

## 8. High-Level Flow (Textual)

Seller Input  
→ Validation Engine  
→ Feasibility & Risk Engines  
→ AI Recommendations  
→ Human Decision  
→ Outcome Logging  
→ Supervisor Analytics  

---

## 9. Architectural Non-Negotiables

- No engine bypass
- No silent decisions
- No hidden automation
- No unexplained outcomes

---

End of document.
