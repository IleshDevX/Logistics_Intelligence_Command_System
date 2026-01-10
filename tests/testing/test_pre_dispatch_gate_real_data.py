"""
Pre-Dispatch Decision Gate - Real Data Integration Test

Tests decision gate with actual shipment data from all three intelligence modules
"""

from ingestion.load_data import load_all_data
from models.risk_engine import calculate_risk_score
from features.address_intelligence import calculate_address_confidence
from features.weather_impact import get_weather_impact
from rules.pre_dispatch_gate import (
    pre_dispatch_decision,
    get_decision_explanation,
    get_action_items
)
import pandas as pd

print("=" * 60)
print("PRE-DISPATCH DECISION GATE - REAL DATA TEST")
print("=" * 60)

# Load data
print("\n📦 Loading datasets...")
shipments, addresses, history, weather_data, resources = load_all_data()
print("✅ Data loaded successfully")

# Process sample shipments through complete pipeline
print("\n🔄 Processing shipments through complete decision pipeline...")
sample_size = 100
sample_shipments = shipments.head(sample_size).copy()
sample_addresses = addresses[addresses['shipment_id'].isin(sample_shipments['shipment_id'])].copy()

# Aggregate weather by city
weather_agg = weather_data.groupby('city').agg({
    'weather_severity': lambda x: x.mode()[0] if len(x.mode()) > 0 else x.iloc[0],
    'weather_impact_factor': 'mean'
}).reset_index()

# Merge data
merged = sample_shipments.merge(sample_addresses, on='shipment_id', how='left')
merged = merged.merge(weather_agg, left_on='destination_city', right_on='city', how='left').drop('city', axis=1)

# Calculate risk scores
print("\n🧮 Calculating risk scores...")
merged['calculated_risk_score'] = merged.apply(
    lambda row: calculate_risk_score(
        weight_kg=row['weight_kg'],
        volumetric_weight=row['volumetric_weight'],
        payment_type=row['payment_type'],
        priority_flag=row['priority_flag'],
        area_type=row['area_type'],
        road_accessibility=row['road_accessibility'],
        address_confidence_score=row['address_confidence_score'],
        weather_severity=row['weather_severity'],
        weather_impact_factor=row['weather_impact_factor']
    ),
    axis=1
)

# Run decision gate for all shipments
print("\n🚦 Running Pre-Dispatch Decision Gate...")
decisions = []
for idx, row in merged.iterrows():
    decision = pre_dispatch_decision(
        risk_score=row['calculated_risk_score'],
        weather_impact_factor=row['weather_impact_factor'],
        address_confidence_score=row['address_confidence_score']
    )
    decisions.append({
        'shipment_id': row['shipment_id'],
        'decision': decision['decision'],
        'reasons': ', '.join(decision['reasons']) if decision['reasons'] else 'All safe',
        'risk_score': decision['risk_score'],
        'weather_impact': decision['weather_impact_factor'],
        'address_confidence': decision['address_confidence_score']
    })

decisions_df = pd.DataFrame(decisions)

print(f"✅ Processed {len(decisions_df)} shipments through decision gate")

# Analysis
print("\n" + "=" * 60)
print("📊 PRE-DISPATCH DECISION GATE ANALYSIS")
print("=" * 60)

print("\n🚦 Decision Distribution:")
decision_counts = decisions_df['decision'].value_counts()
for decision in ['DISPATCH', 'DELAY', 'RESCHEDULE']:
    count = decision_counts.get(decision, 0)
    pct = (count / len(decisions_df)) * 100
    emoji = "✅" if decision == "DISPATCH" else "⏸" if decision == "DELAY" else "🔁"
    print(f"  {emoji} {decision:12s}: {count:3d} shipments ({pct:5.1f}%)")

print("\n⚠️  Most Common Blocking Reasons:")
all_reasons = []
for reasons_str in decisions_df['reasons']:
    if reasons_str != 'All safe':
        all_reasons.extend([r.strip() for r in reasons_str.split(',')])

if all_reasons:
    reason_counts = pd.Series(all_reasons).value_counts()
    for reason, count in reason_counts.items():
        pct = (count / len(decisions_df)) * 100
        print(f"  {reason}: {count} occurrences ({pct:.1f}%)")
else:
    print("  No blocking reasons found")

print("\n📈 Score Distributions (for flagged shipments):")
delay_or_reschedule = decisions_df[decisions_df['decision'] != 'DISPATCH']
if len(delay_or_reschedule) > 0:
    print(f"  Average Risk Score: {delay_or_reschedule['risk_score'].mean():.1f}")
    print(f"  Average Weather Impact: {delay_or_reschedule['weather_impact'].mean():.1f}")
    print(f"  Average Address Confidence: {delay_or_reschedule['address_confidence'].mean():.1f}")
else:
    print("  No flagged shipments")

# Show example decisions
print("\n" + "=" * 60)
print("📋 EXAMPLE DECISIONS")
print("=" * 60)

# Show one of each decision type
for decision_type in ['DISPATCH', 'DELAY', 'RESCHEDULE']:
    example = decisions_df[decisions_df['decision'] == decision_type].head(1)
    if len(example) > 0:
        row = example.iloc[0]
        print(f"\n{decision_type} Example:")
        print(f"  Shipment ID: {row['shipment_id']}")
        print(f"  Risk Score: {row['risk_score']:.1f}")
        print(f"  Weather Impact: {row['weather_impact']:.1f}")
        print(f"  Address Confidence: {row['address_confidence']:.1f}")
        print(f"  Reasons: {row['reasons']}")
        
        # Get full decision object for action items
        full_decision = pre_dispatch_decision(
            risk_score=row['risk_score'],
            weather_impact_factor=row['weather_impact'],
            address_confidence_score=row['address_confidence']
        )
        actions = get_action_items(full_decision)
        print(f"  Action Items:")
        for action in actions[:3]:  # Show first 3 actions
            print(f"    - {action}")

# System Impact Assessment
print("\n" + "=" * 60)
print("🎯 SYSTEM IMPACT ASSESSMENT")
print("=" * 60)

dispatch_rate = (decision_counts.get('DISPATCH', 0) / len(decisions_df)) * 100
intervention_rate = 100 - dispatch_rate

print(f"Dispatch Rate: {dispatch_rate:.1f}%")
print(f"Intervention Rate: {intervention_rate:.1f}%")
print(f"")
print(f"Interpretation:")
if dispatch_rate > 80:
    print(f"  ✅ System is allowing most shipments (low false positive rate)")
elif dispatch_rate > 60:
    print(f"  ⚡ Moderate intervention - system is cautious")
else:
    print(f"  ⚠️  High intervention - review thresholds if too restrictive")

print("\n" + "=" * 60)
print("✅ PRE-DISPATCH DECISION GATE: INTEGRATED & OPERATIONAL")
print("=" * 60)
print("\nKey Achievement:")
print("  'Our system does not blindly dispatch shipments.'")
print("  'Every shipment passes through a pre-dispatch decision gate'")
print("  'that evaluates risk, weather, and address reliability'")
print("  'before allowing execution.'")
print("=" * 60)
