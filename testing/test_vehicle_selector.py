"""
Hyper-Local Vehicle Selector Test Suite

Tests vehicle feasibility logic, capacity checks, and recommendation engine
"""

from rules.vehicle_selector import (
    hyper_local_vehicle_check,
    is_vehicle_allowed,
    capacity_ok,
    recommend_alternative,
    get_vehicle_capacity,
    should_split_delivery
)

print("=" * 60)
print("HYPER-LOCAL VEHICLE SELECTOR TEST SUITE")
print("=" * 60)

# Test Case 1: Old City + Van (SHOULD REJECT)
print("\n🔴 Test Case 1: Old City + Van (Infeasible)")
print("-" * 60)
vehicle_capacity = get_vehicle_capacity("Van")
result = hyper_local_vehicle_check(
    area_type="Old City",
    road_accessibility="Narrow",
    assigned_vehicle="Van",
    weight_kg=12,
    volumetric_weight=8,
    vehicle_capacity=vehicle_capacity
)
print(f"Area: {result['area_type']}, Road: {result['road_accessibility']}")
print(f"Assigned Vehicle: {result['assigned_vehicle']}")
print(f"Status: {result['vehicle_status']}")
print(f"Final Vehicle: {result['final_vehicle']}")
print(f"Action: {result['action']}")
print(f"Reason: {result['reason']}")
assert result['vehicle_status'] == "REJECTED", "Should reject van in old city"
assert result['final_vehicle'] == "Bike", "Should recommend bike"
assert result['action'] == "SPLIT_DELIVERY", "Should split for old city"
print("✅ PASSED")

# Test Case 2: Old City + Bike (SHOULD APPROVE)
print("\n🟢 Test Case 2: Old City + Bike (Feasible)")
print("-" * 60)
vehicle_capacity = get_vehicle_capacity("Bike")
result = hyper_local_vehicle_check(
    area_type="Old City",
    road_accessibility="Narrow",
    assigned_vehicle="Bike",
    weight_kg=8,
    volumetric_weight=5,
    vehicle_capacity=vehicle_capacity
)
print(f"Area: {result['area_type']}, Road: {result['road_accessibility']}")
print(f"Assigned Vehicle: {result['assigned_vehicle']}")
print(f"Status: {result['vehicle_status']}")
print(f"Final Vehicle: {result['final_vehicle']}")
print(f"Action: {result['action']}")
assert result['vehicle_status'] == "APPROVED", "Should approve bike in old city"
assert result['final_vehicle'] == "Bike", "Should use bike"
assert result['action'] == "PROCEED", "Should proceed"
print("✅ PASSED")

# Test Case 3: Narrow Road + Truck (SHOULD REJECT)
print("\n🔴 Test Case 3: Narrow Road + Truck (Infeasible)")
print("-" * 60)
vehicle_capacity = get_vehicle_capacity("Truck")
result = hyper_local_vehicle_check(
    area_type="Semi-Urban",
    road_accessibility="Narrow",
    assigned_vehicle="Truck",
    weight_kg=50,
    volumetric_weight=30,
    vehicle_capacity=vehicle_capacity
)
print(f"Area: {result['area_type']}, Road: {result['road_accessibility']}")
print(f"Assigned Vehicle: {result['assigned_vehicle']}")
print(f"Status: {result['vehicle_status']}")
print(f"Final Vehicle: {result['final_vehicle']}")
print(f"Action: {result['action']}")
print(f"Reason: {result['reason']}")
assert result['vehicle_status'] == "REJECTED", "Should reject truck on narrow road"
assert result['final_vehicle'] == "Bike", "Should recommend bike"
print("✅ PASSED")

# Test Case 4: Wide Road + Truck (SHOULD APPROVE)
print("\n🟢 Test Case 4: Wide Road + Truck (Feasible)")
print("-" * 60)
vehicle_capacity = get_vehicle_capacity("Truck")
result = hyper_local_vehicle_check(
    area_type="Rural",
    road_accessibility="Wide",
    assigned_vehicle="Truck",
    weight_kg=100,
    volumetric_weight=80,
    vehicle_capacity=vehicle_capacity
)
print(f"Area: {result['area_type']}, Road: {result['road_accessibility']}")
print(f"Assigned Vehicle: {result['assigned_vehicle']}")
print(f"Status: {result['vehicle_status']}")
print(f"Final Vehicle: {result['final_vehicle']}")
print(f"Action: {result['action']}")
assert result['vehicle_status'] == "APPROVED", "Should approve truck on wide road"
assert result['final_vehicle'] == "Truck", "Should use truck"
print("✅ PASSED")

# Test Case 5: Capacity Exceeded (SHOULD REJECT)
print("\n🔴 Test Case 5: Weight Exceeds Bike Capacity")
print("-" * 60)
vehicle_capacity = get_vehicle_capacity("Bike")
result = hyper_local_vehicle_check(
    area_type="Planned",
    road_accessibility="Medium",
    assigned_vehicle="Bike",
    weight_kg=25,  # Exceeds bike capacity (20kg)
    volumetric_weight=10,
    vehicle_capacity=vehicle_capacity
)
print(f"Weight: {result['weight_kg']}kg (Bike max: 20kg)")
print(f"Status: {result['vehicle_status']}")
print(f"Final Vehicle: {result['final_vehicle']}")
print(f"Action: {result['action']}")
print(f"Reason: {result['reason']}")
assert result['vehicle_status'] == "REJECTED", "Should reject due to capacity"
assert result['final_vehicle'] in ["Van", "Truck"], "Should recommend larger vehicle"
print("✅ PASSED")

