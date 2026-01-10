"""
Customer Tracking Portal - Real-time Shipment Tracking
Customer-facing interface for tracking and managing deliveries
"""

import streamlit as st
import sys
import os
from datetime import datetime, timedelta
import time
import random

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import authentication
from components.auth import (
    require_role_access, 
    show_user_info_sidebar, 
    get_current_user
)

# Page configuration
st.set_page_config(
    page_title="LICS - Customer Tracking",
    page_icon="📦",
    layout="wide"
)

# Authentication check
require_role_access("📦 Track Shipment")
show_user_info_sidebar()

# Page header
st.title("📦 Customer Portal")
st.markdown("### Track Your Shipments & Manage Deliveries")

# Initialize demo customer data
if 'customer_shipments' not in st.session_state:
    current_user = get_current_user()
    customer_name = current_user.get('name', 'Customer')
    
    st.session_state['customer_shipments'] = [
        {
            'shipment_id': 'SHIP20240115001',
            'status': 'In Transit',
            'tracking_stage': 'out_for_delivery',
            'estimated_delivery': '2024-01-15 15:30',
            'current_location': 'Distribution Hub - Zone A',
            'delivery_address': 'Flat 402, Rainbow Apartments, Bandra West, Mumbai 400050',
            'items': ['Electronics - Smartphone', 'Accessories - Phone Case'],
            'total_value': 25000,
            'delivery_partner': 'Rajesh Kumar',
            'partner_phone': '+91 9876543210',
            'weather_alert': True,
            'can_reschedule': True,
            'delivery_attempts': 0
        },
        {
            'shipment_id': 'SHIP20240114002', 
            'status': 'Delivered',
            'tracking_stage': 'delivered',
            'estimated_delivery': '2024-01-14 14:20',
            'current_location': 'Delivered',
            'delivery_address': 'Office 201, Tech Park, Powai, Mumbai 400076',
            'items': ['Books - Python Programming'],
            'total_value': 1200,
            'delivery_partner': 'Completed',
            'partner_phone': '',
            'weather_alert': False,
            'can_reschedule': False,
            'delivery_attempts': 1,
            'delivered_at': '2024-01-14 14:20',
            'rating': None
        },
        {
            'shipment_id': 'SHIP20240113003',
            'status': 'Scheduled',
            'tracking_stage': 'processing',
            'estimated_delivery': '2024-01-16 10:00',
            'current_location': 'Preparing for Dispatch',
            'delivery_address': 'Flat 402, Rainbow Apartments, Bandra West, Mumbai 400050', 
            'items': ['Clothing - Cotton T-Shirt', 'Clothing - Jeans'],
            'total_value': 2500,
            'delivery_partner': 'To be assigned',
            'partner_phone': '',
            'weather_alert': False,
            'can_reschedule': True,
            'delivery_attempts': 0
        }
    ]

# Tracking stages for progress visualization
TRACKING_STAGES = {
    'order_placed': {'label': 'Order Placed', 'icon': '📝', 'color': 'blue'},
    'processing': {'label': 'Processing', 'icon': '⚙️', 'color': 'orange'},
    'dispatched': {'label': 'Dispatched', 'icon': '🚚', 'color': 'purple'},
    'in_transit': {'label': 'In Transit', 'icon': '🛣️', 'color': 'yellow'},
    'out_for_delivery': {'label': 'Out for Delivery', 'icon': '🚛', 'color': 'green'},
    'delivered': {'label': 'Delivered', 'icon': '✅', 'color': 'green'},
    'attempted': {'label': 'Delivery Attempted', 'icon': '⚠️', 'color': 'red'}
}

