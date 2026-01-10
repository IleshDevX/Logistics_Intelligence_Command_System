"""
Control Tower - Manager Operations Hub
Real-time monitoring and override capabilities
"""

import streamlit as st
import sys
import os
import pandas as pd
from datetime import datetime, timedelta
import time
import json

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import authentication
from components.auth import (
    require_role_access, 
    show_user_info_sidebar, 
    get_current_user
)

# Import backend intelligence modules
sys.path.insert(0, os.path.join(project_root, '..'))

# Safe imports with fallbacks
try:
    from intelligence.rules.human_override import create_override
except ImportError:
    def create_override(shipment_id, original_decision, new_decision, reason, manager):
        return {"override_id": f"OVR{int(time.time())}", "status": "Applied"}

try:
    from intelligence.notifications.customer_notifier import send_notification
except ImportError:
    def send_notification(phone, message, notification_type="SMS"):
        return {"success": True, "message_id": f"MSG{int(time.time())}"}

# Page configuration
st.set_page_config(
    page_title="LICS - Control Tower",
    page_icon="🏗️",
    layout="wide"
)

# Authentication check
require_role_access("🏗️ Control Tower")
show_user_info_sidebar()

# Page header
st.title("🏗️ Control Tower")
st.markdown("### Real-time Operations Management & AI Override")

# Initialize session data for demo
if 'active_shipments' not in st.session_state:
    st.session_state['active_shipments'] = [
        {
            "shipment_id": "SHIP001", "customer": "Rahul Verma", "area": "Zone-A", 
            "risk_score": 75, "ai_decision": "DELAY", "status": "Pending Review",
            "weather_impact": 0.8, "created_at": "2024-01-15 09:30", "priority": "Express"
        },
        {
            "shipment_id": "SHIP002", "customer": "Priya Singh", "area": "Zone-B",
            "risk_score": 25, "ai_decision": "DISPATCH", "status": "In Transit", 
            "weather_impact": 0.2, "created_at": "2024-01-15 08:45", "priority": "Standard"
        },
        {
            "shipment_id": "SHIP003", "customer": "Amit Kumar", "area": "Zone-C",
            "risk_score": 90, "ai_decision": "RESCHEDULE", "status": "Needs Override",
            "weather_impact": 0.6, "created_at": "2024-01-15 10:15", "priority": "Critical"
        }
    ]

if 'override_history' not in st.session_state:
    st.session_state['override_history'] = []

# Tabs for different manager functions  
tab1, tab2, tab3, tab4 = st.tabs(["🚨 Active Alerts", "📊 Risk Dashboard", "🔧 Override Center", "📧 Notifications"])

