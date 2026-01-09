"""
Weather Impact Integration Test with Real Shipment Data

Tests weather impact engine integrated with shipment data
"""

from ingestion.load_data import load_all_data
from features.weather_impact import get_weather_impact
import pandas as pd

print("=" * 60)
print("WEATHER IMPACT - REAL DATA INTEGRATION TEST")
print("=" * 60)

# Load data
print("\n📦 Loading datasets...")
shipments, addresses, history, weather, resources = load_all_data()
print("✅ Data loaded successfully")

# Get unique cities from shipments
print("\n🌍 Analyzing shipment destinations...")
cities = shipments['destination_city'].unique()
print(f"Found {len(cities)} unique destination cities")

# Get weather impact for each city
print("\n🌦️  Fetching weather impact for all cities...")
weather_impacts = []
for city in cities:
    impact = get_weather_impact(city, use_live_api=False)  # Using simulated data
    weather_impacts.append(impact)

weather_df = pd.DataFrame(weather_impacts)
print(f"✅ Weather impact calculated for {len(weather_df)} cities")

# Analysis
print("\n" + "=" * 60)
print("📊 WEATHER IMPACT ANALYSIS")
print("=" * 60)

print("\n🌡️  Weather Conditions Distribution:")
condition_counts = weather_df['weather_condition'].value_counts()
for condition, count in condition_counts.items():
    pct = (count / len(weather_df)) * 100
    print(f"  {condition:12s}: {count} cities ({pct:5.1f}%)")

print("\n⚠️  Weather Severity Distribution:")
severity_counts = weather_df['weather_severity'].value_counts()
for severity in ['Low', 'Medium', 'High']:
    count = severity_counts.get(severity, 0)
    pct = (count / len(weather_df)) * 100
    print(f"  {severity:8s}: {count} cities ({pct:5.1f}%)")

print("\n🌊 Flood Risk Distribution:")
flood_counts = weather_df['flood_risk'].value_counts()
for risk in ['Low', 'Medium', 'High']:
    count = flood_counts.get(risk, 0)
    pct = (count / len(weather_df)) * 100
    print(f"  {risk:8s}: {count} cities ({pct:5.1f}%)")

print("\n📈 Weather Impact Factor Statistics:")
print(f"  Mean:   {weather_df['weather_impact_factor'].mean():.1f}")
print(f"  Median: {weather_df['weather_impact_factor'].median():.1f}")
print(f"  Min:    {weather_df['weather_impact_factor'].min():.1f}")
print(f"  Max:    {weather_df['weather_impact_factor'].max():.1f}")

print("\n⏱️  ETA Buffer Multiplier Statistics:")
print(f"  Mean:   {weather_df['eta_buffer_multiplier'].mean():.2f}x")
print(f"  Median: {weather_df['eta_buffer_multiplier'].median():.2f}x")
print(f"  Range:  {weather_df['eta_buffer_multiplier'].min():.1f}x - {weather_df['eta_buffer_multiplier'].max():.1f}x")

# High impact cities
print("\n🔴 HIGH IMPACT CITIES (Impact >= 70):")
high_impact = weather_df[weather_df['weather_impact_factor'] >= 70]
print(f"  Total: {len(high_impact)} cities")
if len(high_impact) > 0:
    print("\n  Cities requiring dispatch delay:")
    for idx, row in high_impact.iterrows():
        print(f"    - {row['city']}: Impact {row['weather_impact_factor']:.0f}, " +
              f"Severity {row['weather_severity']}, ETA {row['eta_buffer_multiplier']}x")

# Merge with shipment data
print("\n\n📦 SHIPMENT-LEVEL WEATHER IMPACT:")
print("-" * 60)
shipments_weather = shipments.merge(
    weather_df[['city', 'weather_severity', 'weather_impact_factor', 'eta_buffer_multiplier']],
    left_on='destination_city',
    right_on='city',
    how='left'
).drop('city', axis=1)

print(f"✅ Merged weather data with {len(shipments_weather)} shipments")

# Shipments affected by weather
affected_shipments = shipments_weather[shipments_weather['weather_severity'].isin(['Medium', 'High'])]
print(f"\n⚠️  Shipments affected by weather: {len(affected_shipments)} ({len(affected_shipments)/len(shipments)*100:.1f}%)")

delayed_shipments = shipments_weather[shipments_weather['weather_impact_factor'] >= 70]
print(f"🔴 Shipments requiring delay: {len(delayed_shipments)} ({len(delayed_shipments)/len(shipments)*100:.1f}%)")

# Calculate total ETA adjustment
print("\n📊 ETA Adjustment Impact:")
avg_eta_adjustment = (shipments_weather['eta_buffer_multiplier'].mean() - 1.0) * 100
print(f"  Average ETA increase: {avg_eta_adjustment:.1f}%")

high_adjustment = (shipments_weather['eta_buffer_multiplier'] >= 1.5).sum()
print(f"  Shipments with 50%+ delay: {high_adjustment} ({high_adjustment/len(shipments)*100:.1f}%)")

# Sample affected shipments
if len(affected_shipments) > 0:
    print("\n🔎 Sample Weather-Affected Shipments:")
    print("-" * 60)
    sample = affected_shipments[['shipment_id', 'destination_city', 'weather_severity', 
                                  'weather_impact_factor', 'eta_buffer_multiplier']].head(5)
    for idx, row in sample.iterrows():
        print(f"\n  Shipment: {row['shipment_id']}")
        print(f"    Destination: {row['destination_city']}")
        print(f"    Weather Severity: {row['weather_severity']}")
        print(f"    Impact Factor: {row['weather_impact_factor']:.0f}")
        print(f"    ETA Multiplier: {row['eta_buffer_multiplier']:.1f}x")

print("\n" + "=" * 60)
print("✅ WEATHER IMPACT INTEGRATION TEST COMPLETE")
print("=" * 60)
print("\n🎯 Key Achievements:")
print(f"  ✅ Weather impact calculated for {len(cities)} cities")
print(f"  ✅ {len(affected_shipments)} shipments identified as weather-affected")
print(f"  ✅ {len(delayed_shipments)} shipments flagged for delay")
print(f"  ✅ Average ETA adjustment: {avg_eta_adjustment:.1f}%")
print("  ✅ Ready for pre-dispatch decision gate")
print("\n📝 Integration Points:")
print("  → Risk Engine: weather_impact_factor feeds into risk calculation")
print("  → Pre-Dispatch Gate: High impact triggers delay/reschedule")
print("  → Customer Notifications: ETA adjusted based on weather")
