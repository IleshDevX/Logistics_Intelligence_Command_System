"""
Test Suite for Step 18: Learning Loop (Daily Improvement Engine)
================================================================

Tests:
1. Risk weight updates (increase/decrease logic)
2. Address confidence improvement
3. Override effectiveness analysis
4. Learning statistics generation
5. Complete learning loop execution
6. Weight evolution tracking
7. Learning history logging
8. Edge cases (no data, insufficient data)
"""

import os
import json
import pandas as pd
import shutil
from datetime import datetime
from learning.learning_loop import (
    load_risk_weights,
    save_risk_weights,
    update_risk_weights,
    improve_address_scoring,
    analyze_override_effectiveness,
    get_learning_statistics,
    run_learning_loop,
    get_learning_history,
    get_weight_evolution
)


def setup_test_environment():
    """Set up test data for learning loop."""
    # Backup existing files
    if os.path.exists("configs/risk_weights.json"):
        shutil.copy("configs/risk_weights.json", "configs/risk_weights_backup.json")
    if os.path.exists("logs/eod_summary.csv"):
        shutil.copy("logs/eod_summary.csv", "logs/eod_summary_backup.csv")
    if os.path.exists("logs/learning_history.csv"):
        shutil.copy("logs/learning_history.csv", "logs/learning_history_backup.csv")
    
    # Create test EOD data
    test_eod = pd.DataFrame([
        # High-risk failures (should increase weights)
        {
            "shipment_id": "TEST_HR_001",
            "predicted_risk_score": 75,
            "predicted_risk_bucket": "HIGH",
            "predicted_decision": "DELAY",
            "actual_status": "FAILED",
            "delay_minutes": 0,
            "override_flag": False,
            "mismatch_flag": True,
            "prediction_accuracy": 20,
            "was_successful": False,
            "had_delay": False,
            "ai_was_cautious": True
        },
        {
            "shipment_id": "TEST_HR_002",
            "predicted_risk_score": 85,
            "predicted_risk_bucket": "HIGH",
            "predicted_decision": "RESCHEDULE",
            "actual_status": "FAILED",
            "delay_minutes": 0,
            "override_flag": False,
            "mismatch_flag": True,
            "prediction_accuracy": 80,
            "was_successful": False,
            "had_delay": False,
            "ai_was_cautious": True
        },
        # Low-risk successes (should decrease weights)
        {
            "shipment_id": "TEST_LR_001",
            "predicted_risk_score": 15,
            "predicted_risk_bucket": "LOW",
            "predicted_decision": "DISPATCH",
            "actual_status": "DELIVERED",
            "delay_minutes": 0,
            "override_flag": False,
            "mismatch_flag": False,
            "prediction_accuracy": 100,
            "was_successful": True,
            "had_delay": False,
            "ai_was_cautious": False
        },
        {
            "shipment_id": "TEST_LR_002",
            "predicted_risk_score": 20,
            "predicted_risk_bucket": "LOW",
            "predicted_decision": "DISPATCH",
            "actual_status": "DELIVERED",
            "delay_minutes": 0,
            "override_flag": False,
            "mismatch_flag": False,
            "prediction_accuracy": 100,
            "was_successful": True,
            "had_delay": False,
            "ai_was_cautious": False
        },
        {
            "shipment_id": "TEST_LR_003",
            "predicted_risk_score": 25,
            "predicted_risk_bucket": "LOW",
            "predicted_decision": "DISPATCH",
            "actual_status": "DELIVERED",
            "delay_minutes": 0,
            "override_flag": False,
            "mismatch_flag": False,
            "prediction_accuracy": 100,
            "was_successful": True,
            "had_delay": False,
            "ai_was_cautious": False
        },
        {
            "shipment_id": "TEST_LR_004",
            "predicted_risk_score": 28,
            "predicted_risk_bucket": "LOW",
            "predicted_decision": "DISPATCH",
            "actual_status": "DELIVERED",
            "delay_minutes": 0,
            "override_flag": False,
            "mismatch_flag": False,
            "prediction_accuracy": 100,
            "was_successful": True,
            "had_delay": False,
            "ai_was_cautious": False
        },
        {
            "shipment_id": "TEST_LR_005",
            "predicted_risk_score": 22,
            "predicted_risk_bucket": "LOW",
            "predicted_decision": "DISPATCH",
            "actual_status": "DELIVERED",
            "delay_minutes": 0,
            "override_flag": False,
            "mismatch_flag": False,
            "prediction_accuracy": 100,
            "was_successful": True,
            "had_delay": False,
            "ai_was_cautious": False
        },
        {
            "shipment_id": "TEST_LR_006",
            "predicted_risk_score": 18,
            "predicted_risk_bucket": "LOW",
            "predicted_decision": "DISPATCH",
            "actual_status": "DELIVERED",
            "delay_minutes": 0,
            "override_flag": False,
            "mismatch_flag": False,
            "prediction_accuracy": 100,
            "was_successful": True,
            "had_delay": False,
            "ai_was_cautious": False
        },
        # Successful overrides
        {
            "shipment_id": "TEST_OVR_001",
            "predicted_risk_score": 55,
            "predicted_risk_bucket": "MEDIUM",
            "predicted_decision": "DELAY",
            "actual_status": "DELIVERED",
            "delay_minutes": 0,
            "override_flag": True,
            "override_reason": "Manager experience",
            "mismatch_flag": False,
            "prediction_accuracy": 80,
            "was_successful": True,
            "had_delay": False,
            "ai_was_cautious": True
        },
        {
            "shipment_id": "TEST_OVR_002",
            "predicted_risk_score": 50,
            "predicted_risk_bucket": "MEDIUM",
            "predicted_decision": "DELAY",
            "actual_status": "DELIVERED",
            "delay_minutes": 0,
            "override_flag": True,
            "override_reason": "High priority customer",
            "mismatch_flag": False,
            "prediction_accuracy": 80,
            "was_successful": True,
            "had_delay": False,
            "ai_was_cautious": True
        },
        # Failed override
        {
            "shipment_id": "TEST_OVR_003",
            "predicted_risk_score": 60,
            "predicted_risk_bucket": "MEDIUM",
            "predicted_decision": "DELAY",
            "actual_status": "FAILED",
            "delay_minutes": 0,
            "override_flag": True,
            "override_reason": "Business pressure",
            "mismatch_flag": False,
            "prediction_accuracy": 100,
            "was_successful": False,
            "had_delay": False,
            "ai_was_cautious": True
        },
        # Missed risk (DISPATCH but failed)
        {
            "shipment_id": "TEST_MISS_001",
            "predicted_risk_score": 25,
            "predicted_risk_bucket": "LOW",
            "predicted_decision": "DISPATCH",
            "actual_status": "FAILED",
            "delay_minutes": 0,
            "override_flag": False,
            "mismatch_flag": True,
            "prediction_accuracy": 20,
            "was_successful": False,
            "had_delay": False,
            "ai_was_cautious": False
        }
    ])
    
    test_eod.to_csv("logs/eod_summary.csv", index=False)
    
    # Create test address data
    test_addresses = pd.DataFrame([
        # Low confidence but successful
        {"shipment_id": "TEST_LR_001", "address_confidence_score": 45, "area_type": "Urban"},
        {"shipment_id": "TEST_LR_002", "address_confidence_score": 55, "area_type": "Urban"},
        {"shipment_id": "TEST_LR_003", "address_confidence_score": 50, "area_type": "Suburban"},
        # High confidence but failed
        {"shipment_id": "TEST_HR_001", "address_confidence_score": 85, "area_type": "Rural"},
        # Normal
        {"shipment_id": "TEST_HR_002", "address_confidence_score": 70, "area_type": "Urban"},
        {"shipment_id": "TEST_LR_004", "address_confidence_score": 75, "area_type": "Urban"},
        {"shipment_id": "TEST_LR_005", "address_confidence_score": 80, "area_type": "Suburban"},
        {"shipment_id": "TEST_LR_006", "address_confidence_score": 78, "area_type": "Urban"},
        {"shipment_id": "TEST_OVR_001", "address_confidence_score": 60, "area_type": "Urban"},
        {"shipment_id": "TEST_OVR_002", "address_confidence_score": 65, "area_type": "Suburban"},
        {"shipment_id": "TEST_OVR_003", "address_confidence_score": 55, "area_type": "Rural"},
        {"shipment_id": "TEST_MISS_001", "address_confidence_score": 90, "area_type": "Urban"}
    ])
    
    test_addresses.to_csv("data/addresses.csv", index=False)
    
    # Initialize fresh weights
    initial_weights = {
        "cod_risk": 15,
        "address_risk": 15,
        "weather_risk": 20,
        "area_risk": 15,
        "weight_risk": 10,
        "last_updated": datetime.now().isoformat(),
        "update_count": 0,
        "adjustment_history": []
    }
    
    with open("configs/risk_weights.json", "w") as f:
        json.dump(initial_weights, f, indent=2)


