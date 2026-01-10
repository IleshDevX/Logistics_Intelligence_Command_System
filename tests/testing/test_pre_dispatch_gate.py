"""
Pre-Dispatch Decision Gate Test Suite

Tests the decision logic with various combinations of signals
"""

from rules.pre_dispatch_gate import (
    pre_dispatch_decision,
    get_decision_explanation,
    should_dispatch,
    requires_customer_contact,
    get_action_items
)

print("=" * 60)
print("PRE-DISPATCH DECISION GATE TEST SUITE")
print("=" * 60)

# Test Case 1: High Risk + Severe Weather (DELAY)
print("\n🔴 Test Case 1: High Risk + Severe Weather")
print("-" * 60)
result = pre_dispatch_decision(
    risk_score=75,
    weather_impact_factor=70,
    address_confidence_score=80
)
print(f"Risk Score: {result['risk_score']}")
print(f"Weather Impact: {result['weather_impact_factor']}")
print(f"Address Confidence: {result['address_confidence_score']}")
print(f"Decision: {result['decision']}")
print(f"Reasons: {result['reasons']}")
print(f"Explanation: {get_decision_explanation(result)}")
assert result['decision'] == "DELAY", "Should delay due to high risk and weather"
assert "High delivery risk" in result['reasons'], "Should flag high risk"
assert "Severe weather impact" in result['reasons'], "Should flag weather"
print("✅ PASSED")

# Test Case 2: Low Address Confidence (RESCHEDULE)
print("\n🟡 Test Case 2: Low Address Confidence")
print("-" * 60)
result = pre_dispatch_decision(
    risk_score=40,
    weather_impact_factor=20,
    address_confidence_score=45
)
print(f"Risk Score: {result['risk_score']}")
print(f"Weather Impact: {result['weather_impact_factor']}")
print(f"Address Confidence: {result['address_confidence_score']}")
print(f"Decision: {result['decision']}")
print(f"Reasons: {result['reasons']}")
print(f"Explanation: {get_decision_explanation(result)}")
assert result['decision'] == "RESCHEDULE", "Should reschedule due to low address confidence"
assert "Low address confidence" in result['reasons'], "Should flag address issue"
assert requires_customer_contact(result) == True, "Should require customer contact"
print("✅ PASSED")

# Test Case 3: All Safe (DISPATCH)
print("\n🟢 Test Case 3: All Signals Safe")
print("-" * 60)
result = pre_dispatch_decision(
    risk_score=25,
    weather_impact_factor=10,
    address_confidence_score=90
)
print(f"Risk Score: {result['risk_score']}")
print(f"Weather Impact: {result['weather_impact_factor']}")
print(f"Address Confidence: {result['address_confidence_score']}")
print(f"Decision: {result['decision']}")
print(f"Reasons: {result['reasons']}")
print(f"Explanation: {get_decision_explanation(result)}")
assert result['decision'] == "DISPATCH", "Should dispatch when all signals safe"
assert len(result['reasons']) == 0, "Should have no blocking reasons"
assert should_dispatch(result) == True, "Should allow dispatch"
print("✅ PASSED")

# Test Case 4: High Risk Only (DELAY)
print("\n🔴 Test Case 4: High Risk Only")
print("-" * 60)
result = pre_dispatch_decision(
    risk_score=70,
    weather_impact_factor=25,
    address_confidence_score=75
)
print(f"Risk Score: {result['risk_score']}")
print(f"Weather Impact: {result['weather_impact_factor']}")
print(f"Address Confidence: {result['address_confidence_score']}")
print(f"Decision: {result['decision']}")
print(f"Reasons: {result['reasons']}")
print(f"Explanation: {get_decision_explanation(result)}")
assert result['decision'] == "DELAY", "Should delay due to high risk"
assert "High delivery risk" in result['reasons'], "Should flag high risk"
assert len(result['reasons']) == 1, "Should have only one reason"
print("✅ PASSED")

# Test Case 5: Severe Weather Only (DELAY)
print("\n🔴 Test Case 5: Severe Weather Only")
print("-" * 60)
result = pre_dispatch_decision(
    risk_score=30,
    weather_impact_factor=75,
    address_confidence_score=85
)
print(f"Risk Score: {result['risk_score']}")
print(f"Weather Impact: {result['weather_impact_factor']}")
print(f"Address Confidence: {result['address_confidence_score']}")
print(f"Decision: {result['decision']}")
print(f"Reasons: {result['reasons']}")
print(f"Explanation: {get_decision_explanation(result)}")
assert result['decision'] == "DELAY", "Should delay due to weather"
assert "Severe weather impact" in result['reasons'], "Should flag weather"
print("✅ PASSED")

# Test Case 6: Low Address + High Risk (RESCHEDULE Priority)
print("\n🟡 Test Case 6: Multiple Issues (Address Priority)")
print("-" * 60)
result = pre_dispatch_decision(
    risk_score=70,
    weather_impact_factor=65,
    address_confidence_score=50
)
print(f"Risk Score: {result['risk_score']}")
print(f"Weather Impact: {result['weather_impact_factor']}")
print(f"Address Confidence: {result['address_confidence_score']}")
print(f"Decision: {result['decision']}")
print(f"Reasons: {result['reasons']}")
print(f"Explanation: {get_decision_explanation(result)}")
assert result['decision'] == "RESCHEDULE", "Address issue takes priority"
assert "Low address confidence" in result['reasons'], "Should flag address"
assert len(result['reasons']) == 3, "Should flag all three issues"
print("✅ PASSED")

# Test Case 7: Boundary Values (Exactly at threshold)
print("\n⚪ Test Case 7: Boundary Values (At Threshold)")
print("-" * 60)
result = pre_dispatch_decision(
    risk_score=60,  # Exactly at threshold
    weather_impact_factor=60,  # Exactly at threshold
    address_confidence_score=60  # Exactly at threshold
)
print(f"Risk Score: {result['risk_score']}")
print(f"Weather Impact: {result['weather_impact_factor']}")
print(f"Address Confidence: {result['address_confidence_score']}")
print(f"Decision: {result['decision']}")
print(f"Reasons: {result['reasons']}")
print(f"Explanation: {get_decision_explanation(result)}")
# At exactly threshold = safe (> threshold is the trigger)
assert result['decision'] == "DISPATCH", "At threshold should be safe"
print("✅ PASSED")

# Test Case 8: Action Items Generation
print("\n📋 Test Case 8: Action Items Generation")
print("-" * 60)
result = pre_dispatch_decision(
    risk_score=75,
    weather_impact_factor=70,
    address_confidence_score=80
)
actions = get_action_items(result)
print(f"Decision: {result['decision']}")
print(f"Action Items:")
for action in actions:
    print(f"  - {action}")
assert len(actions) > 0, "Should generate action items"
assert "Hold shipment at hub" in actions, "Should have delay action"
print("✅ PASSED")

# Summary
print("\n" + "=" * 60)
print("📊 TEST SUMMARY")
print("=" * 60)
print("✅ All 8 test cases PASSED")
print("\nDecision Logic Validated:")
print("  ✅ DISPATCH: All signals safe")
print("  ✅ DELAY: High risk OR severe weather")
print("  ✅ RESCHEDULE: Low address confidence (priority)")
print("  ✅ Threshold logic: > 60 triggers action")
print("  ✅ Multiple issues: Address takes priority")
print("  ✅ Explainable reasons: Generated correctly")
print("  ✅ Action items: Context-specific guidance")
print("\n" + "=" * 60)
print("✅ PRE-DISPATCH DECISION GATE: OPERATIONAL")
print("=" * 60)
