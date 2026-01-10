"""
Delivery Execution & Live Tracking Simulation
Step 16: Simulates post-dispatch execution with status updates, tracking events, and alerts

Purpose:
- Simulate what happens AFTER dispatch is approved
- Generate tracking events (like real courier systems)
- Detect late packing / execution delays
- Trigger alerts to Ops + Customer

This completes the end-to-end lifecycle:
Input → Intelligence → Decision → Execution → Feedback
"""

import time
import pandas as pd
from datetime import datetime, timedelta
import os
import random

TRACKING_LOG = "logs/tracking_events.csv"

# Industry-standard status flow
STATUS_FLOW = [
    "CREATED",
    "PACKING",
    "DISPATCHED",
    "IN_TRANSIT",
    "OUT_FOR_DELIVERY",
    "DELIVERED"
]

# Expected time for each status (in minutes)
EXPECTED_TIME = {
    "CREATED": 0,
    "PACKING": 30,
    "DISPATCHED": 5,
    "IN_TRANSIT": 120,
    "OUT_FOR_DELIVERY": 60,
    "DELIVERED": 0
}

def log_event(shipment_id: str, status: str, remarks: str = ""):
    """
    Log a tracking event to CSV
    
    Args:
        shipment_id: Unique shipment identifier
        status: Current status
        remarks: Additional notes about the event
    """
    event = {
        "shipment_id": shipment_id,
        "status": status,
        "timestamp": datetime.utcnow().isoformat(),
        "remarks": remarks
    }
    
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    try:
        df = pd.read_csv(TRACKING_LOG)
        df = pd.concat([df, pd.DataFrame([event])], ignore_index=True)
    except FileNotFoundError:
        df = pd.DataFrame([event])
    
    df.to_csv(TRACKING_LOG, index=False)
    
    return event

def simulate_delivery(shipment_id: str, packing_delay: bool = False, delivery_delay: bool = False):
    """
    Simulate complete delivery lifecycle with realistic status progression
    
    Args:
        shipment_id: Unique shipment identifier
        packing_delay: If True, simulate late packing
        delivery_delay: If True, simulate delivery delay
    
    Returns:
        List of tracking events
    """
    events = []
    
    # Start: CREATED
    event = log_event(shipment_id, "CREATED", "Order confirmed, preparing for packing")
    events.append(event)
    time.sleep(0.3)  # Simulate time gap
    
    # PACKING phase
    if packing_delay:
        # Simulate packing taking too long
        event = log_event(
            shipment_id,
            "PACKING_DELAY",
            "Packing exceeded expected time - warehouse congestion"
        )
        events.append(event)
        time.sleep(0.5)
    
    event = log_event(shipment_id, "PACKING", "Item being packed")
    events.append(event)
    time.sleep(0.3)
    
    # DISPATCHED
    event = log_event(shipment_id, "DISPATCHED", "Shipment handed to courier")
    events.append(event)
    time.sleep(0.3)
    
    # IN_TRANSIT
    event = log_event(shipment_id, "IN_TRANSIT", "En route to destination city")
    events.append(event)
    time.sleep(0.3)
    
    # OUT_FOR_DELIVERY
    if delivery_delay:
        event = log_event(
            shipment_id,
            "DELIVERY_DELAY",
            "Delivery delayed - traffic congestion"
        )
        events.append(event)
        time.sleep(0.5)
    
    event = log_event(shipment_id, "OUT_FOR_DELIVERY", "Out for delivery by local courier")
    events.append(event)
    time.sleep(0.3)
    
    # DELIVERED
    event = log_event(shipment_id, "DELIVERED", "Package delivered successfully")
    events.append(event)
    
    return events

def check_late_packing(shipment_id: str) -> bool:
    """
    Check if shipment has late packing issues
    
    Args:
        shipment_id: Unique shipment identifier
    
    Returns:
        bool: True if packing delayed
    """
    try:
        df = pd.read_csv(TRACKING_LOG)
        
        # Check for PACKING_DELAY status
        packing_delays = df[
            (df["shipment_id"] == shipment_id) &
            (df["status"] == "PACKING_DELAY")
        ]
        
        return len(packing_delays) > 0
    
    except FileNotFoundError:
        return False

def check_delivery_delay(shipment_id: str) -> bool:
    """
    Check if shipment has delivery delay issues
    
    Args:
        shipment_id: Unique shipment identifier
    
    Returns:
        bool: True if delivery delayed
    """
    try:
        df = pd.read_csv(TRACKING_LOG)
        
        # Check for DELIVERY_DELAY status
        delivery_delays = df[
            (df["shipment_id"] == shipment_id) &
            (df["status"] == "DELIVERY_DELAY")
        ]
        
        return len(delivery_delays) > 0
    
    except FileNotFoundError:
        return False

def get_current_status(shipment_id: str) -> str:
    """
    Get current status of a shipment
    
    Args:
        shipment_id: Unique shipment identifier
    
    Returns:
        str: Current status or "NOT_FOUND"
    """
    try:
        df = pd.read_csv(TRACKING_LOG)
        
        shipment_events = df[df["shipment_id"] == shipment_id]
        
        if len(shipment_events) == 0:
            return "NOT_FOUND"
        
        # Get latest status
        latest_event = shipment_events.iloc[-1]
        return latest_event["status"]
    
    except FileNotFoundError:
        return "NOT_FOUND"

