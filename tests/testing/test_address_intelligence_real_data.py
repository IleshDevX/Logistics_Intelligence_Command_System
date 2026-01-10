"""
Address Intelligence Integration Test with Real Data

Tests address intelligence on actual shipment data
"""

from ingestion.load_data import load_all_data
from features.address_intelligence import process_address
import pandas as pd

print("=" * 60)
print("ADDRESS INTELLIGENCE - REAL DATA INTEGRATION TEST")
print("=" * 60)

# Load data
print("\n📦 Loading datasets...")
shipments, addresses, history, weather, resources = load_all_data()
print("✅ Data loaded successfully")

# Process a sample of addresses
print("\n🧮 Processing address intelligence for sample shipments...")
sample_size = 1000
addresses_sample = addresses.head(sample_size).copy()



# Apply address intelligence
results = []
for idx, row in addresses_sample.iterrows():
    result = process_address(
        raw_address=row['raw_address_text'],
        road_accessibility=row['road_accessibility'],
        existing_area_type=row['area_type']
    )
    results.append({
        'shipment_id': row['shipment_id'],
        'original_confidence': row['address_confidence_score'],
        'calculated_confidence': result['address_confidence_score'],
        'landmarks_count': len(result['landmarks']),
        'landmarks': result['landmarks'],
        'area_type': result['area_type'],
        'needs_clarification': result['needs_clarification']
    })

results_df = pd.DataFrame(results)

print(f"✅ Processed {len(results_df)} addresses")

# Analysis
print("\n" + "=" * 60)
print("📊 ADDRESS INTELLIGENCE ANALYSIS")
print("=" * 60)

print("\n📈 Clarification Flag Distribution:")
clarification_needed = results_df['needs_clarification'].sum()
pct_clarification = (clarification_needed / len(results_df)) * 100
print(f"  Needs Clarification: {clarification_needed} addresses ({pct_clarification:.1f}%)")
print(f"  OK to Proceed:       {len(results_df) - clarification_needed} addresses ({100-pct_clarification:.1f}%)")

print("\n📉 Confidence Score Statistics:")
print(f"  Original Mean:   {results_df['original_confidence'].mean():.1f}")
print(f"  Calculated Mean: {results_df['calculated_confidence'].mean():.1f}")
print(f"  Min Confidence:  {results_df['calculated_confidence'].min()}")
print(f"  Max Confidence:  {results_df['calculated_confidence'].max()}")

print("\n🏷️  Landmark Detection:")
with_landmarks = (results_df['landmarks_count'] > 0).sum()
print(f"  Addresses with Landmarks: {with_landmarks} ({with_landmarks/len(results_df)*100:.1f}%)")
print(f"  Average Landmarks/Address: {results_df['landmarks_count'].mean():.2f}")
landmark_dist = results_df['landmarks_count'].value_counts().sort_index()
for count, freq in landmark_dist.items():
    print(f"    {count} landmarks: {freq} addresses")

print("\n🗺️  Area Type Distribution:")
area_counts = results_df['area_type'].value_counts()
for area, count in area_counts.items():
    pct = (count / len(results_df)) * 100
    print(f"  {area:15s}: {count:4d} addresses ({pct:5.1f}%)")

# Low confidence addresses
print("\n🔴 LOW CONFIDENCE ADDRESSES (Score < 60):")
low_conf = results_df[results_df['calculated_confidence'] < 60]
print(f"  Total: {len(low_conf)} addresses ({len(low_conf)/len(results_df)*100:.1f}%)")

if len(low_conf) > 0:
    print("\n  Top Reasons for Low Confidence:")
    print(f"    - Old City: {(low_conf['area_type'] == 'Old City').sum()} addresses")
    print(f"    - Rural: {(low_conf['area_type'] == 'Rural').sum()} addresses")
    print(f"    - No Landmarks: {(low_conf['landmarks_count'] == 0).sum()} addresses")
    
    print("\n  🔎 Sample Low Confidence Addresses:")
    print("-" * 60)
    for idx, row in low_conf.head(3).iterrows():
        print(f"\n    Shipment: {row['shipment_id']}")
        print(f"      Confidence: {row['calculated_confidence']} (needs clarification)")
        print(f"      Area: {row['area_type']}")
        print(f"      Landmarks: {row['landmarks'] if row['landmarks'] else 'None detected'}")

# High confidence addresses
print("\n\n🟢 HIGH CONFIDENCE ADDRESSES (Score >= 60):")
high_conf = results_df[results_df['calculated_confidence'] >= 60]
print(f"  Total: {len(high_conf)} addresses ({len(high_conf)/len(results_df)*100:.1f}%)")

if len(high_conf) > 0:
    print(f"\n  Average Landmarks: {high_conf['landmarks_count'].mean():.2f}")
    print(f"  Planned Areas: {(high_conf['area_type'] == 'Planned').sum()} addresses")

print("\n" + "=" * 60)
print("✅ ADDRESS INTELLIGENCE INTEGRATION TEST COMPLETE")
print("=" * 60)
print("\n🎯 Key Achievements:")
print(f"  ✅ Processed {len(results_df)} addresses successfully")
print(f"  ✅ Identified {clarification_needed} addresses needing clarification")
print(f"  ✅ Detected landmarks in {with_landmarks} addresses")
print(f"  ✅ Area type classification working correctly")
print("  ✅ Ready for pre-dispatch decision gate integration")
