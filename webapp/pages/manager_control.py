"""
Manager Control Tower - Risk-First Command Center
🎯 Human Oversight with AI Support
"""

import streamlit as st
import sys
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Add project paths
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from utils.api_client import (
    is_logged_in,
    get_current_user, 
    get_shipments,
    submit_override,
    update_shipment_status,
    get_shipment_details,
    format_risk_level,
    format_shipment_status
)

# Page configuration
st.set_page_config(
    page_title="Manager Control Tower - LICS",
    page_icon="🎯", 
    layout="wide"
)

def apply_custom_css():
    """Apply custom CSS for control tower design"""
    st.markdown("""
    <style>
    .control-tower-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
    }
    
    .risk-heatmap-card {
        background: #f8f9fa;
        border: 2px solid #e9ecef;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .high-risk-alert {
        background: #f8d7da;
        border: 2px solid #dc3545;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        animation: pulse 2s infinite;
    }
    
    .medium-risk-warning {
        background: #fff3cd;
        border: 2px solid #ffc107;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .shipment-card {
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: white;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .override-panel {
        background: #e3f2fd;
        border: 2px solid #2196f3;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .audit-log-entry {
        background: #f1f3f4;
        border-left: 4px solid #4285f4;
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-radius: 0 5px 5px 0;
        font-family: monospace;
        font-size: 0.9em;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.8; }
        100% { opacity: 1; }
    }
    
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

def check_authentication():
    """Ensure user has manager access"""
    if not is_logged_in():
        st.error("🔐 Please login to access the Manager Control Tower")
        st.stop()
    
    user = get_current_user()
    if not user:
        st.error("❌ User session invalid")
        st.stop()
    
    role = user.get('role')
    if role not in ['manager', 'admin', 'dispatcher']:
        st.error(f"⛔ Access denied. Manager control requires manager role, but you have '{role}' role.")
        st.stop()
    
    return user

def show_control_tower_header():
    """Display control tower header with real-time status"""
    st.markdown(f"""
    <div class="control-tower-header">
        <h1>🎯 Manager Control Tower</h1>
        <p style="font-size: 1.2em; margin: 0.5rem 0;">
            🧠 AI Analysis • 👁️ Human Oversight • ⚡ Real-time Decisions
        </p>
        <p style="opacity: 0.9; margin: 0;">
            Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} • 
            System Status: 🟢 Operational
        </p>
    </div>
    """, unsafe_allow_html=True)

def show_executive_dashboard():
    """Show executive-level metrics and alerts"""
    st.markdown("### 📊 Executive Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #dc3545;">🚨 High Risk</h3>
            <h2>4</h2>
            <p style="color: #dc3545;">Require Immediate Attention</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #ffc107;">⚠️ Medium Risk</h3>
            <h2>12</h2>
            <p style="color: #856404;">Monitor Closely</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #28a745;">✅ Low Risk</h3>
            <h2>28</h2>
            <p style="color: #155724;">Proceeding Normally</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #6f42c1;">🎯 Accuracy</h3>
            <h2>94.2%</h2>
            <p style="color: #495057;">AI Prediction Rate</p>
        </div>
        """, unsafe_allow_html=True)

