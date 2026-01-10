"""
Shipment Tracking - Internal Shipment Management
📦 Comprehensive Shipment Overview for Internal Users
"""

import streamlit as st
import sys
import os
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Add project paths
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from utils.api_client import (
    is_logged_in,
    get_current_user,
    get_shipments,
    update_shipment_status,
    format_shipment_status,
    format_risk_level
)

# Page configuration
st.set_page_config(
    page_title="Shipment Tracking - LICS",
    page_icon="📦",
    layout="wide"
)

def apply_custom_css():
    """Apply custom CSS for shipment tracking"""
    st.markdown("""
    <style>
    .tracking-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    
    .shipment-summary {
        background: white;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .status-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.85em;
        font-weight: bold;
        margin: 0.2rem;
    }
    
    .filter-panel {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

def check_authentication():
    """Ensure user is logged in"""
    if not is_logged_in():
        st.error("🔐 Please login to access shipment tracking")
        st.stop()
    
    return get_current_user()

def show_tracking_header():
    """Display tracking header"""
    user = get_current_user()
    
    st.markdown(f"""
    <div class="tracking-header">
        <h1>📦 Shipment Tracking</h1>
        <p>Welcome {user.get('full_name', user.get('username'))} • 
        Real-time shipment monitoring • Comprehensive overview</p>
    </div>
    """, unsafe_allow_html=True)

def show_shipment_overview():
    """Show shipment overview with mock data"""
    st.markdown("### 📊 Shipment Overview")
    
    # Mock data
    shipments = [
        {
            "id": "SH001",
            "tracking_number": "TR001234567",
            "status": "in_transit",
            "origin": "New York, NY",
            "destination": "Los Angeles, CA",
            "created": "2024-01-15 10:30",
            "eta": "2024-01-17 16:00",
            "customer": "John Smith",
            "priority": "express",
            "risk_score": 0.85
        },
        {
            "id": "SH002", 
            "tracking_number": "TR001234568",
            "status": "pending_approval",
            "origin": "Chicago, IL",
            "destination": "Miami, FL",
            "created": "2024-01-15 14:20",
            "eta": "2024-01-18 12:00",
            "customer": "Medical Supplies Inc.",
            "priority": "urgent",
            "risk_score": 0.72
        },
        {
            "id": "SH003",
            "tracking_number": "TR001234569", 
            "status": "delivered",
            "origin": "Seattle, WA",
            "destination": "Denver, CO",
            "created": "2024-01-14 09:15",
            "eta": "2024-01-16 14:00",
            "customer": "Tech Solutions",
            "priority": "standard",
            "risk_score": 0.23
        }
    ]
    
    # Display shipments
    for shipment in shipments:
        risk_label, risk_class, risk_icon = format_risk_level(shipment["risk_score"])
        status_display = format_shipment_status(shipment["status"])
        
        st.markdown(f"""
        <div class="shipment-summary">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h4>{shipment['id']} - {shipment['origin']} → {shipment['destination']}</h4>
                <span class="{risk_class} status-badge">{risk_icon} {risk_label}</span>
            </div>
            <p><strong>Customer:</strong> {shipment['customer']} | 
            <strong>Status:</strong> {status_display} | 
            <strong>Priority:</strong> {shipment['priority'].title()}</p>
            <p><strong>Created:</strong> {shipment['created']} | 
            <strong>ETA:</strong> {shipment['eta']} |
            <strong>Tracking:</strong> {shipment['tracking_number']}</p>
        </div>
        """, unsafe_allow_html=True)

def main():
    """Main shipment tracking function"""
    apply_custom_css()
    
    # Check authentication
    user = check_authentication()
    
    # Header
    show_tracking_header()
    
    # Overview
    show_shipment_overview()

if __name__ == "__main__":
    main()