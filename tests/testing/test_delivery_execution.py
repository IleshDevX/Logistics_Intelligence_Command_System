"""
Test Suite for Step 16: Delivery Execution & Live Tracking Simulation

Tests:
1. Single delivery simulation
2. Late packing detection
3. Delivery delay detection
4. Alert triggering
5. Status tracking
6. Execution statistics
7. Failed delivery attempts
8. Bulk simulation
"""

import os
import sys
import pandas as pd
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from execution.delivery_simulator import (
    simulate_delivery,
    check_late_packing,
    check_delivery_delay,
    get_current_status,
    trigger_execution_alert,
    run_execution_flow,
    get_tracking_history,
    get_execution_stats,
    simulate_failed_delivery_attempt,
    bulk_simulate_deliveries,
    TRACKING_LOG
)

def cleanup_test_data():
    """Remove test tracking log if exists"""
    if os.path.exists(TRACKING_LOG):
        os.remove(TRACKING_LOG)

def test_basic_delivery_simulation():
    """Test 1: Basic delivery simulation without delays"""
    print("\n" + "="*60)
    print("TEST 1: Basic Delivery Simulation")
    print("="*60)
    
    cleanup_test_data()
    
    events = simulate_delivery("SHP_TEST_001")
    
    assert len(events) > 0, "Should create tracking events"
    
    # Check status progression
    statuses = [e['status'] for e in events]
    assert "CREATED" in statuses, "Should have CREATED status"
    assert "DELIVERED" in statuses, "Should have DELIVERED status"
    
    print(f"✅ Created {len(events)} tracking events")
    print(f"✅ Status progression: {' → '.join(statuses)}")
    
    return True

def test_late_packing_detection():
    """Test 2: Late packing detection and alert"""
    print("\n" + "="*60)
    print("TEST 2: Late Packing Detection")
    print("="*60)
    
    cleanup_test_data()
    
    # Simulate with packing delay
    events = simulate_delivery("SHP_TEST_002", packing_delay=True)
    
    # Check if late packing detected
    is_late = check_late_packing("SHP_TEST_002")
    
    assert is_late, "Should detect late packing"
    
    # Check for PACKING_DELAY status
    statuses = [e['status'] for e in events]
    assert "PACKING_DELAY" in statuses, "Should have PACKING_DELAY status"
    
    print("✅ Late packing detected")
    print(f"✅ Statuses: {statuses}")
    
    return True

def test_delivery_delay_detection():
    """Test 3: Delivery delay detection"""
    print("\n" + "="*60)
    print("TEST 3: Delivery Delay Detection")
    print("="*60)
    
    cleanup_test_data()
    
    # Simulate with delivery delay
    events = simulate_delivery("SHP_TEST_003", delivery_delay=True)
    
    # Check if delivery delay detected
    is_delayed = check_delivery_delay("SHP_TEST_003")
    
    assert is_delayed, "Should detect delivery delay"
    
    # Check for DELIVERY_DELAY status
    statuses = [e['status'] for e in events]
    assert "DELIVERY_DELAY" in statuses, "Should have DELIVERY_DELAY status"
    
    print("✅ Delivery delay detected")
    print(f"✅ Statuses: {statuses}")
    
    return True

def test_alert_triggering():
    """Test 4: Alert triggering for different scenarios"""
    print("\n" + "="*60)
    print("TEST 4: Alert Triggering")
    print("="*60)
    
    # Test packing delay alert
    print("\n--- Packing Delay Alert ---")
    alert1 = trigger_execution_alert("SHP_TEST_004", "PACKING_DELAY")
    assert alert1['ops_notified'], "Should notify Ops for packing delay"
    
    # Test delivery delay alert
    print("\n--- Delivery Delay Alert ---")
    alert2 = trigger_execution_alert("SHP_TEST_005", "DELIVERY_DELAY")
    assert alert2['customer_notified'], "Should notify Customer for delivery delay"
    
    # Test failed attempt alert
    print("\n--- Failed Attempt Alert ---")
    alert3 = trigger_execution_alert("SHP_TEST_006", "FAILED_ATTEMPT")
    assert alert3['customer_notified'], "Should notify Customer for failed attempt"
    
    print("\n✅ All alert types working")
    
    return True

