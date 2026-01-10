"""
Hyper-Local Vehicle Selector - Last-Mile Feasibility Engine

Purpose: Ensure assigned vehicle can physically reach the delivery point
Input: Area type, Road accessibility, Weight, Vehicle specs
Output: APPROVED/REJECTED + Alternative recommendations

Prevents:
- Vans stuck in narrow lanes
- Failed attempts in old city areas
- Resource waste from infeasible assignments

Used after Pre-Dispatch Gate (Step 9) and before final dispatch approval
"""

# India-specific operational rules (FROZEN)
AREA_VEHICLE_RULES = {
    "Old City": ["Bike"],
    "Planned": ["Bike", "Van"],
    "Semi-Urban": ["Bike", "Van"],
    "Rural": ["Bike", "Van", "Truck"]
}

ROAD_RESTRICTIONS = {
    "Narrow": ["Bike"],  # Only bikes allowed
    "Medium": ["Bike", "Van"],  # No trucks
    "Wide": ["Bike", "Van", "Truck"]  # All allowed
}


def is_vehicle_allowed(area_type: str, road_accessibility: str, vehicle_type: str) -> bool:
    """
    Check if vehicle is allowed based on area type and road accessibility.
    
    Parameters:
        area_type (str): Old City / Planned / Semi-Urban / Rural
        road_accessibility (str): Narrow / Medium / Wide
        vehicle_type (str): Bike / Van / Truck
    
    Returns:
        bool: True if vehicle is allowed, False otherwise
    
    Rules:
        - Old City: Bike only
        - Narrow roads: Bike only (no Van/Truck)
        - Medium roads: No Truck
        - Wide roads: All allowed
    """
    # Area-based rules (strict)
    if area_type == "Old City" and vehicle_type != "Bike":
        return False
    
    # Road-based rules
    if road_accessibility == "Narrow" and vehicle_type in ["Van", "Truck"]:
        return False
    
    if road_accessibility == "Medium" and vehicle_type == "Truck":
        return False
    
    return True


def capacity_ok(
    weight_kg: float,
    volumetric_weight: float,
    max_load_kg: float,
    max_volume_cm3: float
) -> bool:
    """
    Check if shipment fits within vehicle capacity constraints.
    
    Parameters:
        weight_kg (float): Shipment weight in kg
        volumetric_weight (float): Volumetric weight
        max_load_kg (float): Vehicle max load capacity
        max_volume_cm3 (float): Vehicle max volume capacity
    
    Returns:
        bool: True if shipment fits, False otherwise
    """
    # Weight check
    if weight_kg > max_load_kg:
        return False
    
    # Volume check (convert volumetric weight to cm3)
    if volumetric_weight * 1000 > max_volume_cm3:
        return False
    
    return True


def recommend_alternative(
    area_type: str,
    road_accessibility: str,
    weight_kg: float,
    volumetric_weight: float
) -> dict:
    """
    Recommend alternative vehicle when assigned vehicle is infeasible.
    
    Parameters:
        area_type (str): Area type
        road_accessibility (str): Road accessibility
        weight_kg (float): Shipment weight
        volumetric_weight (float): Volumetric weight
    
    Returns:
        dict: {
            "recommendation": Action to take,
            "suggested_vehicle": Alternative vehicle,
            "reason": Explanation
        }
    """
    # Old city logic (always use bike, may need split)
    if area_type == "Old City":
        return {
            "recommendation": "SPLIT_DELIVERY",
            "suggested_vehicle": "Bike",
            "reason": "Old city access restrictions"
        }
    
    # Narrow road logic
    if road_accessibility == "Narrow":
        return {
            "recommendation": "USE_BIKE",
            "suggested_vehicle": "Bike",
            "reason": "Narrow road accessibility"
        }
    
    # Heavy load logic (but check if truck is allowed)
    if weight_kg > 30 or volumetric_weight > 25:
        if road_accessibility == "Wide":
            return {
                "recommendation": "USE_TRUCK",
                "suggested_vehicle": "Truck",
                "reason": "High shipment volume"
            }
        else:
            return {
                "recommendation": "SPLIT_DELIVERY",
                "suggested_vehicle": "Van",
                "reason": "Heavy load but truck not accessible"
            }
    
    # Medium weight logic
    if weight_kg > 15 or volumetric_weight > 12:
        return {
            "recommendation": "USE_VAN",
            "suggested_vehicle": "Van",
            "reason": "Moderate shipment volume"
        }
    
    # Default fallback - bike for better last-mile
    return {
        "recommendation": "USE_BIKE",
        "suggested_vehicle": "Bike",
        "reason": "Better last-mile accessibility"
    }


