# Data Schema

## Overview

These schemas are **fixed data contracts** used across all models, APIs, and dashboards. Any changes require versioning and migration.

## 1. Shipments Data (`data/shipments.csv`)

| Column | Type | Description | Example | Constraints |
|--------|------|-------------|---------|-------------|
| `shipment_id` | String | Unique shipment identifier | "SH001" | Primary Key, NOT NULL |
| `weight_kg` | Float | Actual package weight in kilograms | 2.5 | > 0, < 100 |
| `volumetric_weight` | Float | Volume-based weight calculation | 3.0 | > 0, < 150 |
| `payment_type` | Enum | Payment method | "COD", "Prepaid" | IN ("COD", "Prepaid") |
| `priority_flag` | Integer | Priority shipment indicator | 0, 1 | IN (0, 1) |
| `dispatch_date` | Date | Planned dispatch date | "2025-01-15" | ISO 8601 format |
| `current_risk_score` | Integer | AI-generated risk score | 45 | 0-100 |

**Purpose**: Core shipment information for risk calculation and decision-making.

**Record Count**: 50,000 shipments

---

## 2. Addresses Data (`data/addresses.csv`)

| Column | Type | Description | Example | Constraints |
|--------|------|-------------|---------|-------------|
| `shipment_id` | String | Foreign key to shipments | "SH001" | FK to shipments.shipment_id |
| `delivery_address` | Text | Full delivery address | "123 MG Road, Bangalore" | NOT NULL, min length 10 |
| `area_type` | Enum | Area classification | "Urban", "Old City" | IN ("Urban", "Old City", "Semi-Urban", "Rural") |
| `road_accessibility` | Enum | Road width classification | "Wide", "Narrow" | IN ("Wide", "Medium", "Narrow") |
| `address_confidence_score` | Float | NLP-based confidence | 85.5 | 0-100 |
| `city` | String | Delivery city | "Bangalore" | NOT NULL |
| `pincode` | String | Postal code | "560001" | 6 digits |
| `landmark_types` | JSON | Nearby landmark categories | ["Mall", "Metro"] | Array of strings |

**Purpose**: Address intelligence and last-mile feasibility assessment.

**Record Count**: 50,000 addresses (1:1 with shipments)

---

## 3. Weather Data (`data/weather_and_environment.csv`)

| Column | Type | Description | Example | Constraints |
|--------|------|-------------|---------|-------------|
| `city` | String | City name | "Bangalore" | NOT NULL |
| `date` | Date | Weather forecast date | "2025-01-15" | ISO 8601 |
| `rainfall_mm` | Float | Rainfall in millimeters | 22.5 | >= 0 |
| `weather_severity` | Enum | Severity classification | "High" | IN ("Low", "Medium", "High") |
| `is_flood_prone` | Boolean | Flood risk indicator | True | IN (True, False) |
| `weather_impact_factor` | Float | ETA buffer multiplier | 1.6 | 1.0 - 2.0 |
| `temperature_c` | Float | Temperature in Celsius | 28.5 | -10 to 50 |

**Purpose**: Weather-based risk adjustment and ETA buffering.

**Record Count**: ~365 × 50 cities = 18,250 records

---

## 4. Resources & Capability (`data/resources_capability.csv`)

| Column | Type | Description | Example | Constraints |
|--------|------|-------------|---------|-------------|
| `vehicle_type` | Enum | Vehicle category | "Bike", "Van" | IN ("Bike", "Van", "Truck") |
| `weight_capacity_kg` | Float | Maximum weight capacity | 150.0 | > 0 |
| `volume_capacity_m3` | Float | Maximum volume capacity | 2.5 | > 0 |
| `vehicle_width_m` | Float | Vehicle width in meters | 2.5 | > 0 |
| `turning_radius_m` | Float | Minimum turning radius | 5.0 | > 0 |
| `co2_emission_kg_per_km` | Float | Carbon emission factor | 0.12 | >= 0 |
| `hourly_cost` | Float | Operational cost per hour | 150.0 | >= 0 |

**Purpose**: Vehicle selection and feasibility checks.

**Record Count**: 3 vehicle types

---

## 5. Delivery History (`data/delivery_history.csv`)

| Column | Type | Description | Example | Constraints |
|--------|------|-------------|---------|-------------|
| `shipment_id` | String | Foreign key to shipments | "SH001" | FK to shipments.shipment_id |
| `final_status` | Enum | Delivery outcome | "DELIVERED" | IN ("DELIVERED", "FAILED", "RETURNED") |
| `delivery_date` | Date | Actual delivery date | "2025-01-16" | ISO 8601 |
| `delivery_time` | Time | Actual delivery time | "14:30:00" | HH:MM:SS |
| `attempts` | Integer | Number of delivery attempts | 1 | >= 1 |
| `failure_reason` | String | Reason for failure (if any) | "Address not found" | NULL if delivered |
| `was_delayed` | Boolean | Delay indicator | False | IN (True, False) |

**Purpose**: EOD logging and learning loop analysis.

**Record Count**: 50,000 records (grows daily)

---

## 6. Risk Weights Configuration (`configs/risk_weights.json`)

