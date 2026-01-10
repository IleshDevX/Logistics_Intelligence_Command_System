"""
Analytics Dashboard - Business Intelligence & AI Monitoring
Comprehensive analytics and reporting for supervisors
"""

import streamlit as st
import sys
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

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
    page_title="LICS - Analytics",
    page_icon="📊",
    layout="wide"
)

# Authentication check
require_role_access("📊 Analytics")
show_user_info_sidebar()

# Page header
st.title("📊 Analytics Dashboard")
st.markdown("### Business Intelligence & AI Decision Monitoring")

# Generate mock data for analytics
@st.cache_data
def generate_analytics_data():
    """Generate comprehensive analytics data for demo"""
    
    # Shipment performance data
    dates = pd.date_range(start='2024-01-01', end='2024-01-15', freq='D')
    
    shipment_data = []
    for date in dates:
        daily_shipments = np.random.randint(30, 80)
        for i in range(daily_shipments):
            risk_score = np.random.normal(45, 20)
            risk_score = max(0, min(100, risk_score))
            
            weather_impact = np.random.uniform(0.1, 0.9)
            
            # AI decision based on risk score and weather
            if risk_score > 70 or weather_impact > 0.7:
                ai_decision = np.random.choice(['DELAY', 'RESCHEDULE'], p=[0.7, 0.3])
            elif risk_score > 40:
                ai_decision = np.random.choice(['DISPATCH', 'DELAY'], p=[0.8, 0.2])
            else:
                ai_decision = 'DISPATCH'
            
            # Human override probability
            override_prob = 0.1 if ai_decision == 'DISPATCH' else 0.3
            is_overridden = np.random.random() < override_prob
            
            delivery_success = True
            if ai_decision == 'DISPATCH' and not is_overridden:
                delivery_success = np.random.random() < 0.94
            elif is_overridden:
                delivery_success = np.random.random() < 0.88
            else:
                delivery_success = np.random.random() < 0.96
            
            shipment_data.append({
                'date': date,
                'shipment_id': f'SHIP{date.strftime("%Y%m%d")}{i:03d}',
                'risk_score': risk_score,
                'weather_impact': weather_impact,
                'ai_decision': ai_decision,
                'is_overridden': is_overridden,
                'delivery_success': delivery_success,
                'zone': np.random.choice(['Zone-A', 'Zone-B', 'Zone-C', 'Zone-D', 'Zone-E']),
                'priority': np.random.choice(['Standard', 'Express', 'Critical'], p=[0.7, 0.25, 0.05])
            })
    
    return pd.DataFrame(shipment_data)

# Load data
df = generate_analytics_data()

# Sidebar filters
st.sidebar.markdown("### 🔍 Analytics Filters")

date_range = st.sidebar.date_input(
    "Date Range",
    value=(df['date'].min().date(), df['date'].max().date()),
    min_value=df['date'].min().date(),
    max_value=df['date'].max().date()
)

selected_zones = st.sidebar.multiselect(
    "Delivery Zones",
    options=df['zone'].unique(),
    default=df['zone'].unique()
)

risk_threshold = st.sidebar.slider(
    "Risk Score Threshold",
    min_value=0,
    max_value=100,
    value=70,
    help="Highlight shipments above this risk score"
)

# Filter data
if len(date_range) == 2:
    start_date, end_date = date_range
    mask = (df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)
    df_filtered = df[mask]
else:
    df_filtered = df

if selected_zones:
    df_filtered = df_filtered[df_filtered['zone'].isin(selected_zones)]

# Main dashboard tabs
tab1, tab2, tab3, tab4 = st.tabs(["📈 Performance Overview", "🤖 AI Decision Analysis", "🎯 Risk Intelligence", "📊 Operational Metrics"])