def cleanup_test_environment():
    """Restore original files."""
    if os.path.exists("configs/risk_weights_backup.json"):
        shutil.move("configs/risk_weights_backup.json", "configs/risk_weights.json")
    if os.path.exists("logs/eod_summary_backup.csv"):
        shutil.move("logs/eod_summary_backup.csv", "logs/eod_summary.csv")
    if os.path.exists("logs/learning_history_backup.csv"):
        shutil.move("logs/learning_history_backup.csv", "logs/learning_history.csv")


def test_1_load_save_weights():
    """Test 1: Load and save risk weights."""
    print("\n" + "="*60)
    print("TEST 1: Load and Save Risk Weights")
    print("="*60)
    
    setup_test_environment()
    
    # Test load
    weights = load_risk_weights()
    assert "cod_risk" in weights
    assert weights["cod_risk"] == 15
    assert weights["weather_risk"] == 20
    print("✅ Initial weights loaded correctly")
    
    # Test save
    weights["cod_risk"] = 16
    save_risk_weights(weights)
    
    # Reload and verify
    reloaded = load_risk_weights()
    assert reloaded["cod_risk"] == 16
    print("✅ Weights saved and reloaded correctly")
    
    cleanup_test_environment()


def test_2_update_risk_weights():
    """Test 2: Update risk weights based on outcomes."""
    print("\n" + "="*60)
    print("TEST 2: Update Risk Weights")
    print("="*60)
    
    setup_test_environment()
    
    # Get initial weights
    initial = load_risk_weights()
    print(f"Initial weights: {initial['address_risk']}, {initial['weather_risk']}, {initial['weight_risk']}")
    
    # Run update
    result = update_risk_weights()
    
    assert "error" not in result
    assert "updated_weights" in result
    assert "adjustments" in result
    assert "learning_signals" in result
    
    print(f"\nLearning signals:")
    print(f"  High-risk failures: {result['learning_signals']['high_risk_failures']}")
    print(f"  Low-risk successes: {result['learning_signals']['low_risk_successes']}")
    print(f"  Missed risks: {result['learning_signals']['missed_risks']}")
    
    print(f"\nAdjustments:")
    print(f"  Address risk: {result['adjustments']['address_risk']:+d}")
    print(f"  Weather risk: {result['adjustments']['weather_risk']:+d}")
    print(f"  Weight risk: {result['adjustments']['weight_risk']:+d}")
    
    # Verify adjustments
    # Should increase address_risk and weather_risk (high-risk failures = 2)
    # Should decrease weight_risk (low-risk successes = 6, so 6//5 = 1)
    # Should increase cod_risk and area_risk (missed risks = 1)
    
    assert result['adjustments']['address_risk'] > 0, "Address risk should increase"
    assert result['adjustments']['weather_risk'] > 0, "Weather risk should increase"
    print("✅ Risk weights adjusted correctly based on failures/successes")
    
    cleanup_test_environment()


