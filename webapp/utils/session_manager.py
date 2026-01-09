"""
Session Manager - Handles session state and data persistence
"""

import streamlit as st
from datetime import datetime
from typing import Any, Dict, List


def init_session_state():
    """Initialize session state variables"""
    
    # Authentication
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if "user" not in st.session_state:
        st.session_state.user = None
    
    # Shipment data
    if "current_shipment" not in st.session_state:
        st.session_state.current_shipment = None
    
    if "shipment_history" not in st.session_state:
        st.session_state.shipment_history = []
    
    # Form state
    if "form_data" not in st.session_state:
        st.session_state.form_data = {}
    
    # Override state
    if "override_pending" not in st.session_state:
        st.session_state.override_pending = None
    
    # Notifications
    if "notifications" not in st.session_state:
        st.session_state.notifications = []
    
    # Filters
    if "filters" not in st.session_state:
        st.session_state.filters = {
            "city": "All",
            "risk": "All",
            "status": "All"
        }


def get_session_value(key: str, default: Any = None) -> Any:
    """Get value from session state"""
    return st.session_state.get(key, default)


def set_session_value(key: str, value: Any):
    """Set value in session state"""
    st.session_state[key] = value


def clear_session():
    """Clear all session data"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_session_state()


def add_notification(message: str, type: str = "info"):
    """
    Add notification to session
    
    Args:
        message: Notification message
        type: Type of notification (info, success, warning, error)
    """
    notification = {
        "message": message,
        "type": type,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    if "notifications" not in st.session_state:
        st.session_state.notifications = []
    
    st.session_state.notifications.append(notification)


def get_notifications() -> List[Dict]:
    """Get all notifications"""
    return st.session_state.get("notifications", [])


def clear_notifications():
    """Clear all notifications"""
    st.session_state.notifications = []


def display_notifications():
    """Display all pending notifications"""
    notifications = get_notifications()
    
    if notifications:
        for notif in notifications:
            if notif["type"] == "success":
                st.success(notif["message"])
            elif notif["type"] == "warning":
                st.warning(notif["message"])
            elif notif["type"] == "error":
                st.error(notif["message"])
            else:
                st.info(notif["message"])
        
        # Clear notifications after displaying
        clear_notifications()


def store_shipment_data(shipment_id: str, data: Dict):
    """Store shipment data in session"""
    if "shipment_history" not in st.session_state:
        st.session_state.shipment_history = []
    
    shipment_record = {
        "shipment_id": shipment_id,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data": data
    }
    
    st.session_state.shipment_history.append(shipment_record)


def get_shipment_history() -> List[Dict]:
    """Get shipment history from session"""
    return st.session_state.get("shipment_history", [])


def update_filters(filter_dict: Dict):
    """Update filter values in session"""
    if "filters" not in st.session_state:
        st.session_state.filters = {}
    
    st.session_state.filters.update(filter_dict)


def get_filters() -> Dict:
    """Get current filter values"""
    return st.session_state.get("filters", {})
