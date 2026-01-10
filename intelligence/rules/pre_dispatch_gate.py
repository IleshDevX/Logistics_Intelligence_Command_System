"""
Pre-Dispatch Decision Gate - Risk-Aware Control Logic

Purpose: Decide if a shipment should be dispatched, delayed, or rescheduled
Input: Risk score, Weather impact, Address confidence (from Steps 6, 7, 8)
Output: Decision (DISPATCH/DELAY/RESCHEDULE) + Reasons

Decision Philosophy:
- One HIGH signal is enough to stop blind dispatch
- Prefer delay + transparency over failure
- Reschedule requires customer involvement

Used before dispatch to prevent:
- Failed deliveries
- Customer dissatisfaction
- Resource waste
"""

# Business Rule Thresholds (Easy to tune, easy to justify)
RISK_THRESHOLD = 60
ADDRESS_CONFIDENCE_THRESHOLD = 60
WEATHER_HIGH_THRESHOLD = 60


def pre_dispatch_decision(
    risk_score: float,
    weather_impact_factor: float,
    address_confidence_score: float
) -> dict:
    """
    Make pre-dispatch decision based on combined intelligence.
    
    Parameters:
        risk_score (float): Risk score 0-100 from risk engine
        weather_impact_factor (float): Weather impact 0-100 from weather engine
        address_confidence_score (float): Address confidence 0-100 from address intelligence
    
    Returns:
        dict: {
            "decision": "DISPATCH" | "DELAY" | "RESCHEDULE",
            "reasons": [list of reasons],
            "risk_score": float,
            "weather_impact_factor": float,
            "address_confidence_score": float
        }
    
    Decision Logic:
        - DISPATCH: All signals safe (no high risk)
        - DELAY: High risk OR high weather (temporary uncertainty, buffer ETA)
        - RESCHEDULE: Low address confidence (needs customer clarification)
    """
    reasons = []
    
    # Check each signal against thresholds
    if risk_score > RISK_THRESHOLD:
        reasons.append("High delivery risk")
    
    if weather_impact_factor > WEATHER_HIGH_THRESHOLD:
        reasons.append("Severe weather impact")
    
    if address_confidence_score < ADDRESS_CONFIDENCE_THRESHOLD:
        reasons.append("Low address confidence")
    
    # Decision rules (priority order matters)
    if len(reasons) == 0:
        # All signals safe - proceed normally
        decision = "DISPATCH"
    
    elif "Low address confidence" in reasons:
        # Address issue requires customer interaction
        decision = "RESCHEDULE"
    
    else:
        # Risk or weather issues - delay with buffer
        decision = "DELAY"
    
    return {
        "decision": decision,
        "reasons": reasons,
        "risk_score": risk_score,
        "weather_impact_factor": weather_impact_factor,
        "address_confidence_score": address_confidence_score
    }


def get_decision_explanation(decision_result: dict) -> str:
    """
    Generate human-readable explanation for the decision.
    
    Parameters:
        decision_result (dict): Output from pre_dispatch_decision()
    
    Returns:
        str: Human-readable explanation
    """
    decision = decision_result["decision"]
    reasons = decision_result["reasons"]
    
    if decision == "DISPATCH":
        return "✅ DISPATCH: All signals safe. Proceed with normal delivery."
    
    elif decision == "DELAY":
        reason_text = " and ".join(reasons)
        return f"⏸ DELAY: {reason_text}. Buffer ETA and inform customer of potential delay."
    
    elif decision == "RESCHEDULE":
        return "🔁 RESCHEDULE: Low address confidence. Contact customer for address clarification before dispatch."
    
    return "Unknown decision"


def should_dispatch(decision_result: dict) -> bool:
    """
    Simple boolean check: Can we dispatch now?
    
    Parameters:
        decision_result (dict): Output from pre_dispatch_decision()
    
    Returns:
        bool: True if DISPATCH, False otherwise
    """
    return decision_result["decision"] == "DISPATCH"


def requires_customer_contact(decision_result: dict) -> bool:
    """
    Check if customer contact is required before proceeding.
    
    Parameters:
        decision_result (dict): Output from pre_dispatch_decision()
    
    Returns:
        bool: True if RESCHEDULE (customer interaction needed)
    """
    return decision_result["decision"] == "RESCHEDULE"


def get_action_items(decision_result: dict) -> list:
    """
    Generate action items for operations team based on decision.
    
    Parameters:
        decision_result (dict): Output from pre_dispatch_decision()
    
    Returns:
        list: Action items for ops team
    """
    decision = decision_result["decision"]
    reasons = decision_result["reasons"]
    
    actions = []
    
    if decision == "DISPATCH":
        actions.append("Proceed with dispatch")
        actions.append("Follow normal delivery process")
    
    elif decision == "DELAY":
        actions.append("Hold shipment at hub")
        actions.append("Buffer ETA by 1.5-2x normal time")
        actions.append("Send pre-dispatch alert to customer")
        
        if "Severe weather impact" in reasons:
            actions.append("Monitor weather conditions")
            actions.append("Reassess after weather improves")
        
        if "High delivery risk" in reasons:
            actions.append("Assign experienced rider")
            actions.append("Consider alternate route")
    
    elif decision == "RESCHEDULE":
        actions.append("DO NOT DISPATCH")
        actions.append("Contact customer via WhatsApp/App/Call")
        actions.append("Request address clarification or landmark details")
        actions.append("Update address in system before reattempt")
    
    return actions
