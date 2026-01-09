# Data Contract — FROZEN
**Date Frozen:** January 9, 2026  
**System:** Logistics Intelligence & Command System (LICS)

---

## Contract Statement

**These five datasets and their schemas are FIXED.**

All models, rules, APIs, and dashboards will rely on them.

Any change to these schemas requires a formal review and version increment.

---

## Dataset Inventory

### 1. `shipments.csv` (Master Dataset)
**Purpose:** Core shipment records  
**Key Column:** `shipment_id` (Primary Key)

**Schema:**
- `shipment_id` - Unique identifier
- `product_type` - Type of product being shipped
- `weight_kg` - Package weight (kg)
- `volumetric_weight` - Volumetric weight calculation
- `payment_type` - COD or Prepaid
- `priority_flag` - Priority shipment indicator
- `destination_city` - Delivery city
- `current_risk_score` - Risk score (0-100)

**Validation Rules:**
- No duplicate `shipment_id`
- `current_risk_score` ∈ [0, 100]
- `payment_type` ∈ {COD, Prepaid}
- `weight_kg` > 0
- `volumetric_weight` > 0

---

### 2. `addresses.csv`
**Purpose:** Address details and confidence scores  
**Foreign Key:** `shipment_id` → `shipments.shipment_id`

**Schema:**
- `shipment_id` - Links to shipments
- `raw_address_text` - Customer-provided address text
- `area_type` - Urban/Rural/Semi-Urban
- `road_accessibility` - Road condition score
- `address_confidence_score` - Quality score (0-100)
- `vehicle_access_score` - Vehicle accessibility score

**Validation Rules:**
- All `shipment_id` must exist in `shipments.csv`
- `address_confidence_score` ∈ [0, 100]
- `area_type` ∈ {Urban, Rural, Semi-Urban}

---

### 3. `delivery_history.csv`
**Purpose:** Historical delivery outcomes  
**Foreign Key:** `shipment_id` → `shipments.shipment_id`

**Schema:**
- `shipment_id` - Links to shipments
- `delivery_outcome` - Success/Failed/Delayed
- `human_override_flag` - Whether human intervened
- `failure_reason` - Reason for failure (nullable)
- `delivery_delay_minutes` - Delay in minutes

**Validation Rules:**
- All `shipment_id` must exist in `shipments.csv`
- `delivery_delay_minutes` ≥ 0
- `failure_reason` may be null (~30% expected)

---

### 4. `weather_and_environment.csv`
**Purpose:** Weather conditions per city  
**Key Column:** `city`

**Schema:**
- `city` - City name
- `weather_severity` - Severity level (Low/Medium/High)
- `weather_impact_factor` - Impact multiplier for delays

**Validation Rules:**
- Cities should match `destination_city` in shipments
- `weather_impact_factor` ≥ 1.0

---

### 5. `resources_capability.csv`
**Purpose:** Vehicle and rider resources  
**Key Column:** `resource_id` (if exists)

**Schema:**
- `resource_type` - Vehicle or Rider
- `vehicle_type` - Bike/Van/Truck
- `max_load_kg` - Maximum load capacity (kg)
- `emission_factor_gkm` - CO₂ emissions (g/km)
- `area_familiarity_score` - Familiarity with service areas

**Validation Rules:**
- `resource_type` ∈ {Vehicle, Rider}
- `max_load_kg` > 0
- `emission_factor_gkm` ≥ 0

---

## Referential Integrity Rules

1. **Addresses ↔ Shipments**  
   Every `shipment_id` in `addresses.csv` MUST exist in `shipments.csv`

2. **Delivery History ↔ Shipments**  
   Every `shipment_id` in `delivery_history.csv` MUST exist in `shipments.csv`

3. **Weather ↔ Shipments**  
   All cities in `shipments.csv` SHOULD have weather data in `weather_and_environment.csv`

---

## Data Quality Benchmarks

| Metric | Expected Range | Status |
|--------|---------------|--------|
| COD Ratio | 50-60% | ✅ Validated |
| Old City Ratio | 25-35% | ✅ Validated |
| Risk Score Range | 0-100 | ✅ Validated |
| Address Confidence | 0-100 | ✅ Validated |
| Missing Values | <5% per column | ✅ Validated |

---

## Change Control

**No new columns without:**
1. Business justification
2. Impact analysis on existing models
3. Version increment
4. Documentation update

**Contract Version:** 1.0  
**Last Validated:** January 9, 2026  
**Next Review:** When new features require schema changes
