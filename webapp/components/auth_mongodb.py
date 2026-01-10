"""
Authentication Component for LICS Web Application
MongoDB-based authentication with user registration
"""

import streamlit as st
import hashlib
import time
from typing import Optional, Dict
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from utils.database import get_users_collection, test_database_connection
import logging

logger = logging.getLogger(__name__)

# Role-based permissions
ROLE_PERMISSIONS = {
    "seller": ["create_shipment", "view_own_shipments", "track_shipments"],
    "manager": ["view_all_shipments", "override_decisions", "send_notifications", "view_analytics"],
    "supervisor": ["view_analytics", "view_reports", "view_all_shipments"],
    "admin": ["all"]
}

def hash_password(password: str) -> str:
    """Hash password using SHA-256 with salt (for demo compatibility)"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against MongoDB hash"""
    try:
        if ':' in hashed:  # New format with salt
            password_hash, salt = hashed.split(':')
            return password_hash == hashlib.sha256((salt + password).encode()).hexdigest()
        else:  # Old format (fallback) or demo format
            return hashed == hashlib.sha256(password.encode()).hexdigest()
    except:
        return False

def verify_credentials(username: str, password: str) -> bool:
    """Verify username and password against MongoDB"""
    try:
        users_collection = get_users_collection()
        
        # Find user by username or email
        user = users_collection.find_one({
            "$or": [
                {"username": username},
                {"email": username.lower()}
            ]
        })
        
        if not user:
            return False
        
        if not user.get('is_active', True):
            return False
        
        # Verify password
        return verify_password(password, user['password_hash'])
        
    except Exception as e:
        logger.error(f"Error verifying credentials: {str(e)}")
        return False

def check_authentication() -> bool:
    """Check if user is authenticated"""
    return st.session_state.get('authenticated', False)

def check_permission(required_permission: str) -> bool:
    """Check if current user has required permission"""
    if not check_authentication():
        return False
    
    user_role = st.session_state.get('role', '')
    permissions = ROLE_PERMISSIONS.get(user_role, [])
    
    return required_permission in permissions or 'all' in permissions

def login_user(username: str) -> None:
    """Log in user and set session state"""
    try:
        users_collection = get_users_collection()
        user = users_collection.find_one({
            "$or": [
                {"username": username},
                {"email": username.lower()}
            ]
        })
        
        if user:
            st.session_state['authenticated'] = True
            st.session_state['user_id'] = str(user['_id'])
            st.session_state['username'] = user['username']
            st.session_state['role'] = user['role']
            st.session_state['full_name'] = user['full_name']
            st.session_state['name'] = user['full_name']  # For backward compatibility
            st.session_state['email'] = user['email']
            st.session_state['department'] = user.get('department', '')
            st.session_state['phone'] = user.get('phone', '')
            st.session_state['is_verified'] = user.get('is_verified', False)
            st.session_state['login_time'] = time.time()
            
            # Update last login in database
            users_collection.update_one(
                {"_id": user["_id"]},
                {"$set": {"last_login": time.time()}}
            )
            
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")

