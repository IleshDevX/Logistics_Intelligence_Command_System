"""
Customer Tracking Portal - Transparent Shipment Monitoring
📱 Real-time Updates with Clear Communication
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
    get_shipment_details,
    format_shipment_status
)

# Page configuration
st.set_page_config(
    page_title="Customer Tracking - LICS",
    page_icon="📱",
    layout="wide"
)

def apply_custom_css():
    """Apply custom CSS for customer-friendly design"""
    st.markdown("""
    <style>
    .customer-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .tracking-card {
        background: white;
        border: 2px solid #e9ecef;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .status-timeline {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .status-active {
        background: #d4edda;
        border-left: 5px solid #28a745;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    
    .status-completed {
        background: #d1ecf1;
        border-left: 5px solid #17a2b8;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        opacity: 0.7;
    }
    
    .status-upcoming {
        background: #f8f9fa;
        border-left: 5px solid #6c757d;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        opacity: 0.5;
    }
    
    .delivery-info {
        background: #e3f2fd;
        border: 2px solid #2196f3;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .contact-info {
        background: #fff3e0;
        border: 2px solid #ff9800;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .tracking-search {
        background: white;
        border: 2px solid #007bff;
        border-radius: 25px;
        padding: 1rem 2rem;
        margin: 2rem auto;
        max-width: 600px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .eta-highlight {
        background: linear-gradient(90deg, #28a745 0%, #20c997 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-size: 1.2em;
        font-weight: bold;
    }
    
    .delay-warning {
        background: #fff3cd;
        border: 2px solid #ffc107;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Mobile responsive */
    @media (max-width: 768px) {
        .customer-header { padding: 1rem; }
        .tracking-card { margin: 0.5rem 0; padding: 1rem; }
        .tracking-search { margin: 1rem; padding: 0.8rem 1rem; }
    }
    </style>
    """, unsafe_allow_html=True)

def show_customer_header():
    """Display customer-friendly header"""
    st.markdown("""
    <div class="customer-header">
        <h1>📱 Track Your Shipment</h1>
        <p style="font-size: 1.2em; margin: 0.5rem 0;">
            Real-time updates • Transparent communication • Always in the know
        </p>
    </div>
    """, unsafe_allow_html=True)

def show_tracking_search():
    """Show shipment tracking search interface"""
    st.markdown("""
    <div class="tracking-search">
        <h3>🔍 Enter Tracking Information</h3>
        <p>Enter your tracking number, order ID, or phone number to track your shipment</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        tracking_input = st.text_input(
            "",
            placeholder="Enter tracking number (e.g., SH001, TR12345, or phone number)",
            key="tracking_search"
        )
    
    with col2:
        search_btn = st.button("🔍 Track Shipment", type="primary", use_container_width=True)
    
    if search_btn or tracking_input:
        if tracking_input.strip():
            show_shipment_tracking_results(tracking_input.strip())
        else:
            st.warning("⚠️ Please enter a tracking number or phone number")

def show_shipment_tracking_results(search_query: str):
    """Display tracking results for the search query"""
    st.markdown("---")
    st.markdown("### 📦 Tracking Results")
    
    # Mock shipment data (in real app, this would query the API)
    mock_shipments = [
        {
            "id": "SH001",
            "tracking_number": "TR001234567",
            "status": "in_transit",
            "created_date": "2024-01-15 10:30:00",
            "pickup_address": "123 Main St, New York, NY 10001",
            "delivery_address": "456 Oak Ave, Los Angeles, CA 90210",
            "customer_name": "John Smith",
            "customer_phone": "+1234567890",
            "estimated_delivery": "2024-01-17 16:00:00",
            "current_location": "Chicago, IL - Distribution Center",
            "driver_name": "Mike Johnson",
            "driver_phone": "+1987654321",
            "special_instructions": "Ring doorbell, safe to leave at door",
            "timeline": [
                {"status": "created", "timestamp": "2024-01-15 10:30:00", "location": "New York, NY", "description": "Shipment created and ready for pickup"},
                {"status": "picked_up", "timestamp": "2024-01-15 14:20:00", "location": "New York, NY", "description": "Package picked up from sender"},
                {"status": "in_transit", "timestamp": "2024-01-16 09:15:00", "location": "Chicago, IL", "description": "Package in transit - Currently at Chicago distribution center"},
                {"status": "out_for_delivery", "timestamp": "", "location": "Los Angeles, CA", "description": "Out for delivery"},
                {"status": "delivered", "timestamp": "", "location": "Los Angeles, CA", "description": "Delivered successfully"}
            ]
        }
    ]
    
    # Simple search matching
    found_shipments = []
    for shipment in mock_shipments:
        if (search_query.lower() in shipment["id"].lower() or 
            search_query in shipment["tracking_number"] or
            search_query in shipment["customer_phone"]):
            found_shipments.append(shipment)
    
    if found_shipments:
        for shipment in found_shipments:
            show_detailed_tracking(shipment)
    else:
        show_no_results_message(search_query)

def show_detailed_tracking(shipment: Dict[str, Any]):
    """Display detailed tracking information for a shipment"""
    st.markdown(f"""
    <div class="tracking-card">
        <h3>📦 Shipment {shipment['id']}</h3>
        <p><strong>Tracking Number:</strong> {shipment['tracking_number']}</p>
        <p><strong>Customer:</strong> {shipment['customer_name']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Status and ETA
    col1, col2 = st.columns(2)
    
    with col1:
        status_display = format_shipment_status(shipment['status'])
        st.markdown(f"""
        <div class="delivery-info">
            <h4>📍 Current Status</h4>
            <p style="font-size: 1.2em;"><strong>{status_display}</strong></p>
            <p><strong>Location:</strong> {shipment['current_location']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        eta_date = datetime.strptime(shipment['estimated_delivery'], '%Y-%m-%d %H:%M:%S')
        time_remaining = eta_date - datetime.now()
        
        if time_remaining.total_seconds() > 0:
            days = time_remaining.days
            hours = time_remaining.seconds // 3600
            eta_text = f"Arriving in {days} days, {hours} hours"
        else:
            eta_text = "Delivery window passed - Checking status"
        
        st.markdown(f"""
        <div class="eta-highlight">
            <h4>🕒 Estimated Delivery</h4>
            <p>{eta_date.strftime('%B %d, %Y at %I:%M %p')}</p>
            <p>{eta_text}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Route information
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown(f"""
        <div class="delivery-info">
            <h4>📍 Pickup Location</h4>
            <p>{shipment['pickup_address']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="delivery-info">
            <h4>🎯 Delivery Location</h4>
            <p>{shipment['delivery_address']}</p>
            <p><strong>Instructions:</strong> {shipment['special_instructions']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Timeline
    show_shipment_timeline(shipment['timeline'])
    
    # Contact information
    show_contact_information(shipment)
    
    # Map view (placeholder)
    show_route_map(shipment)

def show_shipment_timeline(timeline: List[Dict[str, Any]]):
    """Display shipment timeline with status updates"""
    st.markdown("### 🕒 Shipment Timeline")
    
    for i, event in enumerate(timeline):
        timestamp = event.get('timestamp', '')
        
        if timestamp and timestamp != '':
            # Completed status
            css_class = "status-completed"
            icon = "✅"
            time_display = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S').strftime('%B %d, %Y at %I:%M %p')
        elif i == len([e for e in timeline if e.get('timestamp', '') != '']):
            # Current active status
            css_class = "status-active"
            icon = "🔄"
            time_display = "In Progress"
        else:
            # Future status
            css_class = "status-upcoming"
            icon = "⏳"
            time_display = "Pending"
        
        st.markdown(f"""
        <div class="{css_class}">
            <h5>{icon} {event['description']}</h5>
            <p><strong>Location:</strong> {event['location']}</p>
            <p><strong>Time:</strong> {time_display}</p>
        </div>
        """, unsafe_allow_html=True)

def show_contact_information(shipment: Dict[str, Any]):
    """Display driver and support contact information"""
    st.markdown("### 📞 Contact Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if shipment['status'] in ['in_transit', 'out_for_delivery']:
            st.markdown(f"""
            <div class="contact-info">
                <h4>🚛 Your Driver</h4>
                <p><strong>Name:</strong> {shipment['driver_name']}</p>
                <p><strong>Phone:</strong> {shipment['driver_phone']}</p>
                <p><em>You can contact your driver directly for delivery updates</em></p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="contact-info">
                <h4>📞 Customer Support</h4>
                <p><strong>Phone:</strong> 1-800-LICS-HELP</p>
                <p><strong>Email:</strong> support@lics.com</p>
                <p><em>Available 24/7 for assistance</em></p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="contact-info">
            <h4>💬 Quick Actions</h4>
            <p>• Report delivery issue</p>
            <p>• Change delivery address</p>
            <p>• Schedule redelivery</p>
            <p>• Request SMS updates</p>
        </div>
        """, unsafe_allow_html=True)

def show_route_map(shipment: Dict[str, Any]):
    """Display route map visualization"""
    st.markdown("### 🗺️ Route Map")
    
    # Create mock route data
    route_data = pd.DataFrame({
        'Location': ['Pickup', 'Current', 'Delivery'],
        'Latitude': [40.7128, 41.8781, 34.0522],
        'Longitude': [-74.0060, -87.6298, -118.2437],
        'Status': ['Completed', 'Current', 'Pending'],
        'Description': [
            shipment['pickup_address'],
            shipment['current_location'],
            shipment['delivery_address']
        ]
    })
    
    # Create map
    fig = px.line_mapbox(
        route_data,
        lat='Latitude',
        lon='Longitude',
        color='Status',
        color_discrete_map={
            'Completed': 'green',
            'Current': 'blue', 
            'Pending': 'red'
        },
        hover_data=['Description'],
        mapbox_style='open-street-map',
        title='Shipment Route',
        height=400
    )
    
    # Add markers
    for _, row in route_data.iterrows():
        fig.add_trace(go.Scattermapbox(
            lat=[row['Latitude']],
            lon=[row['Longitude']],
            mode='markers',
            marker=dict(size=12, color={'Completed': 'green', 'Current': 'blue', 'Pending': 'red'}[row['Status']]),
            name=row['Location'],
            text=row['Description']
        ))
    
    fig.update_layout(
        mapbox=dict(
            center=dict(lat=38.5, lon=-98),
            zoom=3
        ),
        showlegend=False,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_no_results_message(search_query: str):
    """Display message when no tracking results are found"""
    st.markdown(f"""
    <div class="tracking-card">
        <h3>🔍 No Results Found</h3>
        <p>We couldn't find any shipments matching "<strong>{search_query}</strong>"</p>
        
        <h4>💡 Try these options:</h4>
        <ul>
            <li>Check your tracking number for typos</li>
            <li>Use the full tracking number without spaces</li>
            <li>Try the phone number used when creating the shipment</li>
            <li>Contact customer support at 1-800-LICS-HELP</li>
        </ul>
        
        <h4>📝 Common Tracking Number Formats:</h4>
        <ul>
            <li>TR001234567 (11-digit tracking number)</li>
            <li>SH001 (Shipment ID)</li>
            <li>+1234567890 (Phone number)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

def show_guest_features():
    """Show features for non-logged-in users"""
    st.markdown("### 📱 Guest Tracking Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="tracking-card">
            <h4>📞 SMS Updates</h4>
            <p>Get real-time SMS notifications about your shipment status</p>
            <button style="background: #007bff; color: white; border: none; padding: 0.5rem 1rem; border-radius: 5px; width: 100%;">
                Enable SMS
            </button>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="tracking-card">
            <h4>📧 Email Alerts</h4>
            <p>Receive detailed email updates with delivery photos</p>
            <button style="background: #28a745; color: white; border: none; padding: 0.5rem 1rem; border-radius: 5px; width: 100%;">
                Subscribe
            </button>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="tracking-card">
            <h4>📱 Mobile App</h4>
            <p>Download our mobile app for better tracking experience</p>
            <button style="background: #6c757d; color: white; border: none; padding: 0.5rem 1rem; border-radius: 5px; width: 100%;">
                Download
            </button>
        </div>
        """, unsafe_allow_html=True)

def show_shipment_history():
    """Show shipment history for logged-in customers"""
    st.markdown("### 📋 Your Shipment History")
    
    # Mock shipment history
    history = [
        {"id": "SH001", "date": "2024-01-15", "status": "In Transit", "destination": "Los Angeles, CA"},
        {"id": "TR987", "date": "2024-01-10", "status": "Delivered", "destination": "Chicago, IL"},
        {"id": "SH005", "date": "2024-01-05", "status": "Delivered", "destination": "Miami, FL"}
    ]
    
    for shipment in history:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.write(f"**{shipment['id']}**")
        
        with col2:
            st.write(shipment['date'])
        
        with col3:
            status_color = "🔄" if shipment['status'] == "In Transit" else "✅"
            st.write(f"{status_color} {shipment['status']}")
        
        with col4:
            if st.button("View Details", key=f"view_{shipment['id']}"):
                show_shipment_tracking_results(shipment['id'])

def main():
    """Main customer tracking function"""
    apply_custom_css()
    
    # Header
    show_customer_header()
    
    # Check if user is logged in
    if is_logged_in():
        user = get_current_user()
        st.markdown(f"### Welcome back, {user.get('full_name', user.get('username'))}!")
        
        # Tabs for logged-in users
        tab1, tab2 = st.tabs(["🔍 Track Shipment", "📋 My Shipments"])
        
        with tab1:
            show_tracking_search()
        
        with tab2:
            show_shipment_history()
    
    else:
        # Guest tracking
        show_tracking_search()
        st.markdown("---")
        show_guest_features()
        
        # Login prompt
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: #f8f9fa; border-radius: 10px; margin: 2rem 0;">
            <h4>🔐 Want more features?</h4>
            <p>Login to view shipment history, manage preferences, and get personalized updates</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🚀 Login / Sign Up", type="primary", use_container_width=True):
                st.switch_page("app.py")

if __name__ == "__main__":
    main()