def test_status_tracking():
    """Test 5: Status tracking and history"""
    print("\n" + "="*60)
    print("TEST 5: Status Tracking")
    print("="*60)
    
    cleanup_test_data()
    
    # Simulate delivery
    simulate_delivery("SHP_TEST_007")
    
    # Get current status
    status = get_current_status("SHP_TEST_007")
    assert status == "DELIVERED", f"Final status should be DELIVERED, got {status}"
    
    # Get tracking history
    history = get_tracking_history("SHP_TEST_007")
    assert len(history) > 0, "Should have tracking history"
    
    print(f"✅ Final status: {status}")
    print(f"✅ Tracking events: {len(history)}")
    print("\nTracking History:")
    print(history[['status', 'timestamp', 'remarks']].to_string(index=False))
    
    return True

def test_execution_flow():
    """Test 6: Complete execution flow"""
    print("\n" + "="*60)
    print("TEST 6: Complete Execution Flow")
    print("="*60)
    
    cleanup_test_data()
    
    # Normal flow
    print("\n--- Normal Execution ---")
    result1 = run_execution_flow("SHP_TEST_008")
    assert result1['execution_completed'], "Should complete normally"
    assert result1['alerts_triggered'] == 0, "Should have no alerts"
    
    # Flow with packing delay
    print("\n--- With Packing Delay ---")
    result2 = run_execution_flow("SHP_TEST_009", packing_delay=True)
    assert result2['alerts_triggered'] > 0, "Should trigger alerts"
    
    # Flow with delivery delay
    print("\n--- With Delivery Delay ---")
    result3 = run_execution_flow("SHP_TEST_010", delivery_delay=True)
    assert result3['alerts_triggered'] > 0, "Should trigger alerts"
    
    # Flow with both delays
    print("\n--- With Both Delays ---")
    result4 = run_execution_flow("SHP_TEST_011", packing_delay=True, delivery_delay=True)
    assert result4['alerts_triggered'] >= 2, "Should trigger multiple alerts"
    
    print(f"\n✅ Normal execution: {result1['total_events']} events")
    print(f"✅ With delays: {result4['total_events']} events, {result4['alerts_triggered']} alerts")
    
    return True

def test_execution_statistics():
    """Test 7: Execution statistics for learning loop"""
    print("\n" + "="*60)
    print("TEST 7: Execution Statistics")
    print("="*60)
    
    cleanup_test_data()
    
    # Simulate multiple deliveries
    run_execution_flow("SHP_STAT_001")
    run_execution_flow("SHP_STAT_002", packing_delay=True)
    run_execution_flow("SHP_STAT_003", delivery_delay=True)
    run_execution_flow("SHP_STAT_004")
    
    # Get statistics
    stats = get_execution_stats()
    
    assert stats['total_shipments'] == 4, "Should track 4 shipments"
    assert stats['delivered_count'] == 4, "All should be delivered"
    assert stats['packing_delays'] > 0, "Should have packing delays"
    assert stats['delivery_delays'] > 0, "Should have delivery delays"
    
    print(f"✅ Total shipments: {stats['total_shipments']}")
    print(f"✅ Delivered: {stats['delivered_count']} ({stats['delivery_rate']:.1f}%)")
    print(f"✅ Packing delays: {stats['packing_delays']}")
    print(f"✅ Delivery delays: {stats['delivery_delays']}")
    print(f"✅ Total delays: {stats['total_delays']}")
    
    return True

def test_failed_delivery_attempt():
    """Test 8: Failed delivery attempt handling"""
    print("\n" + "="*60)
    print("TEST 8: Failed Delivery Attempt")
    print("="*60)
    
    cleanup_test_data()
    
    # Simulate normal delivery up to OUT_FOR_DELIVERY
    simulate_delivery("SHP_FAIL_001")
    
    # Simulate failed attempt
    print("\n--- Simulating Failed Attempt ---")
    simulate_failed_delivery_attempt("SHP_FAIL_001", "Customer not at home")
    
    # Check history
    history = get_tracking_history("SHP_FAIL_001")
    statuses = history['status'].tolist()
    
    assert "FAILED_ATTEMPT" in statuses, "Should have FAILED_ATTEMPT status"
    assert "RE_ATTEMPT_SCHEDULED" in statuses, "Should schedule re-attempt"
    
    print("✅ Failed attempt logged")
    print("✅ Re-attempt scheduled")
    
    return True

