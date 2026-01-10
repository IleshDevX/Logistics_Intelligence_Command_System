"""
Session Manager for LICS Web Application
Handles user session state across pages
"""

import streamlit as st
from typing import Any, Dict, Optional
import json
import time

def init_session_state():
    """Initialize all session state variables"""
    
    # Authentication states
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    
    if 'username' not in st.session_state:
        st.session_state['username'] = ''
    
    if 'role' not in st.session_state:
        st.session_state['role'] = ''
    
    if 'name' not in st.session_state:
        st.session_state['name'] = ''
    
    # Application states
    if 'current_shipment' not in st.session_state:
        st.session_state['current_shipment'] = None
    
    if 'form_data' not in st.session_state:
        st.session_state['form_data'] = {}
    
    if 'notifications' not in st.session_state:
        st.session_state['notifications'] = []
    
    if 'dashboard_filters' not in st.session_state:
        st.session_state['dashboard_filters'] = {
            'city': 'All',
            'risk_level': 'All',
            'status': 'All',
            'date_range': 'Today'
        }
    
    # UI states
    if 'sidebar_collapsed' not in st.session_state:
        st.session_state['sidebar_collapsed'] = False
    
    if 'dark_mode' not in st.session_state:
        st.session_state['dark_mode'] = False
    
    if 'last_activity' not in st.session_state:
        st.session_state['last_activity'] = time.time()

def set_session_value(key: str, value: Any) -> None:
    """Set a value in session state"""
    st.session_state[key] = value
    update_last_activity()

def get_session_value(key: str, default: Any = None) -> Any:
    """Get a value from session state"""
    return st.session_state.get(key, default)

def remove_session_value(key: str) -> None:
    """Remove a value from session state"""
    if key in st.session_state:
        del st.session_state[key]

def clear_session() -> None:
    """Clear all session state"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_session_state()

def update_last_activity() -> None:
    """Update last activity timestamp"""
    st.session_state['last_activity'] = time.time()

def is_session_expired(timeout_minutes: int = 60) -> bool:
    """Check if session has expired"""
    if 'last_activity' not in st.session_state:
        return True
    
    elapsed = (time.time() - st.session_state['last_activity']) / 60
    return elapsed > timeout_minutes

def save_form_data(form_name: str, data: Dict[str, Any]) -> None:
    """Save form data to session state"""
    if 'form_data' not in st.session_state:
        st.session_state['form_data'] = {}
    
    st.session_state['form_data'][form_name] = data
    update_last_activity()

def get_form_data(form_name: str) -> Dict[str, Any]:
    """Get saved form data"""
    return st.session_state.get('form_data', {}).get(form_name, {})

def clear_form_data(form_name: str) -> None:
    """Clear specific form data"""
    if 'form_data' in st.session_state and form_name in st.session_state['form_data']:
        del st.session_state['form_data'][form_name]

def add_notification(message: str, type: str = 'info', duration: int = 5000) -> None:
    """Add a notification to the session"""
    notification = {
        'id': int(time.time() * 1000),  # Use timestamp as ID
        'message': message,
        'type': type,  # 'success', 'error', 'warning', 'info'
        'timestamp': time.time(),
        'duration': duration,
        'read': False
    }
    
    if 'notifications' not in st.session_state:
        st.session_state['notifications'] = []
    
    st.session_state['notifications'].append(notification)
    update_last_activity()

def get_notifications(unread_only: bool = False) -> list:
    """Get notifications from session"""
    notifications = st.session_state.get('notifications', [])
    
    if unread_only:
        notifications = [n for n in notifications if not n.get('read', False)]
    
    return notifications

def mark_notification_read(notification_id: int) -> None:
    """Mark a notification as read"""
    notifications = st.session_state.get('notifications', [])
    for notification in notifications:
        if notification['id'] == notification_id:
            notification['read'] = True
            break

def clear_old_notifications(max_age_hours: int = 24) -> None:
    """Clear notifications older than specified hours"""
    if 'notifications' not in st.session_state:
        return
    
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    
    st.session_state['notifications'] = [
        n for n in st.session_state['notifications']
        if (current_time - n['timestamp']) < max_age_seconds
    ]

def set_dashboard_filter(filter_name: str, value: str) -> None:
    """Set dashboard filter value"""
    if 'dashboard_filters' not in st.session_state:
        st.session_state['dashboard_filters'] = {}
    
    st.session_state['dashboard_filters'][filter_name] = value
    update_last_activity()

def get_dashboard_filters() -> Dict[str, str]:
    """Get all dashboard filters"""
    return st.session_state.get('dashboard_filters', {
        'city': 'All',
        'risk_level': 'All',
        'status': 'All',
        'date_range': 'Today'
    })

def reset_dashboard_filters() -> None:
    """Reset dashboard filters to defaults"""
    st.session_state['dashboard_filters'] = {
        'city': 'All',
        'risk_level': 'All',
        'status': 'All',
        'date_range': 'Today'
    }

def get_user_preferences() -> Dict[str, Any]:
    """Get user preferences"""
    return {
        'dark_mode': st.session_state.get('dark_mode', False),
        'sidebar_collapsed': st.session_state.get('sidebar_collapsed', False),
        'notifications_enabled': st.session_state.get('notifications_enabled', True),
        'auto_refresh': st.session_state.get('auto_refresh', True)
    }

def set_user_preference(key: str, value: Any) -> None:
    """Set user preference"""
    st.session_state[key] = value
    update_last_activity()

def export_session_data() -> str:
    """Export session data as JSON (for debugging)"""
    exportable_data = {}
    
    # Only export safe data, not sensitive information
    safe_keys = [
        'role', 'dashboard_filters', 'dark_mode', 'sidebar_collapsed',
        'notifications_enabled', 'auto_refresh', 'form_data'
    ]
    
    for key in safe_keys:
        if key in st.session_state:
            exportable_data[key] = st.session_state[key]
    
    return json.dumps(exportable_data, indent=2)

def get_session_info() -> Dict[str, Any]:
    """Get session information for debugging"""
    info = {
        'authenticated': st.session_state.get('authenticated', False),
        'username': st.session_state.get('username', ''),
        'role': st.session_state.get('role', ''),
        'session_duration': 0,
        'last_activity': 'Never',
        'notifications_count': len(st.session_state.get('notifications', [])),
        'form_data_keys': list(st.session_state.get('form_data', {}).keys())
    }
    
    if 'last_activity' in st.session_state:
        duration = time.time() - st.session_state['last_activity']
        info['session_duration'] = int(duration / 60)  # minutes
        info['last_activity'] = time.strftime('%Y-%m-%d %H:%M:%S', 
                                            time.localtime(st.session_state['last_activity']))
    
    return info

# Initialize session state on module import
init_session_state()