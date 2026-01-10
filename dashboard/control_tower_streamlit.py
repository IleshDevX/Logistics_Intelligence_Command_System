"""
LICS Control Tower - Streamlit Dashboard
========================================

Main entry point for the Streamlit web application.
Integrates with FastAPI backend and MongoDB.
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

import requests
from datetime import datetime
from database.connection import db_connection

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="LICS Control Tower",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'token' not in st.session_state:
    st.session_state.token = None

# ============================================================================
# AUTHENTICATION CHECK
# ============================================================================

def check_authentication():
    """Check if user is authenticated"""
    if not st.session_state.logged_in:
        st.warning("⚠️ Please login to access the dashboard")
        show_login_page()
        st.stop()

def show_login_page():
    """Display login form"""
    st.title("🔐 LICS Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            # TODO: Call FastAPI login endpoint
            # For now, simulate login
            if username and password:
                st.session_state.logged_in = True
                st.session_state.user = {
                    "username": username,
                    "role": "manager"  # TODO: Get from backend
                }
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error("❌ Please enter username and password")
    
    st.divider()
    st.info("**Demo Credentials:** (Will be replaced with real authentication)")
    st.code("Username: demo_manager\nPassword: demo123")

# ============================================================================
# MAIN DASHBOARD
# ============================================================================

def main_dashboard():
    """Main dashboard content"""
    
    # Header
    st.title("🚚 LICS - Logistics Intelligence & Command System")
    st.caption(f"Welcome, **{st.session_state.user['username']}** ({st.session_state.user['role']})")
    
    # Sidebar
    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Select Page",
            ["Dashboard", "Shipments", "Risk Analysis", "AI Decisions", "Settings"]
        )
        
        st.divider()
        
        # Database Status
        st.subheader("System Status")
        if db_connection.connect():
            st.success(f"✅ MongoDB: Connected")
            st.caption(f"Database: {db_connection.DATABASE_NAME}")
        else:
            st.error("❌ MongoDB: Disconnected")
        
        st.divider()
        
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.token = None
            st.rerun()
    
    # Main Content Area
    if page == "Dashboard":
        show_dashboard_overview()
    elif page == "Shipments":
        show_shipments_page()
    elif page == "Risk Analysis":
        show_risk_analysis_page()
    elif page == "AI Decisions":
        show_ai_decisions_page()
    elif page == "Settings":
        show_settings_page()

# ============================================================================
# PAGE FUNCTIONS
# ============================================================================

def show_dashboard_overview():
    """Dashboard overview page"""
    st.header("📊 Dashboard Overview")
    
    # Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Active Shipments", "0", delta="0")
    
    with col2:
        st.metric("High Risk", "0", delta="0")
    
    with col3:
        st.metric("AI Decisions Today", "0", delta="0")
    
    with col4:
        st.metric("Delivery Success", "0%", delta="0%")
    
    st.divider()
    
    # Database Info
    st.subheader("🗄️ Database Collections")
    
    if db_connection.connect():
        collections = db_connection.db.list_collection_names()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Available Collections:**")
            for coll in collections:
                count = db_connection.db[coll].count_documents({})
                st.write(f"- {coll}: {count} documents")
        
        with col2:
            st.write("**Collection Details:**")
            st.json({
                "users": db_connection.users.count_documents({}),
                "shipments": db_connection.shipments.count_documents({}),
                "risk_scores": db_connection.risk_scores.count_documents({}),
                "decisions": db_connection.decisions.count_documents({}),
                "notifications": db_connection.notifications.count_documents({}),
                "learning_logs": db_connection.learning_logs.count_documents({})
            })
    else:
        st.error("❌ Cannot connect to database")

def show_shipments_page():
    """Shipments management page"""
    st.header("📦 Shipments")
    st.info("Shipment management interface coming soon...")
    
    # Example: Create new shipment
    with st.expander("➕ Create New Shipment"):
        with st.form("new_shipment"):
            col1, col2 = st.columns(2)
            
            with col1:
                shipment_id = st.text_input("Shipment ID")
                origin = st.text_input("Origin")
                destination = st.text_input("Destination")
            
            with col2:
                priority = st.selectbox("Priority", ["low", "medium", "high", "critical"])
                vehicle_type = st.selectbox("Vehicle Type", ["truck", "van", "bike"])
                weight = st.number_input("Weight (kg)", min_value=0.0)
            
            if st.form_submit_button("Create Shipment"):
                st.success("✅ Shipment created! (TODO: Connect to backend)")

def show_risk_analysis_page():
    """Risk analysis page"""
    st.header("⚠️ Risk Analysis")
    st.info("Risk analysis dashboard coming soon...")
    
    st.write("**Features to implement:**")
    st.write("- Real-time risk scoring")
    st.write("- Weather impact visualization")
    st.write("- Address intelligence insights")
    st.write("- Historical risk trends")

def show_ai_decisions_page():
    """AI decisions review page"""
    st.header("🤖 AI Decisions")
    st.info("AI decision review interface coming soon...")
    
    st.write("**Human-in-the-Loop Features:**")
    st.write("- Review AI recommendations")
    st.write("- Approve/override decisions")
    st.write("- Provide feedback for learning")
    st.write("- Track decision accuracy")

def show_settings_page():
    """Settings page"""
    st.header("⚙️ Settings")
    
    st.subheader("User Information")
    st.json(st.session_state.user)
    
    st.divider()
    
    st.subheader("Application Configuration")
    
    # Check if we're using Streamlit secrets
    try:
        import streamlit as st_secrets
        if hasattr(st_secrets, 'secrets'):
            st.success("✅ Using Streamlit secrets (Cloud mode)")
            st.write("**MongoDB:**")
            st.write(f"- URI: {st.secrets['mongodb']['uri'][:20]}... (hidden)")
            st.write(f"- Database: {st.secrets['mongodb']['database']}")
    except:
        st.warning("⚠️ Using environment variables (Local mode)")
        st.write("Make sure `.streamlit/secrets.toml` is configured for cloud deployment")
    
    st.divider()
    
    st.subheader("System Information")
    st.write(f"- Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.write(f"- Database: {db_connection.DATABASE_NAME}")
    st.write(f"- Connection: {'Active' if db_connection._client else 'Inactive'}")

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main application entry point"""
    
    # Check authentication
    if not st.session_state.logged_in:
        show_login_page()
    else:
        main_dashboard()

if __name__ == "__main__":
    main()
