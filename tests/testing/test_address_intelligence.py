"""
Address Intelligence Test Suite

Tests the address parsing, landmark extraction, and confidence scoring
"""

from features.address_intelligence import process_address

print("=" * 60)
print("ADDRESS INTELLIGENCE TEST SUITE")
print("=" * 60)

# Test Case 1: Low Confidence - Old City, Vague, Narrow Road
print("\n🔴 Test Case 1: Low Confidence Address")
print("-" * 60)
result = process_address(
    raw_address="Near Hanuman temple, old lane behind market",
    road_accessibility="Narrow"
)
print(f"Raw Address: 'Near Hanuman temple, old lane behind market'")
print(f"Cleaned: '{result['cleaned_address']}'")
print(f"Landmarks: {result['landmarks']}")
print(f"Area Type: {result['area_type']}")
print(f"Confidence Score: {result['address_confidence_score']}")
print(f"Needs Clarification: {result['needs_clarification']}")
assert result['needs_clarification'] == True, "Should need clarification"
assert result['area_type'] == "Old City", "Should detect Old City"
assert len(result['landmarks']) >= 2, "Should detect multiple landmarks"
print("✅ PASSED")

# Test Case 2: High Confidence - Planned Area, Multiple Landmarks
print("\n🟢 Test Case 2: High Confidence Address")
print("-" * 60)
result = process_address(
    raw_address="Sector 15, Phase 2, near Metro Station and Shopping Mall",
    road_accessibility="Wide"
)
print(f"Raw Address: 'Sector 15, Phase 2, near Metro Station and Shopping Mall'")
print(f"Cleaned: '{result['cleaned_address']}'")
print(f"Landmarks: {result['landmarks']}")
print(f"Area Type: {result['area_type']}")
print(f"Confidence Score: {result['address_confidence_score']}")
print(f"Needs Clarification: {result['needs_clarification']}")
assert result['needs_clarification'] == False, "Should NOT need clarification"
assert result['area_type'] == "Planned", "Should detect Planned area"
assert result['address_confidence_score'] >= 60, "Should have high confidence"
print("✅ PASSED")

# Test Case 3: Medium Confidence - Semi-Urban, Single Landmark
print("\n🟡 Test Case 3: Medium Confidence Address")
print("-" * 60)
result = process_address(
    raw_address="123 Main Road, opposite Bank of India",
    road_accessibility="Medium"
)
print(f"Raw Address: '123 Main Road, opposite Bank of India'")
print(f"Cleaned: '{result['cleaned_address']}'")
print(f"Landmarks: {result['landmarks']}")
print(f"Area Type: {result['area_type']}")
print(f"Confidence Score: {result['address_confidence_score']}")
print(f"Needs Clarification: {result['needs_clarification']}")
assert "bank" in result['landmarks'], "Should detect bank landmark"
print("✅ PASSED")

# Test Case 4: Rural Address - Low Confidence
print("\n🔴 Test Case 4: Rural Address")
print("-" * 60)
result = process_address(
    raw_address="Village Rampur, near school, behind old gaon",
    road_accessibility="Narrow"
)
print(f"Raw Address: 'Village Rampur, near school, behind old gaon'")
print(f"Cleaned: '{result['cleaned_address']}'")
print(f"Landmarks: {result['landmarks']}")
print(f"Area Type: {result['area_type']}")
print(f"Confidence Score: {result['address_confidence_score']}")
print(f"Needs Clarification: {result['needs_clarification']}")
assert result['area_type'] == "Rural", "Should detect Rural area"
assert result['needs_clarification'] == True, "Rural + narrow should need clarification"
print("✅ PASSED")

# Test Case 5: No Landmarks, Vague Language
print("\n⚠️  Test Case 5: No Landmarks, Vague")
print("-" * 60)
result = process_address(
    raw_address="Near the corner, behind some shops",
    road_accessibility="Narrow"
)
print(f"Raw Address: 'Near the corner, behind some shops'")
print(f"Cleaned: '{result['cleaned_address']}'")
print(f"Landmarks: {result['landmarks']}")
print(f"Area Type: {result['area_type']}")
print(f"Confidence Score: {result['address_confidence_score']}")
print(f"Needs Clarification: {result['needs_clarification']}")
assert len(result['landmarks']) == 0, "Should have no landmarks"
assert result['needs_clarification'] == True, "Should definitely need clarification"
assert result['address_confidence_score'] < 40, "Should have very low confidence"
print("✅ PASSED")

# Test Case 6: Old City with Gali
print("\n🔴 Test Case 6: Old City Detection")
print("-" * 60)
result = process_address(
    raw_address="Gali number 3, Chowk area",
    road_accessibility="Narrow"
)
print(f"Raw Address: 'Gali number 3, Chowk area'")
print(f"Cleaned: '{result['cleaned_address']}'")
print(f"Landmarks: {result['landmarks']}")
print(f"Area Type: {result['area_type']}")
print(f"Confidence Score: {result['address_confidence_score']}")
print(f"Needs Clarification: {result['needs_clarification']}")
assert result['area_type'] == "Old City", "Should detect Old City from 'gali'"
print("✅ PASSED")

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED")
print("=" * 60)
print("\n📊 Address Intelligence Summary:")
print("  ✅ Address cleaning and normalization")
print("  ✅ Landmark extraction (India-specific)")
print("  ✅ Area type inference")
print("  ✅ Confidence scoring (explainable)")
print("  ✅ Clarification flag logic")
print("\n🎯 Address intelligence is ready for integration!")