def trigger_execution_alert(shipment_id: str, issue_type: str) -> dict:
    """
    Trigger alerts for execution issues (Ops & Customer)
    
    Args:
        shipment_id: Unique shipment identifier
        issue_type: Type of issue (PACKING_DELAY, DELIVERY_DELAY, FAILED_ATTEMPT)
    
    Returns:
        dict: Alert details
    """
    alert = {
        "shipment_id": shipment_id,
        "issue_type": issue_type,
        "timestamp": datetime.utcnow().isoformat(),
        "ops_notified": False,
        "customer_notified": False
    }
    
    if issue_type == "PACKING_DELAY":
        print(f"🚨 OPS ALERT: Shipment {shipment_id} packing delayed")
        print(f"   Action: Check warehouse capacity, expedite packing")
        alert["ops_notified"] = True
        alert["message"] = "Packing delayed - warehouse congestion"
    
    if issue_type == "DELIVERY_DELAY":
        print(f"📲 CUSTOMER ALERT: Shipment {shipment_id} delivery delayed")
        print(f"   Action: Send proactive notification with updated ETA")
        alert["customer_notified"] = True
        alert["message"] = "Delivery delayed - traffic/weather conditions"
    
    if issue_type == "FAILED_ATTEMPT":
        print(f"📲 CUSTOMER ALERT: Delivery attempt failed for {shipment_id}")
        print(f"   Action: Schedule re-delivery, confirm address")
        alert["customer_notified"] = True
        alert["message"] = "Delivery attempt failed - customer unavailable"
    
    return alert

def run_execution_flow(shipment_id: str, packing_delay: bool = False, delivery_delay: bool = False):
    """
    Complete execution flow: simulate delivery + check for issues + trigger alerts
    
    Args:
        shipment_id: Unique shipment identifier
        packing_delay: Simulate late packing
        delivery_delay: Simulate delivery delay
    
    Returns:
        dict: Execution summary
    """
    # Simulate delivery
    events = simulate_delivery(shipment_id, packing_delay, delivery_delay)
    
    # Check for issues
    alerts = []
    
    if check_late_packing(shipment_id):
        alert = trigger_execution_alert(shipment_id, "PACKING_DELAY")
        alerts.append(alert)
    
    if check_delivery_delay(shipment_id):
        alert = trigger_execution_alert(shipment_id, "DELIVERY_DELAY")
        alerts.append(alert)
    
    # Get final status
    final_status = get_current_status(shipment_id)
    
    return {
        "shipment_id": shipment_id,
        "total_events": len(events),
        "final_status": final_status,
        "alerts_triggered": len(alerts),
        "alerts": alerts,
        "execution_completed": final_status == "DELIVERED"
    }

def get_tracking_history(shipment_id: str = None) -> pd.DataFrame:
    """
    Get tracking history for a shipment or all shipments
    
    Args:
        shipment_id: Optional - get history for specific shipment
    
    Returns:
        DataFrame with tracking events
    """
    try:
        df = pd.read_csv(TRACKING_LOG)
        
        if shipment_id:
            return df[df["shipment_id"] == shipment_id]
        
        return df
    
    except FileNotFoundError:
        return pd.DataFrame(columns=["shipment_id", "status", "timestamp", "remarks"])

def get_execution_stats() -> dict:
    """
    Get execution statistics for learning loop
    
    Returns:
        dict: Statistics about deliveries
    """
    try:
        df = pd.read_csv(TRACKING_LOG)
        
        # Count by status
        status_counts = df["status"].value_counts().to_dict()
        
        # Count unique shipments
        total_shipments = df["shipment_id"].nunique()
        
        # Count delivered shipments
        delivered = len(df[df["status"] == "DELIVERED"]["shipment_id"].unique())
        
        # Count delays
        packing_delays = len(df[df["status"] == "PACKING_DELAY"])
        delivery_delays = len(df[df["status"] == "DELIVERY_DELAY"])
        
        return {
            "total_shipments": total_shipments,
            "delivered_count": delivered,
            "delivery_rate": (delivered / total_shipments * 100) if total_shipments > 0 else 0,
            "packing_delays": packing_delays,
            "delivery_delays": delivery_delays,
            "total_delays": packing_delays + delivery_delays,
            "status_distribution": status_counts
        }
    
    except FileNotFoundError:
        return {
            "total_shipments": 0,
            "delivered_count": 0,
            "delivery_rate": 0,
            "packing_delays": 0,
            "delivery_delays": 0,
            "total_delays": 0,
            "status_distribution": {}
        }

def simulate_failed_delivery_attempt(shipment_id: str, reason: str = "Customer unavailable"):
    """
    Simulate a failed delivery attempt
    
    Args:
        shipment_id: Unique shipment identifier
        reason: Reason for failure
    """
    log_event(shipment_id, "FAILED_ATTEMPT", reason)
    trigger_execution_alert(shipment_id, "FAILED_ATTEMPT")
    
    # Schedule re-attempt
    log_event(shipment_id, "RE_ATTEMPT_SCHEDULED", "Delivery will be re-attempted")

def bulk_simulate_deliveries(count: int = 10, delay_probability: float = 0.2):
    """
    Simulate multiple deliveries for testing
    
    Args:
        count: Number of shipments to simulate
        delay_probability: Probability of delays (0.0 to 1.0)
    
    Returns:
        list: Execution summaries
    """
    results = []
    
    for i in range(count):
        shipment_id = f"SHP_EXEC_{i:03d}"
        
        # Randomly introduce delays
        packing_delay = random.random() < delay_probability
        delivery_delay = random.random() < delay_probability
        
        result = run_execution_flow(shipment_id, packing_delay, delivery_delay)
        results.append(result)
        
        print(f"✅ Simulated: {shipment_id} - Status: {result['final_status']}")
    
    return results
