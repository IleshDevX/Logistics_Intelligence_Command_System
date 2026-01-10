"""
Session-based Authentication for LICS Web Application
Demo-safe authentication with role-based access control
"""

import streamlit as st
import hashlib
import time
from typing import Dict, Optional, List
from datetime import datetime, timedelta

# Demo user database (session-based, no persistence)
DEMO_USERS = {
    "seller1": {
        "password_hash": "ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f",  # password123
        "role": "seller",
        "name": "Rajesh Kumar", 
        "email": "rajesh.kumar@lics.com",
        "department": "Sales",
        "permissions": ["create_shipment", "view_own_shipments", "track_shipments"]
    },
    "manager1": {
        "password_hash": "3c9909afec25354d551dae21590bb26e38d53f2173b8d3dc3eee4c047e7ab1c1",  # manager123
        "role": "manager",
        "name": "Priya Sharma",
        "email": "priya.sharma@lics.com", 
        "department": "Operations",
        "permissions": ["view_all_shipments", "override_decisions", "send_notifications", "view_analytics", "manage_team"]
    },
    "supervisor1": {
        "password_hash": "ba3253876aed6bc22d4a6ff53d8406c6ad864195ed144ab5c87621b6c233b548",  # super123
        "role": "supervisor",
        "name": "Amit Singh",
        "email": "amit.singh@lics.com",
        "department": "Analytics", 
        "permissions": ["view_analytics", "view_reports", "view_all_shipments"]
    },
    "customer1": {
        "password_hash": "customer123",
        "role": "customer", 
        "name": "Ananya Patel",
        "email": "ananya.patel@gmail.com",
        "department": "Customer",
        "permissions": ["track_own_shipments", "request_reschedule"]
    }
}

# Role-based page access
ROLE_PAGES = {
    "seller": ["🚀 Seller Portal"],
    "manager": ["🏗️ Control Tower", "🚀 Seller Portal"],
    "supervisor": ["📊 Analytics", "🏗️ Control Tower"], 
    "customer": ["📦 Track Shipment"]
}

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_credentials(username: str, password: str) -> bool:
    """Verify username and password"""
    if username not in DEMO_USERS:
        return False
    
    stored_hash = DEMO_USERS[username]["password_hash"]
    input_hash = hash_password(password)
    
    return stored_hash == input_hash

def get_user_info(username: str) -> Dict:
    """Get user information"""
    return DEMO_USERS.get(username, {})

def check_authentication() -> bool:
    """Check if user is authenticated"""
    return st.session_state.get('authenticated', False)

def get_current_user() -> Dict:
    """Get current authenticated user"""
    if not check_authentication():
        return {}
    
    username = st.session_state.get('username', '')
    return get_user_info(username)

def check_permission(required_permission: str) -> bool:
    """Check if current user has required permission"""
    if not check_authentication():
        return False
    
    user = get_current_user()
    user_permissions = user.get('permissions', [])
    
    return required_permission in user_permissions

def check_role_access(page_name: str) -> bool:
    """Check if current user role can access the page"""
    if not check_authentication():
        return False
    
    user = get_current_user()
    user_role = user.get('role', '')
    allowed_pages = ROLE_PAGES.get(user_role, [])
    
    return page_name in allowed_pages

def login_user(username: str) -> None:
    """Log in user and set session state"""
    user_info = get_user_info(username)
    
    st.session_state['authenticated'] = True
    st.session_state['username'] = username
    st.session_state['user_info'] = user_info
    st.session_state['login_time'] = time.time()

def logout_user() -> None:
    """Log out user and clear session"""
    keys_to_clear = ['authenticated', 'username', 'user_info', 'login_time']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

def show_login_form():
    """Display login form"""
    st.title("🔐 LICS Authentication")
    st.markdown("### Logistics Intelligence & Command System")
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("---")
        
        with st.form("login_form"):
            st.subheader("Please sign in")
            
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
            submitted = st.form_submit_button("Login", use_container_width=True, type="primary")
            
            if submitted:
                if not username or not password:
                    st.error("❌ Please enter both username and password")
                elif verify_credentials(username, password):
                    login_user(username)
                    st.success("✅ Login successful!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
        
        st.markdown("---")
        
        # Demo credentials info
        with st.expander("🔑 Demo Credentials", expanded=True):
            st.markdown("""
            **Available Demo Accounts:**
            
            **👤 Seller Account:**
            - Username: `seller1`
            - Password: `password123`
            - Access: Create shipments, track deliveries
            
            **👑 Manager Account:**
            - Username: `manager1`
            - Password: `manager123` 
            - Access: Control tower, override decisions
            
            **📊 Supervisor Account:**
            - Username: `supervisor1`
            - Password: `super123`
            - Access: Analytics and reports only
            
            **📦 Customer Account:**
            - Username: `customer1`
            - Password: `customer123`
            - Access: Track shipments only
            """)

def show_user_info_sidebar():
    """Show user info in sidebar"""
    if check_authentication():
        user = get_current_user()
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 👤 User Profile")
        st.sidebar.write(f"**Name:** {user.get('name', 'Unknown')}")
        st.sidebar.write(f"**Role:** {user.get('role', 'Unknown').title()}")
        st.sidebar.write(f"**Department:** {user.get('department', 'Unknown')}")
        
        # Session info
        login_time = st.session_state.get('login_time', time.time())
        session_duration = int((time.time() - login_time) / 60)
        st.sidebar.write(f"**Session:** {session_duration} min")
        
        st.sidebar.markdown("---")
        
        if st.sidebar.button("🚪 Logout", use_container_width=True, type="secondary"):
            logout_user()
            st.rerun()

def require_authentication():
    """Require authentication for protected pages"""
    if not check_authentication():
        st.error("🔒 Please login to access this page")
        st.info("👈 Use the Home page to login")
        st.stop()

def require_role_access(page_name: str):
    """Require specific role access for pages"""
    require_authentication()
    
    if not check_role_access(page_name):
        user = get_current_user()
        user_role = user.get('role', 'unknown')
        
        st.error(f"🚫 Access Denied: {user_role.title()} role cannot access {page_name}")
        
        # Show available pages
        available_pages = ROLE_PAGES.get(user_role, [])
        if available_pages:
            st.info(f"**Available pages for {user_role}:** {', '.join(available_pages)}")
        
        st.stop()

def require_permission(permission: str):
    """Require specific permission"""
    require_authentication()
    
    if not check_permission(permission):
        user = get_current_user()
        st.error(f"🚫 Insufficient permissions: '{permission}' required")
        st.info(f"**Your permissions:** {', '.join(user.get('permissions', []))}")
        st.stop()

# Initialize session state
def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
        
    # Initialize notification system
    if 'notifications' not in st.session_state:
        st.session_state['notifications'] = []
        
    # Initialize form data storage
    if 'form_data' not in st.session_state:
        st.session_state['form_data'] = {}

# Run initialization
init_session_state()