with tab1:
    st.header("📈 Performance Overview")
    
    # Key metrics row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_shipments = len(df_filtered)
    success_rate = df_filtered['delivery_success'].mean() * 100
    avg_risk_score = df_filtered['risk_score'].mean()
    override_rate = df_filtered['is_overridden'].mean() * 100
    high_risk_count = len(df_filtered[df_filtered['risk_score'] > risk_threshold])
    
    with col1:
        st.metric("Total Shipments", f"{total_shipments:,}", 
                 delta=f"+{int(total_shipments * 0.08)}" if total_shipments > 0 else "0")
    
    with col2:
        st.metric("Success Rate", f"{success_rate:.1f}%", 
                 delta="+2.3%" if success_rate > 90 else "-1.1%")
    
    with col3:
        st.metric("Avg Risk Score", f"{avg_risk_score:.0f}/100",
                 delta="-3" if avg_risk_score < 50 else "+5")
    
    with col4:
        st.metric("Override Rate", f"{override_rate:.1f}%",
                 delta="-0.5%" if override_rate < 15 else "+1.2%")
    
    with col5:
        st.metric("High Risk Alerts", high_risk_count,
                 delta=f"-{int(high_risk_count * 0.1)}" if high_risk_count < 20 else f"+{int(high_risk_count * 0.05)}")
    
    # Daily performance trend
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("📅 Daily Shipment Volume")
        
        daily_stats = df_filtered.groupby(df_filtered['date'].dt.date).agg({
            'shipment_id': 'count',
            'delivery_success': 'mean',
            'risk_score': 'mean'
        }).reset_index()
        
        daily_stats.columns = ['Date', 'Shipments', 'Success_Rate', 'Avg_Risk']
        
        fig_volume = px.bar(daily_stats, x='Date', y='Shipments',
                           title="Daily Shipment Volume",
                           color='Avg_Risk',
                           color_continuous_scale='RdYlGn_r')
        fig_volume.update_layout(height=400)
        st.plotly_chart(fig_volume, use_container_width=True)
    
    with col_chart2:
        st.subheader("📊 Zone Performance")
        
        zone_stats = df_filtered.groupby('zone').agg({
            'shipment_id': 'count',
            'delivery_success': 'mean',
            'risk_score': 'mean',
            'is_overridden': 'mean'
        }).reset_index()
        
        zone_stats.columns = ['Zone', 'Shipments', 'Success_Rate', 'Avg_Risk', 'Override_Rate']
        
        fig_zone = px.scatter(zone_stats, x='Avg_Risk', y='Success_Rate',
                             size='Shipments', color='Override_Rate',
                             hover_data=['Zone'], 
                             title="Zone Risk vs Success Rate",
                             labels={'Avg_Risk': 'Average Risk Score',
                                    'Success_Rate': 'Success Rate'})
        fig_zone.update_layout(height=400)
        st.plotly_chart(fig_zone, use_container_width=True)
    
    # Success rate breakdown
    st.subheader("🎯 Success Rate Analysis")
    col_success1, col_success2 = st.columns(2)
    
    with col_success1:
        # Success by AI decision
        decision_success = df_filtered.groupby('ai_decision')['delivery_success'].mean().reset_index()
        decision_success.columns = ['AI_Decision', 'Success_Rate']
        
        fig_decision = px.bar(decision_success, x='AI_Decision', y='Success_Rate',
                             title="Success Rate by AI Decision",
                             color='Success_Rate',
                             color_continuous_scale='RdYlGn')
        fig_decision.update_layout(height=300)
        st.plotly_chart(fig_decision, use_container_width=True)
    
    with col_success2:
        # Override impact
        override_success = df_filtered.groupby('is_overridden')['delivery_success'].mean().reset_index()
        override_success['Override_Status'] = override_success['is_overridden'].map({True: 'Overridden', False: 'AI Decision'})
        
        fig_override = px.pie(override_success, names='Override_Status', values='delivery_success',
                             title="Success Rate: AI vs Override")
        fig_override.update_layout(height=300)
        st.plotly_chart(fig_override, use_container_width=True)

