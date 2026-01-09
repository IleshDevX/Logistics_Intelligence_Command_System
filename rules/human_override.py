"""
Human Override System (Decision Authority Layer)
Step 15: Allow operations managers to override AI decisions with accountability

Philosophy:
- AI must NEVER be the final authority
- Overrides must be explicit, reasoned, logged, and traceable
- Manual locks prevent AI from re-evaluating locked shipments
"""

import pandas as pd
from datetime import datetime
import os

LOG_FILE = "logs/override_log.csv"

# Standardized override reasons (prevents random text, improves learning)
OVERRIDE_REASONS = [
    "Manager experience",
    "Local knowledge",
    "Temporary road closure",
    "High priority customer",
    "Operational constraint",
    "Weather cleared manually"
]

def apply_human_override(
    shipment_id: str,
    ai_decision: str,
    override_decision: str,
    override_reason: str
) -> dict:
    """
    Apply human override to AI-generated decision
    
    Args:
        shipment_id: Unique shipment identifier
        ai_decision: AI recommendation (DISPATCH/DELAY/RESCHEDULE)
        override_decision: Manager's decision (DISPATCH/DELAY/RESCHEDULE)
        override_reason: Must be from OVERRIDE_REASONS catalog
    
    Returns:
        dict with status, final_decision, locked flag
    """
    
    # Validate override reason
    if override_reason not in OVERRIDE_REASONS:
        return {
            "status": "ERROR",
            "message": f"Invalid reason. Must be one of: {OVERRIDE_REASONS}",
            "final_decision": ai_decision
        }
    
    # Validate decisions
    valid_decisions = ["DISPATCH", "DELAY", "RESCHEDULE"]
    if ai_decision not in valid_decisions or override_decision not in valid_decisions:
        return {
            "status": "ERROR",
            "message": f"Invalid decision. Must be one of: {valid_decisions}",
            "final_decision": ai_decision
        }
    
    # If AI and manager agree, no override needed
    if ai_decision == override_decision:
        return {
            "status": "NO_OVERRIDE",
            "final_decision": ai_decision,
            "locked": False,
            "message": "Manager agrees with AI decision"
        }
    
    # Create override record
    record = {
        "shipment_id": shipment_id,
        "ai_decision": ai_decision,
        "override_decision": override_decision,
        "override_reason": override_reason,
        "timestamp": datetime.utcnow().isoformat(),
        "manual_lock": True
    }
    
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    # Log the override
    try:
        df = pd.read_csv(LOG_FILE)
        df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
    except FileNotFoundError:
        df = pd.DataFrame([record])
    
    df.to_csv(LOG_FILE, index=False)
    
    return {
        "status": "OVERRIDDEN",
        "final_decision": override_decision,
        "locked": True,
        "message": f"AI decision '{ai_decision}' overridden to '{override_decision}'"
    }


def is_locked(shipment_id: str) -> bool:
    """
    Check if a shipment has a manual lock (human override)
    
    Args:
        shipment_id: Unique shipment identifier
    
    Returns:
        bool: True if shipment is locked by human override
    
    Usage:
        Every decision engine should check this BEFORE acting:
        
        if is_locked(shipment_id):
            return "LOCKED - Respect human decision"
    """
    try:
        df = pd.read_csv(LOG_FILE)
        locked_shipments = df[df["manual_lock"] == True]["shipment_id"].values
        return shipment_id in locked_shipments
    except FileNotFoundError:
        return False


def get_override_history(shipment_id: str = None) -> pd.DataFrame:
    """
    Get override history for analysis and learning
    
    Args:
        shipment_id: Optional - get history for specific shipment
    
    Returns:
        DataFrame with override logs
    """
    try:
        df = pd.read_csv(LOG_FILE)
        if shipment_id:
            return df[df["shipment_id"] == shipment_id]
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=[
            "shipment_id", "ai_decision", "override_decision", 
            "override_reason", "timestamp", "manual_lock"
        ])


def get_override_stats() -> dict:
    """
    Get statistics about overrides for learning loop
    
    Returns:
        dict with override statistics
    """
    try:
        df = pd.read_csv(LOG_FILE)
        
        if len(df) == 0:
            return {
                "total_overrides": 0,
                "override_rate": 0,
                "most_common_reason": None,
                "ai_to_dispatch": 0,
                "ai_to_delay": 0,
                "ai_to_reschedule": 0
            }
        
        return {
            "total_overrides": len(df),
            "override_rate": len(df) / len(df),  # Would need total decisions for real rate
            "most_common_reason": df["override_reason"].mode()[0] if len(df) > 0 else None,
            "ai_to_dispatch": len(df[df["override_decision"] == "DISPATCH"]),
            "ai_to_delay": len(df[df["override_decision"] == "DELAY"]),
            "ai_to_reschedule": len(df[df["override_decision"] == "RESCHEDULE"]),
            "reason_distribution": df["override_reason"].value_counts().to_dict()
        }
    except FileNotFoundError:
        return {
            "total_overrides": 0,
            "override_rate": 0,
            "most_common_reason": None,
            "ai_to_dispatch": 0,
            "ai_to_delay": 0,
            "ai_to_reschedule": 0
        }


def unlock_shipment(shipment_id: str) -> dict:
    """
    Remove manual lock from a shipment (use with caution)
    
    Args:
        shipment_id: Unique shipment identifier
    
    Returns:
        dict with status
    """
    try:
        df = pd.read_csv(LOG_FILE)
        if shipment_id not in df["shipment_id"].values:
            return {
                "status": "NOT_FOUND",
                "message": f"No override found for {shipment_id}"
            }
        
        # Remove the override record
        df = df[df["shipment_id"] != shipment_id]
        df.to_csv(LOG_FILE, index=False)
        
        return {
            "status": "UNLOCKED",
            "message": f"Manual lock removed from {shipment_id}"
        }
    except FileNotFoundError:
        return {
            "status": "NOT_FOUND",
            "message": "No override log found"
        }
