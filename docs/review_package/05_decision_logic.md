# Decision Logic

## Overview

All decision logic is **rule-based and explainable**. No black-box ML models. Every decision can be traced back to specific rules and thresholds.

**Philosophy**: Thresholds are configurable and tuned through the learning loop.

---

## 1. Risk Scoring Logic

### Input Parameters (7 factors):
1. `weight_kg` - Package weight
2. `volumetric_weight` - Volume-based weight
3. `payment_type` - COD or Prepaid
4. `priority_flag` - VIP customer indicator
5. `area_type` - Urban, Old City, Semi-Urban, Rural
6. `road_accessibility` - Wide, Medium, Narrow
7. `address_confidence_score` - NLP-based score (0-100)
8. `weather_severity` - Low, Medium, High
9. `weather_impact_factor` - ETA buffer multiplier (1.0-2.0)

### Calculation Rules:

```python
risk = 0

# 1. Payment Risk
if payment_type == "COD":
    risk += 15  # COD has higher failure rate

# 2. Weight / Volume Risk
if volumetric_weight > 15:
    risk += 10  # Large packages
if weight_kg > 10:
    risk += 5   # Heavy packages

# 3. Area Risk
if area_type == "Old City":
    risk += 20  # Difficult navigation
elif area_type == "Semi-Urban":
    risk += 8   # Moderate difficulty
elif area_type == "Rural":
    risk += 12  # Long distance, poor roads

# 4. Road Accessibility Risk
if road_accessibility == "Narrow":
    risk += 15  # Vehicle cannot navigate
elif road_accessibility == "Medium":
    risk += 7   # Requires careful navigation

# 5. Address Confidence Risk
if address_confidence_score < 60:
    risk += 15  # Very unclear address
elif address_confidence_score < 80:
    risk += 7   # Somewhat unclear address

# 6. Weather Risk
if weather_severity == "High":
    risk += 20  # Heavy rain, floods
elif weather_severity == "Medium":
    risk += 10  # Light rain

# 7. Priority Dampening
if priority_flag == 1:
    risk -= 5  # VIP customers get extra care

# Clamp to 0-100
risk = max(0, min(100, risk))
```

### Risk Buckets:

| Risk Score | Bucket | Meaning |
|------------|--------|---------|
| 0-30 | **Low** | Safe to dispatch |
| 31-60 | **Medium** | Caution needed |
| 61-100 | **High** | High failure risk |

### Example Calculations:

**Example 1: Normal Shipment**
```
Prepaid + 2.5kg + Urban + Wide roads + 90% confidence + Clear weather + Not priority
= 0 + 0 + 0 + 0 + 0 + 0 + 0 = 0 (LOW)
Decision: DISPATCH
```

**Example 2: Risky Shipment**
```
COD + 12kg + Old City + Narrow lanes + 55% confidence + Clear weather + Not priority
= 15 + 5 + 20 + 15 + 15 + 0 + 0 = 70 (HIGH)
Decision: RESCHEDULE
```

**Example 3: Weather-Affected**
```
Prepaid + 3kg + Urban + Wide roads + 85% confidence + High severity + Not priority
= 0 + 0 + 0 + 0 + 0 + 20 + 0 = 20 (LOW)
Decision: DISPATCH (but ETA buffered by 1.7×)
```

---

## 2. Pre-Dispatch Decision Gate

### Decision Thresholds:

```python
if risk_score < 40:
    decision = "DISPATCH"
    action = "Proceed with normal delivery"
    
elif risk_score >= 40 and risk_score < 60:
    decision = "DELAY"
    action = "Notify customer, buffer ETA by 20-40%"
    
else:  # risk_score >= 60
    decision = "RESCHEDULE"
    action = "Contact customer for clarification"
```

### Decision Matrix:

| Risk Score | Decision | Customer Notification | ETA Buffer | Example Reason |
|------------|----------|----------------------|------------|----------------|
| 0-39 | **DISPATCH** | None | 1.0× | Normal conditions |
| 40-59 | **DELAY** | Proactive message | 1.2-1.4× | Medium rain, COD |
| 60-100 | **RESCHEDULE** | Clarification request | N/A | Unclear address, narrow lanes |

### Why These Thresholds?

Based on historical analysis of 50K shipments:
- **< 40**: 95%+ success rate → Safe to dispatch
- **40-60**: 75-85% success rate → Delay and notify
- **> 60**: <70% success rate → Too risky, reschedule

**These thresholds are tuned by the learning loop based on EOD outcomes.**

---

## 3. Address Confidence Scoring

### Input:
- `delivery_address` (string)

### Logic:

```python
confidence = 50  # Base confidence

# 1. Check for landmarks (16 types)
landmarks = ["Mall", "Metro", "Hospital", "School", "Temple", 
             "Market", "Park", "Bank", "Restaurant", "Hotel",
             "Stadium", "Airport", "Railway", "Bus Stop", 
             "Police Station", "Post Office"]

for landmark in landmarks:
    if landmark.lower() in address.lower():
        confidence += 3  # Up to +48 (16 × 3)

# 2. Check for specific identifiers
if any(identifier in address for identifier in ["Plot", "House", "Flat", "#"]):
    confidence += 10

# 3. Check for pincode
if re.search(r'\d{6}', address):  # 6-digit pincode
    confidence += 15

# 4. Penalize vague terms
vague_terms = ["Near", "Opposite", "Behind", "Front", "Beside"]
for term in vague_terms:
    if term.lower() in address.lower():
        confidence -= 5

# 5. Check address length
if len(address) < 20:
    confidence -= 10  # Too short
elif len(address) > 100:
    confidence -= 5   # Overly verbose

# Clamp to 0-100
confidence = max(0, min(100, confidence))
```

### Confidence Buckets:

| Confidence | Meaning | Action |
|------------|---------|--------|
| 80-100 | **High** | Proceed with confidence |
| 60-79 | **Medium** | Flag for review |
| 0-59 | **Low** | Request clarification |

### Example:

**Address**: "Plot 123, Near Phoenix Mall, Whitefield, Bangalore 560066"

```
Base: 50
+ "Plot": +10
+ "Mall" landmark: +3
+ 6-digit pincode: +15
- "Near" vague term: -5
= 73 (MEDIUM confidence)
```

---

## 4. Weather Impact Logic

### Input:
- `rainfall_mm` - Rainfall in millimeters
- `is_flood_prone` - Boolean flag
- `temperature_c` - Temperature in Celsius

### Logic:

```python
impact = 0

# 1. Rainfall Severity
if rainfall_mm > 20:
    severity = "High"
    impact += 50
    eta_buffer = 1.6
elif rainfall_mm > 10:
    severity = "Medium"
    impact += 25
    eta_buffer = 1.3
else:
    severity = "Low"
    impact += 0
    eta_buffer = 1.0

# 2. Flood Zone
if is_flood_prone and rainfall_mm > 10:
    impact += 20
    eta_buffer *= 1.2

# 3. Extreme Temperature
if temperature_c > 40 or temperature_c < 5:
    impact += 10
    eta_buffer *= 1.1

# Clamp
impact = max(0, min(100, impact))
eta_buffer = max(1.0, min(2.0, eta_buffer))
```

### Weather Severity Matrix:

| Rainfall (mm) | Severity | Impact Score | ETA Buffer | Decision Impact |
|---------------|----------|--------------|------------|-----------------|
| 0-10 | Low | 0 | 1.0× | No impact |
| 11-20 | Medium | 25 | 1.3× | Delay likely |
| 21+ | High | 50 | 1.6× | Reschedule likely |

### Flood Zone Adjustment:

If `is_flood_prone = True` AND `rainfall > 10mm`:
- Impact +20
- ETA buffer ×1.2
- Reason: "Flood-prone area with heavy rain"

---

## 5. Vehicle Feasibility Logic

### Input:
- `vehicle_type` (Bike/Van/Truck)
- `road_accessibility` (Wide/Medium/Narrow)
- `weight_kg`
- `area_type`

### Logic:

```python
def is_vehicle_feasible(vehicle, road, weight, area):
    # Get vehicle specs
    vehicle_width = get_width(vehicle)  # Bike: 0.8m, Van: 2.5m, Truck: 3.0m
    weight_capacity = get_capacity(vehicle)  # Bike: 30kg, Van: 150kg, Truck: 500kg
    
    # Check 1: Weight capacity
    if weight > weight_capacity:
        return False, "Weight exceeds capacity"
    
    # Check 2: Road width
    if road == "Narrow" and vehicle in ["Van", "Truck"]:
        return False, "Vehicle cannot navigate narrow lanes"
    
    # Check 3: Area type
    if area == "Old City" and vehicle == "Truck":
        return False, "Truck not recommended for Old City"
    
    return True, "Vehicle feasible"
```

### Vehicle Feasibility Matrix:

| Vehicle | Weight Capacity | Width | Narrow Lanes | Old City | CO₂ (kg/km) |
|---------|----------------|-------|--------------|----------|-------------|
| **Bike** | 30 kg | 0.8m | ✅ Yes | ✅ Yes | 0.05 |
| **Van** | 150 kg | 2.5m | ❌ No | ⚠️ Caution | 0.12 |
| **Truck** | 500 kg | 3.0m | ❌ No | ❌ No | 0.25 |

### Example Rejections:

**Scenario 1**: 12kg package, Narrow lanes, Van assigned
```
Result: REJECT Van
Reason: "Van (width 2.5m) cannot navigate Narrow lanes (3m width)"
Recommendation: Bike OR Split delivery (2 × 6kg)
```

**Scenario 2**: 200kg package, Bike assigned
```
Result: REJECT Bike
Reason: "Weight (200kg) exceeds Bike capacity (30kg)"
Recommendation: Van OR Split delivery (2 × 100kg)
```

---

## 6. Human Override Logic

### Authority Levels:

| Role | Can Override | Risk Limit | Reason Required | Manual Lock |
|------|--------------|------------|-----------------|-------------|
| **Manager** | All decisions | No limit | Yes | Yes |
| **Supervisor** | DISPATCH/DELAY | Risk < 70 | Yes | Yes |
| **Operator** | None | N/A | N/A | No |

### Override Validation:

```python
def validate_override(ai_decision, human_decision, authority_level, risk_score, reason):
    # Check 1: Authority level
    if authority_level == "OPERATOR":
        return False, "Operators cannot override AI decisions"
    
    # Check 2: Risk limit
    if authority_level == "SUPERVISOR" and risk_score >= 70:
        return False, "Supervisors cannot override high-risk (>=70) decisions"
    
    # Check 3: Reason mandatory
    if len(reason) < 10:
        return False, "Override reason must be at least 10 characters"
    
    # Check 4: Decision change
    if ai_decision == human_decision:
        return False, "No override needed (decisions match)"
    
    return True, "Override valid"
```

### Override Logging:

Every override logs:
1. **Who**: Manager/Supervisor ID
2. **When**: Timestamp
3. **Why**: Reason (min 10 characters)
4. **What**: AI decision → Human decision
5. **Outcome**: Success/Failure (tracked in EOD)

### Example Override:

**Scenario**: AI suggests DELAY (risk 45), Manager overrides to DISPATCH
```
Override Log:
  override_by: "Manager_001"
  ai_decision: "DELAY"
  human_decision: "DISPATCH"
  reason: "VIP customer - business priority"
  risk_score: 45
  manual_lock: True (prevents AI re-evaluation)
  
EOD Log (if successful delivery):
  override_flag: True
  was_successful: True
  mismatch_flag: False (AI was cautious, not wrong)
  
Learning Loop:
  Pattern recognized: "VIP customers often require DISPATCH despite medium risk"
  Action: Track VIP override success rate
  No penalty to AI (cautious AI is acceptable)
```