def test_3_address_scoring_improvement():
    """Test 3: Improve address confidence scoring."""
    print("\n" + "="*60)
    print("TEST 3: Address Scoring Improvement")
    print("="*60)
    
    setup_test_environment()
    
    result = improve_address_scoring()
    
    assert "error" not in result
    assert "address_confidence_adjustment" in result
    assert "successful_low_confidence" in result
    assert "failed_high_confidence" in result
    
    print(f"Successful low-confidence deliveries: {result['successful_low_confidence']}")
    print(f"Failed high-confidence deliveries: {result['failed_high_confidence']}")
    print(f"Net adjustment: {result['address_confidence_adjustment']}")
    print(f"Recommendation: {result['recommendation']}")
    
    # We have 3 low-confidence successes (<60) and 2 high-confidence failures (>80: TEST_HR_001=85, TEST_MISS_001=90)
    # Adjustment = (3*2) - (2*2) = 6 - 4 = 2
    assert result['successful_low_confidence'] == 3
    assert result['failed_high_confidence'] == 2
    assert result['address_confidence_adjustment'] == 2
    print("✅ Address scoring analysis correct")
    
    cleanup_test_environment()


def test_4_override_effectiveness():
    """Test 4: Analyze human override effectiveness."""
    print("\n" + "="*60)
    print("TEST 4: Override Effectiveness Analysis")
    print("="*60)
    
    setup_test_environment()
    
    result = analyze_override_effectiveness()
    
    assert "error" not in result
    assert "total_overrides" in result
    assert "successful_overrides" in result
    assert "override_success_rate" in result
    
    print(f"Total overrides: {result['total_overrides']}")
    print(f"Successful overrides: {result['successful_overrides']}")
    print(f"Override success rate: {result['override_success_rate']}")
    print(f"AI success rate: {result.get('ai_success_rate')}")
    print(f"Performance gap: {result.get('performance_gap')}")
    print(f"Insight: {result['insight']}")
    
    # We have 3 overrides: 2 successful, 1 failed
    assert result['total_overrides'] == 3
    assert result['successful_overrides'] == 2
    assert result['override_success_rate'] == 0.67
    print("✅ Override analysis correct")
    
    # Check top override reasons
    if result.get('top_override_reasons'):
        print(f"\nTop override reasons:")
        for reason, count in result['top_override_reasons'].items():
            print(f"  {reason}: {count}")
    
    cleanup_test_environment()


