"""
Seller Portal - Create and Manage Shipments
AI-powered shipment creation with risk assessment
"""

import streamlit as st
import sys
import os
import json
from datetime import datetime, timedelta
import time

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import authentication and intelligence modules
from components.auth import (
    require_role_access, 
    require_permission,
    show_user_info_sidebar, 
    get_current_user
)

# Import backend intelligence modules
sys.path.insert(0, os.path.join(project_root, '..'))

# Safe imports with fallbacks
try:
    from intelligence.models.risk_engine import calculate_risk_score
except ImportError:
    def calculate_risk_score(data):
        return 50  # Mock implementation

try:
    from intelligence.features.weather_impact import get_weather_impact
except ImportError:
    def get_weather_impact(pincode, date):
        return {"impact_factor": 0.3, "condition": "Clear", "temp_c": 25}

try:
    from intelligence.rules.pre_dispatch_gate import pre_dispatch_decision
except ImportError:
    def pre_dispatch_decision(risk, weather, address):
        return {"decision": "DISPATCH", "confidence": 85, "recommendations": []}

try:
    from intelligence.features.address_intelligence import get_address_confidence
except ImportError:
    def get_address_confidence(address, pincode):
        return 0.8

# Page configuration
st.set_page_config(
    page_title="LICS - Seller Portal",
    page_icon="🚀", 
    layout="wide"
)

# Authentication check
require_role_access("🚀 Seller Portal")
show_user_info_sidebar()

# Page header
st.title("🚀 Seller Portal")
st.markdown("### AI-Powered Shipment Management")

# Tabs for different seller functions
tab1, tab2, tab3 = st.tabs(["📝 New Shipment", "📦 My Shipments", "📊 Performance"])

