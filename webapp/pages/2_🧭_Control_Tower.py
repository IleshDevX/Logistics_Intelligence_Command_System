"""
Manager Control Tower - Review AI decisions and apply human overrides
The heart of human-in-the-loop decision making
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import streamlit as st
import pandas as pd
from datetime import datetime
from components.auth import require_auth, get_current_user
from utils.session_manager import init_session_state, add_notification, display_notifications
from utils.styling import apply_custom_css, get_risk_badge_html, get_decision_badge_html

# Import backend modules
from ingestion.load_data import load_all_data
from models.risk_engine import risk_bucket
from rules.human_override import apply_human_override, is_locked, get_override_history, OVERRIDE_REASONS
from rules.pre_dispatch_gate import pre_dispatch_decision, get_decision_explanation

# Page configuration
st.set_page_config(
    page_title="Control Tower - LICS",
    page_icon="🧭",
    layout="wide"
)

# Initialize and apply
init_session_state()
apply_custom_css()
require_auth(allowed_roles=["Manager", "Supervisor"])

# Get current user
user = get_current_user()
user_role = user['role']

# Page header
st.markdown("""
    <div class="page-header">
        <div class="page-title">🧭 Manager Control Tower</div>
        <div class="page-subtitle">Review AI decisions, apply overrides, and manage delivery risk</div>
    </div>
