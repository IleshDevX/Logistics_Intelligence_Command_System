"""
LICS - Logistics Intelligence & Command System  
Main Entry Point and Authentication Portal
Production Web Application with Real Database Integration
"""

import streamlit as st
import sys
import os

# Add project root to Python path for imports
project_root = os.path.dirname(os.path.abspath(__file__))
parent_root = os.path.dirname(project_root)  # Add parent directory for backend imports
sys.path.insert(0, project_root)
sys.path.insert(0, parent_root)

# Import authentication functions from API client
from utils.api_client import (
    is_logged_in, 
    login_user,
    logout_user,
    get_current_user,
    register_user,
    ensure_authenticated,
    test_api_connection,
    format_user_role
)

# Import additional utilities from merged webapp
from utils.styling import apply_custom_styles
from utils.session_manager import update_last_activity

# Page configuration
st.set_page_config(
    page_title="LICS - Logistics Intelligence & Command System", 
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.login_attempts = 0
    st.session_state.show_register = False

# Apply custom styling if available
try:
    apply_custom_styles()
except:
    pass  # Continue without custom styling if not available

# Update user activity
try:
    update_last_activity()
except:
    pass  # Continue without activity tracking if not available

def show_authenticated_home():
    """Show home page for authenticated users"""
    user = get_current_user()
    
    st.title("🚛 LICS Command Center")
    st.markdown(f"### Welcome back, **{user.get('name', 'User')}**!")
    st.markdown("#### Logistics Intelligence & Command System")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Role-specific dashboard content
        role = user.get('role', 'unknown')
        
        if role == 'seller':
            st.markdown("""
            ## 🚀 Seller Portal
            
            **Your Daily Operations:**
            - Create new shipments with AI-powered risk assessment
            - Track your shipment deliveries in real-time
            - View weather and traffic impact alerts
            
            **Quick Actions:**
            """)
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                if st.button("📝 New Shipment", use_container_width=True, type="primary"):
                    st.switch_page("pages/1_🚀_Seller_Portal.py")
            
            with col_b:
                if st.button("📦 Track Shipments", use_container_width=True):
                    st.switch_page("pages/1_🚀_Seller_Portal.py")
                    
            with col_c:
                if st.button("📋 View History", use_container_width=True):
                    st.switch_page("pages/1_🚀_Seller_Portal.py")
        
        elif role == 'manager':
            st.markdown("""
            ## 🏗️ Control Tower
            
            **Management Overview:**
            - Monitor all active shipments and interventions
            - Override AI decisions when human judgment needed
            - Send proactive customer notifications
            - Analyze team performance and efficiency
            
            **Quick Actions:**
            """)
            
            col_a, col_b, col_c, col_d = st.columns(4)
            with col_a:
                if st.button("🏗️ Control Tower", use_container_width=True, type="primary"):
                    st.switch_page("pages/2_🏗️_Control_Tower.py")
            
            with col_b:
                if st.button("📊 Analytics", use_container_width=True):
                    st.switch_page("pages/3_📊_Analytics.py")
                    
            with col_c:
                if st.button("🚀 Seller View", use_container_width=True):
                    st.switch_page("pages/1_🚀_Seller_Portal.py")
                    
            with col_d:
                if st.button("📧 Notifications", use_container_width=True):
                    st.switch_page("pages/2_🏗️_Control_Tower.py")
        
        elif role == 'supervisor':
            st.markdown("""
            ## 📊 Analytics & Insights
            
            **Business Intelligence:**
            - Real-time operational metrics and KPIs
            - Predictive analytics and trend analysis
            - Performance benchmarking and reporting
            - AI decision accuracy monitoring
            
            **Quick Actions:**
            """)
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                if st.button("📊 Analytics", use_container_width=True, type="primary"):
                    st.switch_page("pages/3_📊_Analytics.py")
            
            with col_b:
                if st.button("🏗️ Monitor Ops", use_container_width=True):
                    st.switch_page("pages/2_🏗️_Control_Tower.py")
                    
            with col_c:
                if st.button("📈 Reports", use_container_width=True):
                    st.switch_page("pages/3_📊_Analytics.py")
        
        elif role == 'customer':
            st.markdown("""
            ## 📦 Customer Portal
            
            **Track Your Deliveries:**
            - Real-time shipment tracking with live updates
            - Weather impact and delay notifications
            - Reschedule delivery if needed
            - Rate and review delivery experience
            
            **Quick Actions:**
            """)
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("📦 Track Shipment", use_container_width=True, type="primary"):
                    st.switch_page("pages/4_📦_Customer_Tracking.py")
            
            with col_b:
                if st.button("📅 Reschedule", use_container_width=True):
                    st.switch_page("pages/4_📦_Customer_Tracking.py")
    
    with col2:
        # System status and notifications
        st.markdown("### 📡 System Status")
        
        # AI System Status
        with st.container():
            st.markdown("""
            **🤖 AI Systems:**
            - ✅ Risk Engine: Online
            - ✅ Weather Intelligence: Active  
            - ✅ Address Intelligence: Running
            - ✅ Route Optimizer: Ready
            """)
        
        st.markdown("---")
        
        # Recent notifications (mock data)
        st.markdown("### 🔔 Recent Alerts")
        with st.container():
            st.info("🌧️ Heavy rain alert for Zone-B deliveries")
            st.warning("⚠️ 3 high-risk shipments need review")
            st.success("✅ 94% on-time delivery rate today")
        
        st.markdown("---")
        
        # Quick stats
        st.markdown("### 📈 Today's Metrics")
        col_stat1, col_stat2 = st.columns(2)
        
        with col_stat1:
            st.metric("Active Shipments", "47", "↑ 12%")
            st.metric("AI Decisions", "156", "↑ 8%")
            
        with col_stat2:
            st.metric("On-Time Rate", "94%", "↑ 2%")
            st.metric("Human Overrides", "3", "↓ 5")

def show_login_form():
    """Display login and registration form"""
    st.title("🚛 LICS - Logistics Intelligence & Command System")
    
    # API Connection Status
    st.subheader("System Status")
    test_api_connection()
    
    st.subheader("Authentication")
    
    # Toggle between login and register
    if st.session_state.get('show_register', False):
        st.write("### Register New Account")
        
        with st.form("register_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                username = st.text_input("Username")
                email = st.text_input("Email")
                full_name = st.text_input("Full Name")
            
            with col2:
                password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                role = st.selectbox("Role", ["customer", "dispatcher", "driver"])
                phone = st.text_input("Phone (Optional)")
            
            submit = st.form_submit_button("Register", type="primary")
            
            if submit:
                if not all([username, email, password, full_name]):
                    st.error("Please fill in all required fields")
                elif password != confirm_password:
                    st.error("Passwords do not match")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters long")
                else:
                    user_data = {
                        "username": username,
                        "email": email,
                        "password": password,
                        "full_name": full_name,
                        "role": role,
                        "phone": phone if phone else None
                    }
                    
                    with st.spinner("Creating account..."):
                        result = register_user(user_data)
                    
                    if result['success']:
                        st.success("Account created successfully!")
                        st.rerun()
                    else:
                        st.error(f"Registration failed: {result.get('error', 'Unknown error')}")
        
        if st.button("Back to Login"):
            st.session_state.show_register = False
            st.rerun()
    
    else:
        st.write("### Login to Your Account")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", type="primary")
            
            if submit:
                if username and password:
                    with st.spinner("Authenticating..."):
                        result = login_user(username, password)
                    
                    if result['success']:
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error(f"Login failed: {result.get('error', 'Invalid credentials')}")
                        st.session_state.login_attempts = st.session_state.get('login_attempts', 0) + 1
                else:
                    st.error("Please enter both username and password")
        
        # Demo credentials info
        with st.expander("Demo Credentials (if backend not available)"):
            st.write("**Admin:** admin / admin123")
            st.write("**Dispatcher:** dispatcher / dispatch123")
            st.write("**Driver:** driver / driver123")
            st.write("**Customer:** customer / customer123")
        
        if st.button("Create New Account"):
            st.session_state.show_register = True
            st.rerun()

def show_user_info_sidebar():
    """Show user information in sidebar"""
    if is_logged_in():
        user = get_current_user()
        if user:
            with st.sidebar:
                st.write("---")
                st.write("**Logged in as:**")
                st.write(f"👤 **{user.get('full_name', user.get('username'))}**")
                st.write(f"🏷️ {format_user_role(user.get('role', 'user'))}")
                
                if st.button("🚪 Logout", key="logout_btn"):
                    logout_user()
                    st.rerun()

def main():
    """Main application entry point"""
    
    if not is_logged_in():
        # Show login form if not authenticated
        show_login_form()
    else:
        # Show main application interface
        show_user_info_sidebar()
        
        # Main navigation
        st.title("🚛 LICS Dashboard")
        
        user = get_current_user()
        if user:
            st.write(f"Welcome back, **{user.get('full_name', user.get('username'))}**!")
            
            # Role-based navigation
            user_role = user.get('role')
            
            if user_role == 'admin':
                st.info("🔧 **Administrator Dashboard** - Access all system features")
                show_admin_navigation()
            elif user_role == 'dispatcher':
                st.info("📋 **Dispatcher Dashboard** - Manage shipments and operations")
                show_dispatcher_navigation() 
            elif user_role == 'driver':
                st.info("🚛 **Driver Dashboard** - View assigned deliveries")
                show_driver_navigation()
            elif user_role == 'customer':
                st.info("👤 **Customer Portal** - Track your shipments")
                show_customer_navigation()
            else:
                st.warning("Unknown user role. Please contact administrator.")

def show_admin_navigation():
    """Show admin navigation options"""
    st.subheader("Administrative Functions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 Analytics Dashboard", help="View comprehensive analytics"):
            st.switch_page("pages/admin_page.py")
    
    with col2:
        if st.button("🚚 Dispatch Operations", help="Manage shipment dispatch"):
            st.switch_page("pages/dispatcher_page.py")
    
    with col3:
        if st.button("🚛 Driver Management", help="Manage drivers and routes"):
            st.switch_page("pages/driver_page.py")
    
    with col4:
        if st.button("👤 Customer Service", help="Customer support tools"):
            st.switch_page("pages/customer_page.py")

def show_dispatcher_navigation():
    """Show dispatcher navigation options"""
    st.subheader("Dispatch Operations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📋 Dispatcher Dashboard", help="Main dispatch operations"):
            st.switch_page("pages/dispatcher_page.py")
    
    with col2:
        if st.button("👤 Customer Support", help="Customer service tools"):
            st.switch_page("pages/customer_page.py")

def show_driver_navigation():
    """Show driver navigation options"""
    st.subheader("Driver Portal")
    
    if st.button("🚛 My Deliveries", help="View assigned deliveries and routes"):
        st.switch_page("pages/driver_page.py")

def show_customer_navigation():
    """Show customer navigation options"""
    st.subheader("Customer Portal")
    
    if st.button("📦 Track Shipments", help="Track your shipments and view history"):
        st.switch_page("pages/customer_page.py")

if __name__ == "__main__":
    main()