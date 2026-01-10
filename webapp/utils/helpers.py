"""
Utility functions for data visualization and common operations
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

def format_currency(amount):
    """Format currency in Indian Rupee format"""
    return f"₹{amount:,.0f}"

def format_percentage(value):
    """Format value as percentage"""
    return f"{value:.1f}%" if value is not None else "N/A"

def calculate_risk_level(risk_score):
    """Calculate risk level from score"""
    if risk_score <= 30:
        return {"level": "Low", "color": "green", "icon": "🟢"}
    elif risk_score <= 60:
        return {"level": "Medium", "color": "orange", "icon": "🟡"}
    else:
        return {"level": "High", "color": "red", "icon": "🔴"}

def create_metric_card(title, value, delta=None, help_text=None):
    """Create a styled metric card"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.metric(title, value, delta=delta, help=help_text)

def create_progress_bar(label, value, max_value=100, color="blue"):
    """Create a styled progress bar"""
    progress_pct = (value / max_value) if max_value > 0 else 0
    st.markdown(f"**{label}**")
    st.progress(progress_pct)
    st.caption(f"{value}/{max_value}")

def create_status_badge(status):
    """Create colored status badges"""
    status_colors = {
        "DISPATCH": {"color": "green", "icon": "✅"},
        "DELAY": {"color": "orange", "icon": "⏳"},
        "RESCHEDULE": {"color": "red", "icon": "📅"},
        "CANCEL": {"color": "gray", "icon": "❌"},
        "In Transit": {"color": "blue", "icon": "🚛"},
        "Delivered": {"color": "green", "icon": "📦"},
        "Pending": {"color": "orange", "icon": "⏸️"}
    }
    
    config = status_colors.get(status, {"color": "gray", "icon": "❓"})
    return f"{config['icon']} **{status}**"

