"""
Notification Utilities - Handle system notifications and alerts
"""

import streamlit as st
from datetime import datetime
from typing import Dict, List


def show_success(message: str):
    """Display success notification"""
    st.success(f"✅ {message}")


def show_error(message: str):
    """Display error notification"""
    st.error(f"❌ {message}")


def show_warning(message: str):
    """Display warning notification"""
    st.warning(f"⚠️ {message}")


def show_info(message: str):
    """Display info notification"""
    st.info(f"ℹ️ {message}")


def show_decision_notification(decision: str, reasons: List[str]):
    """
    Display notification based on AI decision
    
    Args:
        decision: DISPATCH, DELAY, or RESCHEDULE
        reasons: List of reasons for the decision
    """
    if decision == "DISPATCH":
        st.success("✅ **Ready for Dispatch!**")
        st.info("Your shipment has been cleared for immediate processing.")
    
    elif decision == "DELAY":
        st.warning("⏸️ **Delay Recommended**")
        st.markdown("**Reasons:**")
        for reason in reasons:
            st.markdown(f"- {reason}")
        st.info("💡 A manager will review this shipment. Customer will be notified if delay is confirmed.")
    
    else:  # RESCHEDULE
        st.error("🔄 **Reschedule Required**")
        st.markdown("**Issues Detected:**")
        for reason in reasons:
            st.markdown(f"- {reason}")
        st.warning("⚠️ Please contact customer for clarification or reschedule delivery.")


def show_risk_alert(risk_score: float, risk_bucket: str):
    """
    Display risk alert based on score
    
    Args:
        risk_score: Risk score (0-100)
        risk_bucket: Low, Medium, or High
    """
    if risk_bucket == "Low":
        st.success(f"🟢 **Low Risk** - Score: {risk_score:.0f}/100")
    elif risk_bucket == "Medium":
        st.warning(f"🟡 **Medium Risk** - Score: {risk_score:.0f}/100")
    else:
        st.error(f"🔴 **High Risk** - Score: {risk_score:.0f}/100")


def show_address_confidence_alert(confidence_score: float, needs_clarification: bool):
    """
    Display address confidence alert
    
    Args:
        confidence_score: Confidence score (0-100)
        needs_clarification: Whether address needs clarification
    """
    if confidence_score >= 80:
        st.success(f"🗺️ **High Address Confidence** - {confidence_score:.0f}%")
    elif confidence_score >= 60:
        st.info(f"🗺️ **Moderate Address Confidence** - {confidence_score:.0f}%")
    else:
        st.warning(f"🗺️ **Low Address Confidence** - {confidence_score:.0f}%")
        if needs_clarification:
            st.error("⚠️ Address clarification required before dispatch")


def show_weather_alert(severity: str, condition: str):
    """
    Display weather alert
    
    Args:
        severity: Low, Medium, or High
        condition: Weather condition description
    """
    if severity == "High":
        st.error(f"🌧️ **Severe Weather Alert** - {condition}")
        st.warning("High impact on delivery. Consider delaying dispatch.")
    elif severity == "Medium":
        st.warning(f"🌤️ **Moderate Weather** - {condition}")
        st.info("Some impact on delivery timing expected.")
    else:
        st.success(f"☀️ **Clear Weather** - {condition}")


def show_override_confirmation(shipment_id: str, original_decision: str, new_decision: str, reason: str):
    """
    Display override confirmation
    
    Args:
        shipment_id: Shipment ID
        original_decision: AI's original decision
        new_decision: Manager's override decision
        reason: Reason for override
    """
    st.success("✋ **Override Applied Successfully**")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Original AI Decision:**")
        st.code(original_decision)
    with col2:
        st.markdown("**Your Override:**")
        st.code(new_decision)
    
    st.info(f"📝 **Reason:** {reason}")
    st.markdown(f"🔒 Shipment `{shipment_id}` is now locked to prevent AI re-evaluation")


def show_customer_notification_sent(shipment_id: str, channel: str):
    """
    Display customer notification confirmation
    
    Args:
        shipment_id: Shipment ID
        channel: Communication channel (SMS, WhatsApp, Email)
    """
    st.success(f"📲 Customer notification sent via {channel}")
    st.info(f"Shipment {shipment_id} - Customer has been informed of the status")


def create_toast(message: str, icon: str = "✅"):
    """
    Create a toast notification (uses Streamlit's toast feature)
    
    Args:
        message: Notification message
        icon: Emoji icon for the toast
    """
    st.toast(f"{icon} {message}", icon=icon)


def show_validation_errors(errors: List[str]):
    """
    Display validation errors
    
    Args:
        errors: List of validation error messages
    """
    st.error("❌ **Validation Errors:**")
    for error in errors:
        st.markdown(f"- {error}")


def show_system_message(title: str, message: str, type: str = "info"):
    """
    Display formatted system message
    
    Args:
        title: Message title
        message: Message content
        type: info, warning, error, success
    """
    if type == "success":
        st.success(f"**{title}**\n\n{message}")
    elif type == "warning":
        st.warning(f"**{title}**\n\n{message}")
    elif type == "error":
        st.error(f"**{title}**\n\n{message}")
    else:
        st.info(f"**{title}**\n\n{message}")
