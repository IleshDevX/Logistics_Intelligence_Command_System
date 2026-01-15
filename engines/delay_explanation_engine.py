# engines/delay_explanation_engine.py

def generate_delay_explanation(
    risk_result: dict,
    area_result: dict,
    weather_result: dict,
    vehicle_result: dict,
    priority_result: dict
):
    """
    Generates human-readable explanation for delivery delay risk.
    """

    reasons = []

    # Area contribution
    if area_result["feasibility_status"] == "BLOCK":
        reasons.append("Severe last-mile access issues in destination area.")
    elif area_result["feasibility_status"] == "WARN":
        reasons.append("Moderate last-mile difficulty in destination area.")

    if area_result.get("difficulty_score", 0) >= 4:
        reasons.append("High congestion and narrow road conditions.")

    # Weather contribution
    if weather_result["severity"] == "HIGH":
        reasons.append("Severe weather conditions affecting delivery.")
    elif weather_result["severity"] == "MODERATE":
        reasons.append("Adverse weather may slow down delivery.")

    # Vehicle contribution
    if vehicle_result["vehicle_status"] == "REJECT":
        reasons.append("Selected vehicle is not suitable for this delivery.")
    elif vehicle_result["vehicle_status"] == "WARN":
        reasons.append("Vehicle suitability issues may impact last-mile delivery.")

    # Priority signal (ML soft explanation)
    if priority_result["priority"] == "HIGH":
        reasons.append("High-priority shipment increases operational sensitivity.")

    # If nothing triggered
    if not reasons:
        reasons.append("No significant risk factors detected.")

    # Rank reasons (keep top 3)
    top_reasons = reasons[:3]

    # Summary sentence
    if risk_result["risk_band"] == "HIGH":
        summary = "High delay risk due to multiple compounding factors."
    elif risk_result["risk_band"] == "MEDIUM":
        summary = "Moderate delay risk due to some operational constraints."
    else:
        summary = "Low delay risk with no major operational issues."

    return {
        "risk_band": risk_result["risk_band"],
        "summary": summary,
        "top_reasons": top_reasons
    }
