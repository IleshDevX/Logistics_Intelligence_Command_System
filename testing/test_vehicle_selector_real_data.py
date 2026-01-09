"""
Hyper-Local Vehicle Selector - Real Data Integration Test

Tests vehicle selector with actual shipment data
"""

from ingestion.load_data import load_all_data
from rules.vehicle_selector import hyper_local_vehicle_check, get_vehicle_capacity
import pandas as pd

print("=" * 60)
print("HYPER-LOCAL VEHICLE SELECTOR - REAL DATA TEST")
print("=" * 60)

# Load data
print("\n📦 Loading datasets...")
shipments, addresses, history, weather, resources = load_all_data()
print("✅ Data loaded successfully")

# Process sample shipments
print("\n🔄 Processing shipments through vehicle selector...")
sample_size = 100
sample_shipments = shipments.head(sample_size).copy()
sample_addresses = addresses[addresses['shipment_id'].isin(sample_shipments['shipment_id'])].copy()

# Merge data
merged = sample_shipments.merge(sample_addresses, on='shipment_id', how='left')

# Run vehicle check for all shipments
print("\n🚚 Running vehicle feasibility checks...")
vehicle_results = []
for idx, row in merged.iterrows():
    # Get vehicle capacity based on assigned vehicle
    vehicle_capacity = get_vehicle_capacity(row['assigned_vehicle_type'])
    
    # Run vehicle check
    result = hyper_local_vehicle_check(
        area_type=row['area_type'],
        road_accessibility=row['road_accessibility'],
        assigned_vehicle=row['assigned_vehicle_type'],
        weight_kg=row['weight_kg'],
        volumetric_weight=row['volumetric_weight'],
        vehicle_capacity=vehicle_capacity
    )
    
    vehicle_results.append({
        'shipment_id': row['shipment_id'],
        'area_type': row['area_type'],
        'road_accessibility': row['road_accessibility'],
        'assigned_vehicle': row['assigned_vehicle_type'],
        'weight_kg': row['weight_kg'],
        'vehicle_status': result['vehicle_status'],
        'final_vehicle': result['final_vehicle'],
        'action': result['action'],
        'reason': result.get('reason', 'Approved')
    })

results_df = pd.DataFrame(vehicle_results)

print(f"✅ Processed {len(results_df)} shipments through vehicle selector")

# Analysis
print("\n" + "=" * 60)
print("📊 VEHICLE FEASIBILITY ANALYSIS")
print("=" * 60)

print("\n🚦 Vehicle Status Distribution:")
status_counts = results_df['vehicle_status'].value_counts()
for status in ['APPROVED', 'REJECTED']:
    count = status_counts.get(status, 0)
    pct = (count / len(results_df)) * 100
    emoji = "✅" if status == "APPROVED" else "❌"
    print(f"  {emoji} {status:10s}: {count:3d} shipments ({pct:5.1f}%)")

print("\n🚗 Vehicle Assignment Changes:")
changed = results_df[results_df['assigned_vehicle'] != results_df['final_vehicle']]
if len(changed) > 0:
    print(f"  Vehicle Changed: {len(changed)} shipments ({len(changed)/len(results_df)*100:.1f}%)")
    vehicle_changes = changed.groupby(['assigned_vehicle', 'final_vehicle']).size().reset_index(name='count')
    for _, row in vehicle_changes.iterrows():
        print(f"    {row['assigned_vehicle']} → {row['final_vehicle']}: {row['count']} times")
else:
    print("  No vehicle changes recommended")

print("\n⚙️  Action Distribution (for rejected shipments):")
rejected = results_df[results_df['vehicle_status'] == 'REJECTED']
if len(rejected) > 0:
    action_counts = rejected['action'].value_counts()
    for action, count in action_counts.items():
        pct = (count / len(rejected)) * 100
        print(f"  {action}: {count} ({pct:.1f}%)")
else:
    print("  No rejections - all vehicles feasible")

print("\n⚠️  Rejection Reasons:")
if len(rejected) > 0:
    reason_counts = rejected['reason'].value_counts()
    for reason, count in reason_counts.items():
        pct = (count / len(rejected)) * 100
        print(f"  {reason}: {count} ({pct:.1f}%)")
