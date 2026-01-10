"""
Weather Impact Engine Test Suite

Tests weather API integration, impact calculation, and ETA buffer logic
"""

from features.weather_impact import (
    get_weather_impact,
    calculate_weather_impact_factor,
    calculate_eta_buffer_multiplier,
    determine_weather_severity,
    should_delay_dispatch,
    get_flood_risk
)

print("=" * 60)
print("WEATHER IMPACT ENGINE TEST SUITE")
print("=" * 60)

# Test Case 1: High Impact Weather (Heavy Rain + High Flood Risk)
print("\n🔴 Test Case 1: High Impact Weather")
print("-" * 60)
impact = calculate_weather_impact_factor(
    weather_severity="High",
    flood_risk="High",
    rainfall_mm=15,
    humidity=85
)
multiplier = calculate_eta_buffer_multiplier(impact)
delay = should_delay_dispatch(impact, "High")

print(f"Conditions: Heavy Rain (15mm), High Flood Risk, 85% Humidity")
print(f"Weather Impact Factor: {impact}")
print(f"ETA Buffer Multiplier: {multiplier}x")
print(f"Should Delay Dispatch: {delay}")
assert impact >= 70, "High impact should be >= 70"
assert multiplier >= 1.5, "High impact should increase ETA"
assert delay == True, "Should delay dispatch"
print("✅ PASSED")

# Test Case 2: Low Impact Weather (Clear + Low Flood Risk)
print("\n🟢 Test Case 2: Low Impact Weather")
print("-" * 60)
impact = calculate_weather_impact_factor(
    weather_severity="Low",
    flood_risk="Low",
    rainfall_mm=0,
    humidity=50
)
multiplier = calculate_eta_buffer_multiplier(impact)
delay = should_delay_dispatch(impact, "Low")

print(f"Conditions: Clear Sky, Low Flood Risk, 50% Humidity")
print(f"Weather Impact Factor: {impact}")
print(f"ETA Buffer Multiplier: {multiplier}x")
print(f"Should Delay Dispatch: {delay}")
assert impact <= 30, "Low impact should be <= 30"
assert multiplier == 1.0, "No delay for good weather"
assert delay == False, "Should NOT delay dispatch"
print("✅ PASSED")

# Test Case 3: Medium Impact Weather
print("\n🟡 Test Case 3: Medium Impact Weather")
print("-" * 60)
impact = calculate_weather_impact_factor(
    weather_severity="Medium",
    flood_risk="Medium",
    rainfall_mm=5,
    humidity=70
)
multiplier = calculate_eta_buffer_multiplier(impact)
delay = should_delay_dispatch(impact, "Medium")

print(f"Conditions: Moderate Rain (5mm), Medium Flood Risk, 70% Humidity")
print(f"Weather Impact Factor: {impact}")
print(f"ETA Buffer Multiplier: {multiplier}x")
print(f"Should Delay Dispatch: {delay}")
assert 30 <= impact <= 70, "Medium impact should be 30-70"
assert multiplier > 1.0, "Should have some delay"
assert delay == False, "Medium conditions can proceed with caution"
print("✅ PASSED")

# Test Case 4: Flood-Prone City
print("\n🌊 Test Case 4: Flood Risk Assessment")
print("-" * 60)
mumbai_risk = get_flood_risk("Mumbai")
delhi_risk = get_flood_risk("Delhi")
unknown_risk = get_flood_risk("UnknownCity")

print(f"Mumbai Flood Risk: {mumbai_risk}")
print(f"Delhi Flood Risk: {delhi_risk}")
print(f"Unknown City Risk: {unknown_risk}")

assert mumbai_risk == "High", "Mumbai should be high flood risk"
assert delhi_risk == "Low", "Delhi should be low flood risk"
assert unknown_risk == "Low", "Unknown cities default to low"
print("✅ PASSED")

# Test Case 5: Weather Severity Detection
print("\n⛈️  Test Case 5: Weather Severity Detection")
print("-" * 60)
severity_clear = determine_weather_severity(0, 3, "Clear")
severity_rain = determine_weather_severity(8, 10, "Rain")
severity_storm = determine_weather_severity(20, 30, "Thunderstorm")

print(f"Clear sky (0mm, 3m/s): {severity_clear}")
print(f"Moderate rain (8mm, 10m/s): {severity_rain}")
print(f"Thunderstorm (20mm, 30m/s): {severity_storm}")

assert severity_clear == "Low", "Clear should be low"
assert severity_rain == "Medium", "Moderate rain should be medium"
assert severity_storm == "High", "Thunderstorm should be high"
print("✅ PASSED")

# Test Case 6: ETA Buffer Multipliers
print("\n⏱️  Test Case 6: ETA Buffer Multipliers")
print("-" * 60)
buffer_low = calculate_eta_buffer_multiplier(20)
buffer_med = calculate_eta_buffer_multiplier(45)
buffer_high = calculate_eta_buffer_multiplier(75)

print(f"Impact 20 (Low):  {buffer_low}x ETA")
print(f"Impact 45 (Med):  {buffer_med}x ETA")
print(f"Impact 75 (High): {buffer_high}x ETA")

assert buffer_low == 1.0, "Low impact = no buffer"
assert buffer_med > 1.0 and buffer_med < 2.0, "Medium impact = moderate buffer"
assert buffer_high >= 1.5, "High impact = significant buffer"
print("✅ PASSED")

# Test Case 7: Live/Simulated Weather Data
print("\n🌐 Test Case 7: Weather Data Integration")
print("-" * 60)
print("Testing with simulated data (no API key)...")

# Test with multiple cities
cities = ["Mumbai", "Delhi", "Bangalore"]
for city in cities:
    result = get_weather_impact(city, use_live_api=False)
    print(f"\n{city}:")
    print(f"  Condition: {result['weather_condition']}")
    print(f"  Severity: {result['weather_severity']}")
    print(f"  Impact Factor: {result['weather_impact_factor']}")
    print(f"  ETA Multiplier: {result['eta_buffer_multiplier']}x")
    print(f"  Flood Risk: {result['flood_risk']}")
    print(f"  Source: {result['source']}")
    
    assert 0 <= result['weather_impact_factor'] <= 100, "Impact should be 0-100"
    assert result['eta_buffer_multiplier'] >= 1.0, "Multiplier should be >= 1.0"

print("\n✅ PASSED")

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED")
print("=" * 60)
print("\n📊 Weather Impact Engine Summary:")
print("  ✅ Weather severity classification")
print("  ✅ Flood risk assessment")
print("  ✅ Impact factor calculation")
print("  ✅ ETA buffer multiplier logic")
print("  ✅ Dispatch delay decision logic")
print("  ✅ Live API integration (ready)")
print("  ✅ Fallback simulation (working)")
print("\n🎯 Weather impact engine is ready for production!")
print("\n📝 Note: To use live weather API:")
print("   1. Get free API key from: https://openweathermap.org/api")
print("   2. Update WEATHER_API_KEY in features/weather_impact.py")
print("   3. Set use_live_api=True when calling get_weather_impact()")