def test_5_learning_statistics():
    """Test 5: Generate learning statistics."""
    print("\n" + "="*60)
    print("TEST 5: Learning Statistics")
    print("="*60)
    
    setup_test_environment()
    
    result = get_learning_statistics()
    
    assert "error" not in result
    assert "total_shipments" in result
    assert "success_rate" in result
    assert "mismatch_rate" in result
    assert "override_rate" in result
    assert "avg_prediction_accuracy" in result
    
    print(f"Total shipments: {result['total_shipments']}")
    print(f"Success rate: {result['success_rate']}")
    print(f"Mismatch rate: {result['mismatch_rate']}")
    print(f"Override rate: {result['override_rate']}")
    print(f"Avg prediction accuracy: {result['avg_prediction_accuracy']}")
    
    # We have 12 shipments total
    # Successful: 8 (6 low-risk + 2 overrides)
    # Mismatches: 3 (2 high-risk failures + 1 missed risk)
    # Overrides: 3
    
    assert result['total_shipments'] == 12
    assert result['success_rate'] == 0.67  # 8/12
    assert result['mismatch_rate'] == 0.25  # 3/12
    assert result['override_rate'] == 0.25  # 3/12
    print("✅ Learning statistics correct")
    
    # Check performance by risk bucket
    if result.get('risk_bucket_performance'):
        print("\nRisk bucket performance:")
        for bucket, metrics in result['risk_bucket_performance'].items():
            print(f"  {bucket}: {metrics}")
    
    cleanup_test_environment()