with tab2:
    st.header("🤖 AI Decision Analysis")
    
    # AI decision distribution
    col_ai1, col_ai2 = st.columns(2)
    
    with col_ai1:
        st.subheader("🎯 AI Decision Distribution")
        
        decision_counts = df_filtered['ai_decision'].value_counts().reset_index()
        decision_counts.columns = ['Decision', 'Count']
        
        fig_decisions = px.pie(decision_counts, names='Decision', values='Count',
                              title="AI Decision Breakdown",
                              color_discrete_map={
                                  'DISPATCH': '#2ecc71',
                                  'DELAY': '#f39c12', 
                                  'RESCHEDULE': '#e74c3c'
                              })
        fig_decisions.update_layout(height=400)
        st.plotly_chart(fig_decisions, use_container_width=True)
        
        # Decision accuracy
        st.metric("AI Decision Accuracy", "91.3%", "+1.8%")
        st.metric("Override Frequency", f"{override_rate:.1f}%", "-2.1%")
    
    with col_ai2:
        st.subheader("⚡ Risk Score Distribution")
        
        # Risk score histogram
        fig_risk_hist = px.histogram(df_filtered, x='risk_score', nbins=20,
                                    title="Risk Score Distribution",
                                    color_discrete_sequence=['#3498db'])
        fig_risk_hist.add_vline(x=risk_threshold, line_dash="dash", line_color="red",
                               annotation_text=f"Risk Threshold ({risk_threshold})")
        fig_risk_hist.update_layout(height=400)
        st.plotly_chart(fig_risk_hist, use_container_width=True)
    
    # AI vs Human decision comparison
    st.subheader("🤖 vs 👤 Decision Comparison")
    
    # Override analysis
    override_analysis = df_filtered[df_filtered['is_overridden'] == True].copy()
    
    if not override_analysis.empty:
        col_override1, col_override2 = st.columns(2)
        
        with col_override1:
            st.markdown("**Override Patterns by Risk Level:**")
            
            risk_bins = pd.cut(override_analysis['risk_score'], bins=[0, 30, 60, 100], 
                              labels=['Low (0-30)', 'Medium (30-60)', 'High (60-100)'])
            override_by_risk = risk_bins.value_counts().reset_index()
            override_by_risk.columns = ['Risk_Level', 'Override_Count']
            
            for _, row in override_by_risk.iterrows():
                st.write(f"• **{row['Risk_Level']}**: {row['Override_Count']} overrides")
        
        with col_override2:
            st.markdown("**Override Success Analysis:**")
            override_success_analysis = override_analysis.groupby('ai_decision').agg({
                'delivery_success': ['count', 'mean']
            }).reset_index()
            override_success_analysis.columns = ['AI_Decision', 'Override_Count', 'Success_Rate']
            
            for _, row in override_success_analysis.iterrows():
                success_pct = row['Success_Rate'] * 100
                st.write(f"• **{row['AI_Decision']}**: {success_pct:.0f}% success ({int(row['Override_Count'])} cases)")
    
    # Weather impact correlation  
    st.subheader("🌤️ Weather Impact Analysis")
    
    # Weather vs risk correlation
    fig_weather = px.scatter(df_filtered, x='weather_impact', y='risk_score',
                            color='ai_decision', size='delivery_success',
                            title="Weather Impact vs Risk Score",
                            labels={'weather_impact': 'Weather Impact Factor',
                                   'risk_score': 'Risk Score'})
    fig_weather.update_layout(height=400)
    st.plotly_chart(fig_weather, use_container_width=True)

