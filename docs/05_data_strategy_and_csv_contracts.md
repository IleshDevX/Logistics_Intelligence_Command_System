# Data Strategy & CSV Contract Design
## Logistics Intelligence & Command System (LICS)

---

## 1. Purpose of Data Strategy

This system is designed to be:
- Stateless
- Database-free
- Predictable and auditable

Therefore, **CSV files act as data contracts**, not temporary storage.

Once defined, CSV schemas must not change casually.

---

## 2. Data Classification

All data used in the system falls into two categories:

### 2.1 Transactional Data
- Generated per shipment
- Changes frequently
- Represents live operational input

### 2.2 Master / Reference Data
- Represents rules, constraints, and environment
- Changes slowly
- Loaded at runtime as read-only input

---

## 3. Required CSV Files (Locked)

### 3.1 `shipments_input.csv` (Transactional)

**Purpose:**  
Primary shipment input from sellers.

**Used by engines:**  
Validation, Risk, Priority, Vehicle, Explanation

**Key Columns:**
- shipment_id (string)
- seller_id (string)
- weight_kg (float)
- dimensions_cm (derived)
- distance_km (float)
- city (string)
- area_type (URBAN / RURAL / OLD_CITY)
- address_type (RESIDENTIAL / COMMERCIAL)
- delivery_date (date)
- delivery_urgency (NORMAL / EXPRESS)
- vehicle_preference (BIKE / VAN / TRUCK)

**Update Frequency:**  
Every shipment creation

---

### 3.2 `area_feasibility_master.csv` (Master)

**Purpose:**  
Define locality-level delivery constraints.

**Used by engines:**  
Area Feasibility Engine

**Key Columns:**
- city (string)
- locality (string)
- area_type (string)
- road_width_category (NARROW / MEDIUM / WIDE)
- heavy_vehicle_allowed (boolean)
- congestion_level (LOW / MEDIUM / HIGH)
- last_mile_difficulty (1–5)

**Update Frequency:**  
Occasional (monthly / quarterly)

---

### 3.3 `traffic_profile.csv` (Master)

**Purpose:**  
Simulate traffic impact on delivery risk.

**Used by engines:**  
Risk Scoring Engine

**Key Columns:**
- city (string)
- area_type (string)
- time_slot (MORNING / AFTERNOON / EVENING)
- traffic_level (LOW / MEDIUM / HIGH)
- avg_delay_minutes (integer)
- risk_weight (float)

**Update Frequency:**  
Occasional

---

### 3.4 `weather_risk_rules.csv` (Master)

**Purpose:**  
Translate weather conditions into risk impact.

**Used by engines:**  
Weather Impact Engine

**Key Columns:**
- weather_condition (CLEAR / RAIN / STORM / HEATWAVE)
- severity (LOW / MODERATE / HIGH)
- risk_score_addition (integer)
- vehicle_stress (boolean)

**Update Frequency:**  
Rare (rule-based)

---

### 3.5 `vehicle_master.csv` (Master)

**Purpose:**  
Define vehicle constraints and feasibility.

**Used by engines:**  
Vehicle Feasibility Engine

**Key Columns:**
- vehicle_type (BIKE / VAN / TRUCK)
- max_weight_kg (float)
- max_volume_cm3 (float)
- allowed_area_type (string)
- allowed_address_type (string)
- last_mile_suitable (boolean)

**Update Frequency:**  
Rare

---

## 4. CSV Contract Rules (Non-Negotiable)

- Column names are case-sensitive
- No engine may add new columns dynamically
- CSVs are read-only during execution
- All derived fields must be computed in memory

---

## 5. Why CSV Contracts Matter

- Enables stateless execution
- Makes debugging easy
- Supports reproducibility
- Allows independent engine testing

CSV files act as **inputs to intelligence**, not mutable storage.

---

## 6. Data Integrity Assumptions

- CSV data is synthetically realistic
- Validation engine enforces correctness
- Missing or malformed rows are rejected early

---

End of document.
