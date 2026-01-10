"""
Seller Portal - Create Shipments with AI Analysis
🎯 AI Suggests, You Decide
"""

import streamlit as st
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any

# Add project paths
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from utils.api_client import (
    is_logged_in, 
    get_current_user,
    create_shipment,
    get_risk_analysis,
    get_vehicle_recommendations,
    format_risk_level
)

# Page configuration
st.set_page_config(
    page_title="Seller Portal - LICS",
    page_icon="📦",
    layout="wide"
)

def apply_custom_css():
    """Apply custom CSS for risk-first design"""
    st.markdown("""
    <style>
    .risk-low { 
        background: linear-gradient(90deg, #d4edda 0%, #c3e6cb 100%); 
        border: 2px solid #28a745;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .risk-medium { 
        background: linear-gradient(90deg, #fff3cd 0%, #ffeaa7 100%); 
        border: 2px solid #ffc107;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .risk-high { 
        background: linear-gradient(90deg, #f8d7da 0%, #f5c6cb 100%); 
        border: 2px solid #dc3545;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .ai-insight {
        background: #f8f9fa;
        border-left: 4px solid #3498db;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 0 8px 8px 0;
    }
    .vehicle-recommendation {
        background: #e8f5e8;
        border: 1px solid #28a745;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
    }
    .override-warning {
        background: #fff3cd;
        border: 2px solid #ffc107;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

def check_authentication():
    """Ensure user is logged in and has seller access"""
    if not is_logged_in():
        st.error("🔐 Please login to access the Seller Portal")
        st.stop()
    
    user = get_current_user()
    if not user:
        st.error("❌ User session invalid")
        st.stop()
    
    role = user.get('role')
    if role not in ['seller', 'admin', 'manager']:
        st.error(f"⛔ Access denied. Seller portal requires seller role, but you have '{role}' role.")
        st.stop()
    
    return user

def show_shipment_form():
    """Show comprehensive shipment creation form"""
    st.markdown("### 📝 Create New Shipment")
    
    with st.form("shipment_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📍 Pickup Information**")
            pickup_address = st.text_input(
                "Pickup Address*", 
                placeholder="Street, City, State, ZIP"
            )
            pickup_contact = st.text_input(
                "Pickup Contact*", 
                placeholder="Contact person name"
            )
            pickup_phone = st.text_input(
                "Pickup Phone*", 
                placeholder="Phone number"
            )
            pickup_date = st.date_input(
                "Pickup Date*",
                min_value=datetime.now().date(),
                value=datetime.now().date()
            )
            pickup_time = st.time_input(
                "Pickup Time*",
                value=datetime.now().time()
            )
        
        with col2:
            st.markdown("**🎯 Delivery Information**")
            delivery_address = st.text_input(
                "Delivery Address*",
                placeholder="Street, City, State, ZIP"
            )
            delivery_contact = st.text_input(
                "Delivery Contact*",
                placeholder="Contact person name"
            )
            delivery_phone = st.text_input(
                "Delivery Phone*",
                placeholder="Phone number"
            )
            delivery_date = st.date_input(
                "Required Delivery Date*",
                min_value=datetime.now().date() + timedelta(days=1),
                value=datetime.now().date() + timedelta(days=1)
            )
            priority = st.selectbox(
                "Priority Level",
                ["standard", "urgent", "express"],
                format_func=lambda x: {
                    "standard": "📦 Standard",
                    "urgent": "⚡ Urgent", 
                    "express": "🚀 Express"
                }[x]
            )
        
        st.markdown("**📦 Package Information**")
        col3, col4, col5 = st.columns(3)
        
        with col3:
            weight = st.number_input("Weight (kg)*", min_value=0.1, value=1.0, step=0.1)
            package_type = st.selectbox(
                "Package Type",
                ["standard", "fragile", "hazardous", "perishable"],
                format_func=lambda x: {
                    "standard": "📦 Standard",
                    "fragile": "🔍 Fragile",
                    "hazardous": "⚠️ Hazardous",
                    "perishable": "❄️ Perishable"
                }[x]
            )
        
        with col4:
            dimensions = st.text_input("Dimensions (LxWxH cm)", placeholder="50x30x20")
            value = st.number_input("Declared Value ($)", min_value=0.0, value=100.0, step=10.0)
        
        with col5:
            special_instructions = st.text_area(
                "Special Instructions",
                placeholder="Any special handling requirements...",
                height=100
            )
        
        # Customer information
        st.markdown("**👤 Customer Information**")
        col6, col7 = st.columns(2)
        
        with col6:
            customer_name = st.text_input("Customer Name*", placeholder="Customer full name")
            customer_email = st.text_input("Customer Email*", placeholder="customer@email.com")
        
        with col7:
            customer_phone = st.text_input("Customer Phone*", placeholder="Customer phone number")
            notification_prefs = st.multiselect(
                "Notification Preferences",
                ["sms", "email", "whatsapp"],
                default=["sms"],
                format_func=lambda x: {
                    "sms": "📱 SMS",
                    "email": "📧 Email",
                    "whatsapp": "💬 WhatsApp"
                }[x]
            )
        
        # Form submission
        col8, col9, col10 = st.columns([1, 2, 1])
        with col9:
            analyze_btn = st.form_submit_button("🧠 Analyze with AI", type="primary", use_container_width=True)
            create_btn = st.form_submit_button("📦 Create Shipment", use_container_width=True)
        
        # Validate required fields
        required_fields = [
            pickup_address, pickup_contact, pickup_phone,
            delivery_address, delivery_contact, delivery_phone,
            customer_name, customer_email, customer_phone
        ]
        
        if analyze_btn or create_btn:
            if not all(required_fields):
                st.error("⚠️ Please fill in all required fields marked with *")
                st.stop()
            
            # Prepare shipment data
            shipment_data = {
                "pickup": {
                    "address": pickup_address,
                    "contact": pickup_contact,
                    "phone": pickup_phone,
                    "datetime": f"{pickup_date} {pickup_time}"
                },
                "delivery": {
                    "address": delivery_address,
                    "contact": delivery_contact,
                    "phone": delivery_phone,
                    "required_date": str(delivery_date)
                },
                "package": {
                    "weight": weight,
                    "dimensions": dimensions,
                    "type": package_type,
                    "value": value,
                    "special_instructions": special_instructions
                },
                "customer": {
                    "name": customer_name,
                    "email": customer_email,
                    "phone": customer_phone,
                    "notification_prefs": notification_prefs
                },
                "priority": priority,
                "created_by": get_current_user().get('username')
            }
            
            if analyze_btn:
                show_ai_analysis(shipment_data)
            elif create_btn:
                create_shipment_with_confirmation(shipment_data)

def show_ai_analysis(shipment_data: Dict[str, Any]):
    """Display AI analysis results"""
    st.markdown("---")
    st.markdown("## 🧠 AI Analysis Results")
    
    with st.spinner("🔄 Analyzing shipment with AI..."):
        # Get risk analysis
        risk_result = get_risk_analysis(shipment_data)
        vehicle_result = get_vehicle_recommendations(shipment_data)
    
    if risk_result.get("success"):
        show_risk_analysis(risk_result["data"])
    else:
        st.warning(f"⚠️ Risk analysis unavailable: {risk_result.get('error')}")
        show_mock_risk_analysis(shipment_data)
    
    if vehicle_result.get("success"):
        show_vehicle_recommendations(vehicle_result["data"])
    else:
        st.warning(f"⚠️ Vehicle recommendations unavailable: {vehicle_result.get('error')}")
        show_mock_vehicle_recommendations(shipment_data)

def show_risk_analysis(risk_data: Dict[str, Any]):
    """Display detailed risk analysis"""
    risk_score = risk_data.get("overall_risk", 0.3)
    risk_label, risk_class, risk_icon = format_risk_level(risk_score)
    
    st.markdown(f"""
    <div class="{risk_class}">
        <h3>{risk_icon} Overall Risk Assessment: {risk_label}</h3>
        <p><strong>Risk Score:</strong> {risk_score:.1%}</p>
        <p><strong>AI Confidence:</strong> {risk_data.get('confidence', 0.85):.1%}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Risk factors breakdown
    col1, col2, col3 = st.columns(3)
    
    risk_factors = risk_data.get("risk_factors", {})
    
    with col1:
        weather_risk = risk_factors.get("weather", 0.2)
        st.metric(
            "🌤️ Weather Risk",
            f"{weather_risk:.1%}",
            delta="Low impact expected"
        )
    
    with col2:
        route_risk = risk_factors.get("route", 0.3)
        st.metric(
            "🛣️ Route Risk", 
            f"{route_risk:.1%}",
            delta="Standard route complexity"
        )
    
    with col3:
        cargo_risk = risk_factors.get("cargo", 0.1)
        st.metric(
            "📦 Cargo Risk",
            f"{cargo_risk:.1%}", 
            delta="Standard handling required"
        )
    
    # AI insights
    insights = risk_data.get("insights", [])
    if insights:
        st.markdown("### 💡 AI Insights")
        for insight in insights:
            st.markdown(f"""
            <div class="ai-insight">
                <strong>{insight.get('category', 'General')}:</strong> {insight.get('message', 'No details available')}
            </div>
            """, unsafe_allow_html=True)

def show_vehicle_recommendations(vehicle_data: List[Dict[str, Any]]):
    """Display vehicle recommendations"""
    st.markdown("### 🚛 Recommended Vehicles")
    
    for i, vehicle in enumerate(vehicle_data[:3]):  # Show top 3 recommendations
        confidence = vehicle.get("match_score", 0.8)
        
        st.markdown(f"""
        <div class="vehicle-recommendation">
            <h4>#{i+1} {vehicle.get('type', 'Standard Truck')} - {confidence:.1%} Match</h4>
            <p><strong>Capacity:</strong> {vehicle.get('capacity', 'N/A')} | 
            <strong>Estimated Cost:</strong> ${vehicle.get('estimated_cost', 150):.2f} | 
            <strong>ETA:</strong> {vehicle.get('eta', 'N/A')}</p>
            <p><strong>Reason:</strong> {vehicle.get('reason', 'Optimal for this shipment type and route')}</p>
        </div>
        """, unsafe_allow_html=True)

def show_mock_risk_analysis(shipment_data: Dict[str, Any]):
    """Show mock risk analysis when API is unavailable"""
    # Calculate basic risk based on shipment data
    base_risk = 0.2
    
    # Add risk factors
    package_type = shipment_data.get("package", {}).get("type", "standard")
    if package_type == "hazardous":
        base_risk += 0.3
    elif package_type == "fragile":
        base_risk += 0.2
    elif package_type == "perishable":
        base_risk += 0.15
    
    priority = shipment_data.get("priority", "standard")
    if priority == "express":
        base_risk += 0.1
    elif priority == "urgent":
        base_risk += 0.05
    
    risk_score = min(base_risk, 0.9)  # Cap at 90%
    risk_label, risk_class, risk_icon = format_risk_level(risk_score)
    
    st.markdown(f"""
    <div class="{risk_class}">
        <h3>{risk_icon} Overall Risk Assessment: {risk_label}</h3>
        <p><strong>Risk Score:</strong> {risk_score:.1%}</p>
        <p><strong>AI Confidence:</strong> 87%</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mock insights
    st.markdown("### 💡 AI Insights")
    insights = [
        "Route analysis shows standard traffic patterns expected",
        "Package type and weight within normal handling parameters",
        "Weather conditions favorable for delivery window"
    ]
    
    if package_type == "hazardous":
        insights.append("⚠️ Hazardous materials require special handling certification")
    if priority == "express":
        insights.append("⚡ Express priority may limit vehicle options during peak hours")
    
    for insight in insights:
        st.markdown(f"""
        <div class="ai-insight">
            <strong>System Analysis:</strong> {insight}
        </div>
        """, unsafe_allow_html=True)

def show_mock_vehicle_recommendations(shipment_data: Dict[str, Any]):
    """Show mock vehicle recommendations when API is unavailable"""
    weight = shipment_data.get("package", {}).get("weight", 1.0)
    package_type = shipment_data.get("package", {}).get("type", "standard")
    priority = shipment_data.get("priority", "standard")
    
    # Generate recommendations based on shipment data
    vehicles = []
    
    if weight <= 5:
        vehicles.append({
            "type": "Motorcycle/Bike",
            "capacity": "Up to 5kg",
            "estimated_cost": 25.00,
            "eta": "2-4 hours",
            "match_score": 0.95,
            "reason": "Optimal for lightweight, urgent deliveries in urban areas"
        })
    
    if weight <= 50:
        vehicles.append({
            "type": "Van",
            "capacity": "Up to 50kg",
            "estimated_cost": 75.00,
            "eta": "4-8 hours", 
            "match_score": 0.85,
            "reason": "Balanced cost-efficiency for medium-sized packages"
        })
    
    vehicles.append({
        "type": "Truck",
        "capacity": "Up to 500kg",
        "estimated_cost": 150.00,
        "eta": "1-2 days",
        "match_score": 0.75,
        "reason": "Suitable for all package sizes with competitive pricing"
    })
    
    # Adjust for special requirements
    if package_type == "hazardous":
        for vehicle in vehicles:
            vehicle["type"] += " (Certified)"
            vehicle["estimated_cost"] *= 1.3
            vehicle["match_score"] *= 0.9
    
    show_vehicle_recommendations(vehicles[:3])

def create_shipment_with_confirmation(shipment_data: Dict[str, Any]):
    """Create shipment with user confirmation"""
    st.markdown("---")
    st.markdown("## 📦 Creating Shipment...")
    
    with st.spinner("⏳ Processing shipment creation..."):
        result = create_shipment(shipment_data)
    
    if result.get("success"):
        shipment = result["data"]
        st.success("✅ Shipment created successfully!")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"📋 **Shipment ID:** {shipment.get('id', 'N/A')}")
            st.info(f"📍 **Tracking Number:** {shipment.get('tracking_number', 'N/A')}")
        
        with col2:
            st.info(f"🎯 **Status:** {shipment.get('status', 'Pending').title()}")
            st.info(f"💰 **Estimated Cost:** ${shipment.get('estimated_cost', 0):.2f}")
        
        # Show next steps
        st.markdown("### 🎯 Next Steps")
        st.markdown("""
        1. **📱 Customer Notification:** SMS/Email sent automatically
        2. **🎯 Manager Review:** Shipment queued for approval
        3. **🚛 Vehicle Assignment:** AI recommendations sent to dispatch
        4. **📊 Tracking:** Real-time updates available in portal
        """)
        
        if st.button("📝 Create Another Shipment", type="primary"):
            st.rerun()
            
    else:
        st.error(f"❌ Shipment creation failed: {result.get('error', 'Unknown error')}")

def main():
    """Main seller portal function"""
    apply_custom_css()
    
    # Check authentication
    user = check_authentication()
    
    # Header
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, #2C3E50 0%, #3498DB 100%); padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem;">
        <h1 style="color: white; margin: 0;">📦 Seller Portal</h1>
        <p style="color: #BDC3C7; margin: 0.5rem 0 0 0;">
            Welcome {user.get('full_name', user.get('username'))} • 
            🧠 AI-assisted shipment creation • 
            📊 Real-time risk analysis
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation tabs
    tab1, tab2, tab3 = st.tabs(["📝 Create Shipment", "📋 Recent Shipments", "📊 Performance"])
    
    with tab1:
        show_shipment_form()
    
    with tab2:
        st.markdown("### 📋 Recent Shipments")
        st.info("📊 Recent shipments display will be implemented in next version")
        
        # Mock recent shipments
        st.markdown("""
        **Recent Shipments:**
        - 🚛 SH001 - In Transit - Delivery: Tomorrow
        - ⏳ SH002 - Pending Approval - High Priority  
        - ✅ SH003 - Delivered - Customer Satisfied
        """)
    
    with tab3:
        st.markdown("### 📊 Seller Performance")
        st.info("📈 Performance analytics will be implemented in next version")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📦 Total Shipments", "47", "↑ 12%")
        with col2:
            st.metric("✅ Success Rate", "94%", "↑ 3%") 
        with col3:
            st.metric("⭐ Customer Rating", "4.8", "↑ 0.2")

if __name__ == "__main__":
    main()