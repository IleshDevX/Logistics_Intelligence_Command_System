from ingestion.load_data import load_all_data

try:
    shipments, addresses, delivery_history, weather, resources = load_all_data()
    print("✅ Data loaded successfully")
    print("Shipments:", shipments.shape)
    print("Addresses:", addresses.shape)
    print("Delivery History:", delivery_history.shape)
    print("Weather:", weather.shape)
    print("Resources:", resources.shape)

except Exception as e:
    print("❌ Data loading failed")
    print(e)

from ingestion.load_data import load_all_data
from ingestion.schema_check import validate_schema, EXPECTED_COLUMNS

shipments, addresses, history, weather, resources = load_all_data()

validate_schema(shipments, EXPECTED_COLUMNS["shipments"], "shipments")
validate_schema(addresses, EXPECTED_COLUMNS["addresses"], "addresses")
validate_schema(history, EXPECTED_COLUMNS["delivery_history"], "delivery_history")
validate_schema(weather, EXPECTED_COLUMNS["weather"], "weather")
validate_schema(resources, EXPECTED_COLUMNS["resources"], "resources")

print("✅ Schema validation passed for all datasets")

# ===================================
# REFERENTIAL INTEGRITY CHECKS
# ===================================
print("\n🔗 Checking referential integrity...")

# Check 1: Every shipment_id in addresses exists in shipments
addresses_orphans = ~addresses["shipment_id"].isin(shipments["shipment_id"])
assert not addresses_orphans.any(), f"❌ {addresses_orphans.sum()} orphaned shipment_ids in addresses.csv"
print(f"  ✅ All {len(addresses)} addresses link to valid shipments")

# Check 2: Every shipment_id in delivery_history exists in shipments
history_orphans = ~history["shipment_id"].isin(shipments["shipment_id"])
assert not history_orphans.any(), f"❌ {history_orphans.sum()} orphaned shipment_ids in delivery_history.csv"
print(f"  ✅ All {len(history)} history records link to valid shipments")

# Check 3: Cities in weather data match shipments
shipment_cities = set(shipments["destination_city"].unique())
weather_cities = set(weather["city"].unique())
unmatched_cities = shipment_cities - weather_cities
if unmatched_cities:
    print(f"  ⚠️  Warning: {len(unmatched_cities)} cities in shipments have no weather data: {unmatched_cities}")
else:
    print(f"  ✅ All cities have weather coverage")

print("✅ Referential integrity checks passed")

# ===================================
# DATA HEALTH CHECKS
# ===================================
print("\n🏥 Running data health checks...")

# Missing value analysis
print("\n📊 Missing Value Analysis:")
for name, df in [("shipments", shipments), ("addresses", addresses), ("history", history), ("weather", weather), ("resources", resources)]:
    missing_pct = (df.isnull().sum() / len(df) * 100)
    if missing_pct.any():
        print(f"  {name}:")
        for col, pct in missing_pct[missing_pct > 0].items():
            print(f"    - {col}: {pct:.1f}% missing")
    else:
        print(f"  {name}: No missing values ✅")

# Distribution sanity checks
print("\n📈 Distribution Sanity Checks:")

# Risk score validation
assert shipments["current_risk_score"].between(0, 100).all(), "❌ Risk score out of bounds"
print(f"  ✅ Risk scores: {shipments['current_risk_score'].min():.0f} - {shipments['current_risk_score'].max():.0f} (valid range)")

# Payment type validation
assert shipments["payment_type"].isin(["COD", "Prepaid"]).all(), "❌ Invalid payment type"
cod_ratio = (shipments["payment_type"] == "COD").mean() * 100
print(f"  ✅ COD ratio: {cod_ratio:.1f}% (expected ~50-60%)")
if not (50 <= cod_ratio <= 60):
    print(f"    ⚠️  Warning: COD ratio outside expected range")

# Address confidence validation
assert addresses["address_confidence_score"].between(0, 100).all(), "❌ Invalid address score"
low_confidence = (addresses["address_confidence_score"] < 50).sum()
print(f"  ✅ Address confidence: {addresses['address_confidence_score'].mean():.1f} avg, {low_confidence} low-confidence addresses")

# Old city analysis
old_cities = ['Delhi', 'Mumbai', 'Kolkata', 'Chennai', 'Bangalore', 'Hyderabad']
old_city_shipments = shipments[shipments['destination_city'].isin(old_cities)]
old_city_ratio = len(old_city_shipments) / len(shipments) * 100
print(f"  ✅ Old city ratio: {old_city_ratio:.1f}% (expected ~25-35%)")
if not (25 <= old_city_ratio <= 35):
    print(f"    ⚠️  Warning: Old city ratio outside expected range")

# Weight and volume checks
print(f"  ✅ Weight range: {shipments['weight_kg'].min():.1f} - {shipments['weight_kg'].max():.1f} kg")
if 'volumetric_weight' in shipments.columns:
    print(f"  ✅ Volumetric weight range: {shipments['volumetric_weight'].min():.1f} - {shipments['volumetric_weight'].max():.1f}")

print("\n✅ Data health checks passed")

print("All tests passed successfully!")
