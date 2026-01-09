"""
LICS Web Application - Main Entry Point
Logistics Intelligence & Command System

A human-in-the-loop logistics platform where AI predicts delivery risks 
before dispatch, managers make transparent decisions, and customers are 
proactively informed.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from components.auth import login, is_authenticated, get_user_role, display_user_info
from utils.session_manager import init_session_state, display_notifications
from utils.styling import apply_custom_css

# Page configuration
st.set_page_config(
    page_title="LICS - Logistics Intelligence",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
init_session_state()

# Apply custom styling
apply_custom_css()

# Main application logic
def main():
    """Main application entry point"""
    
    # Check authentication
    if not is_authenticated():
        # Show login page
        st.markdown("""
            <div style="text-align: center; padding: 50px 0 30px 0;">
                <h1 style="color: #FF6B35; font-size: 48px;">🚚 LICS</h1>
                <h3 style="color: #666;">Logistics Intelligence & Command System</h3>
                <p style="color: #888; font-size: 14px; margin-top: 20px;">
                    AI suggests, humans decide, customers stay informed
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        login()
        return
    
    # User is authenticated - show main application
    user_role = get_user_role()
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 🧭 Navigation")
        
        # Role-based quick actions
        if user_role == "Seller":
            st.info("📦 **Quick Actions**\n- Create Shipment\n- View My Shipments\n- Track Orders")
        elif user_role == "Manager":
            st.info("🧭 **Quick Actions**\n- Review Decisions\n- Override AI\n- View Risk Heatmap")
        elif user_role == "Supervisor":
            st.info("📊 **Quick Actions**\n- View Analytics\n- System Reports\n- Performance Metrics")
        
        st.markdown("---")
        
        # Display user info
        display_user_info()
    
    # Main content area
    st.markdown(f"""
        <div class="page-header">
            <div class="page-title">Welcome, {st.session_state.user['name']}! 👋</div>
            <div class="page-subtitle">Role: {user_role} | Dashboard Overview</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Display any notifications
    display_notifications()
    
    # Role-based dashboard
    if user_role == "Seller":
        show_seller_dashboard()
    elif user_role == "Manager":
        show_manager_dashboard()
    elif user_role == "Supervisor":
        show_supervisor_dashboard()


def show_seller_dashboard():
    """Dashboard for Seller role"""
    
    st.markdown("### 📦 Seller Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-label">📤 SHIPMENTS CREATED</div>
                <div class="metric-value">0</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-label">🚚 IN TRANSIT</div>
                <div class="metric-value">0</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-label">✅ DELIVERED</div>
                <div class="metric-value">0</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick actions
    st.markdown("### 🚀 Quick Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div class="info-box">
                <h4>📦 Create New Shipment</h4>
                <p>Start a new shipment and get AI-powered risk analysis</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("➕ Create Shipment", use_container_width=True, type="primary"):
            st.info("👉 Navigate to **1_Seller_Portal** page from the sidebar to create shipments")
    
    with col2:
        st.markdown("""
            <div class="info-box">
                <h4>📊 Track Your Shipments</h4>
                <p>Monitor status and get real-time updates</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔍 View Shipments", use_container_width=True):
            st.info("Your shipment history will appear here once you create orders")
    
    st.markdown("---")
    
    # System info
    st.markdown("### ℹ️ How It Works")
    
    with st.expander("📖 Seller Workflow"):
        st.markdown("""
        1. **Create Shipment** - Fill in delivery details
        2. **AI Analysis** - System analyzes risk factors:
           - Address confidence
           - Weather impact
           - Area accessibility
           - Vehicle feasibility
        3. **Get Recommendation** - AI suggests DISPATCH/DELAY/RESCHEDULE
        4. **Accept or Wait** - You can accept AI recommendation or wait for manager review
        5. **Track Progress** - Monitor delivery in real-time
        
        **Key Principle**: AI suggests, but managers make final decisions on high-risk orders.
        """)


def show_manager_dashboard():
    """Dashboard for Manager role"""
    
    st.markdown("### 🧭 Manager Control Tower")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-label">⏳ PENDING REVIEW</div>
                <div class="metric-value">0</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-label">🔴 HIGH RISK</div>
                <div class="metric-value">0</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-label">✋ OVERRIDES TODAY</div>
                <div class="metric-value">0</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-label">📊 ACCURACY</div>
                <div class="metric-value">--</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick actions
    st.markdown("### 🎯 Manager Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div class="warning-box">
                <h4>🧭 Control Tower</h4>
                <p>Review AI decisions, see risk heatmap, apply overrides</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Open Control Tower", use_container_width=True, type="primary"):
            st.info("👉 Navigate to **2_Control_Tower** page from the sidebar")
    
    with col2:
        st.markdown("""
            <div class="info-box">
                <h4>📊 Analytics Dashboard</h4>
                <p>View performance metrics and learning insights</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("📈 View Analytics", use_container_width=True):
            st.info("👉 Navigate to **3_Analytics** page from the sidebar")
    
    st.markdown("---")
    
    # Manager philosophy
    st.markdown("### 💡 Manager Philosophy")
    
    with st.expander("🎯 Human-in-the-Loop Approach"):
        st.markdown("""
        **Why Manager Override Matters:**
        
        ✅ **AI Suggests** - System provides data-driven recommendations
        
        ✅ **You Decide** - Your experience and business context matter
        
        ✅ **System Learns** - Every override helps the AI improve
        
        ✅ **Accountability** - All decisions are logged with reasons
        
        **When to Override:**
        - VIP customer needs
        - Business priorities
        - Ground reality differs from data
        - Weather cleared after AI analysis
        
        **Remember**: Customers forgive delays, not silence. Always communicate proactively.
        """)


def show_supervisor_dashboard():
    """Dashboard for Supervisor role"""
    
    st.markdown("### 📊 Supervisor Analytics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-label">📈 SYSTEM ACCURACY</div>
                <div class="metric-value">--</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-label">✋ OVERRIDE RATE</div>
                <div class="metric-value">--</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-label">📊 DELIVERIES</div>
                <div class="metric-value">0</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.info("📊 Navigate to **3_Analytics** page to view detailed performance metrics and insights")


if __name__ == "__main__":
    main()
