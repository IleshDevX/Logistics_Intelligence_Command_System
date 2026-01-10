"""
LICS - Logistics Intelligence & Command System  
Main Application Entry Point
🎯 AI-Assisted Logistics with Human Oversight
"""

import streamlit as st
import sys
import os

# Add project paths for imports
project_root = os.path.dirname(os.path.abspath(__file__))
parent_root = os.path.dirname(project_root)
sys.path.insert(0, project_root)
sys.path.insert(0, parent_root)

from utils.api_client import (
    is_logged_in, 
    login_user,
    logout_user,
    get_current_user,
    register_user,
    test_api_connection,
    format_user_role
)

# Page configuration
st.set_page_config(
    page_title="LICS - Logistics Intelligence", 
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for risk-first design
def apply_custom_css():
    st.markdown("""
    <style>
    /* Risk-first color scheme */
    .risk-low { background: linear-gradient(90deg, #d4edda 0%, #c3e6cb 100%); }
    .risk-medium { background: linear-gradient(90deg, #fff3cd 0%, #ffeaa7 100%); }
    .risk-high { background: linear-gradient(90deg, #f8d7da 0%, #f5c6cb 100%); }
    
    /* Status indicators */
    .status-pending { color: #ffc107; }
    .status-approved { color: #28a745; }
    .status-delayed { color: #dc3545; }
    
    /* Main navigation styling */
    .main-nav {
        background: linear-gradient(90deg, #2C3E50 0%, #3498DB 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    /* Risk score styling */
    .risk-score-low { 
        background: #d4edda; 
        color: #155724; 
        padding: 0.5rem 1rem; 
        border-radius: 20px; 
        font-weight: bold;
    }
    .risk-score-medium { 
        background: #fff3cd; 
        color: #856404; 
        padding: 0.5rem 1rem; 
        border-radius: 20px; 
        font-weight: bold;
    }
    .risk-score-high { 
        background: #f8d7da; 
        color: #721c24; 
        padding: 0.5rem 1rem; 
        border-radius: 20px; 
        font-weight: bold;
    }
    
    /* AI insight styling */
    .ai-insight {
        border-left: 4px solid #3498DB;
        background: #f8f9fa;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 8px 8px 0;
    }
    
    /* Override warning */
    .override-warning {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Mobile responsive */
    @media (max-width: 768px) {
        .main-nav { padding: 0.5rem; }
        .risk-score-low, .risk-score-medium, .risk-score-high { 
            display: block; 
            text-align: center; 
            margin: 0.5rem 0; 
        }
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    """Initialize session state variables"""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.login_attempts = 0
        st.session_state.show_register = False
        st.session_state.selected_shipments = []
        st.session_state.override_reason = ""

def show_login_form():
    """Display enhanced login form with system status"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem;">
        <h1>🚛 LICS</h1>
        <h3>Logistics Intelligence & Command System</h3>
        <p style="color: #666; font-style: italic;">AI-Assisted Decision Making with Human Oversight</p>
        </div>
        """, unsafe_allow_html=True)
        
        # System status check
        st.subheader("🔍 System Status")
        test_api_connection()
        
        # Login form
        st.subheader("🔐 Authentication")
        
        # Toggle between login and register
        if st.session_state.get('show_register', False):
            show_register_form()
        else:
            show_login_form_inputs()

def show_login_form_inputs():
    """Show login input form"""
    with st.form("login_form"):
        st.write("### Sign In")
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        col1, col2 = st.columns(2)
        with col1:
            login_btn = st.form_submit_button("🚀 Sign In", type="primary", use_container_width=True)
        
        if login_btn and username and password:
            with st.spinner("Authenticating..."):
                result = login_user(username, password)
            
            if result['success']:
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error(f"❌ {result.get('error', 'Login failed')}")
                st.session_state.login_attempts += 1
        
    # Demo credentials info
    with st.expander("🧪 Demo Access Credentials"):
        st.info("""
        **Quick Demo Access:**
        - **Seller**: `seller` / `demo123` - Create shipments, view AI recommendations
        - **Manager**: `manager` / `demo123` - Control tower, override decisions
        - **Admin**: `admin` / `demo123` - Full analytics dashboard access
        """)
    
    if st.button("📝 Create New Account", use_container_width=True):
        st.session_state.show_register = True
        st.rerun()

def show_register_form():
    """Show user registration form"""
    with st.form("register_form"):
        st.write("### Create Account")
        
        col1, col2 = st.columns(2)
        with col1:
            username = st.text_input("Username*")
            email = st.text_input("Email*")
            full_name = st.text_input("Full Name*")
        
        with col2:
            password = st.text_input("Password*", type="password")
            confirm_password = st.text_input("Confirm Password*", type="password")
            role = st.selectbox("Role", ["seller", "manager", "customer", "admin"])
            phone = st.text_input("Phone (Optional)")
        
        register_btn = st.form_submit_button("✅ Create Account", type="primary", use_container_width=True)
        
        if register_btn:
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
    
    if st.button("⬅️ Back to Login", use_container_width=True):
        st.session_state.show_register = False
        st.rerun()

def show_user_info_sidebar():
    """Enhanced user information in sidebar"""
    if is_logged_in():
        user = get_current_user()
        if user:
            with st.sidebar:
                st.markdown("---")
                st.markdown("### 👤 Current User")
                
                # User profile card
                st.markdown(f"""
                <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                    <strong>{user.get('full_name', user.get('username'))}</strong><br/>
                    {format_user_role(user.get('role', 'user'))}<br/>
                    <small style="color: #666;">{user.get('email', '')}</small>
                </div>
                """, unsafe_allow_html=True)
                
                # Quick actions based on role
                role = user.get('role')
                if role in ['seller', 'manager']:
                    st.markdown("### ⚡ Quick Actions")
                    if role == 'seller':
                        if st.button("📦 New Shipment", use_container_width=True):
                            st.switch_page("pages/seller_portal.py")
                    elif role == 'manager':
                        if st.button("🎯 Control Tower", use_container_width=True):
                            st.switch_page("pages/manager_control.py")
                
                # System status in sidebar
                st.markdown("### 📊 System Status")
                st.success("🟢 AI Engine: Active")
                st.success("🟢 Database: Connected")
                st.info("🔄 Learning Mode: Enabled")
                
                if st.button("🚪 Logout", type="secondary", use_container_width=True):
                    logout_user()
                    st.rerun()

def show_main_navigation():
    """Show main navigation based on user role"""
    user = get_current_user()
    if not user:
        return
    
    role = user.get('role')
    
    # Welcome message with AI philosophy
    st.markdown(f"""
    <div class="main-nav">
        <h2 style="color: white; margin: 0;">Welcome back, {user.get('full_name', user.get('username'))}!</h2>
        <p style="color: #BDC3C7; margin: 0.5rem 0 0 0;">
            🧠 <strong>AI suggests, you decide</strong> | 
            📍 Transparency builds trust | 
            🔄 Systems learn from outcomes
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Role-specific navigation
    if role == 'seller' or role == 'customer':
        show_seller_navigation()
    elif role == 'manager' or role == 'dispatcher':
        show_manager_navigation()
    elif role == 'admin':
        show_admin_navigation()
    else:
        show_customer_navigation()

def show_seller_navigation():
    """Seller portal navigation"""
    st.markdown("### 📦 Seller Portal")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Create Shipment", help="Create new shipment with AI analysis", use_container_width=True):
            st.switch_page("pages/seller_portal.py")
    
    with col2:
        if st.button("📋 My Shipments", help="View all shipments and status", use_container_width=True):
            st.switch_page("pages/shipment_tracking.py")
    
    with col3:
        if st.button("📊 Performance", help="View delivery performance analytics", use_container_width=True):
            st.switch_page("pages/analytics_dashboard.py")

def show_manager_navigation():
    """Manager control tower navigation"""
    st.markdown("### 🎯 Manager Control Tower")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🗺️ Risk Heatmap", help="View risk heatmap and override decisions", use_container_width=True):
            st.switch_page("pages/manager_control.py")
    
    with col2:
        if st.button("📈 Analytics", help="View comprehensive analytics", use_container_width=True):
            st.switch_page("pages/analytics_dashboard.py")
    
    with col3:
        if st.button("📦 All Shipments", help="Monitor all system shipments", use_container_width=True):
            st.switch_page("pages/shipment_tracking.py")

def show_admin_navigation():
    """Admin dashboard navigation"""
    st.markdown("### 👑 Admin Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 Analytics", help="Full analytics dashboard", use_container_width=True):
            st.switch_page("pages/analytics_dashboard.py")
    
    with col2:
        if st.button("🎯 Control Tower", help="Manager control functions", use_container_width=True):
            st.switch_page("pages/manager_control.py")
    
    with col3:
        if st.button("📦 Create Shipment", help="Seller portal access", use_container_width=True):
            st.switch_page("pages/seller_portal.py")
    
    with col4:
        if st.button("📍 Track Shipments", help="Customer tracking interface", use_container_width=True):
            st.switch_page("pages/customer_tracking.py")

def show_customer_navigation():
    """Customer tracking navigation"""
    st.markdown("### 📍 Customer Portal")
    
    if st.button("📦 Track My Shipments", help="Track shipment status and get updates", use_container_width=True):
        st.switch_page("pages/customer_tracking.py")

def show_dashboard_overview():
    """Show role-based dashboard overview"""
    user = get_current_user()
    if not user:
        return
    
    role = user.get('role')
    
    # Key metrics overview
    st.markdown("### 📊 Today's Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🚛 Active Shipments",
            value="24",
            delta="↑ 3 from yesterday"
        )
    
    with col2:
        st.metric(
            label="⚠️ High Risk",
            value="3",
            delta="↓ 2 from yesterday"
        )
    
    with col3:
        st.metric(
            label="🎯 AI Accuracy",
            value="94.2%",
            delta="↑ 1.3%"
        )
    
    with col4:
        st.metric(
            label="🔄 Override Rate",
            value="12%",
            delta="↓ 3%"
        )
    
    # Recent activity
    st.markdown("### 🕒 Recent Activity")
    
    recent_activities = [
        {"time": "2 mins ago", "action": "High-risk shipment flagged", "status": "pending", "id": "SH001"},
        {"time": "15 mins ago", "action": "Manager override: Approved", "status": "approved", "id": "SH002"},
        {"time": "1 hour ago", "action": "Weather delay predicted", "status": "delayed", "id": "SH003"},
    ]
    
    for activity in recent_activities:
        status_class = f"status-{activity['status']}"
        st.markdown(f"""
        <div style="padding: 0.5rem; margin: 0.5rem 0; border-left: 3px solid #ddd;">
            <span style="color: #666;">{activity['time']}</span> • 
            <strong>{activity['action']}</strong> • 
            <code>{activity['id']}</code>
        </div>
        """, unsafe_allow_html=True)

def main():
    """Main application entry point"""
    # Apply custom styling
    apply_custom_css()
    
    # Initialize session
    init_session_state()
    
    if not is_logged_in():
        # Show login form if not authenticated
        show_login_form()
    else:
        # Show main application interface
        show_user_info_sidebar()
        show_main_navigation()
        show_dashboard_overview()

if __name__ == "__main__":
    main()