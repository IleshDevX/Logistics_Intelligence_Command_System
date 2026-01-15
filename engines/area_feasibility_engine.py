# engines/area_feasibility_engine.py

import pandas as pd
from config import DATA_PATH


def evaluate_area_feasibility(shipment: dict):
    """
    Determines last-mile feasibility based on area constraints.
    Returns ALLOW / WARN / BLOCK with explanation.
    """

    # Load area feasibility master
    df = pd.read_csv(f"{DATA_PATH}/area_feasibility_master.csv")

    city = shipment["destination_city"]
    area_type = shipment["area_type"]

    # Match rows by city + area_type
    matches = df[
        (df["city"].str.lower() == city.lower()) &
        (df["area_type"] == area_type)
    ]

    # If no data found → be cautious
    if matches.empty:
        return {
            "feasibility_status": "WARN",
            "difficulty_score": 3,
            "reason": "No locality data found. Manual review advised."
        }

    # Take average difficulty (simulate locality aggregation)
    avg_difficulty = int(matches["last_mile_difficulty"].mean())
    congestion = matches["congestion_level"].mode()[0]
    heavy_allowed = matches["heavy_vehicle_allowed"].mode()[0]

    # Decision rules
    if avg_difficulty >= 4 and congestion == "HIGH":
        status = "BLOCK"
        reason = "High congestion and difficult last-mile access."
    elif avg_difficulty >= 3:
        status = "WARN"
        reason = "Moderate last-mile difficulty."
    else:
        status = "ALLOW"
        reason = "Area suitable for delivery."

    return {
        "feasibility_status": status,
        "difficulty_score": avg_difficulty,
        "heavy_vehicle_allowed": bool(heavy_allowed),
        "reason": reason
    }
