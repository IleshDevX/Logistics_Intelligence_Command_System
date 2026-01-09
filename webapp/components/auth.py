"""
Authentication Module for LICS Web Application
Handles user login, role-based access, and session management
"""

import streamlit as st
import hashlib
from typing import Optional, Dict

# Demo users database (in production, use MongoDB)
USERS_DB = {
    "seller1": {
        "password": hashlib.sha256("seller123".encode()).hexdigest(),
        "role": "Seller",
        "name": "Rajesh Kumar",
        "email": "rajesh@seller.com"
    },
    "seller2": {
        "password": hashlib.sha256("seller123".encode()).hexdigest(),
        "role": "Seller",
        "name": "Priya Sharma",
        "email": "priya@seller.com"
    },
    "manager1": {
        "password": hashlib.sha256("manager123".encode()).hexdigest(),
        "role": "Manager",
        "name": "Amit Patel",
        "email": "amit@manager.com"
    },
    "manager2": {
        "password": hashlib.sha256("manager123".encode()).hexdigest(),
        "role": "Manager",
        "name": "Sneha Gupta",
        "email": "sneha@manager.com"
    },
    "supervisor1": {
        "password": hashlib.sha256("super123".encode()).hexdigest(),
        "role": "Supervisor",
        "name": "Vikram Singh",
        "email": "vikram@supervisor.com"
    }
}


def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def authenticate(username: str, password: str) -> Optional[Dict]:
    """
    Authenticate user credentials
    
    Args:
        username: Username
        password: Plain text password
        
    Returns:
        User dict if authenticated, None otherwise
    """
    if username in USERS_DB:
        hashed_input = hash_password(password)
        if USERS_DB[username]["password"] == hashed_input:
            return {
                "username": username,
                "role": USERS_DB[username]["role"],
                "name": USERS_DB[username]["name"],
                "email": USERS_DB[username]["email"]
            }
    return None


def login():
    """Display login form and handle authentication"""
    
    # Custom CSS for login page
    st.markdown("""
        <style>
        .login-container {
            max-width: 400px;
            margin: 100px auto;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            background: white;
        }
        .login-title {
            text-align: center;
            color: #FF6B35;
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .login-subtitle {
            text-align: center;
            color: #666;
            font-size: 14px;
            margin-bottom: 30px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Center column for login
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-title">🚚 LICS</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subtitle">Logistics Intelligence & Command System</div>', unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            submit = st.form_submit_button("🔐 Login", use_container_width=True)
            
            if submit:
                if username and password:
                    user = authenticate(username, password)
                    if user:
                        # Store user in session
                        st.session_state.user = user
                        st.session_state.authenticated = True
                        st.success(f"✅ Welcome, {user['name']}!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
                else:
                    st.warning("⚠️ Please enter both username and password")
        
        # Demo credentials
        with st.expander("📋 Demo Credentials"):
            st.markdown("""
            **Sellers:**
            - `seller1` / `seller123`
            - `seller2` / `seller123`
            
            **Managers:**
            - `manager1` / `manager123`
            - `manager2` / `manager123`
            
            **Supervisor:**
            - `supervisor1` / `super123`
            """)


def logout():
    """Clear session and logout user"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


def is_authenticated() -> bool:
    """Check if user is authenticated"""
    return st.session_state.get("authenticated", False)


def get_current_user() -> Optional[Dict]:
    """Get current logged-in user"""
    return st.session_state.get("user", None)


def get_user_role() -> Optional[str]:
    """Get current user's role"""
    user = get_current_user()
    return user["role"] if user else None


def require_auth(allowed_roles: list = None):
    """
    Decorator/function to require authentication
    
    Args:
        allowed_roles: List of roles allowed to access (None = all authenticated users)
    """
    if not is_authenticated():
        st.warning("🔒 Please login to access this page")
        login()
        st.stop()
    
    if allowed_roles:
        user_role = get_user_role()
        if user_role not in allowed_roles:
            st.error(f"❌ Access Denied: This page requires {' or '.join(allowed_roles)} role")
            st.info(f"Your role: {user_role}")
            st.stop()


def display_user_info():
    """Display current user info in sidebar"""
    if is_authenticated():
        user = get_current_user()
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 👤 Current User")
        st.sidebar.markdown(f"**Name:** {user['name']}")
        st.sidebar.markdown(f"**Role:** {user['role']}")
        st.sidebar.markdown(f"**Email:** {user['email']}")
        
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            logout()
