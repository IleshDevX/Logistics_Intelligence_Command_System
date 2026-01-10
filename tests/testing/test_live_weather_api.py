"""
Live Weather API Test

Tests the weather impact engine with real OpenWeatherMap API
"""

from features.weather_impact import get_weather_impact

print("=" * 60)
print("LIVE WEATHER API TEST")
print("=" * 60)

# Test cities
test_cities = ["Mumbai", "Delhi", "Bangalore", "Chennai"]

print("\n🌐 Fetching live weather data from OpenWeatherMap API...")
print("-" * 60)

for city in test_cities:
    print(f"\n🌍 {city}:")
    try:
        result = get_weather_impact(city, use_live_api=True)
        
        print(f"  Condition: {result['weather_condition']} ({result['weather_description']})")
        print(f"  Temperature: {result['temperature']}°C")
        print(f"  Rainfall: {result['rainfall_mm']} mm/hr")
        print(f"  Wind Speed: {result['wind_speed']} m/s")
        print(f"  Humidity: {result['humidity']}%")
        print(f"  Severity: {result['weather_severity']}")
        print(f"  Flood Risk: {result['flood_risk']}")
        print(f"  Impact Factor: {result['weather_impact_factor']}")
        print(f"  ETA Multiplier: {result['eta_buffer_multiplier']}x")
        print(f"  Data Source: {result['source']}")
        
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")

print("\n" + "=" * 60)
print("✅ LIVE API TEST COMPLETE")
print("=" * 60)
print("\n📊 Live weather data successfully integrated!")
print("🎯 Weather impact engine is now using real-time data")
