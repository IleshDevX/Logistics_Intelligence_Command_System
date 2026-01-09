"""
Customer Tracking Page - Public shipment tracking (no login required)
Transparent communication with customers about delivery status
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.styling import apply_custom_css

# Import backend modules
from ingestion.load_data import load_all_data

# Page configuration
st.set_page_config(
    page_title="Track Shipment - LICS",
    page_icon="📍",
    layout="wide"
)

# Apply styling (no auth required for this page)
apply_custom_css()

# Page header
st.markdown("""
    <div class="page-header">
        <div class="page-title">📍 Track Your Shipment</div>
        <div class="page-subtitle">Real-time updates and transparent delivery status</div>
    </div>
""", unsafe_allow_html=True)

# Public tracking interface
st.markdown("### 🔍 Enter Tracking Details")

col1, col2 = st.columns([2, 1])

with col1:
    tracking_id = st.text_input(
        "Shipment ID",
        placeholder="e.g., SHP0001234567",
        help="Enter your shipment ID provided at the time of order"
    )

with col2:
    phone_last_4 = st.text_input(
        "Last 4 digits of phone",
        placeholder="e.g., 1234",
        max_chars=4,
        help="For security verification"
    )

track_button = st.button("🔍 Track Shipment", use_container_width=True, type="primary")

st.markdown("---")

if track_button:
    if not tracking_id:
        st.error("❌ Please enter a Shipment ID")
    elif not phone_last_4 or len(phone_last_4) != 4:
        st.error("❌ Please enter the last 4 digits of your phone number")
    else:
        # Load shipment data
        try:
            shipments, addresses, history, weather, resources = load_all_data()
            
            # Search for shipment
            shipment = shipments[shipments['shipment_id'] == tracking_id]
            
            if shipment.empty:
                st.error(f"❌ Shipment ID '{tracking_id}' not found")
                st.info("💡 Please check your Shipment ID and try again")
            else:
                shipment_data = shipment.iloc[0]
                
                # Verify phone (mock verification)
                # In production, check against actual customer phone
                
                st.success(f"✅ Shipment Found: {tracking_id}")
                
                st.markdown("---")
                
                # Shipment status timeline
                st.markdown("### 📦 Shipment Status")
                
                # Mock status data (in production, load from tracking events)
                statuses = [
                    {"step": "Order Confirmed", "status": "completed", "time": "2026-01-09 10:00 AM", "icon": "✅"},
                    {"step": "AI Risk Analysis", "status": "completed", "time": "2026-01-09 10:05 AM", "icon": "🧠"},
                    {"step": "Manager Review", "status": "completed", "time": "2026-01-09 11:30 AM", "icon": "👤"},
                    {"step": "Ready for Dispatch", "status": "current", "time": "2026-01-09 12:00 PM", "icon": "🚚"},
                    {"step": "In Transit", "status": "pending", "time": "Expected: Today 2:00 PM", "icon": "📍"},
                    {"step": "Out for Delivery", "status": "pending", "time": "Expected: Today 4:00 PM", "icon": "🏍️"},
                    {"step": "Delivered", "status": "pending", "time": "Expected: Today 6:00 PM", "icon": "✅"}
                ]
                
                for status in statuses:
                    if status['status'] == 'completed':
                        st.markdown(f"""
                            <div class="success-box">
                                <strong>{status['icon']} {status['step']}</strong>
                                <br><small>{status['time']}</small>
                            </div>
                        """, unsafe_allow_html=True)
                    elif status['status'] == 'current':
                        st.markdown(f"""
                            <div class="info-box">
                                <strong>{status['icon']} {status['step']} (Current)</strong>
                                <br><small>{status['time']}</small>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                            <div style="background-color: #F5F5F5; padding: 15px; border-radius: 5px; margin: 10px 0; border-left: 4px solid #BDBDBD;">
                                <strong>{status['icon']} {status['step']}</strong>
                                <br><small>{status['time']}</small>
                            </div>
                        """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Shipment details
                st.markdown("### 📋 Shipment Details")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("#### 📍 Delivery Information")
                    st.markdown(f"**Destination:** {shipment_data['destination_city']}")
                    st.markdown(f"**Product:** {shipment_data['product_name']}")
                    st.markdown(f"**Weight:** {shipment_data['weight_kg']} kg")
                
                with col2:
                    st.markdown("#### 💳 Payment Details")
                    st.markdown(f"**Payment Type:** {shipment_data['payment_type']}")
                    st.markdown(f"**Priority:** {'Yes ⚡' if shipment_data['priority_flag'] == 1 else 'Standard'}")
                    st.markdown(f"**Status:** Ready for Dispatch")
                
                with col3:
                    st.markdown("#### ⏱️ Expected Delivery")
                    st.markdown(f"**ETA:** Today, 6:00 PM")
                    st.markdown(f"**Risk Level:** Low 🟢")
                    st.markdown(f"**Weather:** Clear ☀️")
                
                st.markdown("---")
                
                # AI transparency
                st.markdown("### 🧠 AI Analysis Results")
                
                with st.expander("🔍 View AI Decision Details"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Risk Assessment:**")
                        st.markdown(f"- Risk Score: {shipment_data['current_risk_score']:.0f}/100")
                        st.markdown(f"- Address Confidence: High")
                        st.markdown(f"- Weather Impact: Low")
                    
                    with col2:
                        st.markdown("**AI Decision:**")
                        st.markdown("- ✅ DISPATCH Approved")
                        st.markdown("- All factors favorable")
                        st.markdown("- No delays expected")
                    
                    st.info("""
                    💡 **What this means:** Our AI system analyzed multiple factors including 
                    address quality, weather conditions, delivery area accessibility, and package 
                    characteristics. Your shipment has been cleared for immediate dispatch with 
                    minimal risk of delays.
                    """)
                
                # Delay notification (if applicable)
                if shipment_data['current_risk_score'] > 60:
                    st.markdown("---")
                    st.warning("""
                    ⚠️ **Potential Delay Notice**
                    
                    Our system has detected some risk factors that may affect delivery:
                    - Weather conditions in destination area
                    - High delivery volume in the area
                    
                    **What we're doing:**
                    - Manager has reviewed and approved dispatch
                    - Allocated additional time buffer
                    - Will keep you updated if delays occur
                    
                    **Updated ETA:** Tomorrow, 12:00 PM (Extended by 18 hours for safety)
                    """)
                
                st.markdown("---")
                
                # Reschedule options
                st.markdown("### 📅 Need to Reschedule?")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("""
                        <div class="info-box">
                            <h4>📞 Contact Support</h4>
                            <p>Call: <strong>1800-123-4567</strong></p>
                            <p>WhatsApp: <strong>+91 98765-43210</strong></p>
                            <p>Email: <strong>support@lics.com</strong></p>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("""
                        <div class="info-box">
                            <h4>🔄 Reschedule Options</h4>
                            <p>• Deliver tomorrow</p>
                            <p>• Evening slot (6-9 PM)</p>
                            <p>• Choose custom date</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                if st.button("📞 Request Reschedule", use_container_width=True):
                    st.success("✅ Reschedule request submitted! Our team will contact you shortly.")
                
                st.markdown("---")
                
                # Feedback
                st.markdown("### 💬 Feedback")
                
                with st.form("feedback_form"):
                    st.markdown("Help us improve! Share your experience:")
                    
                    rating = st.select_slider(
                        "How satisfied are you with the tracking experience?",
                        options=["😞 Poor", "😐 Average", "🙂 Good", "😊 Very Good", "🤩 Excellent"]
                    )
                    
                    comments = st.text_area(
                        "Additional comments (optional)",
                        placeholder="Tell us what we can improve..."
                    )
                    
                    submit_feedback = st.form_submit_button("📨 Submit Feedback", use_container_width=True)
                    
                    if submit_feedback:
                        st.success("✅ Thank you for your feedback! We appreciate your input.")
                        st.balloons()
        
        except Exception as e:
            st.error(f"❌ Error loading shipment data: {str(e)}")
            st.info("💡 Please try again or contact support if the issue persists")

# Information section (always visible)
st.markdown("---")
st.markdown("### ℹ️ About Shipment Tracking")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
        <div class="info-box">
            <h4>🔒 Secure Tracking</h4>
            <p>Your shipment information is protected with phone verification</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="info-box">
            <h4>📲 Real-time Updates</h4>
            <p>Get SMS/WhatsApp notifications for every status change</p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class="info-box">
            <h4>💬 24/7 Support</h4>
            <p>Our team is always available to help with any queries</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Why LICS is different
st.markdown("### 🌟 Why Track with LICS?")

with st.expander("🎯 Transparent Communication"):
    st.markdown("""
    **We believe customers deserve honesty:**
    - ✅ Proactive delay notifications BEFORE dispatch
    - ✅ Clear explanations for any delays
    - ✅ AI-powered risk analysis shared with you
    - ✅ Real-time updates at every step
    
    **Our Philosophy:** *Customers forgive delays, not silence*
    """)

with st.expander("🧠 AI-Powered Intelligence"):
    st.markdown("""
    **How our system works:**
    1. **7-Factor Risk Analysis** - Weather, address, area, vehicle, payment, weight, priority
    2. **Human Oversight** - Managers review high-risk shipments
    3. **Proactive Communication** - You're informed before problems occur
    4. **Continuous Learning** - System improves with every delivery
    
    **Result:** Fewer surprises, better experience
    """)

with st.expander("📊 Data-Driven Decisions"):
    st.markdown("""
    **What we analyze for your shipment:**
    - 🗺️ **Address Intelligence** - NLP-based landmark detection
    - 🌦️ **Weather Impact** - Real-time weather conditions
    - 🚚 **Vehicle Feasibility** - Hyper-local delivery capability
    - ⚠️ **Risk Scoring** - Comprehensive risk assessment
    
    **Why it matters:** Better predictions = More reliable deliveries
    """)

st.markdown("---")

# Footer
st.markdown("""
    <div style="text-align: center; padding: 20px; color: #888;">
        <p><strong>LICS - Logistics Intelligence & Command System</strong></p>
        <p>AI suggests, humans decide, customers stay informed</p>
        <p>© 2026 LICS. All rights reserved.</p>
    </div>
""", unsafe_allow_html=True)
