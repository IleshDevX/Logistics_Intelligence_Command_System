"""
Test Suite for Human Override System (Step 15)
Tests override logic, locking mechanism, and logging
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from rules.human_override import (
    apply_human_override,
    is_locked,
    get_override_history,
    get_override_stats,
    unlock_shipment,
    OVERRIDE_REASONS
)
import pandas as pd

def test_override_ai_decision():
    """Test 1: Manager overrides AI DELAY to DISPATCH"""
    result = apply_human_override(
        shipment_id="SHP000456",
        ai_decision="DELAY",
        override_decision="DISPATCH",
        override_reason="High priority customer"
    )
    
    assert result["status"] == "OVERRIDDEN"
    assert result["final_decision"] == "DISPATCH"
    assert result["locked"] == True
    print("✅ Test 1: Override AI decision - PASSED")


def test_no_override_needed():
    """Test 2: Manager agrees with AI (no override)"""
    result = apply_human_override(
        shipment_id="SHP000457",
        ai_decision="DISPATCH",
        override_decision="DISPATCH",
        override_reason="Manager experience"
    )
    
    assert result["status"] == "NO_OVERRIDE"
    assert result["final_decision"] == "DISPATCH"
    assert result["locked"] == False
    print("✅ Test 2: No override needed - PASSED")


def test_invalid_reason():
    """Test 3: Invalid override reason rejected"""
    result = apply_human_override(
        shipment_id="SHP000458",
        ai_decision="DELAY",
        override_decision="DISPATCH",
        override_reason="Random reason not in catalog"
    )
    
    assert result["status"] == "ERROR"
    assert "Invalid reason" in result["message"]
    print("✅ Test 3: Invalid reason rejected - PASSED")


def test_invalid_decision():
    """Test 4: Invalid decision type rejected"""
    result = apply_human_override(
        shipment_id="SHP000459",
        ai_decision="WRONG_DECISION",
        override_decision="DISPATCH",
        override_reason="Manager experience"
    )
    
    assert result["status"] == "ERROR"
    assert "Invalid decision" in result["message"]
    print("✅ Test 4: Invalid decision rejected - PASSED")


def test_lock_mechanism():
    """Test 5: Lock prevents AI re-evaluation"""
    # Apply override
    apply_human_override(
        shipment_id="SHP000460",
        ai_decision="RESCHEDULE",
        override_decision="DISPATCH",
        override_reason="Operational constraint"
    )
    
    # Check if locked
    assert is_locked("SHP000460") == True
    assert is_locked("SHP999999") == False  # Non-existent shipment
    print("✅ Test 5: Lock mechanism works - PASSED")


def test_override_history():
    """Test 6: Override history retrieval"""
    # Get history for specific shipment
    history = get_override_history("SHP000456")
    assert len(history) > 0
    assert history.iloc[0]["shipment_id"] == "SHP000456"
    
    # Get all history
    all_history = get_override_history()
    assert len(all_history) > 0
    print("✅ Test 6: Override history retrieval - PASSED")


def test_override_stats():
    """Test 7: Override statistics calculation"""
    stats = get_override_stats()
    
    assert "total_overrides" in stats
    assert "most_common_reason" in stats
    assert "reason_distribution" in stats
    assert stats["total_overrides"] > 0
    print("✅ Test 7: Override statistics - PASSED")
    print(f"   Total overrides: {stats['total_overrides']}")
    print(f"   Most common reason: {stats['most_common_reason']}")


def test_all_override_reasons():
    """Test 8: All catalog reasons are valid"""
    for reason in OVERRIDE_REASONS:
        result = apply_human_override(
            shipment_id=f"SHP_TEST_{reason.replace(' ', '_')}",
            ai_decision="DELAY",
            override_decision="DISPATCH",
            override_reason=reason
        )
        assert result["status"] == "OVERRIDDEN"
    
    print(f"✅ Test 8: All {len(OVERRIDE_REASONS)} override reasons valid - PASSED")


def test_unlock_shipment():
    """Test 9: Unlock mechanism works"""
    # First, create an override
    apply_human_override(
        shipment_id="SHP_UNLOCK_TEST",
        ai_decision="DELAY",
        override_decision="DISPATCH",
        override_reason="Manager experience"
    )
    
    # Verify it's locked
    assert is_locked("SHP_UNLOCK_TEST") == True
    
    # Unlock it
    result = unlock_shipment("SHP_UNLOCK_TEST")
    assert result["status"] == "UNLOCKED"
    
    # Verify it's unlocked
    assert is_locked("SHP_UNLOCK_TEST") == False
    print("✅ Test 9: Unlock shipment - PASSED")


def test_multiple_overrides_same_shipment():
    """Test 10: Multiple overrides on same shipment"""
    shipment_id = "SHP_MULTI_OVERRIDE"
    
    # First override
    apply_human_override(
        shipment_id=shipment_id,
        ai_decision="DELAY",
        override_decision="DISPATCH",
        override_reason="High priority customer"
    )
    
    # Second override (different reason)
    apply_human_override(
        shipment_id=shipment_id,
        ai_decision="DELAY",
        override_decision="RESCHEDULE",
        override_reason="Weather cleared manually"
    )
    
    # Check history
    history = get_override_history(shipment_id)
    assert len(history) >= 2
    print("✅ Test 10: Multiple overrides tracked - PASSED")


def test_reschedule_override():
    """Test 11: Override AI to RESCHEDULE"""
    result = apply_human_override(
        shipment_id="SHP_RESCHEDULE_TEST",
        ai_decision="DISPATCH",
        override_decision="RESCHEDULE",
        override_reason="Temporary road closure"
    )
    
    assert result["status"] == "OVERRIDDEN"
    assert result["final_decision"] == "RESCHEDULE"
    print("✅ Test 11: Override to RESCHEDULE - PASSED")


def test_delay_override():
    """Test 12: Override AI to DELAY"""
    result = apply_human_override(
        shipment_id="SHP_DELAY_TEST",
        ai_decision="DISPATCH",
        override_decision="DELAY",
        override_reason="Local knowledge"
    )
    
    assert result["status"] == "OVERRIDDEN"
    assert result["final_decision"] == "DELAY"
    print("✅ Test 12: Override to DELAY - PASSED")


def run_all_tests():
    """Run all human override tests"""
    print("\n" + "="*60)
    print("STEP 15: HUMAN OVERRIDE SYSTEM - TEST SUITE")
    print("="*60 + "\n")
    
    test_override_ai_decision()
    test_no_override_needed()
    test_invalid_reason()
    test_invalid_decision()
    test_lock_mechanism()
    test_override_history()
    test_override_stats()
    test_all_override_reasons()
    test_unlock_shipment()
    test_multiple_overrides_same_shipment()
    test_reschedule_override()
    test_delay_override()
    
    print("\n" + "="*60)
    print("✅ ALL 12 TESTS PASSED")
    print("="*60)
    print("\n🎯 Key Validations:")
    print("   ✅ Override logic works correctly")
    print("   ✅ Lock mechanism prevents AI re-evaluation")
    print("   ✅ Invalid inputs rejected")
    print("   ✅ Override history logged")
    print("   ✅ Statistics calculated")
    print("   ✅ All override reasons valid")
    print("   ✅ Unlock mechanism functional")
    print("\n🔒 Human Authority: ESTABLISHED")
    print("📊 Accountability: LOGGED")
    print("🎓 Learning Loop: ENABLED")
    print("\n" + "="*60)


if __name__ == "__main__":
    run_all_tests()
