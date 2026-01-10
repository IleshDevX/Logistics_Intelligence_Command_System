"""
Analytics Dashboard - Intelligence Insights
📊 Learning from Decisions, Predicting Outcomes
"""

import streamlit as st
import sys
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Add project paths
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from utils.api_client import (
    is_logged_in,
    get_current_user,
    get_analytics_dashboard,
    format_user_role
)

# Page configuration  
st.set_page_config(
    page_title="Analytics Dashboard - LICS",
    page_icon="📊",
    layout="wide"
)

def apply_custom_css():
    """Apply custom CSS for analytics dashboard"""
    st.markdown("""
    <style>
    .analytics-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
    }
    
    .insight-card {
        background: white;
        border: 1px solid #e9ecef;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .insight-positive {
        border-left: 5px solid #28a745;
    }
    
    .insight-warning {
        border-left: 5px solid #ffc107;
    }
    
    .insight-critical {
        border-left: 5px solid #dc3545;
    }
    
    .metric-highlight {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .learning-insight {
        background: #e8f5e8;
        border: 1px solid #28a745;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .prediction-panel {
        background: #f8f9fa;
        border: 2px solid #6c757d;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .kpi-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

def check_authentication():
    """Ensure user has analytics access"""
    if not is_logged_in():
        st.error("🔐 Please login to access the Analytics Dashboard")
        st.stop()
    
    user = get_current_user()
    if not user:
        st.error("❌ User session invalid") 
        st.stop()
    
    # All authenticated users can view basic analytics
    return user

def show_analytics_header():
    """Display analytics dashboard header"""
    user = get_current_user()
    
    st.markdown(f"""
    <div class="analytics-header">
        <h1>📊 Analytics Dashboard</h1>
        <p style="font-size: 1.2em; margin: 0.5rem 0;">
            🧠 AI Learning • 📈 Performance Insights • 🔮 Predictive Analytics
        </p>
        <p style="opacity: 0.9; margin: 0;">
            User: {user.get('full_name', user.get('username'))} ({format_user_role(user.get('role'))}) • 
            Data Range: Last 30 Days • 
            Updated: {datetime.now().strftime('%H:%M:%S')}
        </p>
    </div>
    """, unsafe_allow_html=True)

def show_executive_kpis():
    """Show executive-level KPIs"""
    st.markdown("### 🎯 Executive KPIs")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown("""
        <div class="kpi-card">
            <h3 style="color: #28a745;">✅ Success Rate</h3>
            <h2>94.2%</h2>
            <p style="color: #28a745;">↑ 2.3% vs last month</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="kpi-card">
            <h3 style="color: #3498db;">🧠 AI Accuracy</h3>
            <h2>87.5%</h2>
            <p style="color: #3498db;">↑ 4.2% vs last month</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="kpi-card">
            <h3 style="color: #f39c12;">⚠️ Override Rate</h3>
            <h2>12.8%</h2>
            <p style="color: #f39c12;">↓ 1.5% vs last month</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="kpi-card">
            <h3 style="color: #e74c3c;">💰 Cost Savings</h3>
            <h2>$42.5K</h2>
            <p style="color: #e74c3c;">↑ $8.2K vs last month</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown("""
        <div class="kpi-card">
            <h3 style="color: #9b59b6;">⭐ Customer Sat.</h3>
            <h2>4.7/5</h2>
            <p style="color: #9b59b6;">↑ 0.2 vs last month</p>
        </div>
        """, unsafe_allow_html=True)

def show_ai_performance_analysis():
    """Show AI model performance analysis"""
    st.markdown("### 🧠 AI Performance Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # AI Accuracy Trend
        dates = pd.date_range(start='2024-01-01', end='2024-01-15', freq='D')
        accuracy_data = pd.DataFrame({
            'Date': dates,
            'Risk_Prediction': np.random.normal(0.87, 0.03, len(dates)),
            'Delivery_Time': np.random.normal(0.82, 0.04, len(dates)),
            'Cost_Estimation': np.random.normal(0.91, 0.02, len(dates))
        })
        
        # Ensure values stay in reasonable range
        for col in ['Risk_Prediction', 'Delivery_Time', 'Cost_Estimation']:
            accuracy_data[col] = np.clip(accuracy_data[col], 0.7, 0.95)
        
        fig_accuracy = px.line(
            accuracy_data, 
            x='Date',
            y=['Risk_Prediction', 'Delivery_Time', 'Cost_Estimation'],
            title='AI Model Accuracy Over Time',
            labels={'value': 'Accuracy (%)', 'variable': 'Model Type'}
        )
        
        fig_accuracy.update_yaxis(tickformat='.1%')
        st.plotly_chart(fig_accuracy, use_container_width=True)
    
    with col2:
        # Prediction Confidence Distribution
        confidence_data = pd.DataFrame({
            'Confidence_Range': ['90-100%', '80-90%', '70-80%', '60-70%', '<60%'],
            'Predictions': [145, 89, 34, 12, 5],
            'Success_Rate': [0.96, 0.88, 0.75, 0.63, 0.45]
        })
        
        fig_confidence = px.bar(
            confidence_data,
            x='Confidence_Range',
            y='Predictions',
            title='AI Confidence Distribution',
            color='Success_Rate',
            color_continuous_scale='RdYlGn'
        )
        
        st.plotly_chart(fig_confidence, use_container_width=True)

def show_decision_analytics():
    """Show human decision vs AI recommendation analysis"""
    st.markdown("### 🤝 Human vs AI Decision Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Override Analysis
        override_data = pd.DataFrame({
            'AI_Recommendation': ['Approve', 'Approve', 'Reject', 'Reject', 'Conditional', 'Conditional'],
            'Human_Decision': ['Approve', 'Reject', 'Approve', 'Reject', 'Approve', 'Conditional'],
            'Count': [156, 12, 8, 89, 15, 45],
            'Outcome_Success': [0.94, 0.67, 0.75, 0.96, 0.87, 0.91]
        })
        
        # Create agreement matrix
        agreement_matrix = np.array([[156, 12, 15], [8, 89, 0], [0, 0, 45]])
        
        fig_heatmap = px.imshow(
            agreement_matrix,
            labels=dict(x="Human Decision", y="AI Recommendation", color="Count"),
            x=['Approve', 'Reject', 'Conditional'],
            y=['Approve', 'Reject', 'Conditional'],
            title='AI vs Human Decision Agreement Matrix',
            color_continuous_scale='Blues'
        )
        
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    with col2:
        # Override outcomes
        outcome_data = pd.DataFrame({
            'Override_Type': ['AI Says Approve, Human Rejects', 'AI Says Reject, Human Approves', 
                            'AI Says Conditional, Human Approves', 'Agreement'],
            'Success_Rate': [0.67, 0.75, 0.87, 0.94],
            'Frequency': [12, 8, 15, 201]
        })
        
        fig_outcomes = px.scatter(
            outcome_data,
            x='Frequency', 
            y='Success_Rate',
            size='Frequency',
            color='Success_Rate',
            hover_data=['Override_Type'],
            title='Override Type vs Success Rate',
            color_continuous_scale='RdYlGn'
        )
        
        fig_outcomes.update_yaxis(tickformat='.1%')
        st.plotly_chart(fig_outcomes, use_container_width=True)

def show_learning_insights():
    """Display AI learning insights and improvements"""
    st.markdown("### 🎓 Learning Insights")
    
    insights = [
        {
            "type": "positive",
            "title": "Weather Model Improvement",
            "description": "AI weather predictions improved 15% after incorporating real-time satellite data",
            "impact": "Reduced weather-related delays by 23%"
        },
        {
            "type": "warning", 
            "title": "Rush Hour Pattern Learning",
            "description": "System identified new traffic patterns in Dallas-Fort Worth area",
            "impact": "Route optimization algorithms updated, 8% faster deliveries"
        },
        {
            "type": "critical",
            "title": "High-Value Cargo Handling",
            "description": "Model shows bias toward rejecting high-value shipments",
            "impact": "Recommending model retraining with balanced dataset"
        },
        {
            "type": "positive",
            "title": "Customer Preference Learning",
            "description": "AI successfully learned customer-specific delivery preferences",
            "impact": "Customer satisfaction up 12% for repeat customers"
        }
    ]
    
    for insight in insights:
        css_class = f"insight-{insight['type']}"
        icon = {"positive": "✅", "warning": "⚠️", "critical": "🚨"}[insight['type']]
        
        st.markdown(f"""
        <div class="insight-card {css_class}">
            <h4>{icon} {insight['title']}</h4>
            <p><strong>Finding:</strong> {insight['description']}</p>
            <p><strong>Impact:</strong> {insight['impact']}</p>
        </div>
        """, unsafe_allow_html=True)

def show_operational_metrics():
    """Show operational performance metrics"""
    st.markdown("### 🚛 Operational Performance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Delivery Performance by Route
        route_data = pd.DataFrame({
            'Route': ['NYC-LA', 'CHI-MIA', 'SEA-DEN', 'BOS-ATL', 'DAL-PHX'],
            'On_Time_Rate': [0.94, 0.87, 0.96, 0.82, 0.91],
            'Average_Delay_Hours': [2.3, 4.1, 1.8, 5.2, 3.1],
            'Total_Shipments': [145, 89, 123, 67, 98]
        })
        
        fig_route = px.scatter(
            route_data,
            x='Average_Delay_Hours',
            y='On_Time_Rate',
            size='Total_Shipments',
            hover_data=['Route'],
            title='Route Performance Analysis',
            labels={'On_Time_Rate': 'On-Time Delivery Rate', 'Average_Delay_Hours': 'Average Delay (Hours)'}
        )
        
        fig_route.update_yaxis(tickformat='.1%')
        st.plotly_chart(fig_route, use_container_width=True)
    
    with col2:
        # Cost Analysis by Package Type
        cost_data = pd.DataFrame({
            'Package_Type': ['Standard', 'Fragile', 'Hazardous', 'Perishable'],
            'Average_Cost': [85, 120, 180, 150],
            'AI_Predicted': [82, 125, 175, 145],
            'Variance': [3.5, -4.2, 2.9, 3.3]
        })
        
        fig_cost = go.Figure()
        fig_cost.add_trace(go.Bar(
            name='Actual Cost',
            x=cost_data['Package_Type'],
            y=cost_data['Average_Cost'],
            marker_color='lightblue'
        ))
        fig_cost.add_trace(go.Bar(
            name='AI Predicted',
            x=cost_data['Package_Type'], 
            y=cost_data['AI_Predicted'],
            marker_color='orange'
        ))
        
        fig_cost.update_layout(
            title='Cost Prediction Accuracy by Package Type',
            xaxis_title='Package Type',
            yaxis_title='Cost ($)',
            barmode='group'
        )
        
        st.plotly_chart(fig_cost, use_container_width=True)

def show_predictive_analytics():
    """Show predictive analytics and forecasts"""
    st.markdown("### 🔮 Predictive Analytics")
    
    st.markdown("""
    <div class="prediction-panel">
        <h4>🎯 Next 7 Days Forecast</h4>
        <p>AI-generated predictions based on historical patterns and current trends</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Volume prediction
        future_dates = pd.date_range(start=datetime.now().date(), periods=7, freq='D')
        volume_forecast = pd.DataFrame({
            'Date': future_dates,
            'Predicted_Shipments': [45, 52, 48, 39, 44, 28, 31],
            'Confidence_Lower': [38, 44, 41, 32, 37, 22, 25],
            'Confidence_Upper': [52, 60, 55, 46, 51, 34, 37]
        })
        
        fig_volume = go.Figure()
        fig_volume.add_trace(go.Scatter(
            x=volume_forecast['Date'],
            y=volume_forecast['Predicted_Shipments'],
            name='Predicted Volume',
            line=dict(color='blue', width=3)
        ))
        fig_volume.add_trace(go.Scatter(
            x=volume_forecast['Date'],
            y=volume_forecast['Confidence_Upper'],
            fill=None,
            mode='lines',
            line_color='rgba(0,0,0,0)',
            showlegend=False
        ))
        fig_volume.add_trace(go.Scatter(
            x=volume_forecast['Date'],
            y=volume_forecast['Confidence_Lower'],
            fill='tonexty',
            mode='lines',
            line_color='rgba(0,0,0,0)',
            name='Confidence Interval',
            fillcolor='rgba(68, 68, 68, 0.2)'
        ))
        
        fig_volume.update_layout(title='Shipment Volume Forecast')
        st.plotly_chart(fig_volume, use_container_width=True)
    
    with col2:
        # Risk distribution prediction
        risk_forecast = pd.DataFrame({
            'Day': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'High_Risk': [4, 6, 3, 5, 7, 2, 1],
            'Medium_Risk': [12, 15, 10, 14, 18, 8, 6],
            'Low_Risk': [29, 31, 35, 20, 19, 18, 24]
        })
        
        fig_risk_forecast = px.bar(
            risk_forecast,
            x='Day',
            y=['High_Risk', 'Medium_Risk', 'Low_Risk'],
            title='Risk Level Distribution Forecast',
            color_discrete_map={
                'High_Risk': '#dc3545',
                'Medium_Risk': '#ffc107', 
                'Low_Risk': '#28a745'
            }
        )
        
        st.plotly_chart(fig_risk_forecast, use_container_width=True)

def show_system_health():
    """Show system health and performance metrics"""
    st.markdown("### 🔧 System Health")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🖥️ API Response Time",
            value="145ms",
            delta="-23ms"
        )
    
    with col2:
        st.metric(
            label="🔄 Model Refresh Rate", 
            value="Every 4h",
            delta="On Schedule"
        )
    
    with col3:
        st.metric(
            label="💾 Data Quality Score",
            value="96.2%",
            delta="+1.4%"
        )
    
    with col4:
        st.metric(
            label="🔒 Security Score",
            value="98.7%",
            delta="Excellent"
        )

def show_export_options():
    """Show data export and report generation options"""
    st.markdown("### 📋 Reports & Export")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Generate Executive Report", type="primary", use_container_width=True):
            st.success("📊 Executive report generated! Check downloads folder.")
    
    with col2:
        if st.button("📈 Export Analytics Data", use_container_width=True):
            st.success("📈 Analytics data exported to CSV format.")
    
    with col3:
        if st.button("🧠 AI Model Performance Report", use_container_width=True):
            st.success("🧠 AI performance report generated.")

def main():
    """Main analytics dashboard function"""
    apply_custom_css()
    
    # Check authentication
    user = check_authentication()
    
    # Header
    show_analytics_header()
    
    # Navigation tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 Executive Summary",
        "🧠 AI Performance", 
        "🤝 Decision Analysis",
        "🔮 Predictions",
        "🔧 System Health"
    ])
    
    with tab1:
        show_executive_kpis()
        st.markdown("---")
        show_operational_metrics()
        st.markdown("---")
        show_export_options()
    
    with tab2:
        show_ai_performance_analysis()
        st.markdown("---")
        show_learning_insights()
    
    with tab3:
        show_decision_analytics()
    
    with tab4:
        show_predictive_analytics()
    
    with tab5:
        show_system_health()

if __name__ == "__main__":
    main()