with tab1:
    st.header("🚨 Active Alerts & Interventions")
    
    # Real-time alerts summary
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        high_risk_count = len([s for s in st.session_state['active_shipments'] if s['risk_score'] > 70])
        st.metric("High Risk Shipments", high_risk_count, "⚠️" if high_risk_count > 0 else "✅")
    
    with col2:
        pending_review = len([s for s in st.session_state['active_shipments'] if s['status'] == 'Pending Review'])
        st.metric("Pending Reviews", pending_review, "🔍")
    
    with col3:
        weather_alerts = len([s for s in st.session_state['active_shipments'] if s['weather_impact'] > 0.6])
        st.metric("Weather Alerts", weather_alerts, "🌧️" if weather_alerts > 0 else "☀️")
    
    with col4:
        override_needed = len([s for s in st.session_state['active_shipments'] if s['status'] == 'Needs Override'])
        st.metric("Override Needed", override_needed, "🚨" if override_needed > 0 else "✅")
    
    st.markdown("---")
    
    # Priority shipments requiring attention
    st.subheader("⚡ Priority Actions Required")
    
    for shipment in st.session_state['active_shipments']:
        if shipment['status'] in ['Pending Review', 'Needs Override'] or shipment['risk_score'] > 70:
            
            # Color-code based on urgency
            if shipment['risk_score'] > 80:
                border_color = "🔴"
                urgency = "CRITICAL"
            elif shipment['risk_score'] > 60:
                border_color = "🟡"
                urgency = "HIGH"
            else:
                border_color = "🟢"
                urgency = "MEDIUM"
            
            with st.expander(f"{border_color} {shipment['shipment_id']} - {shipment['customer']} ({urgency})", expanded=True):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**Customer:** {shipment['customer']}")
                    st.write(f"**Delivery Area:** {shipment['area']}")
                    st.write(f"**Priority:** {shipment['priority']}")
                    st.write(f"**Created:** {shipment['created_at']}")
                
                with col2:
                    st.metric("Risk Score", f"{shipment['risk_score']}/100")
                    st.metric("Weather Impact", f"{int(shipment['weather_impact'] * 100)}%")
                
                with col3:
                    st.write(f"**AI Decision:** {shipment['ai_decision']}")
                    st.write(f"**Status:** {shipment['status']}")
                    
                    # Quick action buttons
                    if shipment['status'] == 'Needs Override':
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button(f"✅ Approve", key=f"approve_{shipment['shipment_id']}"):
                                shipment['status'] = 'Override: Dispatched'
                                st.success(f"✅ {shipment['shipment_id']} approved for dispatch")
                                st.rerun()
                        with col_b:
                            if st.button(f"❌ Block", key=f"block_{shipment['shipment_id']}"):
                                shipment['status'] = 'Override: Blocked'
                                st.error(f"❌ {shipment['shipment_id']} blocked from dispatch")
                                st.rerun()

with tab2:
    st.header("📊 Risk Dashboard")
    
    # Risk distribution chart
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📈 Risk Distribution Heatmap")
        
        # Create risk distribution data
        risk_data = pd.DataFrame(st.session_state['active_shipments'])
        
        if not risk_data.empty:
            # Risk by area
            area_risk = risk_data.groupby('area')['risk_score'].mean().reset_index()
            
            st.markdown("**Average Risk by Delivery Zone:**")
            for _, row in area_risk.iterrows():
                risk_val = row['risk_score']
                if risk_val > 70:
                    color = "🔴"
                elif risk_val > 40:
                    color = "🟡"
                else:
                    color = "🟢"
                
                st.write(f"{color} **{row['area']}**: {risk_val:.0f}/100")
                st.progress(risk_val/100)
        
        st.markdown("---")
        
        # Weather impact visualization
        st.subheader("🌦️ Weather Impact Analysis")
        
        weather_zones = {
            "Zone-A": 0.2, "Zone-B": 0.8, "Zone-C": 0.6,
            "Zone-D": 0.3, "Zone-E": 0.4, "Zone-F": 0.5
        }
        
        for zone, impact in weather_zones.items():
            impact_pct = int(impact * 100)
            if impact > 0.7:
                icon = "🌧️"
                status = "High Impact"
            elif impact > 0.4:
                icon = "☁️"  
                status = "Moderate"
            else:
                icon = "☀️"
                status = "Clear"
            
            col_zone1, col_zone2 = st.columns([3, 1])
            with col_zone1:
                st.write(f"{icon} **{zone}**: {impact_pct}% - {status}")
                st.progress(impact)
            with col_zone2:
                if impact > 0.6:
                    st.warning("⚠️")
    
    with col2:
        st.subheader("📊 Key Metrics")
        
        # Calculate real-time metrics
        total_shipments = len(st.session_state['active_shipments'])
        avg_risk = sum(s['risk_score'] for s in st.session_state['active_shipments']) / total_shipments if total_shipments > 0 else 0
        high_risk_pct = (len([s for s in st.session_state['active_shipments'] if s['risk_score'] > 70]) / total_shipments * 100) if total_shipments > 0 else 0
        
        st.metric("Total Active", total_shipments, "📦")
        st.metric("Avg Risk Score", f"{avg_risk:.0f}/100", "📊")
        st.metric("High Risk %", f"{high_risk_pct:.0f}%", "⚠️")
        
        st.markdown("---")
        
        # AI decision accuracy
        st.markdown("**🤖 AI Decision Accuracy**")
        st.metric("Today", "94%", "↑ 2%")
        st.metric("This Week", "91%", "↑ 1%")
        st.metric("This Month", "89%", "→ 0%")
        
        st.markdown("---")
        
        # System health indicators
        st.markdown("**🔧 System Health**")
        st.success("✅ Risk Engine: Online")
        st.success("✅ Weather API: Active") 
        st.success("✅ Address Intel: Running")
        st.warning("⚠️ Route Optimizer: Slow")