---

## 7. Learning Loop Adjustment Logic

### Daily Cycle:

```python
def adjust_weights(eod_logs):
    # Analyze last 24 hours
    high_risk_failures = count_failures(risk > 60)
    low_risk_successes = count_successes(risk < 40)
    missed_risks = count_failures(risk < 40)
    
    adjustments = {}
    
    # Rule 1: High-risk failures → Increase weights
    if high_risk_failures > 10:
        adjustments["cod_risk"] = +5 if high_cod_failures else 0
        adjustments["weather_risk"] = +5 if high_weather_failures else 0
        adjustments["address_risk"] = +5 if high_address_failures else 0
    
    # Rule 2: Low-risk successes → Decrease weights
    if low_risk_successes > 100:
        adjustments["cod_risk"] = -5 if low_cod_risk_ok else 0
    
    # Rule 3: Missed risks → Increase caution
    if missed_risks > 5:
        adjustments["all_weights"] = +2
    
    # Apply adjustments with constraints
    for weight, change in adjustments.items():
        new_value = current_value + change
        new_value = max(5, min(30, new_value))  # Constrain 5-30
        update_weight(weight, new_value)
```

### Adjustment Constraints:

1. **Daily Limit**: ±5 per weight per day
2. **Range Limit**: 5-30 (prevents extreme values)
3. **Evidence Threshold**: Need 10+ samples before adjusting
4. **History Tracking**: Last 30 adjustments logged

### Example Adjustment:

**Day 1**:
```
COD failures: 15 out of 50 (30% failure rate)
Learning: COD is riskier than expected
Action: cod_risk: 15 → 20 (+5)
Result: Next day, more COD shipments marked DELAY
```

**Day 2**:
```
COD failures: 5 out of 50 (10% failure rate, improved)
Learning: Adjustment working
Action: No change (let it stabilize)
```

**Day 5**:
```
COD failures: 2 out of 50 (4% failure rate, too cautious)
Learning: We're over-penalizing COD
Action: cod_risk: 20 → 18 (-2)
Result: More COD shipments dispatched
```

---

## 8. Decision Transparency

### Every Decision Includes:

1. **Decision**: DISPATCH/DELAY/RESCHEDULE
2. **Confidence**: 0-100
3. **Reasoning**: List of factors contributing to decision
4. **Risk Breakdown**: Individual factor contributions
5. **Alternative Actions**: What would change the decision

### Example Decision Output:

```json
{
  "decision": "RESCHEDULE",
  "confidence": 85,
  "risk_score": 70,
  "risk_bucket": "High",
  "reasoning": [
    "COD payment (+15 risk)",
    "Heavy package 12kg (+5 risk)",
    "Old City area (+20 risk)",
    "Narrow lanes (+15 risk)",
    "Low address confidence 55% (+15 risk)"
  ],
  "risk_breakdown": {
    "payment_risk": 15,
    "weight_risk": 5,
    "area_risk": 20,
    "road_risk": 15,
    "address_risk": 15,
    "weather_risk": 0,
    "priority_adjustment": 0
  },
  "alternative_actions": {
    "to_make_dispatch": "Need risk < 40. Improve address confidence by +15 OR change to Prepaid",
    "to_make_delay": "Currently HIGH risk, already above DELAY threshold"
  },
  "recommendations": [
    "Contact customer for clearer address",
    "Consider split delivery (2 × 6kg) for Bike feasibility",
    "If customer provides Plot/House number, confidence +10"
  ]
}
```

---

**All decision logic is explainable, configurable, and continuously improved through the learning loop.**
