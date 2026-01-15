# engines/vehicle_feasibility_engine.py

import pandas as pd
from config import DATA_PATH


def evaluate_vehicle_feasibility(shipment: dict):
    """
    Determines whether the selected vehicle is feasible
    for last-mile delivery.
    """

    df = pd.read_csv(f"{DATA_PATH}/vehicle_master.csv")

    # Default vehicle suggestion based on weight
    if shipment["weight_kg"] <= 5:
        vehicle = "BIKE"
    elif shipment["weight_kg"] <= 50:
        vehicle = "VAN"
    else:
        vehicle = "TRUCK"

    area_type = shipment["area_type"]
    address_type = shipment["address_type"]
    weight = shipment["weight_kg"]
    volume = shipment["volume_cm3"]

    vehicle_row = df[df["vehicle_type"] == vehicle]

    # If vehicle not found
    if vehicle_row.empty:
        return {
            "vehicle_status": "WARN",
            "selected_vehicle": vehicle,
            "suggested_vehicle": "VAN",
            "reason": "Unknown vehicle type. Default review required."
        }

    row = vehicle_row.iloc[0]

    # HARD REJECTION RULES
    if area_type == "OLD_CITY" and vehicle == "TRUCK":
        return {
            "vehicle_status": "REJECT",
            "selected_vehicle": vehicle,
            "suggested_vehicle": "BIKE",
            "reason": "Trucks are not allowed in old city narrow lanes."
        }

    if weight > row["max_weight_kg"]:
        return {
            "vehicle_status": "REJECT",
            "selected_vehicle": vehicle,
            "suggested_vehicle": "TRUCK",
            "reason": "Vehicle cannot carry the shipment weight."
        }

    if volume > row["max_volume_cm3"]:
        return {
            "vehicle_status": "WARN",
            "selected_vehicle": vehicle,
            "suggested_vehicle": "SPLIT",
            "reason": "Shipment volume exceeds vehicle capacity. Split delivery advised."
        }

    # WARNING RULES
    if area_type not in row["allowed_area_type"]:
        return {
            "vehicle_status": "WARN",
            "selected_vehicle": vehicle,
            "suggested_vehicle": "VAN",
            "reason": "Vehicle may face access issues in this area."
        }

    if address_type not in row["allowed_address_type"]:
        return {
            "vehicle_status": "WARN",
            "selected_vehicle": vehicle,
            "suggested_vehicle": "VAN",
            "reason": "Address type may not be ideal for selected vehicle."
        }

    # ACCEPT
    return {
        "vehicle_status": "ACCEPT",
        "selected_vehicle": vehicle,
        "suggested_vehicle": vehicle,
        "reason": "Vehicle is suitable for this delivery."
    }