def hyper_local_vehicle_check(
    area_type: str,
    road_accessibility: str,
    assigned_vehicle: str,
    weight_kg: float,
    volumetric_weight: float,
    vehicle_capacity: dict
) -> dict:
    """
    End-to-end vehicle feasibility check with recommendation engine.
    
    Parameters:
        area_type (str): Old City / Planned / Semi-Urban / Rural
        road_accessibility (str): Narrow / Medium / Wide
        assigned_vehicle (str): Currently assigned vehicle type
        weight_kg (float): Shipment weight
        volumetric_weight (float): Volumetric weight
        vehicle_capacity (dict): {
            "max_load_kg": float,
            "max_volume_cm3": float
        }
    
    Returns:
        dict: {
            "vehicle_status": "APPROVED" | "REJECTED",
            "final_vehicle": Vehicle to use,
            "action": Action to take,
            "reason": Explanation (if rejected),
            "area_type": Input area type,
            "road_accessibility": Input road accessibility,
            "assigned_vehicle": Original assignment,
            "weight_kg": Shipment weight
        }
    """
    # Check if assigned vehicle is allowed in area/road
    feasible = is_vehicle_allowed(
        area_type, 
        road_accessibility, 
        assigned_vehicle
    )
    
    # Check if shipment fits in vehicle capacity
    capacity_fit = capacity_ok(
        weight_kg,
        volumetric_weight,
        vehicle_capacity["max_load_kg"],
        vehicle_capacity["max_volume_cm3"]
    )
    
    # If both checks pass, approve
    if feasible and capacity_fit:
        return {
            "vehicle_status": "APPROVED",
            "final_vehicle": assigned_vehicle,
            "action": "PROCEED",
            "area_type": area_type,
            "road_accessibility": road_accessibility,
            "assigned_vehicle": assigned_vehicle,
            "weight_kg": weight_kg
        }
    
    # If failed, get recommendation
    recommendation = recommend_alternative(
        area_type,
        road_accessibility,
        weight_kg,
        volumetric_weight
    )
    
    # Determine rejection reason
    if not feasible and not capacity_fit:
        reason = f"{recommendation['reason']} + Capacity exceeded"
    elif not feasible:
        reason = recommendation['reason']
    else:
        reason = "Vehicle capacity exceeded"
    
    return {
        "vehicle_status": "REJECTED",
        "final_vehicle": recommendation["suggested_vehicle"],
        "action": recommendation["recommendation"],
        "reason": reason,
        "area_type": area_type,
        "road_accessibility": road_accessibility,
        "assigned_vehicle": assigned_vehicle,
        "weight_kg": weight_kg
    }


def get_vehicle_capacity(vehicle_type: str) -> dict:
    """
    Get standard vehicle capacity specifications.
    
    Parameters:
        vehicle_type (str): Bike / Van / Truck
    
    Returns:
        dict: Capacity specifications
    """
    capacities = {
        "Bike": {
            "max_load_kg": 20,
            "max_volume_cm3": 15000
        },
        "Van": {
            "max_load_kg": 50,
            "max_volume_cm3": 40000
        },
        "Truck": {
            "max_load_kg": 200,
            "max_volume_cm3": 150000
        }
    }
    
    return capacities.get(vehicle_type, capacities["Bike"])


def should_split_delivery(result: dict) -> bool:
    """
    Check if delivery should be split based on vehicle check result.
    
    Parameters:
        result (dict): Output from hyper_local_vehicle_check()
    
    Returns:
        bool: True if split delivery recommended
    """
    return result.get("action") == "SPLIT_DELIVERY"
