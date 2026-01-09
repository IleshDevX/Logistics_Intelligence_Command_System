"""
Seller Portal - Create and manage shipments
Allows sellers to create new shipments with AI-powered risk analysis
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
from models.risk_engine import calculate_risk_score, risk_bucket
from features.address_intelligence import process_address
from features.weather_impact import get_weather_impact
from rules.pre_dispatch_gate import pre_dispatch_decision
from rules.vehicle_selector import hyper_local_vehicle_check, get_vehicle_capacity
from features.carbon_tradeoff_engine import co2_speed_tradeoff

# Page configuration
st.set_page_config(
    page_title="Seller Portal - LICS",
    page_icon="📦",
    layout="wide"
)

# Initialize and apply
init_session_state()
apply_custom_css()
require_auth(allowed_roles=["Seller"])

# Page header
st.markdown("""
    <div class="page-header">
        <div class="page-title">📦 Seller Portal</div>
        <div class="page-subtitle">Create shipments with AI-powered risk analysis</div>
    </div>
""", unsafe_allow_html=True)

display_notifications()

# Tabs for different sections
tab1, tab2 = st.tabs(["📤 Create Shipment", "📋 My Shipments"])

with tab1:
    st.markdown("### ✏️ New Shipment Details")
    
    with st.form("shipment_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📍 Delivery Information")
            
            customer_name = st.text_input(
                "Customer Name *",
                placeholder="e.g., Rajesh Kumar"
            )
            
            customer_phone = st.text_input(
                "Customer Phone *",
                placeholder="e.g., +91 9876543210"
            )
            
            delivery_address = st.text_area(
                "Delivery Address *",
                placeholder="e.g., Plot 123, Near Metro Station, MG Road, Bangalore",
                height=100
            )
            
            destination_city = st.selectbox(
                "Destination City *",
                ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad", 
                 "Pune", "Ahmedabad", "Jaipur", "Lucknow"]
            )
            
            pincode = st.text_input(
                "Pincode *",
                placeholder="e.g., 560001"
            )
        
        with col2:
            st.markdown("#### 📦 Package Information")
            
            product_name = st.text_input(
                "Product Name *",
                placeholder="e.g., Electronic Gadget"
            )
            
            weight_kg = st.number_input(
                "Weight (kg) *",
                min_value=0.1,
                max_value=100.0,
                value=2.0,
                step=0.5
            )
            
            dimensions = st.text_input(
                "Dimensions (L x W x H cm)",
                placeholder="e.g., 30 x 20 x 10"
            )
            
            payment_type = st.selectbox(
                "Payment Type *",
                ["Prepaid", "COD"]
            )
            
            priority_flag = st.checkbox(
                "Priority Delivery",
                help="Check for faster delivery (additional charges may apply)"
            )
            
            special_instructions = st.text_area(
                "Special Instructions",
                placeholder="e.g., Fragile, Handle with care",
                height=60
            )
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            submit_button = st.form_submit_button(
                "🚀 Analyze & Create Shipment",
                use_container_width=True,
                type="primary"
            )
    
    # Process form submission
    if submit_button:
        # Validate required fields
        if not all([customer_name, customer_phone, delivery_address, destination_city, pincode, product_name]):
            st.error("❌ Please fill all required fields marked with *")
        else:
            with st.spinner("🧠 AI is analyzing your shipment..."):
                # Generate shipment ID
                shipment_id = f"SHP{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
                # Calculate volumetric weight (simple estimation)
                if dimensions:
                    try:
                        dims = [float(x.strip()) for x in dimensions.split('x')]
                        volumetric_weight = (dims[0] * dims[1] * dims[2]) / 5000
                    except:
                        volumetric_weight = weight_kg * 1.2
                else:
                    volumetric_weight = weight_kg * 1.2
                
                # Step 1: Address Intelligence Analysis
                st.markdown("### 🧠 AI Analysis Results")
                
                with st.expander("🗺️ Address Intelligence Analysis", expanded=True):
                    address_result = process_address(
                        raw_address=delivery_address,
                        road_accessibility="Wide"  # Default, can be enhanced
                    )
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(
                            "Address Confidence",
                            f"{address_result['address_confidence_score']:.0f}%",
                            delta="Good" if address_result['address_confidence_score'] > 70 else "Needs Review"
                        )
                    with col2:
                        st.metric("Area Type", address_result['area_type'])
                    with col3:
                        st.metric("Landmarks Found", len(address_result['landmarks']))
                    
                    if address_result['landmarks']:
                        st.info(f"🏛️ Landmarks: {', '.join(address_result['landmarks'])}")
                    
                    if address_result['needs_clarification']:
                        st.warning("⚠️ Address may need clarification before dispatch")
                
                # Step 2: Weather Impact Analysis
                with st.expander("🌦️ Weather Impact Analysis", expanded=True):
                    weather_result = get_weather_impact(destination_city, use_live_api=False)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Weather", weather_result['weather_condition'])
                    with col2:
                        st.metric("Severity", weather_result['weather_severity'])
                    with col3:
                        st.metric("Impact Factor", f"{weather_result['weather_impact_factor']:.0f}")
                    with col4:
                        st.metric("ETA Buffer", f"{weather_result['eta_buffer_multiplier']:.1f}x")
                    
                    if weather_result['weather_severity'] == "High":
                        st.error(f"🌧️ High weather impact: {weather_result['weather_description']}")
                    elif weather_result['weather_severity'] == "Medium":
                        st.warning(f"🌤️ Moderate weather: {weather_result['weather_description']}")
                    else:
                        st.success(f"☀️ Clear conditions: {weather_result['weather_description']}")
                
                # Step 3: Risk Calculation
                risk_score = calculate_risk_score(
                    weight_kg=weight_kg,
                    volumetric_weight=volumetric_weight,
                    payment_type=payment_type,
                    priority_flag=1 if priority_flag else 0,
                    area_type=address_result['area_type'],
                    road_accessibility="Wide",
                    address_confidence_score=address_result['address_confidence_score'],
                    weather_severity=weather_result['weather_severity'],
                    weather_impact_factor=weather_result['weather_impact_factor']
                )
                
                risk_category = risk_bucket(risk_score)
                
                st.markdown("---")
                st.markdown("### ⚠️ Risk Assessment")
                
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.markdown(
                        get_risk_badge_html(risk_score, risk_category),
                        unsafe_allow_html=True
                    )
                
                # Step 4: Pre-Dispatch Decision
                decision_result = pre_dispatch_decision(
                    risk_score=risk_score,
                    weather_impact_factor=weather_result['weather_impact_factor'],
                    address_confidence_score=address_result['address_confidence_score']
                )
                
                st.markdown("---")
                st.markdown("### 🚦 AI Decision")
                
                st.markdown(
                    get_decision_badge_html(decision_result['decision']),
                    unsafe_allow_html=True
                )
                
                if decision_result['reasons']:
                    st.markdown("**Reasons:**")
                    for reason in decision_result['reasons']:
                        st.markdown(f"- {reason}")
                
                # Step 5: Vehicle Recommendation
                with st.expander("🚚 Vehicle Feasibility", expanded=True):
                    default_vehicle = "Van" if weight_kg > 10 else "Bike"
                    vehicle_capacity = get_vehicle_capacity(default_vehicle)
                    
                    vehicle_result = hyper_local_vehicle_check(
                        area_type=address_result['area_type'],
                        road_accessibility="Wide",
                        assigned_vehicle=default_vehicle,
                        weight_kg=weight_kg,
                        volumetric_weight=volumetric_weight,
                        vehicle_capacity=vehicle_capacity
                    )
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Recommended Vehicle", vehicle_result['final_vehicle'])
                    with col2:
                        status_color = "green" if vehicle_result['vehicle_status'] == "APPROVED" else "orange"
                        st.metric("Status", vehicle_result['vehicle_status'])
                    
                    if vehicle_result.get('reason'):
                        st.info(f"ℹ️ {vehicle_result['reason']}")
                
                # Step 6: CO₂ Trade-off (for managers, just show info)
                with st.expander("🌱 Sustainability Impact"):
                    vehicle_emissions = {"Bike": 50, "Van": 120, "Truck": 180}
                    emission_factor = vehicle_emissions.get(vehicle_result['final_vehicle'], 100)
                    
                    co2_result = co2_speed_tradeoff(emission_factor_gkm=emission_factor)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Fast Route CO₂", f"{co2_result['fast_route']['co2_kg']:.2f} kg")
                    with col2:
                        st.metric("Green Route CO₂", f"{co2_result['green_route']['co2_kg']:.2f} kg")
                    
                    st.info(f"🌿 Potential CO₂ savings: {co2_result['co2_saved_kg']:.2f} kg (adds {co2_result['time_cost_hours']:.1f}h)")
                
                # Final Actions
                st.markdown("---")
                st.markdown("### ✅ Next Steps")
                
                if decision_result['decision'] == "DISPATCH":
                    st.success("✅ **Ready for Dispatch!** Your shipment is cleared for immediate processing.")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("✅ Accept & Create", use_container_width=True, type="primary"):
                            add_notification(f"Shipment {shipment_id} created successfully!", "success")
                            st.balloons()
                            st.rerun()
                    with col2:
                        if st.button("📝 Modify Details", use_container_width=True):
                            st.info("Please edit the form above and resubmit")
                
                elif decision_result['decision'] == "DELAY":
                    st.warning("⏸️ **Delay Recommended** - AI suggests waiting for better conditions")
                    st.info("A manager will review this shipment. Customer will be notified if delay is confirmed.")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✅ Submit for Review", use_container_width=True, type="primary"):
                            add_notification(f"Shipment {shipment_id} submitted for manager review", "info")
                            st.rerun()
                    with col2:
                        if st.button("📝 Modify Details", use_container_width=True):
                            st.info("Please edit the form above and resubmit")
                
                else:  # RESCHEDULE
                    st.error("🔄 **Reschedule Required** - Issues detected that need resolution")
                    st.warning("Please contact customer for address clarification or reschedule delivery")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📞 Contact Customer", use_container_width=True, type="primary"):
                            st.info(f"Customer contact: {customer_phone}")
                    with col2:
                        if st.button("📝 Update Address", use_container_width=True):
                            st.info("Please edit the address above and resubmit")

with tab2:
    st.markdown("### 📋 Your Shipment History")
    
    # Show message when no shipments
    st.info("📦 No shipments created yet. Create your first shipment in the 'Create Shipment' tab!")
    
    # Placeholder for future shipment list
    st.markdown("""
    **Your shipments will appear here with:**
    - Shipment ID and status
    - Customer details
    - AI decision and risk score
    - Real-time tracking
    - Delivery updates
    """)