with tab3:
    st.header("🎯 Risk Intelligence")
    
    # Risk factor analysis
    col_risk1, col_risk2 = st.columns(2)
    
    with col_risk1:
        st.subheader("⚠️ High Risk Shipments")
        
        high_risk_shipments = df_filtered[df_filtered['risk_score'] > risk_threshold].copy()
        
        if not high_risk_shipments.empty:
            st.write(f"**Found {len(high_risk_shipments)} high-risk shipments**")
            
            # High risk by zone
            high_risk_zones = high_risk_shipments['zone'].value_counts().reset_index()
            high_risk_zones.columns = ['Zone', 'High_Risk_Count']
            
            fig_high_risk = px.bar(high_risk_zones, x='Zone', y='High_Risk_Count',
                                  title="High-Risk Shipments by Zone",
                                  color='High_Risk_Count',
                                  color_continuous_scale='Reds')
            fig_high_risk.update_layout(height=300)
            st.plotly_chart(fig_high_risk, use_container_width=True)
            
            # Risk trends
            st.markdown("**Risk Trend Insights:**")
            avg_daily_risk = df_filtered.groupby(df_filtered['date'].dt.date)['risk_score'].mean()
            risk_trend = "📈 Increasing" if avg_daily_risk.iloc[-1] > avg_daily_risk.iloc[0] else "📉 Decreasing"
            st.write(f"• Risk trend: {risk_trend}")
            st.write(f"• Peak risk day: {avg_daily_risk.idxmax()}")
            st.write(f"• Lowest risk day: {avg_daily_risk.idxmin()}")
        else:
            st.success("✅ No high-risk shipments in selected period!")
    
    with col_risk2:
        st.subheader("📊 Risk Factor Correlation")
        
        # Risk vs other factors
        risk_weather_corr = df_filtered['risk_score'].corr(df_filtered['weather_impact'])
        
        st.metric("Risk-Weather Correlation", f"{risk_weather_corr:.3f}",
                 help="Correlation between risk score and weather impact")
        
        # Priority impact on risk
        priority_risk = df_filtered.groupby('priority')['risk_score'].mean().reset_index()
        
        st.markdown("**Average Risk by Priority:**")
        for _, row in priority_risk.iterrows():
            st.write(f"• **{row['priority']}**: {row['risk_score']:.0f}/100")
        
        # Risk mitigation effectiveness
        st.markdown("**Risk Mitigation Analysis:**")
        high_risk_with_override = df_filtered[(df_filtered['risk_score'] > risk_threshold) & 
                                             (df_filtered['is_overridden'] == True)]
        high_risk_without_override = df_filtered[(df_filtered['risk_score'] > risk_threshold) & 
                                                (df_filtered['is_overridden'] == False)]
        
        if not high_risk_with_override.empty and not high_risk_without_override.empty:
            override_success = high_risk_with_override['delivery_success'].mean() * 100
            no_override_success = high_risk_without_override['delivery_success'].mean() * 100
            
            st.write(f"• High-risk with override: {override_success:.0f}% success")
            st.write(f"• High-risk without override: {no_override_success:.0f}% success")
            
            if override_success > no_override_success:
                st.success("✅ Human overrides improve high-risk outcomes")
            else:
                st.warning("⚠️ AI decisions may be optimal for high-risk cases")
    
    # Risk prediction model performance
    st.subheader("🔮 Risk Prediction Insights")
    
    col_pred1, col_pred2, col_pred3 = st.columns(3)
    
    with col_pred1:
        # Prediction accuracy by risk level
        risk_categories = pd.cut(df_filtered['risk_score'], bins=[0, 30, 70, 100], 
                               labels=['Low', 'Medium', 'High'])
        accuracy_by_risk = df_filtered.groupby(risk_categories)['delivery_success'].mean() * 100
        
        st.markdown("**Prediction Accuracy:**")
        for risk_level, accuracy in accuracy_by_risk.items():
            icon = "🟢" if accuracy > 90 else "🟡" if accuracy > 80 else "🔴"
            st.write(f"{icon} **{risk_level} Risk**: {accuracy:.0f}%")
    
    with col_pred2:
        # False positive/negative analysis
        false_positives = len(df_filtered[(df_filtered['risk_score'] > risk_threshold) & 
                                         (df_filtered['delivery_success'] == True)])
        false_negatives = len(df_filtered[(df_filtered['risk_score'] <= risk_threshold) & 
                                        (df_filtered['delivery_success'] == False)])
        
        total_high_risk = len(df_filtered[df_filtered['risk_score'] > risk_threshold])
        total_low_risk = len(df_filtered[df_filtered['risk_score'] <= risk_threshold])
        
        fp_rate = (false_positives / total_high_risk * 100) if total_high_risk > 0 else 0
        fn_rate = (false_negatives / total_low_risk * 100) if total_low_risk > 0 else 0
        
        st.markdown("**Model Performance:**")
        st.write(f"• False Positive Rate: {fp_rate:.1f}%")
        st.write(f"• False Negative Rate: {fn_rate:.1f}%")
    
    with col_pred3:
        # Improvement recommendations
        st.markdown("**Optimization Tips:**")
        if fp_rate > 10:
            st.write("🔧 Consider raising risk threshold")
        if fn_rate > 5:
            st.write("🔧 Consider lowering risk threshold")
        if override_rate > 20:
            st.write("🔧 Review AI decision logic")
        else:
            st.write("✅ Model performance is optimal")