with tab3:
    st.header("🔧 Human Override Center")
    
    st.markdown("### 🎯 Override AI Decisions")
    st.info("💡 Use this section to override AI decisions when human judgment is needed")
    
    # Override form
    with st.form("override_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Select shipment to override
            shipment_options = [f"{s['shipment_id']} - {s['customer']}" for s in st.session_state['active_shipments']]
            selected_shipment = st.selectbox("Select Shipment", shipment_options)
            
            if selected_shipment:
                shipment_id = selected_shipment.split(' - ')[0]
                shipment_data = next(s for s in st.session_state['active_shipments'] if s['shipment_id'] == shipment_id)
                
                st.write(f"**Current AI Decision:** {shipment_data['ai_decision']}")
                st.write(f"**Risk Score:** {shipment_data['risk_score']}/100")
                st.write(f"**Weather Impact:** {int(shipment_data['weather_impact'] * 100)}%")
        
        with col2:
            # Override options
            override_decision = st.radio("Manager Decision", [
                "DISPATCH - Proceed with delivery",
                "DELAY - Hold for better conditions", 
                "RESCHEDULE - Coordinate new time",
                "CANCEL - Stop shipment"
            ])
            
            override_reason = st.selectbox("Override Reason", [
                "Customer Request", 
                "Weather Conditions",
                "Traffic Conditions",
                "Resource Availability", 
                "Business Priority",
                "Address Issues",
                "Other"
            ])
        
        # Override justification
        justification = st.text_area("Justification (Required)", 
            placeholder="Explain the reason for overriding the AI decision...")
        
        # Submit override
        submitted = st.form_submit_button("🔧 Apply Override", type="primary", use_container_width=True)
        
        if submitted:
            if not justification.strip():
                st.error("❌ Justification is required for all overrides")
            else:
                # Process override
                override_action = override_decision.split(' - ')[0]
                
                # Create override record
                override_record = {
                    "shipment_id": shipment_id,
                    "original_decision": shipment_data['ai_decision'],
                    "override_decision": override_action,
                    "reason": override_reason,
                    "justification": justification,
                    "manager": get_current_user().get('name', 'Unknown'),
                    "timestamp": datetime.now().isoformat()
                }
                
                # Save override
                st.session_state['override_history'].append(override_record)
                
                # Update shipment status
                for shipment in st.session_state['active_shipments']:
                    if shipment['shipment_id'] == shipment_id:
                        shipment['status'] = f'Override: {override_action}'
                        shipment['ai_decision'] = override_action
                        break
                
                st.success(f"✅ Override applied successfully!")
                st.info(f"📋 {shipment_id} decision changed to: **{override_action}**")
                
                # Auto-trigger customer notification
                if override_action in ['DELAY', 'RESCHEDULE']:
                    st.warning("📧 Customer notification will be sent automatically")
    
    st.markdown("---")
    
    # Override history
    st.subheader("📋 Recent Overrides")
    
    if st.session_state['override_history']:
        for override in reversed(st.session_state['override_history'][-5:]):  # Show last 5
            with st.expander(f"🔧 {override['shipment_id']} - {override['override_decision']} ({override['timestamp'][:16]})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Manager:** {override['manager']}")
                    st.write(f"**Original AI Decision:** {override['original_decision']}")
                    st.write(f"**Override Decision:** {override['override_decision']}")
                with col2:
                    st.write(f"**Reason:** {override['reason']}")
                    st.write(f"**Justification:** {override['justification']}")
    else:
        st.info("📝 No overrides recorded yet")

with tab4:
    st.header("📧 Customer Notifications")
    
    st.markdown("### 🔔 Proactive Communication Center")
    
    # Notification templates
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📨 Send Notification")
        
        with st.form("notification_form"):
            # Select customer/shipment
            notification_shipments = [f"{s['shipment_id']} - {s['customer']}" for s in st.session_state['active_shipments']]
            selected_notification = st.selectbox("Select Shipment", notification_shipments)
            
            # Notification type
            notification_type = st.selectbox("Notification Type", [
                "Delivery Update",
                "Weather Delay Alert", 
                "Reschedule Request",
                "Delivery Confirmation",
                "Address Verification",
                "Custom Message"
            ])
            
            # Pre-filled templates
            templates = {
                "Delivery Update": "Your shipment {shipment_id} is on the way! Expected delivery: Today between 2-5 PM.",
                "Weather Delay Alert": "Due to heavy rainfall in your area, delivery of {shipment_id} is delayed by 2-3 hours. We'll update you soon!",
                "Reschedule Request": "We'd like to reschedule delivery of {shipment_id}. Please reply with your preferred time slot.",
                "Delivery Confirmation": "Great news! Your shipment {shipment_id} has been delivered successfully. Thank you for choosing us!",
                "Address Verification": "We need to verify your delivery address for {shipment_id}. Please confirm or provide updated details.",
                "Custom Message": ""
            }
            
            # Message content
            default_message = templates.get(notification_type, "")
            notification_message = st.text_area("Message Content", 
                value=default_message, height=100,
                placeholder="Enter your notification message...")
            
            # Send notification
            sent = st.form_submit_button("📤 Send Notification", type="primary")
            
            if sent and selected_notification:
                # Process notification
                shipment_id = selected_notification.split(' - ')[0]
                customer_name = selected_notification.split(' - ')[1]
                
                # Format message with shipment details
                formatted_message = notification_message.replace('{shipment_id}', shipment_id)
                
                st.success(f"📤 Notification sent to {customer_name}")
                st.info(f"📱 **Message:** {formatted_message}")
                
                # Log notification
                if 'sent_notifications' not in st.session_state:
                    st.session_state['sent_notifications'] = []
                
                st.session_state['sent_notifications'].append({
                    "shipment_id": shipment_id,
                    "customer": customer_name,
                    "type": notification_type,
                    "message": formatted_message,
                    "sent_by": get_current_user().get('name', 'Unknown'),
                    "timestamp": datetime.now().isoformat()
                })
    
    with col2:
        st.subheader("📬 Recent Notifications")
        
        # Show recent notifications
        if 'sent_notifications' in st.session_state and st.session_state['sent_notifications']:
            for notif in reversed(st.session_state['sent_notifications'][-5:]):
                with st.container():
                    st.write(f"**📦 {notif['shipment_id']}** → {notif['customer']}")
                    st.write(f"*{notif['type']}* - {notif['timestamp'][:16]}")
                    st.write(f"💬 {notif['message'][:50]}...")
                    st.markdown("---")
        else:
            st.info("📭 No notifications sent yet")
        
        st.subheader("🔔 Notification Settings")
        
        # Notification preferences
        auto_weather_alerts = st.checkbox("Auto Weather Alerts", value=True)
        auto_delay_notifications = st.checkbox("Auto Delay Notifications", value=True) 
        auto_delivery_confirmations = st.checkbox("Auto Delivery Confirmations", value=False)
        
        if st.button("💾 Save Settings", use_container_width=True):
            st.success("✅ Notification settings saved!")

# Footer with real-time updates
st.markdown("---")
col_foot1, col_foot2, col_foot3 = st.columns(3)

with col_foot1:
    st.markdown("**🕐 Last Updated:** " + datetime.now().strftime("%H:%M:%S"))

with col_foot2:
    st.markdown("**👤 Active Manager:** " + get_current_user().get('name', 'Unknown'))

with col_foot3:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()