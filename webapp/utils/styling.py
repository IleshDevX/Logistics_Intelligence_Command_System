"""
Styling utilities for LICS Web Application
Custom CSS injection and responsive design
"""

import streamlit as st

def apply_custom_styles():
    """Apply custom CSS styles to the Streamlit app"""
    st.markdown("""
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Global Styles */
        .stApp {
            font-family: 'Inter', sans-serif;
        }
        
        /* Header Styles */
        h1 {
            color: #1f2937;
            font-weight: 700;
            border-bottom: 3px solid #FF6B35;
            padding-bottom: 0.5rem;
            margin-bottom: 1.5rem;
        }
        
        h2 {
            color: #374151;
            font-weight: 600;
            margin-top: 2rem;
        }
        
        h3 {
            color: #4b5563;
            font-weight: 500;
        }
        
        /* Custom Components */
        .risk-indicator {
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
            font-weight: 600;
            text-align: center;
            margin: 0.5rem 0;
        }
        
        .risk-low {
            background-color: #d1fae5;
            color: #065f46;
            border: 1px solid #a7f3d0;
        }
        
        .risk-medium {
            background-color: #fef3c7;
            color: #92400e;
            border: 1px solid #fde68a;
        }
        
        .risk-high {
            background-color: #fee2e2;
            color: #991b1b;
            border: 1px solid #fca5a5;
        }
        
        /* Card Styles */
        .custom-card {
            background: white;
            padding: 1.5rem;
            border-radius: 0.75rem;
            border: 1px solid #e5e7eb;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
            margin: 1rem 0;
        }
        
        .dashboard-metric {
            text-align: center;
            padding: 1rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 0.5rem;
            margin: 0.5rem;
        }
        
        /* Button Styles */
        .stButton > button {
            border-radius: 0.5rem;
            border: none;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        
        /* Form Styles */
        .stTextInput > div > div > input {
            border-radius: 0.5rem;
            border: 1px solid #d1d5db;
            padding: 0.75rem;
        }
        
        .stSelectbox > div > div > select {
            border-radius: 0.5rem;
            border: 1px solid #d1d5db;
        }
        
        .stTextArea > div > div > textarea {
            border-radius: 0.5rem;
            border: 1px solid #d1d5db;
        }
        
        /* Sidebar Styles */
        .css-1d391kg {
            background-color: #f8fafc;
        }
        
        /* Alert Styles */
        .stAlert {
            border-radius: 0.5rem;
            border-left: 4px solid;
        }
        
        /* Status Indicators */
        .status-dispatched {
            color: #059669;
            font-weight: 600;
        }
        
        .status-delayed {
            color: #d97706;
            font-weight: 600;
        }
        
        .status-cancelled {
            color: #dc2626;
            font-weight: 600;
        }
        
        /* Mobile Responsive */
        @media (max-width: 768px) {
            .custom-card {
                padding: 1rem;
                margin: 0.5rem 0;
            }
            
            h1 {
                font-size: 1.5rem;
            }
            
            .dashboard-metric {
                margin: 0.25rem;
                padding: 0.75rem;
            }
        }
        
        /* Loading Spinner */
        .loading-spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #FF6B35;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Navigation Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            background-color: #f8fafc;
            border-radius: 0.5rem;
            color: #6b7280;
            font-weight: 500;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #FF6B35;
            color: white;
        }
        
        /* Hide Streamlit Branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Custom Success/Error Messages */
        .success-message {
            background-color: #d1fae5;
            color: #065f46;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #10b981;
            margin: 1rem 0;
        }
        
        .error-message {
            background-color: #fee2e2;
            color: #991b1b;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #ef4444;
            margin: 1rem 0;
        }
        
        .warning-message {
            background-color: #fef3c7;
            color: #92400e;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #f59e0b;
            margin: 1rem 0;
        }
        
        .info-message {
            background-color: #dbeafe;
            color: #1e40af;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #3b82f6;
            margin: 1rem 0;
        }
    </style>
    """, unsafe_allow_html=True)

def show_risk_indicator(score: int, size: str = "normal") -> str:
    """Display risk indicator based on score"""
    if score < 40:
        risk_level = "LOW"
        emoji = "🟢"
        css_class = "risk-low"
    elif score < 60:
        risk_level = "MEDIUM"
        emoji = "🟡"
        css_class = "risk-medium"
    else:
        risk_level = "HIGH"
        emoji = "🔴"
        css_class = "risk-high"
    
    size_class = "text-sm" if size == "small" else "text-base"
    
    return f"""
    <div class="risk-indicator {css_class} {size_class}">
        {emoji} {risk_level} RISK ({score}/100)
    </div>
    """

def show_status_badge(status: str) -> str:
    """Display status badge"""
    status_lower = status.lower()
    
    if status_lower in ['dispatched', 'delivered', 'completed']:
        color_class = "status-dispatched"
        emoji = "✅"
    elif status_lower in ['delayed', 'pending', 'processing']:
        color_class = "status-delayed"  
        emoji = "⏳"
    elif status_lower in ['cancelled', 'failed', 'rejected']:
        color_class = "status-cancelled"
        emoji = "❌"
    else:
        color_class = ""
        emoji = "📦"
    
    return f'<span class="{color_class}">{emoji} {status.upper()}</span>'

def create_metric_card(title: str, value: str, delta: str = "", color: str = "blue") -> str:
    """Create a styled metric card"""
    delta_html = f'<div style="font-size: 0.875rem; opacity: 0.8;">{delta}</div>' if delta else ""
    
    color_map = {
        "blue": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "green": "linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%)",
        "orange": "linear-gradient(135deg, #fa709a 0%, #fee140 100%)",
        "red": "linear-gradient(135deg, #fc466b 0%, #3f5efb 100%)"
    }
    
    gradient = color_map.get(color, color_map["blue"])
    
    return f"""
    <div style="
        background: {gradient};
        color: white;
        padding: 1.5rem;
        border-radius: 0.75rem;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    ">
        <div style="font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;">
            {value}
        </div>
        <div style="font-size: 0.875rem; font-weight: 500; opacity: 0.9;">
            {title}
        </div>
        {delta_html}
    </div>
    """

def show_loading_spinner(text: str = "Loading..."):
    """Display loading spinner"""
    return st.markdown(f"""
    <div style="text-align: center; padding: 2rem;">
        <div class="loading-spinner"></div>
        <p style="margin-top: 1rem; color: #6b7280;">{text}</p>
    </div>
    """, unsafe_allow_html=True)

def create_page_header(title: str, subtitle: str = "", icon: str = ""):
    """Create a consistent page header"""
    st.markdown(f"""
    <div style="margin-bottom: 2rem;">
        <h1>{icon} {title}</h1>
        {f'<p style="font-size: 1.1rem; color: #6b7280; margin-top: -1rem;">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)