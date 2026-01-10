"""
Shipment Creation Form Component
Integrates with backend AI modules for real-time risk assessment
"""

import streamlit as st
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import time

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from utils.styling import show_risk_indicator, show_loading_spinner
from utils.session_manager import save_form_data, get_form_data, add_notification

# Mock backend functions (replace with actual imports when backend is available)
def mock_calculate_risk_score(product_data: Dict[str, Any]) -> int:
    """Mock risk calculation - replace with actual backend function"""
    # Simple mock logic
    base_risk = 30
    
    # Add risk based on weight
    if product_data.get('weight', 0) > 10:
        base_risk += 15
    
    # Add risk for high value items
    if product_data.get('value', 0) > 50000:
        base_risk += 20
    
    # Add risk for COD
    if product_data.get('payment', '') == 'COD':
        base_risk += 10
    
    # Add risk for fragile items
    if product_data.get('fragile', False):
        base_risk += 5
    
    # Random variation for demo
    import random
    base_risk += random.randint(-10, 15)
    
    return max(0, min(100, base_risk))

def mock_calculate_address_confidence(address: str) -> int:
    """Mock address confidence calculation"""
    confidence = 50
    
    # Check for landmarks
    landmarks = ['hospital', 'school', 'metro', 'mall', 'temple', 'mosque', 'church', 'park']
    for landmark in landmarks:
        if landmark.lower() in address.lower():
            confidence += 15
            break
    
    # Check for pincode
    if any(char.isdigit() for char in address) and len([c for c in address if c.isdigit()]) >= 6:
        confidence += 20
    
    # Check for specific address details
    if 'house' in address.lower() or 'flat' in address.lower() or 'apartment' in address.lower():
        confidence += 10
    
    return min(100, confidence)

def mock_get_weather_impact(city: str) -> Dict[str, Any]:
    """Mock weather impact calculation"""
    import random
    
    weather_conditions = ['Clear', 'Light Rain', 'Heavy Rain', 'Fog', 'Storm']
    condition = random.choice(weather_conditions)
    
    impact_map = {
        'Clear': {'severity': 'Low', 'delay_factor': 1.0},
        'Light Rain': {'severity': 'Low', 'delay_factor': 1.1},
        'Heavy Rain': {'severity': 'High', 'delay_factor': 1.4},
        'Fog': {'severity': 'Medium', 'delay_factor': 1.2},
        'Storm': {'severity': 'High', 'delay_factor': 1.6}
    }
    
    return {
        'condition': condition,
        'severity': impact_map[condition]['severity'],
        'delay_factor': impact_map[condition]['delay_factor']
    }

def mock_select_vehicle(weight: float, dimensions: str, city: str, address: str) -> Dict[str, Any]:
    """Mock vehicle selection"""
    if weight < 5:
        return {
            'type': 'Bike',
            'eco_friendly': True,
            'co2_emission': 0.5,
            'suitable': True
        }
    elif weight < 20:
        return {
            'type': 'EV Truck',
            'eco_friendly': True,
            'co2_emission': 6,
            'suitable': True
        }
    else:
        return {
            'type': 'Diesel Truck',
            'eco_friendly': False,
            'co2_emission': 16,
            'suitable': True
        }

def mock_make_dispatch_decision(risk_score: int, weather_impact: Dict, address_confidence: int) -> Dict[str, Any]:
    """Mock dispatch decision logic"""
    reasons = []
    
    if risk_score >= 70:
        decision = "RESCHEDULE"
        reasons.append("High risk score detected")
    elif risk_score >= 50:
        decision = "DELAY"
        reasons.append("Medium risk - buffer time recommended")
    elif weather_impact['severity'] == 'High':
        decision = "DELAY"
        reasons.append("Severe weather conditions")
    elif address_confidence < 60:
        decision = "RESCHEDULE"
        reasons.append("Address needs clarification")
    else:
        decision = "DISPATCH"
        reasons.append("All conditions favorable")
    
    return {
        'decision': decision,
        'reasons': reasons,
        'confidence': 85
    }