def create_risk_gauge(risk_score, title="Risk Score"):
    """Create a risk gauge chart"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = risk_score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 30], 'color': "lightgreen"},
                {'range': [30, 60], 'color': "yellow"},
                {'range': [60, 100], 'color': "lightcoral"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 70
            }
        }
    ))
    
    fig.update_layout(height=300)
    return fig

def create_timeline_chart(data, x_col, y_col, title="Timeline"):
    """Create a timeline chart"""
    fig = px.line(data, x=x_col, y=y_col, title=title, markers=True)
    fig.update_layout(
        xaxis_title=x_col.title(),
        yaxis_title=y_col.title(),
        hovermode='x unified'
    )
    return fig

def create_zone_heatmap(data, zone_col, metric_col, title="Zone Performance"):
    """Create a zone-based heatmap"""
    zone_data = data.groupby(zone_col)[metric_col].mean().reset_index()
    
    fig = px.bar(zone_data, x=zone_col, y=metric_col, title=title,
                color=metric_col, color_continuous_scale='RdYlGn')
    
    fig.update_layout(
        xaxis_title="Zone",
        yaxis_title=metric_col.title()
    )
    return fig

def format_time_ago(timestamp_str):
    """Format timestamp as 'time ago' string"""
    try:
        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        now = datetime.now()
        diff = now - timestamp
        
        if diff.days > 0:
            return f"{diff.days} days ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hours ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minutes ago"
        else:
            return "Just now"
    except:
        return "Unknown"

def create_notification_alert(message, alert_type="info"):
    """Create styled notification alerts"""
    alert_configs = {
        "info": {"icon": "ℹ️", "color": "info"},
        "success": {"icon": "✅", "color": "success"},
        "warning": {"icon": "⚠️", "color": "warning"},
        "error": {"icon": "❌", "color": "error"}
    }
    
    config = alert_configs.get(alert_type, alert_configs["info"])
    
    if config["color"] == "info":
        st.info(f"{config['icon']} {message}")
    elif config["color"] == "success":
        st.success(f"{config['icon']} {message}")
    elif config["color"] == "warning":
        st.warning(f"{config['icon']} {message}")
    else:
        st.error(f"{config['icon']} {message}")

def validate_phone_number(phone):
    """Validate Indian phone number format"""
    import re
    pattern = r'^[\+]?[91]?[6789]\d{9}$'
    return re.match(pattern, phone.replace(' ', '').replace('-', '')) is not None

def validate_pincode(pincode):
    """Validate Indian pincode format"""
    import re
    pattern = r'^[1-9][0-9]{5}$'
    return re.match(pattern, pincode) is not None

def generate_shipment_id():
    """Generate unique shipment ID"""
    import time
    return f"SHIP{int(time.time())}"

def calculate_eta(distance_km, traffic_factor=1.0):
    """Calculate estimated time of arrival"""
    # Assuming average speed of 25 km/h in city traffic
    base_speed = 25
    adjusted_speed = base_speed / traffic_factor
    hours = distance_km / adjusted_speed
    
    return datetime.now() + timedelta(hours=hours)

def get_weather_icon(condition):
    """Get weather icon for condition"""
    weather_icons = {
        "Clear": "☀️",
        "Sunny": "🌞", 
        "Cloudy": "☁️",
        "Overcast": "🌫️",
        "Rain": "🌧️",
        "Heavy Rain": "⛈️",
        "Thunderstorm": "⚡",
        "Snow": "❄️",
        "Fog": "🌫️"
    }
    return weather_icons.get(condition, "🌤️")

def create_data_table(data, columns_config=None):
    """Create a styled data table with optional column configuration"""
    if columns_config:
        # Apply column formatting
        for col, config in columns_config.items():
            if col in data.columns:
                if config.get('format') == 'currency':
                    data[col] = data[col].apply(format_currency)
                elif config.get('format') == 'percentage':
                    data[col] = data[col].apply(format_percentage)
    
    return st.dataframe(data, use_container_width=True)

def export_to_csv(data, filename):
    """Export data to CSV with download button"""
    csv = data.to_csv(index=False)
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=filename,
        mime='text/csv'
    )

class SessionState:
    """Helper class for managing session state"""
    
    @staticmethod
    def init_key(key, default_value):
        """Initialize session state key if not exists"""
        if key not in st.session_state:
            st.session_state[key] = default_value
    
    @staticmethod
    def get(key, default=None):
        """Get session state value"""
        return st.session_state.get(key, default)
    
    @staticmethod
    def set(key, value):
        """Set session state value"""
        st.session_state[key] = value
    
    @staticmethod
    def clear(key):
        """Clear session state key"""
        if key in st.session_state:
            del st.session_state[key]

def create_loading_spinner(text="Processing..."):
    """Create a loading spinner with text"""
    with st.spinner(text):
        return True

def create_confirmation_dialog(message, key=None):
    """Create a confirmation dialog"""
    if key is None:
        key = "confirm_dialog"
    
    st.warning(message)
    col1, col2 = st.columns(2)
    
    with col1:
        confirm = st.button("✅ Confirm", key=f"{key}_confirm", type="primary")
    with col2:
        cancel = st.button("❌ Cancel", key=f"{key}_cancel")
    
    return {"confirm": confirm, "cancel": cancel}

def create_info_box(title, content, icon="ℹ️"):
    """Create an info box with title and content"""
    with st.container():
        st.markdown(f"### {icon} {title}")
        if isinstance(content, list):
            for item in content:
                st.write(f"• {item}")
        else:
            st.write(content)

def format_delivery_address(address, max_length=50):
    """Format delivery address for display"""
    if len(address) <= max_length:
        return address
    return address[:max_length] + "..."

def calculate_delivery_zones():
    """Calculate delivery zone mappings"""
    return {
        "Zone-A": {"name": "Central Mumbai", "avg_time": "2-4 hours"},
        "Zone-B": {"name": "North Mumbai", "avg_time": "3-5 hours"},
        "Zone-C": {"name": "South Mumbai", "avg_time": "2-4 hours"},
        "Zone-D": {"name": "East Mumbai", "avg_time": "4-6 hours"},
        "Zone-E": {"name": "West Mumbai", "avg_time": "3-5 hours"},
        "Zone-F": {"name": "Suburbs", "avg_time": "6-8 hours"}
    }

def get_priority_config(priority):
    """Get priority configuration"""
    configs = {
        "Standard": {"icon": "📦", "color": "blue", "sla": "24 hours"},
        "Express": {"icon": "⚡", "color": "orange", "sla": "12 hours"},
        "Same Day": {"icon": "🚀", "color": "purple", "sla": "6 hours"},
        "Critical": {"icon": "🚨", "color": "red", "sla": "3 hours"}
    }
    return configs.get(priority, configs["Standard"])