def test_6_complete_learning_loop():
    """Test 6: Run complete learning loop."""
    print("\n" + "="*60)
    print("TEST 6: Complete Learning Loop Execution")
    print("="*60)
    
    setup_test_environment()
    
    # Delete learning history to start fresh
    if os.path.exists("logs/learning_history.csv"):
        os.remove("logs/learning_history.csv")
    
    result = run_learning_loop()
    
    assert "updated_weights" in result
    assert "address_learning" in result
    assert "override_metrics" in result
    assert "learning_statistics" in result
    assert "execution_timestamp" in result
    
    print("\n✅ Complete learning loop executed successfully")
    
    # Verify all components
    assert "error" not in result["updated_weights"]
    assert "error" not in result["address_learning"]
    assert "error" not in result["override_metrics"]
    assert "error" not in result["learning_statistics"]
    
    print("✅ All learning loop components functional")
    
    # Check that weights were actually updated
    updated_weights = load_risk_weights()
    assert updated_weights["update_count"] >= 1, "Update count should be at least 1"
    assert len(updated_weights["adjustment_history"]) >= 1, "Should have adjustment history"
    print("✅ Weight update metadata correct")
    
    # Check that learning history was logged
    assert os.path.exists("logs/learning_history.csv")
    history = pd.read_csv("logs/learning_history.csv")
    assert len(history) >= 1, "Should have at least 1 history record"
    print("✅ Learning history logged")
    
    cleanup_test_environment()


def test_7_weight_evolution():
    """Test 7: Track weight evolution over time."""
    print("\n" + "="*60)
    print("TEST 7: Weight Evolution Tracking")
    print("="*60)
    
    setup_test_environment()
    
    # Run learning loop multiple times
    for i in range(3):
        run_learning_loop()
        print(f"  Cycle {i+1} completed")
    
    # Get weight evolution
    evolution = get_weight_evolution()
    
    assert "evolution" in evolution
    assert len(evolution["evolution"]) >= 3
    print(f"\n✅ Tracked {len(evolution['evolution'])} learning cycles")
    
    # Display evolution
    print("\nWeight evolution:")
    for i, record in enumerate(evolution["evolution"][-3:]):
        print(f"  Cycle {i+1}: {record['weights']}")
    
    cleanup_test_environment()


def test_8_learning_history():
    """Test 8: Retrieve learning history."""
    print("\n" + "="*60)
    print("TEST 8: Learning History Retrieval")
    print("="*60)
    
    setup_test_environment()
    
    # Run learning loop
    run_learning_loop()
    
    # Get history
    history = get_learning_history(last_n=5)
    
    assert not history.empty
    assert "timestamp" in history.columns
    assert "weight_updates" in history.columns
    assert "override_effectiveness" in history.columns
    
    print(f"✅ Retrieved {len(history)} learning history records")
    print(f"\nColumns: {list(history.columns)}")
    
    cleanup_test_environment()


def test_9_edge_case_no_data():
    """Test 9: Handle edge case with no data."""
    print("\n" + "="*60)
    print("TEST 9: Edge Case - No Data")
    print("="*60)
    
    # Remove EOD file
    if os.path.exists("logs/eod_summary.csv"):
        os.remove("logs/eod_summary.csv")
    
    result = update_risk_weights()
    assert "error" in result
    print("✅ Handled missing EOD data gracefully")
    
    result = get_learning_statistics()
    assert "error" in result
    print("✅ Handled missing data in statistics gracefully")