def show_shipment_form():
    """Display comprehensive shipment creation form"""
    
    st.subheader("📝 New Shipment Details")
    
    # Load saved form data if exists
    saved_data = get_form_data('new_shipment')
    
    # Create form
    with st.form("new_shipment_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📦 Product Information**")
            
            product_name = st.text_input(
                "Product Name*",
                value=saved_data.get('product_name', ''),
                placeholder="e.g., Samsung Galaxy S24"
            )
            
            product_category = st.selectbox(
                "Category*",
                ["Electronics", "Clothing", "Food & Beverages", "Furniture", "Documents", "Jewelry", "Books", "Other"],
                index=0 if not saved_data.get('product_category') else ["Electronics", "Clothing", "Food & Beverages", "Furniture", "Documents", "Jewelry", "Books", "Other"].index(saved_data.get('product_category', 'Electronics'))
            )
            
            weight = st.number_input(
                "Weight (kg)*",
                min_value=0.1,
                max_value=500.0,
                value=saved_data.get('weight', 2.0),
                step=0.1,
                help="Accurate weight helps in vehicle selection"
            )
            
            col1a, col1b, col1c = st.columns(3)
            with col1a:
                length = st.number_input("Length (cm)", min_value=1, max_value=500, value=saved_data.get('length', 30), step=1)
            with col1b:
                width = st.number_input("Width (cm)", min_value=1, max_value=500, value=saved_data.get('width', 20), step=1)
            with col1c:
                height = st.number_input("Height (cm)", min_value=1, max_value=500, value=saved_data.get('height', 10), step=1)
            
            dimensions = f"{length}x{width}x{height}"
            
            value = st.number_input(
                "Declared Value (₹)*",
                min_value=100,
                max_value=10000000,
                value=saved_data.get('value', 5000),
                step=100,
                help="Affects insurance and risk calculation"
            )
            
            # Additional options
            st.markdown("**⚙️ Additional Options**")
            
            col1_opt1, col1_opt2 = st.columns(2)
            with col1_opt1:
                fragile = st.checkbox("Fragile Item", value=saved_data.get('fragile', False))
                liquid = st.checkbox("Contains Liquid", value=saved_data.get('liquid', False))
            
            with col1_opt2:
                perishable = st.checkbox("Perishable", value=saved_data.get('perishable', False))
                valuable = st.checkbox("High Value (>₹50k)", value=value > 50000)
            
            payment = st.selectbox(
                "Payment Type*",
                ["Prepaid", "COD"],
                index=0 if saved_data.get('payment', 'Prepaid') == 'Prepaid' else 1
            )
            
            if payment == "COD":
                cod_amount = st.number_input(
                    "COD Amount (₹)",
                    min_value=0,
                    max_value=value,
                    value=saved_data.get('cod_amount', value),
                    step=100
                )
            else:
                cod_amount = 0
        
        with col2:
            st.markdown("**📍 Delivery Information**")
            
            delivery_address = st.text_area(
                "Delivery Address*",
                value=saved_data.get('delivery_address', ''),
                placeholder="Full address with landmarks\ne.g., House No. 123, Near AIIMS Hospital, Ansari Nagar, New Delhi - 110029",
                height=120,
                help="Include landmarks for better delivery accuracy"
            )
            
            city = st.selectbox(
                "City*",
                ["Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune", "Ahmedabad", "Jaipur", "Lucknow"],
                index=0 if not saved_data.get('city') else ["Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune", "Ahmedabad", "Jaipur", "Lucknow"].index(saved_data.get('city', 'Delhi'))
            )
            
            priority = st.select_slider(
                "Priority Level",
                options=["Standard", "Express", "Urgent"],
                value=saved_data.get('priority', 'Standard'),
                help="Higher priority may affect delivery time and cost"
            )
            
            delivery_date = st.date_input(
                "Preferred Delivery Date",
                value=datetime.now() + timedelta(days=1),
                min_value=datetime.now().date(),
                max_value=datetime.now().date() + timedelta(days=30)
            )
            
            # Time slot selection
            time_slot = st.selectbox(
                "Preferred Time Slot",
                ["Any Time", "Morning (9 AM - 12 PM)", "Afternoon (12 PM - 4 PM)", "Evening (4 PM - 8 PM)"],
                index=0
            )
            
            # Contact information
            st.markdown("**📞 Contact Information**")
            
            recipient_name = st.text_input(
                "Recipient Name*",
                value=saved_data.get('recipient_name', ''),
                placeholder="Full name of the person receiving"
            )
            
            recipient_phone = st.text_input(
                "Recipient Phone*",
                value=saved_data.get('recipient_phone', ''),
                placeholder="+91 XXXXX XXXXX",
                help="WhatsApp number preferred for delivery updates"
            )
            
            # Special instructions
            special_instructions = st.text_area(
                "Special Instructions (Optional)",
                value=saved_data.get('special_instructions', ''),
                placeholder="Any specific delivery instructions...",
                height=60
            )
        
        st.markdown("---")
        
        # Submit button
        submitted = st.form_submit_button(
            "🔍 Analyze & Create Shipment",
            use_container_width=True,
            type="primary"
        )
        
        if submitted:
            # Validate required fields
            required_fields = {
                'Product Name': product_name,
                'Weight': weight,
                'Value': value,
                'Delivery Address': delivery_address,
                'City': city,
                'Recipient Name': recipient_name,
                'Recipient Phone': recipient_phone
            }
            
            missing_fields = [field for field, value in required_fields.items() if not value]
            
            if missing_fields:
                st.error(f"❌ Please fill the following required fields: {', '.join(missing_fields)}")
            else:
                # Save form data
                form_data = {
                    'product_name': product_name,
                    'product_category': product_category,
                    'weight': weight,
                    'dimensions': dimensions,
                    'value': value,
                    'fragile': fragile,
                    'liquid': liquid,
                    'perishable': perishable,
                    'payment': payment,
                    'cod_amount': cod_amount,
                    'delivery_address': delivery_address,
                    'city': city,
                    'priority': priority,
                    'delivery_date': delivery_date.isoformat(),
                    'time_slot': time_slot,
                    'recipient_name': recipient_name,
                    'recipient_phone': recipient_phone,
                    'special_instructions': special_instructions
                }
                
                save_form_data('new_shipment', form_data)
                
                # Show processing spinner
                with st.spinner("🤖 AI analyzing shipment risk..."):
                    time.sleep(2)  # Simulate AI processing
                    
                    analyze_and_create_shipment(form_data)