def test_bulk_simulation():
    """Test 9: Bulk delivery simulation"""
    print("\n" + "="*60)
    print("TEST 9: Bulk Delivery Simulation")
    print("="*60)
    
    cleanup_test_data()
    
    # Simulate 20 deliveries with 30% delay probability
    print("\n--- Simulating 20 Deliveries ---")
    results = bulk_simulate_deliveries(count=20, delay_probability=0.3)
    
    assert len(results) == 20, "Should simulate 20 deliveries"
    
    # Count outcomes
    completed = sum(1 for r in results if r['execution_completed'])
    with_alerts = sum(1 for r in results if r['alerts_triggered'] > 0)
    
    # Get final stats
    stats = get_execution_stats()
    
    print(f"\n✅ Simulated: {len(results)} deliveries")
    print(f"✅ Completed: {completed}")
    print(f"✅ With alerts: {with_alerts}")
    print(f"✅ Delivery rate: {stats['delivery_rate']:.1f}%")
    print(f"✅ Total delays: {stats['total_delays']}")
    
    return True

def test_tracking_log_structure():
    """Test 10: Tracking log structure validation"""
    print("\n" + "="*60)
    print("TEST 10: Tracking Log Structure")
    print("="*60)
    
    cleanup_test_data()
    
    # Generate some data
    run_execution_flow("SHP_STRUCT_001")
    
    # Check log structure
    df = pd.read_csv(TRACKING_LOG)
    
    required_columns = ['shipment_id', 'status', 'timestamp', 'remarks']
    for col in required_columns:
        assert col in df.columns, f"Should have {col} column"
    
    # Check timestamp format
    try:
        pd.to_datetime(df['timestamp'])
        timestamp_valid = True
    except:
        timestamp_valid = False
    
    assert timestamp_valid, "Timestamps should be valid ISO format"
    
    print(f"✅ All required columns present: {required_columns}")
    print(f"✅ Timestamp format: ISO 8601")
    print(f"✅ Total events logged: {len(df)}")
    
    return True

def run_all_tests():
    """Run complete test suite"""
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + "  STEP 16: DELIVERY EXECUTION - TEST SUITE  ".center(58) + "║")
    print("╚" + "="*58 + "╝")
    
    tests = [
        ("Basic Delivery Simulation", test_basic_delivery_simulation),
        ("Late Packing Detection", test_late_packing_detection),
        ("Delivery Delay Detection", test_delivery_delay_detection),
        ("Alert Triggering", test_alert_triggering),
        ("Status Tracking", test_status_tracking),
        ("Complete Execution Flow", test_execution_flow),
        ("Execution Statistics", test_execution_statistics),
        ("Failed Delivery Attempt", test_failed_delivery_attempt),
        ("Bulk Simulation", test_bulk_simulation),
        ("Tracking Log Structure", test_tracking_log_structure)
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ FAILED: {name}")
            print(f"   Error: {e}")
            failed += 1
        except Exception as e:
            print(f"\n❌ ERROR: {name}")
            print(f"   Exception: {e}")
            failed += 1
    
    # Final summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Total Tests: {len(tests)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Success Rate: {(passed/len(tests)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n✅ STEP 16 VALIDATION COMPLETE")
        print("\nFeatures Validated:")
        print("  ✓ Shipment status updates")
        print("  ✓ Live-like tracking events")
        print("  ✓ Late packing detection")
        print("  ✓ Delivery delay detection")
        print("  ✓ Ops & customer alerts")
        print("  ✓ Execution logging")
        print("  ✓ Failed delivery handling")
        print("  ✓ Bulk simulation")
        print("  ✓ Statistics for learning loop")
    else:
        print(f"\n⚠️ {failed} test(s) failed. Review output above.")
    
    print("="*60)

if __name__ == "__main__":
    run_all_tests()
