"""
Styling Utilities - Custom CSS and theme management
"""

import streamlit as st


def apply_custom_css():
    """Apply custom CSS styling to the application"""
    
    st.markdown("""
        <style>
        /* Global Styles */
        .main {
            background-color: #F8F9FA;
        }
        
        /* Risk Indicators */
        .risk-low {
            background: linear-gradient(135deg, #00C853 0%, #64DD17 100%);
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            font-weight: bold;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .risk-medium {
            background: linear-gradient(135deg, #FFB300 0%, #FFC107 100%);
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            font-weight: bold;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .risk-high {
            background: linear-gradient(135deg, #D32F2F 0%, #F44336 100%);
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            font-weight: bold;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        /* Decision Cards */
        .decision-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin: 10px 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border-left: 5px solid #FF6B35;
        }
        
        .decision-dispatch {
            border-left-color: #00C853;
        }
        
        .decision-delay {
            border-left-color: #FFB300;
        }
        
        .decision-reschedule {
            border-left-color: #D32F2F;
        }
        
        /* Status Badges */
        .status-badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            margin: 5px;
        }
        
        .status-pending {
            background-color: #FFF9C4;
            color: #F57F17;
        }
        
        .status-in-transit {
            background-color: #B3E5FC;
            color: #01579B;
        }
        
        .status-delivered {
            background-color: #C8E6C9;
            color: #1B5E20;
        }
        
        .status-delayed {
            background-color: #FFCCBC;
            color: #BF360C;
        }
        
        /* Metric Cards */
        .metric-card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
            margin: 10px 0;
        }
        
        .metric-value {
            font-size: 32px;
            font-weight: bold;
            color: #FF6B35;
            margin: 10px 0;
        }
        
        .metric-label {
            font-size: 14px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        /* AI Indicator */
        .ai-badge {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 11px;
            font-weight: bold;
            display: inline-block;
            margin-left: 10px;
        }
        
        /* Human Override Indicator */
        .human-badge {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 11px;
            font-weight: bold;
            display: inline-block;
            margin-left: 10px;
        }
        
        /* Info Boxes */
        .info-box {
            background-color: #E3F2FD;
            border-left: 4px solid #2196F3;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }
        
        .warning-box {
            background-color: #FFF3E0;
            border-left: 4px solid #FF9800;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }
        
        .success-box {
            background-color: #E8F5E9;
            border-left: 4px solid #4CAF50;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }
        
        .error-box {
            background-color: #FFEBEE;
            border-left: 4px solid #F44336;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }
        
        /* Page Headers */
        .page-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .page-title {
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .page-subtitle {
            font-size: 16px;
            opacity: 0.9;
        }
        
        /* Buttons */
        .stButton > button {
            border-radius: 8px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        
        /* Forms */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > select,
        .stTextArea > div > div > textarea {
            border-radius: 8px;
            border: 2px solid #E0E0E0;
            padding: 10px;
        }
        
        .stTextInput > div > div > input:focus,
        .stSelectbox > div > div > select:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: #FF6B35;
            box-shadow: 0 0 0 2px rgba(255, 107, 53, 0.1);
        }
        
        /* Sidebar */
        .css-1d391kg {
            background-color: #F8F9FA;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Tables */
        .dataframe {
            border-radius: 8px;
            overflow: hidden;
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            background-color: #F5F5F5;
            border-radius: 8px;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)


def get_risk_color(risk_score: float) -> str:
    """Get color code based on risk score"""
    if risk_score < 40:
        return "#00C853"  # Green
    elif risk_score < 70:
        return "#FFB300"  # Orange
    else:
        return "#D32F2F"  # Red


def get_risk_badge_html(risk_score: float, risk_bucket: str) -> str:
    """Generate HTML for risk badge"""
    
    if risk_bucket == "Low":
        css_class = "risk-low"
        icon = "🟢"
    elif risk_bucket == "Medium":
        css_class = "risk-medium"
        icon = "🟡"
    else:
        css_class = "risk-high"
        icon = "🔴"
    
    return f"""
        <div class="{css_class}">
            {icon} {risk_bucket} Risk - Score: {risk_score:.0f}
        </div>
    """


def get_decision_badge_html(decision: str) -> str:
    """Generate HTML for decision badge"""
    
    decision_config = {
        "DISPATCH": {"color": "#00C853", "icon": "✅", "text": "DISPATCH"},
        "DELAY": {"color": "#FFB300", "icon": "⏸️", "text": "DELAY"},
        "RESCHEDULE": {"color": "#D32F2F", "icon": "🔄", "text": "RESCHEDULE"}
    }
    
    config = decision_config.get(decision, decision_config["DISPATCH"])
    
    return f"""
        <div style="background-color: {config['color']}; color: white; padding: 10px 20px; 
                    border-radius: 8px; font-weight: bold; text-align: center; 
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            {config['icon']} {config['text']}
        </div>
    """


def display_metric_card(label: str, value: str, icon: str = "📊"):
    """Display a metric card"""
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{icon} {label}</div>
            <div class="metric-value">{value}</div>
        </div>
    """, unsafe_allow_html=True)