def show_risk_heatmap():
    """Display interactive risk heatmap"""
    st.markdown("### 🗺️ Risk Heatmap")
    
    # Create mock data for risk heatmap
    risk_data = [
        {"shipment_id": "SH001", "route": "NYC → LA", "risk": 0.85, "priority": "express", "status": "pending"},
        {"shipment_id": "SH002", "route": "Chicago → Miami", "risk": 0.72, "priority": "urgent", "status": "approved"}, 
        {"shipment_id": "SH003", "route": "Seattle → Denver", "risk": 0.45, "priority": "standard", "status": "in_transit"},
        {"shipment_id": "SH004", "route": "Boston → Atlanta", "risk": 0.91, "priority": "express", "status": "pending"},
        {"shipment_id": "SH005", "route": "Dallas → Phoenix", "risk": 0.23, "priority": "standard", "status": "approved"},
        {"shipment_id": "SH006", "route": "Portland → Vegas", "risk": 0.58, "priority": "urgent", "status": "pending"}
    ]
    
    df = pd.DataFrame(risk_data)
    
    # Create risk visualization
    fig = px.scatter(
        df,
        x="shipment_id",
        y="risk",
        color="risk",
        size=[1]*len(df),  # Uniform size
        color_continuous_scale=["green", "yellow", "red"],
        hover_data=["route", "priority", "status"],
        title="Shipment Risk Analysis"
    )
    
    fig.update_layout(
        height=400,
        xaxis_title="Shipment ID",
        yaxis_title="Risk Score",
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_high_priority_alerts():
    """Display high-priority alerts requiring immediate attention"""
    st.markdown("### 🚨 High Priority Alerts")
    
    # High risk shipments
    high_risk_shipments = [
        {
            "id": "SH004",
            "route": "Boston → Atlanta",
            "risk": 0.91,
            "reason": "Weather alert: Severe storm predicted in delivery zone",
            "ai_recommendation": "Delay shipment by 24 hours or use alternate route",
            "customer": "Tech Solutions Inc.",
            "value": 15000
        },
        {
            "id": "SH001", 
            "route": "NYC → LA",
            "risk": 0.85,
            "reason": "High-value cargo + Express priority + Limited vehicle availability",
            "ai_recommendation": "Assign premium vehicle with tracking + insurance",
            "customer": "Luxury Retail Co.",
            "value": 25000
        }
    ]
    
    for shipment in high_risk_shipments:
        risk_label, risk_class, risk_icon = format_risk_level(shipment["risk"])
        
        st.markdown(f"""
        <div class="high-risk-alert">
            <h4>{risk_icon} {shipment['id']} - {shipment['route']} ({risk_label})</h4>
            <p><strong>Customer:</strong> {shipment['customer']} | <strong>Value:</strong> ${shipment['value']:,}</p>
            <p><strong>Risk Factor:</strong> {shipment['reason']}</p>
            <p><strong>🧠 AI Recommendation:</strong> {shipment['ai_recommendation']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Override decision panel
        show_override_panel(shipment["id"], shipment)

def show_override_panel(shipment_id: str, shipment_data: Dict[str, Any]):
    """Show manager override decision panel"""
    st.markdown(f"""
    <div class="override-panel">
        <h4>🎯 Manager Decision Required - {shipment_id}</h4>
        <p style="margin: 0; font-style: italic;">
            AI suggests action, but human judgment takes precedence
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(f"✅ Approve as Planned", key=f"approve_{shipment_id}", type="primary"):
            handle_override_decision(shipment_id, "approve", "Approved as planned despite risk")
    
    with col2:
        if st.button(f"⚠️ Approve with Conditions", key=f"conditional_{shipment_id}"):
            handle_override_decision(shipment_id, "conditional", "Approved with special conditions")
    
    with col3:
        if st.button(f"❌ Reject/Delay", key=f"reject_{shipment_id}", type="secondary"):
            handle_override_decision(shipment_id, "reject", "Rejected due to high risk")
    
    # Override reason input
    reason = st.text_input(
        f"Override Reason for {shipment_id}",
        key=f"reason_{shipment_id}",
        placeholder="Explain your decision (required for audit trail)..."
    )
    
    return reason

def handle_override_decision(shipment_id: str, decision: str, default_reason: str):
    """Handle manager override decision"""
    reason = st.session_state.get(f"reason_{shipment_id}", default_reason)
    
    if not reason.strip():
        st.error("⚠️ Override reason is required for audit trail")
        return
    
    with st.spinner(f"⏳ Processing override decision for {shipment_id}..."):
        result = submit_override(shipment_id, decision, reason)
    
    if result.get("success"):
        st.success(f"✅ Override decision recorded for {shipment_id}")
        
        # Log to audit trail
        log_entry = {
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "shipment_id": shipment_id,
            "decision": decision,
            "reason": reason,
            "manager": get_current_user().get('username')
        }
        
        if 'audit_log' not in st.session_state:
            st.session_state.audit_log = []
        
        st.session_state.audit_log.insert(0, log_entry)
        
        # Show confirmation
        st.info(f"📋 Decision: {decision.title()} | Reason: {reason}")
        
    else:
        st.error(f"❌ Failed to record override: {result.get('error')}")

def show_shipment_monitoring():
    """Show comprehensive shipment monitoring"""
    st.markdown("### 📦 Active Shipment Monitoring")
    
    # Get shipments (mock data for demo)
    shipments = [
        {
            "id": "SH001",
            "status": "pending_approval",
            "route": "NYC → LA", 
            "customer": "Luxury Retail Co.",
            "risk": 0.85,
            "priority": "express",
            "created": "2024-01-15 10:30",
            "deadline": "2024-01-17 18:00"
        },
        {
            "id": "SH002",
            "status": "in_transit",
            "route": "Chicago → Miami",
            "customer": "Medical Supplies Inc.", 
            "risk": 0.72,
            "priority": "urgent",
            "created": "2024-01-15 08:15", 
            "deadline": "2024-01-16 12:00"
        },
        {
            "id": "SH003",
            "status": "delivered",
            "route": "Seattle → Denver",
            "customer": "Tech Solutions",
            "risk": 0.45,
            "priority": "standard",
            "created": "2024-01-14 14:20",
            "deadline": "2024-01-16 17:00"
        }
    ]
    
    # Filter controls
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            ["all", "pending_approval", "in_transit", "delivered", "delayed"],
            format_func=lambda x: "All Statuses" if x == "all" else format_shipment_status(x)
        )
    
    with col2:
        risk_filter = st.selectbox(
            "Filter by Risk",
            ["all", "high", "medium", "low"],
            format_func=lambda x: "All Risk Levels" if x == "all" else f"{x.title()} Risk"
        )
    
    with col3:
        priority_filter = st.selectbox(
            "Filter by Priority", 
            ["all", "express", "urgent", "standard"],
            format_func=lambda x: "All Priorities" if x == "all" else x.title()
        )
    
    # Display shipments
    for shipment in shipments:
        risk_label, risk_class, risk_icon = format_risk_level(shipment["risk"])
        status_display = format_shipment_status(shipment["status"])
        
        st.markdown(f"""
        <div class="shipment-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h4>{shipment['id']} - {shipment['route']}</h4>
                <span class="{risk_class}" style="padding: 0.3rem 0.8rem; border-radius: 15px;">
                    {risk_icon} {risk_label}
                </span>
            </div>
            <p><strong>Customer:</strong> {shipment['customer']} | 
            <strong>Priority:</strong> {shipment['priority'].title()} | 
            <strong>Status:</strong> {status_display}</p>
            <p><strong>Created:</strong> {shipment['created']} | 
            <strong>Deadline:</strong> {shipment['deadline']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Action buttons for pending shipments
        if shipment["status"] == "pending_approval":
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                if st.button("✅ Approve", key=f"quick_approve_{shipment['id']}"):
                    update_shipment_status(shipment["id"], "approved", "Quick approval by manager")
                    st.success(f"Approved {shipment['id']}")
            
            with col2:
                if st.button("⏸️ Hold", key=f"hold_{shipment['id']}"):
                    update_shipment_status(shipment["id"], "on_hold", "Put on hold for review")
                    st.warning(f"Put {shipment['id']} on hold")

def show_audit_trail():
    """Display audit trail of all manager decisions"""
    st.markdown("### 📋 Audit Trail")
    
    # Initialize audit log if not exists
    if 'audit_log' not in st.session_state:
        st.session_state.audit_log = [
            {
                "timestamp": "2024-01-15 10:45:23",
                "shipment_id": "SH007",
                "decision": "approve",
                "reason": "Weather cleared, proceed as planned",
                "manager": "admin"
            },
            {
                "timestamp": "2024-01-15 09:30:15", 
                "shipment_id": "SH005",
                "decision": "conditional",
                "reason": "Approved with additional insurance requirement",
                "manager": "admin"
            },
            {
                "timestamp": "2024-01-15 08:15:42",
                "shipment_id": "SH003",
                "decision": "reject",
                "reason": "Customer requested delay due to facility closure",
                "manager": "admin"
            }
        ]
    
    # Display audit entries
    for entry in st.session_state.audit_log[:10]:  # Show last 10 entries
        decision_icon = {"approve": "✅", "conditional": "⚠️", "reject": "❌"}.get(entry["decision"], "📋")
        
        st.markdown(f"""
        <div class="audit-log-entry">
            <strong>{entry['timestamp']}</strong> | {decision_icon} {entry['decision'].upper()} | 
            <strong>{entry['shipment_id']}</strong><br/>
            <strong>Manager:</strong> {entry['manager']} | 
            <strong>Reason:</strong> {entry['reason']}
        </div>
        """, unsafe_allow_html=True)

def show_analytics_summary():
    """Show manager analytics summary"""
    st.markdown("### 📊 Decision Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Override rate chart
        override_data = {
            "Decision": ["Approved", "Conditional", "Rejected", "Auto-Approved"],
            "Count": [25, 8, 5, 62]
        }
        
        fig_pie = px.pie(
            values=override_data["Count"],
            names=override_data["Decision"],
            title="Manager Decision Distribution (Last 30 Days)"
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Risk trend over time
        dates = pd.date_range(start='2024-01-01', end='2024-01-15', freq='D')
        risk_trend = {
            "Date": dates,
            "High Risk": [4, 3, 5, 2, 6, 4, 3, 5, 4, 6, 3, 4, 2, 5, 4],
            "Medium Risk": [12, 10, 15, 8, 18, 12, 10, 14, 11, 16, 9, 12, 7, 13, 12]
        }
        
        fig_line = px.line(
            pd.DataFrame(risk_trend),
            x="Date",
            y=["High Risk", "Medium Risk"],
            title="Risk Trends Over Time"
        )
        st.plotly_chart(fig_line, use_container_width=True)

def main():
    """Main manager control tower function"""
    apply_custom_css()
    
    # Check authentication
    user = check_authentication()
    
    # Header
    show_control_tower_header()
    
    # Navigation tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Command Center", 
        "📦 Shipment Monitor", 
        "📋 Audit Trail",
        "📊 Analytics"
    ])
    
    with tab1:
        show_executive_dashboard()
        st.markdown("---")
        show_high_priority_alerts()
        st.markdown("---") 
        show_risk_heatmap()
    
    with tab2:
        show_shipment_monitoring()
    
    with tab3:
        show_audit_trail()
    
    with tab4:
        show_analytics_summary()

if __name__ == "__main__":
    main()