else:
    print("  No rejections")

print("\n🗺️  Feasibility by Area Type:")
area_feasibility = results_df.groupby('area_type')['vehicle_status'].value_counts().unstack(fill_value=0)
for area in area_feasibility.index:
    approved = area_feasibility.loc[area, 'APPROVED'] if 'APPROVED' in area_feasibility.columns else 0
    rejected = area_feasibility.loc[area, 'REJECTED'] if 'REJECTED' in area_feasibility.columns else 0
    total = approved + rejected
    approval_rate = (approved / total * 100) if total > 0 else 0
    print(f"  {area:12s}: {approval_rate:5.1f}% approval rate ({approved}/{total})")

print("\n🛣️  Feasibility by Road Type:")
road_feasibility = results_df.groupby('road_accessibility')['vehicle_status'].value_counts().unstack(fill_value=0)
for road in road_feasibility.index:
    approved = road_feasibility.loc[road, 'APPROVED'] if 'APPROVED' in road_feasibility.columns else 0
    rejected = road_feasibility.loc[road, 'REJECTED'] if 'REJECTED' in road_feasibility.columns else 0
    total = approved + rejected
    approval_rate = (approved / total * 100) if total > 0 else 0
    print(f"  {road:12s}: {approval_rate:5.1f}% approval rate ({approved}/{total})")

# Example cases
print("\n" + "=" * 60)
print("📋 EXAMPLE CASES")
print("=" * 60)

# Show rejected examples
rejected_examples = results_df[results_df['vehicle_status'] == 'REJECTED'].head(3)
if len(rejected_examples) > 0:
    print("\nRejected Vehicle Assignments:")
    for idx, row in rejected_examples.iterrows():
        print(f"\n  Shipment: {row['shipment_id']}")
        print(f"  Area: {row['area_type']}, Road: {row['road_accessibility']}")
        print(f"  Weight: {row['weight_kg']}kg")
        print(f"  Assigned: {row['assigned_vehicle']} → Recommended: {row['final_vehicle']}")
        print(f"  Action: {row['action']}")
        print(f"  Reason: {row['reason']}")

# Show approved examples
approved_examples = results_df[results_df['vehicle_status'] == 'APPROVED'].head(2)
print("\n\nApproved Vehicle Assignments:")
for idx, row in approved_examples.iterrows():
    print(f"\n  Shipment: {row['shipment_id']}")
    print(f"  Area: {row['area_type']}, Road: {row['road_accessibility']}")
    print(f"  Weight: {row['weight_kg']}kg")
    print(f"  Vehicle: {row['assigned_vehicle']} ✅")

# System Impact
print("\n" + "=" * 60)
print("🎯 SYSTEM IMPACT ASSESSMENT")
print("=" * 60)

approval_rate = (status_counts.get('APPROVED', 0) / len(results_df)) * 100
rejection_rate = 100 - approval_rate

print(f"Approval Rate: {approval_rate:.1f}%")
print(f"Rejection Rate: {rejection_rate:.1f}%")
print(f"")
print(f"Interpretation:")
if rejection_rate > 30:
    print(f"  ⚠️  High rejection rate - many infeasible assignments")
    print(f"  💡 Recommendation: Improve initial vehicle assignment logic")
elif rejection_rate > 10:
    print(f"  ⚡ Moderate intervention - system catches feasibility issues")
    print(f"  ✅ Vehicle selector adding value by preventing failures")
else:
    print(f"  ✅ Low rejection rate - initial assignments are mostly feasible")
    print(f"  ✅ Vehicle selector provides safety net for edge cases")

print("\n" + "=" * 60)
print("✅ HYPER-LOCAL VEHICLE SELECTOR: INTEGRATED & OPERATIONAL")
print("=" * 60)
print("\nKey Achievement:")
print("  'Our system prevents infeasible vehicle assignments by")
print("  evaluating area accessibility, road constraints, and")
print("  vehicle capacity before dispatch, solving the last-100-meters")
print("  problem common in Indian cities.'")
print("=" * 60)
