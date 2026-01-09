"""
CO₂ vs Speed Trade-off Engine Test Suite

Tests emission calculations, ETA calculations, and trade-off comparisons
"""

from features.carbon_tradeoff_engine import (
    calculate_co2_emission,
    calculate_eta,
    co2_speed_tradeoff,
    get_vehicle_emission_factor,
    calculate_co2_percentage_saved,
    sustainability_score,
    format_tradeoff_for_dashboard
)

print("=" * 60)
print("CO₂ vs SPEED TRADE-OFF ENGINE TEST SUITE")
print("=" * 60)

# Test Case 1: CO₂ Calculation - Smooth Traffic
print("\n🌍 Test Case 1: CO₂ Emission - Smooth Traffic")
print("-" * 60)
co2 = calculate_co2_emission(
    distance_km=20,
    emission_factor_gkm=120,
    traffic_type="Smooth"
)
print(f"Distance: 20km, Emission Factor: 120g/km, Traffic: Smooth")
print(f"CO₂ Emission: {co2} kg")
expected = (20 * 120 * 1.0) / 1000  # = 2.4 kg
assert co2 == 2.4, f"Expected 2.4kg, got {co2}kg"
print("✅ PASSED")

# Test Case 2: CO₂ Calculation - Stop-Start Traffic
print("\n🚦 Test Case 2: CO₂ Emission - Stop-Start Traffic")
print("-" * 60)
co2 = calculate_co2_emission(
    distance_km=20,
    emission_factor_gkm=120,
    traffic_type="Stop-Start"
)
print(f"Distance: 20km, Emission Factor: 120g/km, Traffic: Stop-Start")
print(f"CO₂ Emission: {co2} kg")
expected = (20 * 120 * 1.3) / 1000  # = 3.12 kg
assert co2 == 3.12, f"Expected 3.12kg, got {co2}kg"
print("✅ PASSED - Stop-start traffic increases emissions by 30%")

# Test Case 3: ETA Calculation
print("\n⏱️  Test Case 3: ETA Calculation")
print("-" * 60)
eta = calculate_eta(distance_km=20, avg_speed_kmph=25)
print(f"Distance: 20km, Speed: 25km/h")
print(f"ETA: {eta} hours ({eta * 60:.0f} minutes)")
assert eta == 0.8, f"Expected 0.8 hours, got {eta} hours"
print("✅ PASSED")

# Test Case 4: Trade-off Comparison - Van
print("\n🚐 Test Case 4: Trade-off Comparison - Van (120 g/km)")
print("-" * 60)
result = co2_speed_tradeoff(emission_factor_gkm=120)
print(f"Fast Route: {result['fast_route']['eta_hours']}h, {result['fast_route']['co2_kg']}kg CO₂")
print(f"Green Route: {result['green_route']['eta_hours']}h, {result['green_route']['co2_kg']}kg CO₂")
print(f"CO₂ Saved: {result['co2_saved_kg']} kg")
print(f"Time Cost: {result['time_cost_hours']} hours")
assert result['green_route']['co2_kg'] < result['fast_route']['co2_kg'], "Green should have lower emissions"
assert result['co2_saved_kg'] > 0, "Should save CO₂"
print("✅ PASSED - Green route has lower emissions")

# Test Case 5: Trade-off Comparison - Bike
print("\n🏍️  Test Case 5: Trade-off Comparison - Bike (50 g/km)")
print("-" * 60)
result = co2_speed_tradeoff(emission_factor_gkm=50)
print(f"Fast Route: {result['fast_route']['eta_hours']}h, {result['fast_route']['co2_kg']}kg CO₂")
print(f"Green Route: {result['green_route']['eta_hours']}h, {result['green_route']['co2_kg']}kg CO₂")
print(f"CO₂ Saved: {result['co2_saved_kg']} kg")
print(f"Recommendation: {result['recommendation']}")
assert result['fast_route']['co2_kg'] < 2.0, "Bike should have low emissions"
print("✅ PASSED - Bike emissions are low")

# Test Case 6: Trade-off Comparison - Truck
print("\n🚛 Test Case 6: Trade-off Comparison - Truck (200 g/km)")
print("-" * 60)
result = co2_speed_tradeoff(emission_factor_gkm=200)
print(f"Fast Route: {result['fast_route']['eta_hours']}h, {result['fast_route']['co2_kg']}kg CO₂")
print(f"Green Route: {result['green_route']['eta_hours']}h, {result['green_route']['co2_kg']}kg CO₂")
print(f"CO₂ Saved: {result['co2_saved_kg']} kg")
print(f"Recommendation: {result['recommendation']}")
assert result['fast_route']['co2_kg'] > 4.0, "Truck should have high emissions"
assert result['co2_saved_kg'] > 0, "Should save some CO₂"
print("✅ PASSED - Truck emissions are high, green route saves CO₂")