def show_tracking_progress(current_stage):
    """Show tracking progress bar"""
    stages = ['order_placed', 'processing', 'dispatched', 'in_transit', 'out_for_delivery', 'delivered']
    current_index = stages.index(current_stage) if current_stage in stages else 0
    
    cols = st.columns(len(stages))
    
    for i, stage in enumerate(stages):
        with cols[i]:
            stage_info = TRACKING_STAGES[stage]
            
            if i <= current_index:
                # Completed or current stage
                st.markdown(f"""
                <div style="text-align: center; background-color: #28a745; color: white; 
                           padding: 10px; border-radius: 5px; margin: 2px;">
                    <div style="font-size: 20px;">{stage_info['icon']}</div>
                    <div style="font-size: 12px; font-weight: bold;">{stage_info['label']}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Future stage
                st.markdown(f"""
                <div style="text-align: center; background-color: #e9ecef; color: #6c757d; 
                           padding: 10px; border-radius: 5px; margin: 2px;">
                    <div style="font-size: 20px;">{stage_info['icon']}</div>
                    <div style="font-size: 12px;">{stage_info['label']}</div>
                </div>
                """, unsafe_allow_html=True)

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs(["🔍 Track Shipment", "📦 My Orders", "📅 Reschedule", "⭐ Feedback"])

with tab1:
    st.header("🔍 Track Your Shipment")
    
    # Shipment lookup
    col_search1, col_search2 = st.columns([3, 1])
    
    with col_search1:
        tracking_id = st.text_input("Enter Shipment ID", 
                                   placeholder="e.g., SHIP20240115001",
                                   help="Enter your shipment ID to track your order")
    
    with col_search2:
        st.markdown("<br>", unsafe_allow_html=True)  # Add space
        search_clicked = st.button("🔍 Track", use_container_width=True, type="primary")
    
    # Quick access to customer's shipments
    if not tracking_id and not search_clicked:
        st.info("💡 **Quick Access**: Use the 'My Orders' tab to view all your shipments")
        
        st.markdown("### 🚀 Active Shipments")
        active_shipments = [s for s in st.session_state['customer_shipments'] if s['status'] in ['In Transit', 'Scheduled']]
        
        for shipment in active_shipments:
            with st.expander(f"📦 {shipment['shipment_id']} - {shipment['status']}", expanded=True):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Items:** {', '.join(shipment['items'])}")
                    st.write(f"**Current Location:** {shipment['current_location']}")
                    st.write(f"**Estimated Delivery:** {shipment['estimated_delivery']}")
                
                with col2:
                    if st.button(f"📍 Track Details", key=f"track_{shipment['shipment_id']}", use_container_width=True):
                        st.session_state['selected_tracking'] = shipment['shipment_id']
                        st.rerun()
    
    # Show tracking details
    selected_shipment = None
    
    # Check if tracking from input or session
    if search_clicked and tracking_id:
        selected_shipment = next((s for s in st.session_state['customer_shipments'] if s['shipment_id'] == tracking_id), None)
        if not selected_shipment:
            st.error("❌ Shipment not found. Please check your tracking ID.")
    elif 'selected_tracking' in st.session_state:
        selected_shipment = next((s for s in st.session_state['customer_shipments'] if s['shipment_id'] == st.session_state['selected_tracking']), None)
    
    if selected_shipment:
        st.markdown("---")
        st.subheader(f"📦 Shipment Details: {selected_shipment['shipment_id']}")
        
        # Weather alert if applicable
        if selected_shipment.get('weather_alert'):
            st.warning("🌧️ **Weather Alert**: Heavy rain expected in your area. Delivery may be delayed by 1-2 hours.")
        
        # Tracking progress
        st.markdown("### 🛣️ Tracking Progress")
        show_tracking_progress(selected_shipment['tracking_stage'])
        
        # Shipment information
        col_details1, col_details2, col_details3 = st.columns(3)
        
        with col_details1:
            st.markdown("**📋 Order Information**")
            st.write(f"**Status:** {selected_shipment['status']}")
            st.write(f"**Items:** {', '.join(selected_shipment['items'])}")
            st.write(f"**Value:** ₹{selected_shipment['total_value']:,}")
            st.write(f"**Delivery Address:** {selected_shipment['delivery_address']}")
        
        with col_details2:
            st.markdown("**🚚 Delivery Information**")
            st.write(f"**Current Location:** {selected_shipment['current_location']}")
            st.write(f"**Estimated Delivery:** {selected_shipment['estimated_delivery']}")
            st.write(f"**Delivery Partner:** {selected_shipment['delivery_partner']}")
            if selected_shipment.get('partner_phone'):
                st.write(f"**Partner Phone:** {selected_shipment['partner_phone']}")
        
        with col_details3:
            st.markdown("**⚡ Quick Actions**")
            
            if selected_shipment['can_reschedule'] and selected_shipment['status'] not in ['Delivered']:
                if st.button("📅 Reschedule Delivery", use_container_width=True):
                    st.info("📅 Redirecting to reschedule options...")
            
            if selected_shipment.get('partner_phone'):
                if st.button("📞 Call Delivery Partner", use_container_width=True):
                    st.success(f"📞 Calling {selected_shipment['partner_phone']}")
            
            if st.button("📧 Get Updates via SMS", use_container_width=True):
                st.success("📧 SMS updates enabled!")
        
        # Live tracking map placeholder
        if selected_shipment['status'] == 'In Transit':
            st.markdown("### 🗺️ Live Tracking")
            st.info("🗺️ **Live Map**: Your delivery partner is 15 minutes away from your location")
            
            # Simulate live updates
            with st.expander("📍 Recent Location Updates", expanded=True):
                st.write("🕐 **14:45** - Vehicle reached Junction 1, Bandra")
                st.write("🕐 **14:30** - Left distribution hub, en route to delivery")
                st.write("🕐 **14:15** - Package loaded for delivery")
        
        # Delivery instructions
        if selected_shipment['status'] in ['In Transit', 'Out for Delivery']:
            st.markdown("### 📝 Special Instructions")
            
            special_instructions = st.text_area(
                "Add delivery instructions",
                placeholder="e.g., Ring doorbell twice, leave with security guard, etc.",
                help="These instructions will be shared with your delivery partner"
            )
            
            if st.button("💾 Save Instructions"):
                st.success("✅ Instructions saved and shared with delivery partner!")

with tab2:
    st.header("📦 My Orders")
    
    # Order summary
    total_orders = len(st.session_state['customer_shipments'])
    delivered_orders = len([s for s in st.session_state['customer_shipments'] if s['status'] == 'Delivered'])
    active_orders = total_orders - delivered_orders
    
    col_summary1, col_summary2, col_summary3 = st.columns(3)
    
    with col_summary1:
        st.metric("Total Orders", total_orders, "📦")
    with col_summary2:
        st.metric("Active Orders", active_orders, "🚛")
    with col_summary3:
        st.metric("Delivered Orders", delivered_orders, "✅")
    
    st.markdown("---")
    
    # Filter options
    col_filter1, col_filter2 = st.columns(2)
    
    with col_filter1:
        status_filter = st.selectbox("Filter by Status", 
                                   ["All Orders", "Active Orders", "Delivered", "Scheduled"])
    
    with col_filter2:
        date_filter = st.selectbox("Time Period",
                                 ["All Time", "Last 7 days", "Last 30 days", "Last 3 months"])
    
    # Display orders
    filtered_shipments = st.session_state['customer_shipments']
    
    if status_filter != "All Orders":
        if status_filter == "Active Orders":
            filtered_shipments = [s for s in filtered_shipments if s['status'] in ['In Transit', 'Scheduled']]
        else:
            filtered_shipments = [s for s in filtered_shipments if s['status'] == status_filter]
    
    st.markdown(f"### 📋 Your Orders ({len(filtered_shipments)} found)")
    
    for shipment in filtered_shipments:
        # Color-code based on status
        if shipment['status'] == 'Delivered':
            status_color = "🟢"
        elif shipment['status'] == 'In Transit':
            status_color = "🟡"
        else:
            status_color = "🔵"
        
        with st.expander(f"{status_color} {shipment['shipment_id']} - {shipment['status']}", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**Items:** {', '.join(shipment['items'])}")
                st.write(f"**Value:** ₹{shipment['total_value']:,}")
                st.write(f"**Delivery Address:** {shipment['delivery_address'][:50]}...")
            
            with col2:
                if shipment['status'] == 'Delivered':
                    st.write(f"**Delivered At:** {shipment.get('delivered_at', 'N/A')}")
                    if not shipment.get('rating'):
                        st.write("**Rating:** ⭐ Not rated yet")
                    else:
                        st.write(f"**Rating:** {'⭐' * shipment['rating']}")
                else:
                    st.write(f"**Estimated Delivery:** {shipment['estimated_delivery']}")
                    st.write(f"**Current Location:** {shipment['current_location']}")
            
            with col3:
                if shipment['status'] == 'Delivered' and not shipment.get('rating'):
                    if st.button(f"⭐ Rate Order", key=f"rate_{shipment['shipment_id']}"):
                        st.session_state['rating_shipment'] = shipment['shipment_id']
                        st.rerun()
                elif shipment['status'] in ['In Transit', 'Scheduled']:
                    if st.button(f"📍 Track", key=f"track_list_{shipment['shipment_id']}"):
                        st.session_state['selected_tracking'] = shipment['shipment_id']
                        st.rerun()
                
                if shipment['can_reschedule']:
                    if st.button(f"📅 Reschedule", key=f"reschedule_{shipment['shipment_id']}"):
                        st.session_state['reschedule_shipment'] = shipment['shipment_id']
                        st.rerun()

with tab3:
    st.header("📅 Reschedule Delivery")
    
    # Get reschedulable shipments
    reschedulable = [s for s in st.session_state['customer_shipments'] if s['can_reschedule'] and s['status'] != 'Delivered']
    
    if not reschedulable:
        st.info("📦 No shipments available for rescheduling at the moment.")
    else:
        # Select shipment to reschedule
        shipment_options = [f"{s['shipment_id']} - {', '.join(s['items'][:2])}" for s in reschedulable]
        
        col_reschedule1, col_reschedule2 = st.columns(2)
        
        with col_reschedule1:
            selected_reschedule = st.selectbox("Select Shipment to Reschedule", shipment_options)
            
            if selected_reschedule:
                shipment_id = selected_reschedule.split(' - ')[0]
                selected_shipment = next(s for s in reschedulable if s['shipment_id'] == shipment_id)
                
                st.write(f"**Current Delivery:** {selected_shipment['estimated_delivery']}")
                st.write(f"**Items:** {', '.join(selected_shipment['items'])}")
        
        with col_reschedule2:
            st.markdown("**💡 Reschedule Options:**")
            st.write("• Choose your preferred date and time")
            st.write("• Minimum 2 hours advance notice required")
            st.write("• Subject to delivery partner availability")
        
        # Reschedule form
        with st.form("reschedule_form"):
            st.subheader("🗓️ Choose New Delivery Slot")
            
            col_date, col_time = st.columns(2)
            
            with col_date:
                new_date = st.date_input("Preferred Date",
                                       min_value=datetime.now().date(),
                                       max_value=datetime.now().date() + timedelta(days=7),
                                       value=datetime.now().date() + timedelta(days=1))
            
            with col_time:
                time_slots = [
                    "9:00 AM - 12:00 PM",
                    "12:00 PM - 3:00 PM", 
                    "3:00 PM - 6:00 PM",
                    "6:00 PM - 9:00 PM"
                ]
                new_time = st.selectbox("Preferred Time Slot", time_slots)
            
            reschedule_reason = st.selectbox("Reason for Rescheduling", [
                "Personal Schedule Conflict",
                "Not Available at Home", 
                "Weather Concerns",
                "Address Issues",
                "Other"
            ])
            
            additional_notes = st.text_area("Additional Notes (Optional)",
                                          placeholder="Any special instructions or requirements...")
            
            submitted_reschedule = st.form_submit_button("📅 Request Reschedule", type="primary")
            
            if submitted_reschedule and selected_reschedule:
                # Process reschedule request
                new_datetime = f"{new_date} {new_time.split(' - ')[0]}"
                
                # Update the shipment
                for shipment in st.session_state['customer_shipments']:
                    if shipment['shipment_id'] == shipment_id:
                        shipment['estimated_delivery'] = new_datetime
                        shipment['status'] = 'Rescheduled'
                        break
                
                st.success("✅ Reschedule request submitted successfully!")
                st.info(f"📅 New delivery slot: **{new_datetime}**")
                st.info("📧 You will receive confirmation via SMS and email within 30 minutes.")
                
                # Show confirmation details
                with st.container():
                    st.markdown("**📋 Request Summary:**")
                    st.write(f"• **Shipment ID:** {shipment_id}")
                    st.write(f"• **New Date & Time:** {new_datetime}")
                    st.write(f"• **Reason:** {reschedule_reason}")
                    if additional_notes:
                        st.write(f"• **Notes:** {additional_notes}")

with tab4:
    st.header("⭐ Feedback & Reviews")
    
    # Show delivered orders that can be rated
    delivered_orders = [s for s in st.session_state['customer_shipments'] if s['status'] == 'Delivered']
    unrated_orders = [s for s in delivered_orders if not s.get('rating')]
    
    if unrated_orders:
        st.subheader("📦 Rate Your Recent Deliveries")
        
        for order in unrated_orders:
            with st.expander(f"⭐ Rate {order['shipment_id']}", expanded=True):
                col_rate1, col_rate2 = st.columns([2, 1])
                
                with col_rate1:
                    st.write(f"**Items:** {', '.join(order['items'])}")
                    st.write(f"**Delivered:** {order.get('delivered_at', 'Recently')}")
                    st.write(f"**Value:** ₹{order['total_value']:,}")
                
                with col_rate2:
                    # Rating form
                    with st.form(f"rating_form_{order['shipment_id']}"):
                        st.markdown("**Rate Your Experience:**")
                        
                        rating = st.radio("Overall Rating", 
                                        ["⭐ (1) Poor", "⭐⭐ (2) Fair", "⭐⭐⭐ (3) Good", 
                                         "⭐⭐⭐⭐ (4) Very Good", "⭐⭐⭐⭐⭐ (5) Excellent"],
                                        key=f"rating_{order['shipment_id']}")
                        
                        delivery_rating = st.radio("Delivery Experience",
                                                  ["😞 Poor", "😐 Average", "😊 Good", "😍 Excellent"],
                                                  key=f"delivery_{order['shipment_id']}")
                        
                        feedback_text = st.text_area("Comments (Optional)",
                                                   placeholder="Share your delivery experience...",
                                                   key=f"feedback_{order['shipment_id']}")
                        
                        submit_rating = st.form_submit_button("📤 Submit Review")
                        
                        if submit_rating:
                            # Extract rating number
                            rating_value = int(rating.split('(')[1].split(')')[0])
                            
                            # Save rating
                            order['rating'] = rating_value
                            order['delivery_rating'] = delivery_rating
                            order['feedback'] = feedback_text
                            
                            st.success("✅ Thank you for your feedback!")
                            st.balloons()
                            time.sleep(1)
                            st.rerun()
    
    # Show previous ratings
    rated_orders = [s for s in delivered_orders if s.get('rating')]
    
    if rated_orders:
        st.subheader("📋 Your Previous Reviews")
        
        for order in rated_orders:
            with st.expander(f"⭐ {order['shipment_id']} - {'⭐' * order['rating']}", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Items:** {', '.join(order['items'])}")
                    st.write(f"**Delivered:** {order.get('delivered_at', 'N/A')}")
                    st.write(f"**Overall Rating:** {'⭐' * order['rating']}")
                
                with col2:
                    st.write(f"**Delivery Experience:** {order.get('delivery_rating', 'N/A')}")
                    if order.get('feedback'):
                        st.write(f"**Your Comment:** {order['feedback']}")
    
    # Overall satisfaction survey
    st.markdown("---")
    st.subheader("📊 Help Us Improve")
    
    with st.form("satisfaction_survey"):
        st.markdown("**How satisfied are you with LICS overall?**")
        
        col_survey1, col_survey2 = st.columns(2)
        
        with col_survey1:
            overall_satisfaction = st.radio("Overall Satisfaction",
                                          ["😞 Very Dissatisfied", "😐 Dissatisfied", "😊 Neutral",
                                           "😍 Satisfied", "🤩 Very Satisfied"])
            
            likelihood_recommend = st.radio("Likelihood to Recommend",
                                           ["0-2 (Not Likely)", "3-5 (Neutral)", "6-8 (Likely)", "9-10 (Very Likely)"])
        
        with col_survey2:
            improvement_areas = st.multiselect("Areas for Improvement",
                                             ["Delivery Speed", "Communication", "Tracking Accuracy",
                                              "Delivery Partner Behavior", "Website/App Experience",
                                              "Customer Support", "Pricing"])
            
            additional_feedback = st.text_area("Additional Suggestions",
                                             placeholder="Any other feedback or suggestions...")
        
        submit_survey = st.form_submit_button("📤 Submit Feedback", type="primary")
        
        if submit_survey:
            st.success("🙏 Thank you for your valuable feedback!")
            st.info("💡 Your feedback helps us improve our services for all customers.")

# Footer
st.markdown("---")
col_footer1, col_footer2, col_footer3 = st.columns(3)

with col_footer1:
    st.markdown("**📞 Customer Support**")
    st.write("📱 **Phone:** +91-8000-LICS-01")
    st.write("📧 **Email:** support@lics.com")

with col_footer2:
    st.markdown("**⏰ Support Hours**")
    st.write("🕐 **Mon-Sat:** 9 AM - 9 PM")
    st.write("🕐 **Sunday:** 10 AM - 6 PM")

with col_footer3:
    if st.button("💬 Live Chat Support", use_container_width=True):
        st.success("💬 Connecting you to live support...")