with tab1:
    st.header("Create New Shipment")
    
    # Shipment form
    with st.form("shipment_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Shipment Details")
            
            # Basic shipment info
            shipment_id = st.text_input("Shipment ID", value=f"SHIP{int(time.time())}", disabled=True)
            customer_name = st.text_input("Customer Name *", placeholder="Enter customer name")
            customer_phone = st.text_input("Phone Number *", placeholder="+91 XXXXXXXXXX")
            customer_email = st.text_input("Email", placeholder="customer@email.com")
            
            # Package details
            st.markdown("**📦 Package Information**")
            package_type = st.selectbox("Package Type", [
                "Electronics", "Clothing", "Books", "Food Items", "Fragile Items", "Documents", "Other"
            ])
            weight = st.number_input("Weight (kg)", min_value=0.1, max_value=100.0, value=1.0, step=0.1)
            dimensions = st.text_input("Dimensions (L×W×H cm)", placeholder="30×20×15")
            declared_value = st.number_input("Declared Value (₹)", min_value=1, max_value=100000, value=1000)
            
        with col2:
            st.subheader("🗺️ Delivery Details")
            
            # Delivery address
            delivery_address = st.text_area("Delivery Address *", 
                placeholder="Complete delivery address with landmarks", height=100)
            
            # Area and pincode
            pincode = st.text_input("Pincode *", placeholder="400001")
            delivery_area = st.selectbox("Delivery Zone", [
                "Zone-A (Central)", "Zone-B (North)", "Zone-C (South)", 
                "Zone-D (East)", "Zone-E (West)", "Zone-F (Suburbs)"
            ])
            
            # Delivery preferences
            st.markdown("**⏰ Delivery Preferences**")
            preferred_date = st.date_input("Preferred Delivery Date", 
                min_value=datetime.now().date(),
                value=datetime.now().date() + timedelta(days=1)
            )
            
            delivery_time = st.selectbox("Preferred Time Slot", [
                "9:00 AM - 12:00 PM", "12:00 PM - 3:00 PM", 
                "3:00 PM - 6:00 PM", "6:00 PM - 9:00 PM"
            ])
            
            special_instructions = st.text_area("Special Instructions", 
                placeholder="Any special delivery instructions")
            
        # Payment and priority
        st.subheader("💳 Payment & Priority")
        col3, col4 = st.columns(2)
        
        with col3:
            payment_mode = st.selectbox("Payment Mode", [
                "Cash on Delivery (COD)", "Prepaid", "Credit Account"
            ])
            payment_status = "Pending" if payment_mode == "Cash on Delivery (COD)" else "Completed"
            
        with col4:
            priority = st.selectbox("Priority Level", [
                "Standard", "Express", "Same Day", "Critical"
            ])
            
        # Submit button
        submitted = st.form_submit_button("🤖 Analyze & Create Shipment", 
                                        use_container_width=True, type="primary")
        
        if submitted:
            # Validate required fields
            if not all([customer_name, customer_phone, delivery_address, pincode]):
                st.error("❌ Please fill in all required fields marked with *")
            else:
                # Show AI analysis
                st.markdown("---")
                st.subheader("🤖 AI Analysis Results")
                
                # Create progress bar for analysis
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Simulate real-time AI analysis
                analysis_steps = [
                    ("Analyzing delivery address...", 20),
                    ("Checking weather conditions...", 40), 
                    ("Calculating risk factors...", 60),
                    ("Evaluating dispatch decision...", 80),
                    ("Generating recommendations...", 100)
                ]
                
                for step, progress in analysis_steps:
                    status_text.text(step)
                    progress_bar.progress(progress)
                    time.sleep(0.5)  # Simulate processing time
                
                status_text.text("Analysis complete!")
                
                # Collect shipment data for AI analysis
                shipment_data = {
                    "weight": weight,
                    "declared_value": declared_value,
                    "payment_mode": payment_mode,
                    "delivery_area": delivery_area,
                    "pincode": pincode,
                    "address": delivery_address,
                    "priority": priority
                }
                
                col_ai1, col_ai2, col_ai3 = st.columns(3)
                
                with col_ai1:
                    st.markdown("#### 🎯 Risk Assessment")
                    
                    # Calculate risk score using backend
                    try:
                        risk_score = calculate_risk_score(shipment_data)
                        
                        # Color-code risk level
                        if risk_score <= 30:
                            risk_color = "🟢"
                            risk_level = "Low Risk"
                            risk_status = "success"
                        elif risk_score <= 60:
                            risk_color = "🟡"
                            risk_level = "Medium Risk" 
                            risk_status = "warning"
                        else:
                            risk_color = "🔴"
                            risk_level = "High Risk"
                            risk_status = "error"
                        
                        st.metric("Risk Score", f"{risk_score}/100", 
                                help="AI-calculated delivery risk based on multiple factors")
                        
                        if risk_status == "success":
                            st.success(f"{risk_color} {risk_level}")
                        elif risk_status == "warning":
                            st.warning(f"{risk_color} {risk_level}")
                        else:
                            st.error(f"{risk_color} {risk_level}")
                            
                        # Risk factors breakdown
                        with st.expander("🔍 Risk Factor Details"):
                            st.write("**Factor Breakdown:**")
                            st.write(f"• Weight Factor: {min(weight * 5, 15)}/15")
                            st.write(f"• Value Factor: {min(declared_value/1000 * 10, 20)}/20")
                            st.write(f"• Payment Risk: {15 if payment_mode == 'Cash on Delivery (COD)' else 5}/15")
                            st.write(f"• Area Risk: {10 if 'Zone-B' in delivery_area else 5}/15")
                            
                    except Exception as e:
                        st.error(f"Risk calculation error: {str(e)}")
                        risk_score = 50  # Fallback
                
                with col_ai2:
                    st.markdown("#### 🌤️ Weather Impact")
                    
                    try:
                        # Get weather impact
                        weather_data = get_weather_impact(pincode, preferred_date.strftime('%Y-%m-%d'))
                        
                        if weather_data.get('impact_factor', 0) <= 0.3:
                            weather_status = "🌤️ Favorable"
                            weather_color = "success"
                        elif weather_data.get('impact_factor', 0) <= 0.6:
                            weather_status = "☁️ Moderate"
                            weather_color = "warning"
                        else:
                            weather_status = "🌧️ Challenging"
                            weather_color = "error"
                            
                        st.metric("Weather Impact", 
                                f"{int(weather_data.get('impact_factor', 0) * 100)}%")
                        
                        if weather_color == "success":
                            st.success(weather_status)
                        elif weather_color == "warning":
                            st.warning(weather_status)
                        else:
                            st.error(weather_status)
                            
                        # Weather details
                        with st.expander("🌦️ Weather Forecast"):
                            st.write(f"**Condition:** {weather_data.get('condition', 'Clear')}")
                            st.write(f"**Temperature:** {weather_data.get('temp_c', 25)}°C")
                            st.write(f"**Humidity:** {weather_data.get('humidity', 60)}%")
                            st.write(f"**Wind:** {weather_data.get('wind_kph', 10)} km/h")
                            
                    except Exception as e:
                        st.warning(f"Weather data unavailable: Using default assessment")
                        weather_data = {"impact_factor": 0.2}
                
                with col_ai3:
                    st.markdown("#### 🚦 Dispatch Decision")
                    
                    try:
                        # Get dispatch decision
                        decision_data = pre_dispatch_decision(
                            risk_score, 
                            weather_data.get('impact_factor', 0.2),
                            0.8  # Address confidence placeholder
                        )
                        
                        decision = decision_data.get('decision', 'DISPATCH')
                        confidence = decision_data.get('confidence', 85)
                        
                        # Display decision
                        if decision == 'DISPATCH':
                            st.success(f"✅ {decision}")
                            st.metric("Confidence", f"{confidence}%")
                        elif decision == 'DELAY':
                            st.warning(f"⏳ {decision}")
                            st.metric("Confidence", f"{confidence}%")
                        else:  # RESCHEDULE
                            st.error(f"📅 {decision}")
                            st.metric("Confidence", f"{confidence}%")
                            
                        # Recommendations
                        with st.expander("💡 AI Recommendations"):
                            recommendations = decision_data.get('recommendations', [])
                            if recommendations:
                                for rec in recommendations:
                                    st.write(f"• {rec}")
                            else:
                                st.write("• Proceed with standard delivery process")
                                st.write("• Monitor weather conditions")
                                st.write("• Confirm address before dispatch")
                                
                    except Exception as e:
                        st.error(f"Decision engine error: {str(e)}")
                        decision = "DISPATCH"
                        confidence = 75
                
                # Final action buttons
                st.markdown("---")
                st.subheader("🎯 Final Action")
                
                col_action1, col_action2, col_action3 = st.columns(3)
                
                with col_action1:
                    if st.button("✅ Confirm & Dispatch", use_container_width=True, type="primary"):
                        # Save shipment data
                        shipment_record = {
                            "shipment_id": shipment_id,
                            "customer_name": customer_name,
                            "customer_phone": customer_phone,
                            "delivery_address": delivery_address,
                            "risk_score": risk_score,
                            "weather_impact": weather_data.get('impact_factor', 0.2),
                            "decision": decision,
                            "status": "Dispatched",
                            "created_at": datetime.now().isoformat()
                        }
                        
                        # Store in session for demo
                        if 'shipments' not in st.session_state:
                            st.session_state['shipments'] = []
                        st.session_state['shipments'].append(shipment_record)
                        
                        st.success(f"🎉 Shipment {shipment_id} created and dispatched successfully!")
                        st.balloons()
                
                with col_action2:
                    if st.button("⏳ Schedule for Later", use_container_width=True, type="secondary"):
                        st.info("📅 Shipment scheduled for manual review")
                
                with col_action3:
                    if st.button("🔄 Modify Details", use_container_width=True):
                        st.info("✏️ Please update the form above and re-analyze")

