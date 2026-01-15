# engines/risk_scoring_engine.py

import numpy as np


def compute_risk_score(
    shipment: dict,
    area_result: dict,
    weather_result: dict,
    vehicle_result: dict,
    priority_result: dict
):
    """
    Computes final delivery risk score and band.
    """

    risk_score = 0

    # 1. Distance-based risk
    if shipment["distance_km"] > 500:
        risk_score += 30
    elif shipment["distance_km"] > 100:
        risk_score += 20
    else:
        risk_score += 10

    # 2. Area-based risk
    risk_score += area_result["difficulty_score"] * 5

    if area_result["feasibility_status"] == "BLOCK":
        risk_score += 25
    elif area_result["feasibility_status"] == "WARN":
        risk_score += 15

    # 3. Weather-based risk
    risk_score += weather_result["risk_adjustment"]

    # 4. Vehicle feasibility risk
    if vehicle_result["vehicle_status"] == "REJECT":
        risk_score += 30
    elif vehicle_result["vehicle_status"] == "WARN":
        risk_score += 15

    # Normalize rule-based risk (0–100)
    rule_risk = min(risk_score, 100)

    # 5. ML-based soft risk (priority proxy)
    if priority_result["priority"] == "HIGH":
        ml_risk = 70
    elif priority_result["priority"] == "MEDIUM":
        ml_risk = 40
    else:
        ml_risk = 20

    # 6. Final combined risk
    final_risk = int(0.7 * rule_risk + 0.3 * ml_risk)

    # Risk band
    if final_risk >= 70:
        band = "HIGH"
    elif final_risk >= 40:
        band = "MEDIUM"
    else:
        band = "LOW"

    return {
        "risk_score": final_risk,
        "risk_band": band,
        "rule_risk_component": rule_risk,
        "ml_risk_component": ml_risk
    }