with tab4:
    st.header("📊 Operational Metrics")
    
    # Operational efficiency metrics
    col_ops1, col_ops2 = st.columns(2)
    
    with col_ops1:
        st.subheader("⏱️ Processing Efficiency")
        
        # Daily processing volume
        daily_volume = df_filtered.groupby(df_filtered['date'].dt.date).size().reset_index()
        daily_volume.columns = ['Date', 'Volume']
        
        fig_volume_trend = px.line(daily_volume, x='Date', y='Volume',
                                  title="Daily Processing Volume",
                                  markers=True)
        fig_volume_trend.update_layout(height=300)
        st.plotly_chart(fig_volume_trend, use_container_width=True)
        
        # Processing metrics
        avg_daily_volume = daily_volume['Volume'].mean()
        peak_volume = daily_volume['Volume'].max()
        
        st.metric("Avg Daily Volume", f"{avg_daily_volume:.0f}", "📦")
        st.metric("Peak Volume", f"{peak_volume}", "⚡")
    
    with col_ops2:
        st.subheader("🎯 Quality Metrics")
        
        # Quality trends
        daily_quality = df_filtered.groupby(df_filtered['date'].dt.date).agg({
            'delivery_success': 'mean',
            'is_overridden': 'mean'
        }).reset_index()
        daily_quality.columns = ['Date', 'Success_Rate', 'Override_Rate']
        
        fig_quality = go.Figure()
        fig_quality.add_trace(go.Scatter(x=daily_quality['Date'], y=daily_quality['Success_Rate']*100,
                                        mode='lines+markers', name='Success Rate (%)',
                                        line=dict(color='green')))
        fig_quality.add_trace(go.Scatter(x=daily_quality['Date'], y=daily_quality['Override_Rate']*100,
                                        mode='lines+markers', name='Override Rate (%)',
                                        line=dict(color='orange')))
        
        fig_quality.update_layout(title="Quality Metrics Trend", height=300,
                                 yaxis_title="Percentage")
        st.plotly_chart(fig_quality, use_container_width=True)
        
        # Quality benchmarks
        st.metric("Quality Score", "91.3%", "+2.1%")
        st.metric("SLA Compliance", "96.7%", "+1.4%")
    
    # Resource utilization
    st.subheader("🔧 System Resource Analysis")
    
    col_res1, col_res2, col_res3 = st.columns(3)
    
    with col_res1:
        st.markdown("**AI Engine Utilization:**")
        st.progress(0.87, "Risk Engine: 87%")
        st.progress(0.92, "Weather API: 92%") 
        st.progress(0.78, "Address Intel: 78%")
        st.progress(0.65, "Route Optimizer: 65%")
    
    with col_res2:
        st.markdown("**Processing Capacity:**")
        current_load = len(df_filtered) / 1000 * 100  # Simulate capacity
        st.metric("Current Load", f"{current_load:.0f}%", "📊")
        st.metric("Available Capacity", f"{100-current_load:.0f}%", "🔋")
        
        if current_load > 80:
            st.error("⚠️ High system load detected")
        elif current_load > 60:
            st.warning("💡 Consider capacity planning")
        else:
            st.success("✅ Optimal system performance")
    
    with col_res3:
        st.markdown("**Response Times:**")
        st.metric("Risk Analysis", "1.2s", "-0.3s")
        st.metric("Weather Lookup", "0.8s", "-0.1s")
        st.metric("Address Validation", "2.1s", "+0.4s")
        st.metric("Decision Engine", "0.5s", "→")
    
    # Performance insights
    st.markdown("---")
    st.subheader("💡 Performance Insights & Recommendations")
    
    col_insights1, col_insights2 = st.columns(2)
    
    with col_insights1:
        st.markdown("**🎯 Key Findings:**")
        
        # Generate insights based on data
        insights = []
        
        if success_rate > 95:
            insights.append("✅ Exceptional delivery performance maintained")
        elif success_rate > 90:
            insights.append("✅ Strong delivery performance")
        else:
            insights.append("⚠️ Delivery performance needs attention")
        
        if override_rate > 20:
            insights.append("🔧 High override rate suggests AI tuning needed")
        elif override_rate < 5:
            insights.append("🤖 AI decisions are highly trusted")
        else:
            insights.append("✅ Balanced AI-human collaboration")
        
        if avg_risk_score > 60:
            insights.append("⚠️ Risk levels are elevated - review factors")
        else:
            insights.append("✅ Risk management is effective")
        
        for insight in insights:
            st.write(f"• {insight}")
    
    with col_insights2:
        st.markdown("**🚀 Action Items:**")
        
        recommendations = [
            "📈 Monitor Zone-B performance closely",
            "🌧️ Improve weather prediction accuracy", 
            "🤖 Fine-tune risk threshold parameters",
            "📞 Enhance customer communication flow",
            "⚡ Optimize peak hour processing"
        ]
        
        for rec in recommendations:
            st.write(f"• {rec}")

# Export functionality
st.markdown("---")
col_export1, col_export2, col_export3 = st.columns([2, 1, 1])

with col_export1:
    st.markdown("**📊 Export Analytics Data**")

with col_export2:
    if st.button("📄 Export CSV", use_container_width=True):
        csv_data = df_filtered.to_csv(index=False)
        st.download_button("⬇️ Download CSV", csv_data, "lics_analytics.csv", "text/csv")

with col_export3:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()