def analyze_and_create_shipment(form_data: Dict[str, Any]):
    """Analyze shipment using AI and show results"""
    
    st.markdown("---")
    st.success("✅ **Shipment Analysis Complete!**")
    
    # Calculate various risk factors
    risk_score = mock_calculate_risk_score(form_data)
    address_confidence = mock_calculate_address_confidence(form_data['delivery_address'])
    weather_impact = mock_get_weather_impact(form_data['city'])
    vehicle_recommendation = mock_select_vehicle(
        form_data['weight'],
        form_data['dimensions'],
        form_data['city'],
        form_data['delivery_address']
    )
    dispatch_decision = mock_make_dispatch_decision(risk_score, weather_impact, address_confidence)
    
    # Display risk analysis
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Risk Score", f"{risk_score}/100")
        st.markdown(show_risk_indicator(risk_score), unsafe_allow_html=True)
    
    with col2:
        st.metric("Address Confidence", f"{address_confidence}%")
        conf_color = "🟢" if address_confidence > 75 else "🟡" if address_confidence > 50 else "🔴"
        st.markdown(f"{conf_color} {address_confidence}% confidence")
    
    with col3:
        st.metric("Weather Impact", weather_impact['severity'])
        weather_color = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}[weather_impact['severity']]
        st.markdown(f"{weather_color} {weather_impact['condition']} in {form_data['city']}")
    
    # Detailed breakdown
    with st.expander("📊 **Detailed Risk Analysis**", expanded=True):
        st.write("**Risk Factors Analyzed:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"• **Weight:** {form_data['weight']} kg - {'✅ Standard' if form_data['weight'] < 10 else '⚠️ Heavy'}")
            st.write(f"• **Value:** ₹{form_data['value']:,} - {'✅ Standard' if form_data['value'] < 50000 else '⚠️ High Value'}")
            st.write(f"• **Payment:** {form_data['payment']} - {'✅ Prepaid' if form_data['payment'] == 'Prepaid' else '⚠️ COD Risk'}")
            st.write(f"• **Fragile:** {'⚠️ Yes' if form_data['fragile'] else '✅ No'}")
        
        with col2:
            st.write(f"• **Address:** {address_confidence}% confidence - {'✅ Clear' if address_confidence > 75 else '⚠️ Needs clarification'}")
            st.write(f"• **Weather:** {weather_impact['severity']} impact - {weather_impact['condition']}")
            st.write(f"• **City:** {form_data['city']} - {'✅ Serviceable' if form_data['city'] in ['Delhi', 'Mumbai', 'Bangalore'] else '⚠️ Extended area'}")
            st.write(f"• **Priority:** {form_data['priority']} - {'✅ Standard' if form_data['priority'] == 'Standard' else '⚠️ Rush delivery'}")
    
    # Vehicle and delivery recommendation
    st.subheader("🚛 **Recommended Delivery Plan**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Vehicle Selection:**")
        eco_badge = "🌱" if vehicle_recommendation['eco_friendly'] else "⛽"
        st.write(f"{eco_badge} **{vehicle_recommendation['type']}**")
        st.write(f"CO₂ Emission: **{vehicle_recommendation['co2_emission']} kg**")
        
        if vehicle_recommendation['eco_friendly']:
            st.success("✅ Eco-friendly option selected")
        
        # CO2 comparison
        if vehicle_recommendation['eco_friendly']:
            diesel_emission = vehicle_recommendation['co2_emission'] * 2.5
            savings = diesel_emission - vehicle_recommendation['co2_emission']
            st.info(f"🌱 **{savings:.1f} kg CO₂ saved** vs diesel vehicle")
    
    with col2:
        st.write("**Delivery Timeline:**")
        base_eta = "Tomorrow, 2-5 PM"
        
        if weather_impact['delay_factor'] > 1.2:
            adjusted_eta = "Tomorrow, 3-6 PM (+1 hour buffer)"
            st.warning(f"⏰ **Adjusted ETA:** {adjusted_eta}")
            st.write(f"Reason: {weather_impact['condition']} expected")
        else:
            st.success(f"⏰ **Expected:** {base_eta}")
        
        st.write(f"**Time Slot:** {form_data['time_slot']}")
        st.write(f"**Priority:** {form_data['priority']}")
    
    # AI Decision and Actions
    st.subheader("🤖 **AI Recommendation**")
    
    decision_colors = {
        "DISPATCH": "success",
        "DELAY": "warning", 
        "RESCHEDULE": "error"
    }
    
    decision_emojis = {
        "DISPATCH": "✅",
        "DELAY": "⏸️",
        "RESCHEDULE": "🔄"
    }
    
    decision_color = decision_colors[dispatch_decision['decision']]
    decision_emoji = decision_emojis[dispatch_decision['decision']]
    
    if decision_color == "success":
        st.success(f"{decision_emoji} **{dispatch_decision['decision']}** - Ready to proceed!")
    elif decision_color == "warning":
        st.warning(f"{decision_emoji} **{dispatch_decision['decision']}** - Minor adjustments recommended")
    else:
        st.error(f"{decision_emoji} **{dispatch_decision['decision']}** - Action required before dispatch")
    
    # Show reasons
    st.write("**Reasoning:**")
    for reason in dispatch_decision['reasons']:
        st.write(f"• {reason}")
    
    # Action buttons based on decision
    st.markdown("---")
    
    if dispatch_decision['decision'] == "DISPATCH":
        st.subheader("✅ **Ready for Dispatch**")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.info("""
            **What happens next:**
            1. Shipment will be picked up within 2 hours
            2. Customer will receive WhatsApp notification
            3. Real-time tracking will be activated
            4. Delivery scheduled for tomorrow
            """)
        
        with col2:
            if st.button("✅ **Confirm & Create Shipment**", type="primary", use_container_width=True):
                # Generate shipment ID
                shipment_id = f"SHP{int(time.time() * 1000) % 100000:05d}"
                
                # Add success notification
                add_notification(
                    f"✅ Shipment {shipment_id} created successfully!",
                    "success"
                )
                
                # Show success
                st.balloons()
                st.success(f"""
                🎉 **Shipment Created Successfully!**
                
                **Tracking ID:** {shipment_id}
                **Customer Notification:** Sent via WhatsApp
                **Pickup:** Within 2 hours
                **Delivery:** Tomorrow, 2-5 PM
                """)
                
                # Clear form data
                save_form_data('new_shipment', {})
                
                time.sleep(2)
                st.rerun()
    
    elif dispatch_decision['decision'] == "DELAY":
        st.subheader("⏸️ **Delay Recommended**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.warning(f"""
            **Recommended Actions:**
            • Buffer delivery window by 1-2 hours
            • Notify customer about potential delay
            • Monitor weather conditions
            
            **Adjusted Timeline:**
            • Pickup: Within 3 hours  
            • Delivery: Tomorrow, 3-6 PM
            """)
            
            if st.button("✅ **Accept Recommendation**", type="primary"):
                st.success("Shipment created with adjusted timeline")
                add_notification("Shipment created with delay buffer", "info")
        
        with col2:
            st.info("**Override Options:**")
            
            if st.button("⚡ **Force Dispatch (Override)**", type="secondary"):
                st.warning("⚠️ Override logged. Higher risk of delivery issues.")
                add_notification("AI recommendation overridden", "warning")
                
                if st.button("Confirm Override", type="primary"):
                    st.success("Shipment created with original timeline")
    
    else:  # RESCHEDULE
        st.subheader("🔄 **Clarification Needed**")
        
        st.error(f"""
        **Issues Detected:**
        {chr(10).join('• ' + reason for reason in dispatch_decision['reasons'])}
        
        **Required Actions:**
        1. Clarify delivery address with customer
        2. Choose alternative delivery date  
        3. Wait for better weather conditions
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📞 **Send Address Clarification Request**", use_container_width=True):
                st.success("📱 WhatsApp message sent to customer requesting detailed address")
                add_notification("Address clarification request sent", "info")
        
        with col2:
            if st.button("📅 **Reschedule Delivery**", use_container_width=True):
                st.info("Redirecting to reschedule options...")
    
    # Save shipment data for analytics
    st.session_state['last_analysis'] = {
        'risk_score': risk_score,
        'decision': dispatch_decision['decision'],
        'timestamp': datetime.now().isoformat(),
        'form_data': form_data
    }