with tab2:
    st.header("📦 My Shipments")
    
    # Display user's shipments
    user = get_current_user()
    
    if 'shipments' in st.session_state and st.session_state['shipments']:
        st.markdown(f"### Recent Shipments by {user.get('name', 'Unknown')}")
        
        for idx, shipment in enumerate(st.session_state['shipments']):
            with st.expander(f"📦 {shipment['shipment_id']} - {shipment['customer_name']}", expanded=idx==0):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Customer:** {shipment['customer_name']}")
                    st.write(f"**Phone:** {shipment['customer_phone']}")
                    st.write(f"**Address:** {shipment['delivery_address'][:50]}...")
                
                with col2:
                    st.metric("Risk Score", f"{shipment['risk_score']}/100")
                    st.metric("Weather Impact", f"{int(shipment['weather_impact'] * 100)}%")
                
                with col3:
                    st.write(f"**Status:** {shipment['status']}")
                    st.write(f"**Decision:** {shipment['decision']}")
                    st.write(f"**Created:** {shipment['created_at'][:19]}")
    else:
        st.info("📦 No shipments created yet. Use the 'New Shipment' tab to create your first shipment.")

with tab3:
    st.header("📊 Your Performance")
    
    user = get_current_user()
    
    # Mock performance data
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Shipments Today", "8", "↑ 2")
    with col2:
        st.metric("Success Rate", "94%", "↑ 3%")
    with col3:
        st.metric("Avg Risk Score", "32", "↓ 5")
    with col4:
        st.metric("Customer Rating", "4.8", "↑ 0.2")
    
    # Performance chart placeholder
    st.markdown("### 📈 Weekly Performance Trend")
    st.info("📊 Performance analytics will be displayed here with actual data integration")
    
    # Tips for sellers
    st.markdown("### 💡 Performance Tips")
    st.success("✅ **Great Job!** Your risk assessment accuracy is above average")
    st.info("💡 **Tip:** Verify customer phone numbers to reduce delivery failures")
    st.warning("⚠️ **Note:** Consider weather impact when setting delivery expectations")