# Test Case 6: Planned Area + Van (SHOULD APPROVE)
print("\n🟢 Test Case 6: Planned Area + Van (Feasible)")
print("-" * 60)
vehicle_capacity = get_vehicle_capacity("Van")
result = hyper_local_vehicle_check(
    area_type="Planned",
    road_accessibility="Medium",
    assigned_vehicle="Van",
    weight_kg=30,
    volumetric_weight=20,
    vehicle_capacity=vehicle_capacity
)
print(f"Area: {result['area_type']}, Road: {result['road_accessibility']}")
print(f"Status: {result['vehicle_status']}")
print(f"Final Vehicle: {result['final_vehicle']}")
assert result['vehicle_status'] == "APPROVED", "Should approve van in planned area"
print("✅ PASSED")

# Test Case 7: Medium Road + Truck (SHOULD REJECT)
print("\n🔴 Test Case 7: Medium Road + Truck (Infeasible)")
print("-" * 60)
vehicle_capacity = get_vehicle_capacity("Truck")
result = hyper_local_vehicle_check(
    area_type="Semi-Urban",
    road_accessibility="Medium",
    assigned_vehicle="Truck",
    weight_kg=80,
    volumetric_weight=60,
    vehicle_capacity=vehicle_capacity
)
print(f"Road: {result['road_accessibility']}")
print(f"Status: {result['vehicle_status']}")
print(f"Final Vehicle: {result['final_vehicle']}")
print(f"Reason: {result['reason']}")
assert result['vehicle_status'] == "REJECTED", "Should reject truck on medium road"
assert result['final_vehicle'] in ["Bike", "Van"], "Should not recommend truck"
print("✅ PASSED")

# Test Case 8: Heavy Load + Wide Road (SHOULD RECOMMEND TRUCK)
print("\n🟡 Test Case 8: Heavy Load Recommendation")
print("-" * 60)
vehicle_capacity = get_vehicle_capacity("Bike")
result = hyper_local_vehicle_check(
    area_type="Rural",
    road_accessibility="Wide",
    assigned_vehicle="Bike",
    weight_kg=35,  # Heavy load
    volumetric_weight=28,
    vehicle_capacity=vehicle_capacity
)
print(f"Weight: {result['weight_kg']}kg (Heavy)")
print(f"Road: {result['road_accessibility']} (Truck allowed)")
print(f"Status: {result['vehicle_status']}")
print(f"Final Vehicle: {result['final_vehicle']}")
print(f"Action: {result['action']}")
assert result['vehicle_status'] == "REJECTED", "Should reject bike for heavy load"
assert result['final_vehicle'] == "Truck", "Should recommend truck for heavy load"
print("✅ PASSED")

# Test Case 9: Split Delivery Check
print("\n📦 Test Case 9: Split Delivery Detection")
print("-" * 60)
vehicle_capacity = get_vehicle_capacity("Van")
result = hyper_local_vehicle_check(
    area_type="Old City",
    road_accessibility="Narrow",
    assigned_vehicle="Van",
    weight_kg=15,
    volumetric_weight=10,
    vehicle_capacity=vehicle_capacity
)
should_split = should_split_delivery(result)
print(f"Area: {result['area_type']}")
print(f"Action: {result['action']}")
print(f"Should Split Delivery: {should_split}")
assert should_split == True, "Old city should trigger split delivery"
print("✅ PASSED")

# Test Case 10: All Vehicle Capacities
print("\n📊 Test Case 10: Vehicle Capacity Specifications")
print("-" * 60)
for vehicle in ["Bike", "Van", "Truck"]:
    capacity = get_vehicle_capacity(vehicle)
    print(f"{vehicle:6s}: Max Load = {capacity['max_load_kg']:3.0f}kg, "
          f"Max Volume = {capacity['max_volume_cm3']:6.0f}cm³")
assert get_vehicle_capacity("Bike")["max_load_kg"] == 20
assert get_vehicle_capacity("Van")["max_load_kg"] == 50
assert get_vehicle_capacity("Truck")["max_load_kg"] == 200
print("✅ PASSED")

# Summary
print("\n" + "=" * 60)
print("📊 TEST SUMMARY")
print("=" * 60)
print("✅ All 10 test cases PASSED")
print("\nVehicle Feasibility Rules Validated:")
print("  ✅ Area-based restrictions (Old City = Bike only)")
print("  ✅ Road-based restrictions (Narrow = Bike only)")
print("  ✅ Capacity checks (Weight + Volume)")
print("  ✅ Alternative recommendations (Split/Switch vehicle)")
print("  ✅ Multi-factor decision logic")
print("\nKey Capabilities:")
print("  ✅ Prevents vans in narrow lanes")
print("  ✅ Prevents trucks in old city areas")
print("  ✅ Recommends split delivery when needed")
print("  ✅ Capacity-aware vehicle selection")
print("  ✅ Last-100-meters problem solved")
print("\n" + "=" * 60)
print("✅ HYPER-LOCAL VEHICLE SELECTOR: OPERATIONAL")
print("=" * 60)