def test_10_edge_case_insufficient_overrides():
    """Test 10: Handle edge case with no overrides."""
    print("\n" + "="*60)
    print("TEST 10: Edge Case - No Overrides")
    print("="*60)
    
    setup_test_environment()
    
    # Create EOD without overrides
    test_eod = pd.DataFrame([
        {
            "shipment_id": "TEST_001",
            "predicted_risk_score": 25,
            "predicted_decision": "DISPATCH",
            "actual_status": "DELIVERED",
            "override_flag": False,
            "mismatch_flag": False,
            "prediction_accuracy": 100,
            "was_successful": True,
            "had_delay": False
        }
    ])
    test_eod.to_csv("logs/eod_summary.csv", index=False)
    
    result = analyze_override_effectiveness()
    
    assert result["total_overrides"] == 0
    assert result["override_success_rate"] is None
    assert "message" in result
    print("✅ Handled no overrides gracefully")
    
    cleanup_test_environment()


def test_11_weight_constraints():
    """Test 11: Verify weight constraints (5-30 range)."""
    print("\n" + "="*60)
    print("TEST 11: Weight Constraints")
    print("="*60)
    
    setup_test_environment()
    
    # Set extreme initial weights
    weights = load_risk_weights()
    weights["weight_risk"] = 6  # Near minimum
    weights["address_risk"] = 29  # Near maximum
    save_risk_weights(weights)
    
    # Run update
    update_risk_weights()
    
    # Verify constraints
    updated = load_risk_weights()
    for key in ["cod_risk", "address_risk", "weather_risk", "area_risk", "weight_risk"]:
        assert updated[key] >= 5, f"{key} below minimum"
        assert updated[key] <= 30, f"{key} above maximum"
        print(f"  {key}: {updated[key]} (within constraints)")
    
    print("✅ All weights within constraints (5-30)")
    
    cleanup_test_environment()


def test_12_adjustment_history_limit():
    """Test 12: Verify adjustment history is limited to 30 entries."""
    print("\n" + "="*60)
    print("TEST 12: Adjustment History Limit")
    print("="*60)
    
    setup_test_environment()
    
    # Run learning loop 35 times
    for i in range(35):
        run_learning_loop()
        if (i + 1) % 10 == 0:
            print(f"  Completed {i+1} cycles")
    
    # Check history limit
    weights = load_risk_weights()
    assert len(weights["adjustment_history"]) == 30
    print("✅ Adjustment history limited to 30 entries")
    
    cleanup_test_environment()


def run_all_tests():
    """Run all learning loop tests."""
    print("\n" + "="*80)
    print(" "*20 + "STEP 18: LEARNING LOOP TEST SUITE")
    print("="*80)
    
    tests = [
        test_1_load_save_weights,
        test_2_update_risk_weights,
        test_3_address_scoring_improvement,
        test_4_override_effectiveness,
        test_5_learning_statistics,
        test_6_complete_learning_loop,
        test_7_weight_evolution,
        test_8_learning_history,
        test_9_edge_case_no_data,
        test_10_edge_case_insufficient_overrides,
        test_11_weight_constraints,
        test_12_adjustment_history_limit
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ {test_func.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"\n❌ {test_func.__name__} ERROR: {e}")
            failed += 1
    
    print("\n" + "="*80)
    print(" "*20 + "TEST SUMMARY")
    print("="*80)
    print(f"Total Tests: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {passed/len(tests)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n✅ LEARNING LOOP COMPLETE")
        print("=" * 80)
        print("The system now learns from its own outcomes:")
        print("  • Risk weights adjust based on failures/successes")
        print("  • Address confidence improves from delivery patterns")
        print("  • Human override effectiveness is measured")
        print("  • Safe, explainable, incremental learning")
        print("=" * 80)
    else:
        print("\n⚠️  SOME TESTS FAILED")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