def logout_user() -> None:
    """Log out user and clear session"""
    keys_to_clear = [
        'authenticated', 'user_id', 'username', 'role', 'full_name', 'name',
        'email', 'department', 'phone', 'is_verified', 'login_time'
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

def get_user_info() -> Dict[str, str]:
    """Get current user information"""
    return {
        'user_id': st.session_state.get('user_id', ''),
        'username': st.session_state.get('username', ''),
        'role': st.session_state.get('role', ''),
        'full_name': st.session_state.get('full_name', ''),
        'name': st.session_state.get('name', ''),  # For backward compatibility
        'email': st.session_state.get('email', ''),
        'department': st.session_state.get('department', ''),
        'phone': st.session_state.get('phone', ''),
        'is_verified': st.session_state.get('is_verified', False)
    }

def show_login() -> None:
    """Display enhanced login form with registration option"""
    st.title("🔐 LICS Login")
    st.markdown("### Logistics Intelligence & Command System")
    
    # Check database connection
    db_status = test_database_connection()
    if db_status['status'] != 'connected':
        st.error("❌ Database connection failed. Please try again later.")
        st.error(f"Error: {db_status.get('error', 'Unknown error')}")
        return
    
    # Tabs for login and registration
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        # Center the login form
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("---")
            
            with st.form("login_form"):
                st.subheader("Welcome Back!")
                
                username = st.text_input(
                    "Username or Email", 
                    key="login_username",
                    placeholder="Enter username or email"
                )
                
                password = st.text_input(
                    "Password", 
                    type="password", 
                    key="login_password",
                    placeholder="Enter password"
                )
                
                # Remember me checkbox
                remember_me = st.checkbox("Remember me")
                
                submitted = st.form_submit_button("Login", use_container_width=True, type="primary")
                
                if submitted:
                    if not username or not password:
                        st.error("❌ Please enter both username/email and password")
                    elif verify_credentials(username, password):
                        login_user(username)
                        user_info = get_user_info()
                        st.success(f"✅ Welcome {user_info['full_name']}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials")
            
            st.markdown("---")
            
            # Database status
            with st.expander("� System Status"):
                st.success(f"✅ Database: {db_status['database_name']}")
                st.info(f"📊 Collections: {', '.join(db_status.get('collections', []))}")
    
    with tab2:
        # Registration form
        try:
            from components.user_registration import show_registration_form
            show_registration_form()
        except ImportError as e:
            st.error("Registration component not available")
            st.error(f"Error: {str(e)}")

def show_logout_button() -> None:
    """Display user info and logout button in sidebar"""
    if check_authentication():
        user_info = get_user_info()
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 👤 User Profile")
        st.sidebar.write(f"**Name:** {user_info['full_name']}")
        st.sidebar.write(f"**Username:** {user_info['username']}")
        st.sidebar.write(f"**Role:** {user_info['role'].title()}")
        st.sidebar.write(f"**Department:** {user_info['department']}")
        
        # Verification status
        if user_info['is_verified']:
            st.sidebar.success("✅ Verified Account")
        else:
            st.sidebar.warning("⚠️ Email Not Verified")
        
        # Session info
        login_time = st.session_state.get('login_time', time.time())
        session_duration = int((time.time() - login_time) / 60)  # minutes
        st.sidebar.write(f"**Session:** {session_duration} min")
        
        st.sidebar.markdown("---")
        
        if st.sidebar.button("🚪 Logout", use_container_width=True, type="secondary"):
            logout_user()
            st.rerun()

def require_authentication(page_name: str = "this page"):
    """Decorator function to require authentication for a page"""
    if not check_authentication():
        st.error(f"🔒 Please login to access {page_name}")
        
        # Show mini login form
        with st.expander("🔐 Quick Login", expanded=True):
            with st.form("quick_login"):
                username = st.text_input("Username/Email")
                password = st.text_input("Password", type="password")
                
                if st.form_submit_button("Login"):
                    if verify_credentials(username, password):
                        login_user(username)
                        st.success("✅ Logged in successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials")
        
        st.info("👈 Or use the main login page")
        st.stop()

def require_permission(permission: str, page_name: str = "this page"):
    """Decorator function to require specific permission for a page"""
    require_authentication(page_name)
    
    if not check_permission(permission):
        user_role = st.session_state.get('role', 'unknown')
        st.error(f"🚫 Access Denied: {user_role.title()} role cannot access {page_name}")
        st.info("Contact your administrator for access permissions")
        
        # Show available permissions
        permissions = ROLE_PERMISSIONS.get(user_role, [])
        if permissions:
            st.info(f"**Your permissions:** {', '.join(permissions)}")
        
        st.stop()

# Session state initialization
def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False

# Initialize on import
init_session_state()