""", unsafe_allow_html=True)

display_notifications()

# Load data
@st.cache_data
def load_shipment_data():
    """Load and process shipment data"""
    shipments, addresses, history, weather, resources = load_all_data()
    
    # Merge shipment with address data
    merged = shipments.merge(addresses, on='shipment_id', how='left')
    
    # Add risk bucket
    merged['risk_bucket'] = merged['current_risk_score'].apply(risk_bucket)
    
    # Add status (mock for now)
    merged['status'] = 'Pending Review'
    
    return merged

try:
    df = load_shipment_data()
    
    # Sidebar filters
    with st.sidebar:
        st.markdown("### 🔍 Filters")
        
        # City filter
        cities = ['All'] + sorted(df['destination_city'].unique().tolist())
        selected_city = st.selectbox("City", cities, key="city_filter")
        
        # Risk filter
        risk_levels = ['All', 'High', 'Medium', 'Low']
        selected_risk = st.selectbox("Risk Level", risk_levels, key="risk_filter")
        
        # Status filter
        statuses = ['All', 'Pending Review', 'Approved', 'Delayed', 'Rescheduled']
        selected_status = st.selectbox("Status", statuses, key="status_filter")
        
        # Score range filter
        st.markdown("**Risk Score Range**")
        score_range = st.slider("Score", 0, 100, (0, 100), key="score_range")
        
        # Apply filters
        filtered_df = df.copy()
        
        if selected_city != 'All':
            filtered_df = filtered_df[filtered_df['destination_city'] == selected_city]
        
        if selected_risk != 'All':
            filtered_df = filtered_df[filtered_df['risk_bucket'] == selected_risk]
        
        if selected_status != 'All':
            filtered_df = filtered_df[filtered_df['status'] == selected_status]
        
        filtered_df = filtered_df[
            (filtered_df['current_risk_score'] >= score_range[0]) & 
            (filtered_df['current_risk_score'] <= score_range[1])
        ]
        
        st.markdown("---")
        st.info(f"📊 Showing **{len(filtered_df)}** of {len(df)} shipments")
        
        # Reset filters
        if st.button("🔄 Reset Filters", use_container_width=True):
            st.rerun()
    
    # Main content - Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Risk Heatmap", "📋 Shipment Review", "📜 Override History"])
    
    with tab1:
        st.markdown("### 📊 Risk Distribution Heatmap")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            high_risk_count = len(filtered_df[filtered_df['risk_bucket'] == 'High'])
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">🔴 HIGH RISK</div>
                    <div class="metric-value">{high_risk_count}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            medium_risk_count = len(filtered_df[filtered_df['risk_bucket'] == 'Medium'])
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">🟡 MEDIUM RISK</div>
                    <div class="metric-value">{medium_risk_count}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            low_risk_count = len(filtered_df[filtered_df['risk_bucket'] == 'Low'])
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">🟢 LOW RISK</div>
                    <div class="metric-value">{low_risk_count}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col4:
            avg_risk = filtered_df['current_risk_score'].mean()
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">📊 AVG RISK</div>
                    <div class="metric-value">{avg_risk:.0f}</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Risk by city
        st.markdown("#### 🗺️ Risk Distribution by City")
        
        city_risk = filtered_df.groupby(['destination_city', 'risk_bucket']).size().unstack(fill_value=0)
        
        # Display as colored table
        for city in city_risk.index:
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                st.markdown(f"**{city}**")
            with col2:
                high = city_risk.loc[city, 'High'] if 'High' in city_risk.columns else 0
                st.markdown(f"🔴 {high}")
            with col3:
                medium = city_risk.loc[city, 'Medium'] if 'Medium' in city_risk.columns else 0
                st.markdown(f"🟡 {medium}")
            with col4:
                low = city_risk.loc[city, 'Low'] if 'Low' in city_risk.columns else 0
                st.markdown(f"🟢 {low}")
        
        st.markdown("---")
        
        # Top risky shipments
        st.markdown("#### ⚠️ Highest Risk Shipments (Top 10)")
        
        top_risky = filtered_df.nlargest(10, 'current_risk_score')[
            ['shipment_id', 'destination_city', 'current_risk_score', 'risk_bucket', 'payment_type', 'area_type']
        ]
        
        for idx, row in top_risky.iterrows():
            with st.expander(f"🔴 {row['shipment_id']} - Score: {row['current_risk_score']:.0f} ({row['risk_bucket']})"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("City", row['destination_city'])
                with col2:
                    st.metric("Payment", row['payment_type'])
                with col3:
                    st.metric("Area", row['area_type'])
                
                if st.button(f"📝 Review {row['shipment_id']}", key=f"review_{row['shipment_id']}"):
                    st.session_state.selected_shipment = row['shipment_id']
                    st.info("👉 Go to 'Shipment Review' tab to review this shipment")
    
    with tab2:
        st.markdown("### 📋 Shipment Review & Override")
        
        # Select shipment to review
        if 'selected_shipment' not in st.session_state:
            st.session_state.selected_shipment = None
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            shipment_ids = filtered_df['shipment_id'].tolist()
            selected_id = st.selectbox(
                "Select Shipment to Review",
                shipment_ids,
                index=shipment_ids.index(st.session_state.selected_shipment) if st.session_state.selected_shipment in shipment_ids else 0
            )
            st.session_state.selected_shipment = selected_id
        
        with col2:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()
        
        if selected_id:
            # Get shipment details
            shipment = filtered_df[filtered_df['shipment_id'] == selected_id].iloc[0]
            
            st.markdown("---")
            st.markdown(f"### 📦 Shipment: {selected_id}")
            
            # Shipment details
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("#### 📍 Delivery Info")
                st.markdown(f"**City:** {shipment['destination_city']}")
                st.markdown(f"**Area:** {shipment['area_type']}")
                st.markdown(f"**Road:** {shipment['road_accessibility']}")
                st.markdown(f"**Address Confidence:** {shipment['address_confidence_score']:.0f}%")
            
            with col2:
                st.markdown("#### 📦 Package Info")
                st.markdown(f"**Product:** {shipment['product_name']}")
                st.markdown(f"**Weight:** {shipment['weight_kg']} kg")
                st.markdown(f"**Payment:** {shipment['payment_type']}")
                st.markdown(f"**Priority:** {'Yes' if shipment['priority_flag'] == 1 else 'No'}")
            
            with col3:
                st.markdown("#### ⚠️ Risk Assessment")
                st.markdown(
                    get_risk_badge_html(shipment['current_risk_score'], shipment['risk_bucket']),
                    unsafe_allow_html=True
                )
                st.markdown(f"**Weather Severity:** {shipment['weather_severity']}")
                st.markdown(f"**Weather Impact:** {shipment['weather_impact_factor']:.0f}")
            
            st.markdown("---")
            
            # AI Decision
            st.markdown("### 🤖 AI Recommendation")
            
            decision_result = pre_dispatch_decision(
                risk_score=shipment['current_risk_score'],
                weather_impact_factor=shipment['weather_impact_factor'],
                address_confidence_score=shipment['address_confidence_score']
            )
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown(
                    get_decision_badge_html(decision_result['decision']),
                    unsafe_allow_html=True
                )
            
            with col2:
                st.markdown("**AI Reasoning:**")
                if decision_result['reasons']:
                    for reason in decision_result['reasons']:
                        st.markdown(f"- {reason}")
                else:
                    st.markdown("- All factors within safe thresholds")
            
            st.markdown("---")
            
            # Manager Override Section (only for Managers)
            if user_role == "Manager":
                st.markdown("### ✋ Manager Override")
                
                # Check if already locked
                if is_locked(selected_id):
                    st.warning("🔒 This shipment has already been overridden and is locked")
                    
                    # Show override history for this shipment
                    history = get_override_history()
                    if not history.empty:
                        shipment_history = history[history['shipment_id'] == selected_id]
                        if not shipment_history.empty:
                            last_override = shipment_history.iloc[-1]
                            st.info(f"""
                            **Last Override:**
                            - Original Decision: {last_override['ai_decision']}
                            - Override Decision: {last_override['override_decision']}
                            - Reason: {last_override['reason']}
                            - By: Manager at {last_override['timestamp']}
                            """)
                else:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### 🎯 Your Decision")
                        
                        override_decision = st.radio(
                            "Override AI Decision?",
                            ["Accept AI Recommendation", "Override: DISPATCH", "Override: DELAY", "Override: RESCHEDULE"],
                            key=f"override_{selected_id}"
                        )
                        
                        # Determine final decision
                        if override_decision == "Accept AI Recommendation":
                            final_decision = decision_result['decision']
                            is_override = False
                        else:
                            final_decision = override_decision.split(": ")[1]
                            is_override = True
                    
                    with col2:
                        st.markdown("#### 📝 Mandatory Reason")
                        
                        if is_override:
                            override_reason = st.selectbox(
                                "Select Reason for Override *",
                                OVERRIDE_REASONS,
                                key=f"reason_{selected_id}"
                            )
                            
                            additional_notes = st.text_area(
                                "Additional Notes (Optional)",
                                placeholder="Any extra context for this decision...",
                                key=f"notes_{selected_id}"
                            )
                        else:
                            st.info("✅ Accepting AI recommendation - no override reason needed")
                            override_reason = None
                            additional_notes = ""
                    
                    st.markdown("---")
                    
                    # Preview decision
                    st.markdown("### 👁️ Decision Preview")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown("**AI Recommended:**")
                        st.code(decision_result['decision'])
                    
                    with col2:
                        st.markdown("**Your Decision:**")
                        st.code(final_decision)
                    
                    with col3:
                        st.markdown("**Status:**")
                        if is_override:
                            st.markdown("🔄 **OVERRIDE**")
                        else:
                            st.markdown("✅ **ACCEPTED**")
                    
                    st.markdown("---")
                    
                    # Apply decision
                    col1, col2, col3 = st.columns([1, 1, 1])
                    
                    with col2:
                        if is_override and not override_reason:
                            st.warning("⚠️ Please select a reason for override")
                        else:
                            if st.button("✅ Confirm & Apply Decision", use_container_width=True, type="primary"):
                                # Apply override (or log acceptance)
                                if is_override:
                                    reason_text = override_reason
                                    if additional_notes:
                                        reason_text += f" | Notes: {additional_notes}"
                                    
                                    result = apply_human_override(
                                        shipment_id=selected_id,
                                        ai_decision=decision_result['decision'],
                                        override_decision=final_decision,
                                        override_reason=reason_text
                                    )
                                    
                                    if result['status'] == 'OVERRIDDEN':
                                        add_notification(
                                            f"✋ Override applied to {selected_id}: {decision_result['decision']} → {final_decision}",
                                            "success"
                                        )
                                        st.balloons()
                                    else:
                                        add_notification(f"Error: {result.get('message', 'Unknown error')}", "error")
                                else:
                                    add_notification(
                                        f"✅ AI recommendation accepted for {selected_id}: {final_decision}",
                                        "success"
                                    )
                                
                                st.rerun()
            else:
                # Supervisor view only
                st.info("👁️ **Supervisor View Only** - You can review decisions but cannot apply overrides")
                st.markdown(f"**AI Decision:** {decision_result['decision']}")
                st.markdown(f"**Reasoning:** {get_decision_explanation(decision_result)}")
    
    with tab3:
        st.markdown("### 📜 Override History & Audit Log")
        
        # Load override history
        history = get_override_history()
        
        if history.empty:
            st.info("📋 No overrides recorded yet. All decisions are following AI recommendations.")
        else:
            # Summary metrics
            total_overrides = len(history)
            override_types = history['override_decision'].value_counts()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Overrides", total_overrides)
            with col2:
                dispatch_overrides = override_types.get('DISPATCH', 0)
                st.metric("→ DISPATCH", dispatch_overrides)
            with col3:
                delay_overrides = override_types.get('DELAY', 0)
                st.metric("→ DELAY", delay_overrides)
            with col4:
                reschedule_overrides = override_types.get('RESCHEDULE', 0)
                st.metric("→ RESCHEDULE", reschedule_overrides)
            
            st.markdown("---")
            
            # Filter options
            col1, col2 = st.columns(2)
            with col1:
                filter_shipment = st.text_input("Filter by Shipment ID", placeholder="e.g., SHP001")
            with col2:
                filter_decision = st.selectbox("Filter by Override Decision", ["All", "DISPATCH", "DELAY", "RESCHEDULE"])
            
            # Apply filters
            filtered_history = history.copy()
            if filter_shipment:
                filtered_history = filtered_history[filtered_history['shipment_id'].str.contains(filter_shipment, case=False)]
            if filter_decision != "All":
                filtered_history = filtered_history[filtered_history['override_decision'] == filter_decision]
            
            st.markdown(f"**Showing {len(filtered_history)} of {len(history)} overrides**")
            
            # Display history
            for idx, row in filtered_history.iterrows():
                with st.expander(f"📝 {row['shipment_id']} - {row['timestamp']} - {row['ai_decision']} → {row['override_decision']}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown("**Original AI Decision:**")
                        st.code(row['ai_decision'])
                    
                    with col2:
                        st.markdown("**Manager Override:**")
                        st.code(row['override_decision'])
                    
                    with col3:
                        st.markdown("**Locked:**")
                        st.code("Yes" if row['manual_lock'] else "No")
                    
                    st.markdown("**Reason:**")
                    st.info(row['reason'])
                    
                    st.markdown(f"**Timestamp:** {row['timestamp']}")
            
            st.markdown("---")
            
            # Download option
            if st.button("📥 Download Override History (CSV)"):
                csv = history.to_csv(index=False)
                st.download_button(
                    label="⬇️ Download CSV",
                    data=csv,
                    file_name=f"override_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

except Exception as e:
    st.error(f"❌ Error loading data: {str(e)}")
    st.info("💡 Make sure the data files are in the correct location and the backend is properly set up.")
    
    with st.expander("🐛 Debug Information"):
        st.code(str(e))
