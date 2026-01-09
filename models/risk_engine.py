"""
Risk Scoring Engine - Core Intelligence Module

Purpose: Quantify delivery risk BEFORE dispatch
Output: Risk Score (0-100) + Risk Bucket (Low/Medium/High)
Approach: Explainable, rule-based, tunable

Risk = Probability of: Delay | Failure | Customer Dissatisfaction
Risk ≠ ETA Prediction
"""

def calculate_risk_score(
    weight_kg,
    volumetric_weight,
    payment_type,
    priority_flag,
    area_type,
    road_accessibility,
    address_confidence_score,
    weather_severity,
    weather_impact_factor
):
    """
    Calculate delivery risk score based on multiple factors.
    
    Parameters:
        weight_kg (float): Package weight in kg
        volumetric_weight (float): Volumetric weight calculation
        payment_type (str): "COD" or "Prepaid"
        priority_flag (int): 1 if priority, 0 otherwise
        area_type (str): "Old City", "Urban", "Semi-Urban", "Rural"
        road_accessibility (str): "Wide", "Medium", "Narrow"
        address_confidence_score (float): 0-100 score
        weather_severity (str): "Low", "Medium", "High"
        weather_impact_factor (float): Weather impact multiplier
    
    Returns:
        int: Risk score between 0-100
    """
    risk = 0

    # 1️⃣ Payment Risk (COD)
    if payment_type == "COD":
        risk += 15

    # 2️⃣ Weight / Volume Risk
    if volumetric_weight > 15:
        risk += 10
    if weight_kg > 10:
        risk += 5

    # 3️⃣ Area Risk
    if area_type == "Old City":
        risk += 15
    elif area_type == "Semi-Urban":
        risk += 8
    elif area_type == "Rural":
        risk += 12

    # 4️⃣ Road Accessibility
    if road_accessibility == "Narrow":
        risk += 15
    elif road_accessibility == "Medium":
        risk += 7

    # 5️⃣ Address Confidence
    if address_confidence_score < 60:
        risk += 15
    elif address_confidence_score < 80:
        risk += 7

    # 6️⃣ Weather Impact
    if weather_severity == "High":
        risk += weather_impact_factor * 0.3
    elif weather_severity == "Medium":
        risk += weather_impact_factor * 0.15

    # 7️⃣ Priority Dampening
    if priority_flag == 1:
        risk -= 5  # priority shipments get more care

    # Clamp score to 0-100 range
    risk = max(0, min(100, int(risk)))

    return risk


def risk_bucket(risk_score):
    """
    Map risk score to risk bucket category.
    
    Parameters:
        risk_score (int): Risk score 0-100
    
    Returns:
        str: "Low", "Medium", or "High"
    """
    if risk_score <= 30:
        return "Low"
    elif risk_score <= 60:
        return "Medium"
    else:
        return "High"
