"""
Demo: Human Override System with Real Shipment Data
Shows override in action with realistic scenarios
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from rules.human_override import (
    apply_human_override,
    is_locked,
    get_override_stats,
    OVERRIDE_REASONS
)
from rules.pre_dispatch_gate import pre_dispatch_decision
import pandas as pd

def demo_human_override():
    print("\n" + "="*70)
    print("DEMO: HUMAN OVERRIDE SYSTEM (Step 15)")
    print("="*70)
    
    # Load real shipment data
    print("\n📦 Loading shipment data...")
    shipments = pd.read_csv("Data/shipments.csv")
    
    # Select 3 shipments for demo
    demo_shipments = shipments.head(3)
    
    print(f"✅ Loaded {len(shipments)} shipments")
    print(f"🎯 Demo with 3 shipments\n")
    
    # Scenario 1: Override high-risk shipment to DISPATCH
    print("="*70)
    print("SCENARIO 1: High-Priority Customer Override")
    print("="*70)
    
    shipment_1 = demo_shipments.iloc[0]
    shipment_id_1 = shipment_1['shipment_id']
    
    # Get AI decision (simulated from Step 9)
    risk_score = shipment_1['current_risk_score']
    ai_decision_1 = "DELAY" if risk_score > 50 else "DISPATCH"
    
    print(f"\n📋 Shipment: {shipment_id_1}")
    print(f"📍 Destination: {shipment_1['destination_city']}")
    print(f"📦 Product: {shipment_1['product_name']}")
    print(f"⚠️  Risk Score: {risk_score:.1f}")
    print(f"🤖 AI Decision: {ai_decision_1}")
    print(f"\n💼 Manager Context: VIP customer called, needs urgent delivery")
    print(f"✋ Manager Override: DISPATCH (High priority customer)")
    
    result_1 = apply_human_override(
        shipment_id=shipment_id_1,
        ai_decision=ai_decision_1,
        override_decision="DISPATCH",
        override_reason="High priority customer"
    )
    
    print(f"\n✅ Result: {result_1['status']}")
    print(f"🔒 Final Decision: {result_1['final_decision']}")
    print(f"🔐 Locked: {result_1['locked']}")
    
    # Scenario 2: Manager agrees with AI
    print("\n" + "="*70)
    print("SCENARIO 2: Manager Agrees with AI (No Override)")
    print("="*70)
    
    shipment_2 = demo_shipments.iloc[1]
    shipment_id_2 = shipment_2['shipment_id']
    risk_score_2 = shipment_2['current_risk_score']
    ai_decision_2 = "DISPATCH" if risk_score_2 < 40 else "DELAY"
    
    print(f"\n📋 Shipment: {shipment_id_2}")
    print(f"📍 Destination: {shipment_2['destination_city']}")
    print(f"📦 Product: {shipment_2['product_name']}")
    print(f"⚠️  Risk Score: {risk_score_2:.1f}")
    print(f"🤖 AI Decision: {ai_decision_2}")
    print(f"\n💼 Manager Review: AI assessment looks correct")
    print(f"✋ Manager Decision: {ai_decision_2} (Same as AI)")
    
    result_2 = apply_human_override(
        shipment_id=shipment_id_2,
        ai_decision=ai_decision_2,
        override_decision=ai_decision_2,
        override_reason="Manager experience"
    )
    
    print(f"\n✅ Result: {result_2['status']}")
    print(f"🔒 Final Decision: {result_2['final_decision']}")
    print(f"ℹ️  No override needed - Manager confirms AI")
    
    # Scenario 3: Weather cleared manually
    print("\n" + "="*70)
    print("SCENARIO 3: Weather Cleared (Local Knowledge)")
    print("="*70)
    
    shipment_3 = demo_shipments.iloc[2]
    shipment_id_3 = shipment_3['shipment_id']
    risk_score_3 = shipment_3['current_risk_score']
    ai_decision_3 = "RESCHEDULE"  # Simulated weather delay
    
    print(f"\n📋 Shipment: {shipment_id_3}")
    print(f"📍 Destination: {shipment_3['destination_city']}")
    print(f"📦 Product: {shipment_3['product_name']}")
    print(f"⚠️  Risk Score: {risk_score_3:.1f}")
    print(f"🤖 AI Decision: {ai_decision_3} (weather warning)")
    print(f"\n💼 Manager Context: Just checked - storm passed, roads clear")
    print(f"✋ Manager Override: DISPATCH (Weather cleared manually)")
    
    result_3 = apply_human_override(
        shipment_id=shipment_id_3,
        ai_decision=ai_decision_3,
        override_decision="DISPATCH",
        override_reason="Weather cleared manually"
    )
    
    print(f"\n✅ Result: {result_3['status']}")
    print(f"🔒 Final Decision: {result_3['final_decision']}")
    print(f"🔐 Locked: {result_3['locked']}")
    
    # Test lock mechanism
    print("\n" + "="*70)
    print("TESTING LOCK MECHANISM")
    print("="*70)
    
    print(f"\n🔍 Checking locks...")
    for sid in [shipment_id_1, shipment_id_2, shipment_id_3]:
        locked = is_locked(sid)
        status = "🔒 LOCKED" if locked else "🔓 UNLOCKED"
        print(f"  {sid}: {status}")
    
    # Show override statistics
    print("\n" + "="*70)
    print("OVERRIDE STATISTICS (Learning Loop)")
    print("="*70)
    
    stats = get_override_stats()
    
    print(f"\n📊 Total Overrides: {stats['total_overrides']}")
    print(f"🎯 Most Common Reason: {stats['most_common_reason']}")
    print(f"\n📈 Override Distribution:")
    print(f"  ✅ To DISPATCH: {stats['ai_to_dispatch']}")
    print(f"  ⏸️  To DELAY: {stats['ai_to_delay']}")
    print(f"  🔄 To RESCHEDULE: {stats['ai_to_reschedule']}")
    
    if 'reason_distribution' in stats:
        print(f"\n🔍 Reason Breakdown:")
        for reason, count in stats['reason_distribution'].items():
            print(f"  • {reason}: {count}")
    
    # Show override catalog
    print("\n" + "="*70)
    print("STANDARDIZED OVERRIDE REASONS")
    print("="*70)
    
    print("\n📋 Catalog (prevents random text):")
    for i, reason in enumerate(OVERRIDE_REASONS, 1):
        print(f"  {i}. {reason}")
    
    # Key takeaways
    print("\n" + "="*70)
    print("KEY TAKEAWAYS")
    print("="*70)
    
    print("""
✅ ESTABLISHED:
  • Human authority over AI decisions
  • Lock mechanism prevents AI re-evaluation
  • Full audit trail in logs/override_log.csv
  • Standardized reasons enable learning

🎯 USE CASES:
  • VIP customer urgency
  • Local knowledge AI doesn't have
  • Temporary conditions (road closure)
  • Weather updates not in system
  • Operational priorities

🎓 LEARNING LOOP:
  • Analyze override patterns monthly
  • Identify AI blind spots
  • Add new data sources
  • Reduce override rate over time
  • Target: 20% → 5% in 6 months

🔒 TRUST:
  • AI provides intelligence
  • Human makes final call
  • System logs everything
  • Accountability maintained
    """)
    
    print("="*70)
    print("✅ DEMO COMPLETE: Human Override System Operational")
    print("="*70 + "\n")

if __name__ == "__main__":
    demo_human_override()