```json
{
  "cod_risk": 15,
  "address_risk": 15,
  "weather_risk": 20,
  "area_risk": 15,
  "weight_risk": 10,
  "last_updated": "2025-01-15T10:30:00",
  "update_count": 45,
  "adjustment_history": [
    {
      "timestamp": "2025-01-15T10:30:00",
      "field": "cod_risk",
      "old_value": 14,
      "new_value": 15,
      "reason": "High COD failure rate"
    }
  ]
}
```

**Purpose**: Learning loop weight adjustments (±5/day, 5-30 range).

---

## 7. Learning History (`logs/learning_history.csv`)

| Column | Type | Description | Example | Constraints |
|--------|------|-------------|---------|-------------|
| `timestamp` | DateTime | Learning cycle timestamp | "2025-01-15 10:30:00" | NOT NULL |
| `weight_updates` | JSON | Weight adjustments made | {"cod_risk": "+5"} | JSON object |
| `address_adjustment` | Float | Address confidence change | +2.5 | -10 to +10 |
| `override_effectiveness` | Float | % of successful overrides | 78.5 | 0-100 |
| `total_shipments` | Integer | Shipments analyzed | 1500 | >= 0 |
| `learning_signals` | Integer | Signals triggering learning | 12 | >= 0 |

**Purpose**: Audit trail for learning loop changes.

**Record Count**: Grows daily (1 row per learning cycle)

---

## 8. EOD Logs (`logs/eod_logs.csv`)

| Column | Type | Description | Example | Constraints |
|--------|------|-------------|---------|-------------|
| `shipment_id` | String | Shipment identifier | "SH001" | FK to shipments |
| `predicted_risk_score` | Integer | AI risk score | 45 | 0-100 |
| `predicted_decision` | Enum | AI decision | "DISPATCH" | IN ("DISPATCH", "DELAY", "RESCHEDULE") |
| `predicted_risk_bucket` | Enum | Risk classification | "Medium" | IN ("Low", "Medium", "High") |
| `actual_status` | Enum | Delivery outcome | "DELIVERED" | IN ("DELIVERED", "FAILED", "RETURNED") |
| `mismatch_flag` | Boolean | Prediction error indicator | False | IN (True, False) |
| `override_flag` | Boolean | Human override indicator | False | IN (True, False) |
| `override_by` | String | Manager name (if override) | "Manager_001" | NULL if no override |
| `override_reason` | Text | Override justification | "VIP customer" | NULL if no override |
| `was_successful` | Boolean | Delivery success indicator | True | IN (True, False) |
| `had_delay` | Boolean | Delay indicator | False | IN (True, False) |
| `prediction_accuracy` | Float | Accuracy score (0-100) | 95.0 | 0-100 |
| `timestamp` | DateTime | Log creation time | "2025-01-15 18:00:00" | NOT NULL |

**Purpose**: Prediction vs reality tracking for learning loop.

**Record Count**: Grows daily (1 row per completed delivery)

---

## 9. Override Logs (`logs/override_logs.csv`)

| Column | Type | Description | Example | Constraints |
|--------|------|-------------|---------|-------------|
| `override_id` | String | Unique override ID | "OVR_001" | Primary Key |
| `shipment_id` | String | Shipment identifier | "SH001" | FK to shipments |
| `ai_decision` | Enum | Original AI decision | "DELAY" | IN ("DISPATCH", "DELAY", "RESCHEDULE") |
| `human_decision` | Enum | Manager override decision | "DISPATCH" | IN ("DISPATCH", "DELAY", "RESCHEDULE") |
| `override_by` | String | Manager identifier | "Manager_001" | NOT NULL |
| `authority_level` | Enum | Manager authority | "MANAGER" | IN ("MANAGER", "SUPERVISOR", "OPERATOR") |
| `reason` | Text | Override justification | "VIP customer" | NOT NULL, min length 10 |
| `timestamp` | DateTime | Override time | "2025-01-15 12:00:00" | NOT NULL |
| `manual_lock` | Boolean | Prevent re-evaluation | True | IN (True, False) |

**Purpose**: Accountability trail for human overrides.

**Record Count**: Grows as overrides occur (~5-10% of shipments)

---

## Data Relationships

```
shipments (1) ← → (1) addresses
      ↓
      ↓ (1) → (1) delivery_history
      ↓
      ↓ (1) → (0..1) override_logs
      ↓
      ↓ (1) → (1) eod_logs

weather (N) ← → (1) city

resources_capability (N) ← → (1) vehicle_type
```

## Data Quality Rules

1. **Referential Integrity**: All foreign keys must exist in parent tables
2. **Range Validation**: Risk scores (0-100), weights (> 0), confidence (0-100)
3. **Enum Validation**: Only allowed values for categorical fields
4. **Timestamp Format**: ISO 8601 (YYYY-MM-DD HH:MM:SS)
5. **No NULL Values**: For critical fields (shipment_id, decision, status)

## Data Versioning

**Current Version**: 1.0

**Migration Path**:
- CSV files → PostgreSQL/MongoDB (Version 2.0)
- Add indexes on shipment_id, city, date
- Add triggers for automatic timestamp updates
- Add views for common analytics queries

---

**These schemas are production-ready with clear migration paths to relational/NoSQL databases.**