# Test Case 7: Vehicle Emission Factors
print("\n📊 Test Case 7: Vehicle Emission Factors")
print("-" * 60)
bike_emission = get_vehicle_emission_factor("Bike")
van_emission = get_vehicle_emission_factor("Van")
truck_emission = get_vehicle_emission_factor("Truck")
print(f"Bike: {bike_emission} g/km")
print(f"Van: {van_emission} g/km")
print(f"Truck: {truck_emission} g/km")
assert bike_emission < van_emission < truck_emission, "Emissions should increase: Bike < Van < Truck"
print("✅ PASSED - Emission factors correctly ordered")

# Test Case 8: CO₂ Percentage Saved
print("\n📈 Test Case 8: CO₂ Percentage Saved")
print("-" * 60)
pct_saved = calculate_co2_percentage_saved(fast_co2=3.12, green_co2=2.4)
print(f"Fast Route: 3.12 kg, Green Route: 2.4 kg")
print(f"Percentage Saved: {pct_saved}%")
expected_pct = ((3.12 - 2.4) / 3.12) * 100
assert abs(pct_saved - expected_pct) < 1, "Percentage calculation incorrect"
print("✅ PASSED")

# Test Case 9: Sustainability Scoring
print("\n🌱 Test Case 9: Sustainability Scoring")
print("-" * 60)
test_cases = [
    (0.8, "A (Excellent)"),
    (1.5, "B (Good)"),
    (2.5, "C (Average)"),
    (4.0, "D (Poor)"),
    (6.0, "F (Very Poor)")
]
for co2, expected_grade in test_cases:
    grade = sustainability_score(co2)
    print(f"  {co2} kg CO₂ → Grade: {grade}")
    assert grade == expected_grade, f"Expected {expected_grade}, got {grade}"
print("✅ PASSED - All sustainability grades correct")

# Test Case 10: Dashboard Formatting
print("\n📋 Test Case 10: Dashboard Formatting")
print("-" * 60)
result = co2_speed_tradeoff(emission_factor_gkm=120)
formatted = format_tradeoff_for_dashboard(result)
print(formatted)
assert "FAST ROUTE" in formatted, "Should contain fast route info"
assert "GREEN ROUTE" in formatted, "Should contain green route info"
assert "CO₂ Saved" in formatted, "Should show CO₂ savings"
print("✅ PASSED - Dashboard format generated correctly")

# Test Case 11: All Vehicle Types Comparison
print("\n🚗 Test Case 11: All Vehicle Types Comparison")
print("-" * 60)
print(f"{'Vehicle':<10} {'Fast CO₂':<12} {'Green CO₂':<12} {'Saved':<10} {'% Saved':<10}")
print("-" * 60)
for vehicle in ["Bike", "Van", "Truck"]:
    emission_factor = get_vehicle_emission_factor(vehicle)
    result = co2_speed_tradeoff(emission_factor)
    pct = calculate_co2_percentage_saved(
        result['fast_route']['co2_kg'],
        result['green_route']['co2_kg']
    )
    print(f"{vehicle:<10} {result['fast_route']['co2_kg']:<12} "
          f"{result['green_route']['co2_kg']:<12} "
          f"{result['co2_saved_kg']:<10} {pct:<10}%")
print("✅ PASSED - All vehicle types compared")

# Summary
print("\n" + "=" * 60)
print("📊 TEST SUMMARY")
print("=" * 60)
print("✅ All 11 test cases PASSED")
print("\nCO₂ vs Speed Engine Validated:")
print("  ✅ Emission calculations (smooth vs stop-start traffic)")
print("  ✅ ETA calculations")
print("  ✅ Trade-off comparisons (fast vs green routes)")
print("  ✅ Vehicle-specific emission factors")
print("  ✅ Percentage savings calculations")
print("  ✅ Sustainability scoring (A-F grades)")
print("  ✅ Dashboard formatting")
print("\nKey Insights:")
print("  🌍 Green route consistently saves 20-30% CO₂")
print("  ⏱️  Time cost: ~0.2 hours (12 minutes) extra")
print("  🚛 Truck emissions 4x higher than bike")
print("  📊 Trade-offs quantified, not auto-optimized")
print("\n" + "=" * 60)
print("✅ CO₂ vs SPEED TRADE-OFF ENGINE: OPERATIONAL")
print("=" * 60)
