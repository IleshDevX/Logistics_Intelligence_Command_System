"""
Customer Notification & Reschedule Engine - Pre-Dispatch Communication

Purpose: Proactively notify customers BEFORE dispatch when delays/issues occur
Input: Decision from Step 9 (Pre-Dispatch Gate) + Shipment details
Output: Customer notification + Response capture

Philosophy:
- Notify BEFORE inconvenience, not after
- Be HONEST about reasons
- Offer ACTIONABLE choices
- Customers forgive delay, NOT silence

Triggered by:
- Step 9 Decision = DELAY → Inform customer of adjusted timeline
- Step 9 Decision = RESCHEDULE → Ask customer to confirm/choose new time
- Step 9 Decision = DISPATCH → No notification (normal flow)
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional


def generate_message(shipment_id: str, decision: str, reasons: List[str]) -> str:
    """
    Generate customer-facing message based on decision and reasons.
    
    Message Principles:
        - Honest: State real reason
        - Short: Under 160 characters ideal (SMS-friendly)
        - Reason-based: Explain WHY
        - Action-oriented: Tell customer what happens next
    
    Parameters:
        shipment_id (str): Unique shipment identifier
        decision (str): DISPATCH / DELAY / RESCHEDULE
        reasons (list): Human-readable reasons from decision gate
    
    Returns:
        str: Customer notification message
    
    Examples:
        DELAY: "Your delivery may be delayed due to severe weather. 
                We're adjusting delivery window for safe delivery."
        
        RESCHEDULE: "We need address confirmation due to low address confidence. 
                     Please choose a new delivery time."
    """
    base = f"Update for Shipment {shipment_id}: "
    
    if decision == "DELAY":
        # Customer is informed but no action needed
        message = (
            base +
            "Your delivery may be delayed due to " +
            ", ".join(reasons) +
            ". We are adjusting the delivery window to ensure safe delivery. "
            "You'll receive updated ETA shortly."
        )
    
    elif decision == "RESCHEDULE":
        # Customer action required
        message = (
            base +
            "We need your confirmation due to " +
            ", ".join(reasons) +
            ". Please choose a new delivery time or provide additional details. "
            "This helps us ensure successful delivery."
        )
    
    else:  # DISPATCH
        # All good - optional confirmation message
        message = (
            base +
            "Your shipment is on track for dispatch. "
            "Expected delivery as scheduled."
        )
    
    return message


def notify_customer(
    shipment_id: str,
    decision: str,
    reasons: List[str],
    channel: str = "console"
) -> Optional[Dict]:
    """
    Send notification to customer via specified channel.
    
    Parameters:
        shipment_id (str): Unique shipment identifier
        decision (str): DISPATCH / DELAY / RESCHEDULE
        reasons (list): Reasons for decision
        channel (str): "console" / "whatsapp" / "sms" / "email"
    
    Returns:
        dict: Notification record or None if no notification needed
    
    Channels:
        - console: Print to screen (development/testing)
        - whatsapp: Mock WhatsApp API (production-ready placeholder)
        - sms: Mock SMS gateway
        - email: Mock email service
    """
    # Skip notification for normal dispatch (optional)
    if decision == "DISPATCH":
        return None
    
    # Generate message
    message = generate_message(shipment_id, decision, reasons)
    
    # Send via channel (mocked for prototype)
    if channel == "console":
        print("📲 CUSTOMER NOTIFICATION SENT")
        print(f"   Channel: Console/Log")
        print(f"   Message: {message}")
    
    elif channel == "whatsapp":
        # Mock WhatsApp Business API
        print("📲 WHATSAPP NOTIFICATION SENT (Mocked)")
        print(f"   To: +91-XXXX-XXXX-XX (from shipment DB)")
        print(f"   Message: {message}")
        # In production: whatsapp_api.send_message(phone, message)
    
    elif channel == "sms":
        # Mock SMS gateway
        print("📲 SMS NOTIFICATION SENT (Mocked)")
        print(f"   Message: {message}")
        # In production: sms_gateway.send(phone, message)
    
    elif channel == "email":
        # Mock email service
        print("📲 EMAIL NOTIFICATION SENT (Mocked)")
        print(f"   Subject: Delivery Update - {shipment_id}")
        print(f"   Body: {message}")
        # In production: email_service.send(to, subject, body)
    
    # Return notification record for logging
    return {
        "shipment_id": shipment_id,
        "decision": decision,
        "message": message,
        "channel": channel,
        "timestamp": datetime.now().isoformat(),
        "status": "sent"
    }


def reschedule_options() -> List[str]:
    """
    Generate reschedule options for customer.
    
    Returns:
        list: Available reschedule options
    
    Options:
        - Deliver tomorrow: Next day delivery
        - Deliver in evening slot: 6-9 PM today/tomorrow
        - Choose custom date: Customer picks specific date
        - Provide more address details: For address clarity issues
    """
    return [
        "Deliver tomorrow",
        "Deliver in evening slot (6-9 PM)",
        "Choose custom date",
        "Provide more address details"
    ]


def capture_customer_response(option_selected: str, shipment_id: str) -> Dict:
    """
    Capture and log customer's reschedule choice.
    
    Parameters:
        option_selected (str): Customer's choice
        shipment_id (str): Shipment identifier
    
    Returns:
        dict: Response record for database/learning
    
    Learning Value:
        - Track which options customers prefer
        - Identify patterns (e.g., address issues → need details)
        - Improve future predictions
    """
    print(f"📩 CUSTOMER RESPONSE CAPTURED")
    print(f"   Shipment: {shipment_id}")
    print(f"   Choice: {option_selected}")
    
    # Calculate new delivery date based on choice
    new_delivery_date = None
    if "tomorrow" in option_selected.lower():
        new_delivery_date = (datetime.now() + timedelta(days=1)).date().isoformat()
    elif "evening" in option_selected.lower():
        new_delivery_date = datetime.now().date().isoformat()
    
    return {
        "shipment_id": shipment_id,
        "customer_choice": option_selected,
        "new_delivery_date": new_delivery_date,
        "response_timestamp": datetime.now().isoformat(),
        "response_source": "customer_direct"
    }


def pre_dispatch_customer_flow(
    shipment_id: str,
    decision: str,
    reasons: List[str],
    channel: str = "console",
    mock_customer_choice: int = 0
) -> Dict:
    """
    End-to-end pre-dispatch customer communication flow.
    
    Flow:
        1. Check decision from Step 9 gate
        2. Send notification if needed (DELAY/RESCHEDULE)
        3. If RESCHEDULE → Present options → Capture response
        4. Return final action for system
    
    Parameters:
        shipment_id (str): Unique shipment identifier
        decision (str): DISPATCH / DELAY / RESCHEDULE (from Step 9)
        reasons (list): Reasons for decision (from Step 9)
        channel (str): Notification channel
        mock_customer_choice (int): Index of option (for testing)
    
    Returns:
        dict: {
            "final_action": Action to take,
            "notification": Notification record,
            "customer_response": Response record (if applicable)
        }
    
    Integration:
        Step 9 Output → THIS MODULE → Updated shipment status
    """
    # Send notification
    notification = notify_customer(shipment_id, decision, reasons, channel)
    
    # Handle RESCHEDULE flow
    if decision == "RESCHEDULE":
        print("\n🔄 RESCHEDULE FLOW INITIATED")
        
        # Show options to customer
        options = reschedule_options()
        print(f"   Available options:")
        for i, opt in enumerate(options):
            print(f"      {i+1}. {opt}")
        
        # Mock customer selection (in production: API/UI input)
        customer_choice = options[mock_customer_choice]
        response = capture_customer_response(customer_choice, shipment_id)
        
        return {
            "final_action": "RESCHEDULED",
            "notification": notification,
            "customer_response": response,
            "next_step": "Update shipment delivery date and re-run decision gate"
        }
    
    # Handle DELAY flow
    if decision == "DELAY":
        print("\n⏸ DELAY FLOW INITIATED")
        print(f"   Customer informed, no action required")
        print(f"   System will buffer ETA automatically")
        
        return {
            "final_action": "DELAY_ACCEPTED",
            "notification": notification,
            "customer_response": None,
            "next_step": "Proceed with buffered ETA (from weather/risk engine)"
        }
    
    # Handle DISPATCH flow (normal)
    print("\n✅ DISPATCH FLOW")
    print(f"   No customer notification needed")
    print(f"   Shipment proceeding normally")
    
    return {
        "final_action": "DISPATCHED",
        "notification": None,
        "customer_response": None,
        "next_step": "Assign rider and dispatch"
    }


def get_notification_template(decision: str, reason_type: str) -> str:
    """
    Get pre-defined template for specific decision-reason combinations.
    
    Parameters:
        decision (str): DELAY / RESCHEDULE
        reason_type (str): Type of reason (weather/address/risk)
    
    Returns:
        str: Template string
    
    Use Case:
        Maintain consistent messaging across channels
        A/B test different message formats
        Multi-language support (future)
    """
    templates = {
        "DELAY_weather": "Weather conditions may cause delivery delays. We're monitoring closely for safe delivery.",
        "DELAY_risk": "We're adjusting delivery schedule to ensure quality service. Updated ETA coming soon.",
        "RESCHEDULE_address": "We need to confirm delivery address details. Please provide landmark or alternate contact.",
        "RESCHEDULE_general": "We need your confirmation to proceed with delivery. Please choose a convenient time."
    }
    
    key = f"{decision}_{reason_type}"
    return templates.get(key, templates.get(f"{decision}_general", ""))


def should_notify_customer(decision: str, reasons: List[str]) -> bool:
    """
    Determine if customer notification is needed.
    
    Parameters:
        decision (str): Decision from gate
        reasons (list): Reasons
    
    Returns:
        bool: True if notification needed
    
    Rules:
        - DISPATCH → No notification (optional confirmation only)
        - DELAY → Always notify
        - RESCHEDULE → Always notify + action required
    """
    return decision in ["DELAY", "RESCHEDULE"]
