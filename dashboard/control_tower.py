"""
Logistics Control Tower - Operations Dashboard

Purpose: Real-time decision cockpit for operations managers
Philosophy: Not just charts - ACTIONABLE intelligence display
Run: streamlit run dashboard/control_tower.py

Features:
- Real-time shipment visibility
- Risk awareness (heatmap)
- Weather alerts
- Address issue flags
- Vehicle feasibility warnings
- CO₂ vs Speed trade-off slider
- Decision support (not just reporting)
"""

import streamlit as st
import pandas as pd
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.risk_engine import risk_bucket
from features.carbon_tradeoff_engine import co2_speed_tradeoff, get_vehicle_emission_factor
from rules.vehicle_selector import hyper_local_vehicle_check, get_vehicle_capacity
from features.weather_impact import get_flood_risk
from rules.human_override import (
    apply_human_override, 
    is_locked, 
    get_override_history, 
    get_override_stats,
    OVERRIDE_REASONS
)
from rules.pre_dispatch_gate import pre_dispatch_decision
from execution.delivery_simulator import (
    get_tracking_history, 
    get_execution_stats,
    get_current_status
)
from analytics.end_of_day_logger import (
    get_eod_statistics,
    get_learning_insights,
    get_top_mismatch_patterns
)

# Page configuration
st.set_page_config(
    page_title="Logistics Control Tower",
    page_icon="🧭",
    layout="wide"
)

# Cache data loading for performance
@st.cache_data
def load_data():
    """Load all datasets and merge for dashboard."""
    try:
        shipments = pd.read_csv("Data/shipments.csv")
        addresses = pd.read_csv("Data/addresses.csv")
        weather = pd.read_csv("Data/weather_and_environment.csv")
        
        # Add risk bucket based on risk score
        shipments['risk_bucket'] = shipments['current_risk_score'].apply(risk_bucket)
        
        return shipments, addresses, weather
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.stop()

# Main dashboard
def main():
    # Header
    st.title("🧭 Logistics Control Tower")
    st.markdown("**Real-Time Decision Cockpit for Operations Managers**")
    st.markdown("---")
    
    # Load data
    shipments, addresses, weather = load_data()
    
    # Merge shipments with addresses for complete view
    shipments_full = shipments.merge(addresses, on='shipment_id', how='left')
    
    # ========== SECTION 1: GLOBAL FILTERS ==========
    st.sidebar.header("🔍 Filters")
    
    # City filter
    cities = ["All"] + sorted(shipments["destination_city"].unique().tolist())
    city_filter = st.sidebar.selectbox("Filter by City", cities)
    
    # Risk filter
    risk_filter = st.sidebar.selectbox(
        "Filter by Risk",
        ["All", "Low", "Medium", "High"]
    )
    
    # Apply filters
    filtered_shipments = shipments_full.copy()
    
    if city_filter != "All":
        filtered_shipments = filtered_shipments[
            filtered_shipments["destination_city"] == city_filter
        ]
    
    if risk_filter != "All":
        filtered_shipments = filtered_shipments[
            filtered_shipments["risk_bucket"] == risk_filter
        ]
    
    # ========== SECTION 2: KEY METRICS ==========
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Shipments",
            len(filtered_shipments),
            delta=None
        )
    
    with col2:
        high_risk_count = len(filtered_shipments[filtered_shipments['risk_bucket'] == 'High'])
        st.metric(
            "High Risk Shipments",
            high_risk_count,
            delta=f"{(high_risk_count/len(filtered_shipments)*100):.1f}%" if len(filtered_shipments) > 0 else "0%",
            delta_color="inverse"
        )
    
    with col3:
        low_address_count = len(filtered_shipments[filtered_shipments['address_confidence_score'] < 60])
        st.metric(
            "Low Address Confidence",
            low_address_count,
            delta=f"{(low_address_count/len(filtered_shipments)*100):.1f}%" if len(filtered_shipments) > 0 else "0%",
            delta_color="inverse"
        )
    
    with col4:
        avg_risk = filtered_shipments['current_risk_score'].mean() if len(filtered_shipments) > 0 else 0
        st.metric(
            "Average Risk Score",
            f"{avg_risk:.1f}",
            delta=None
        )
    
    st.markdown("---")
    
    # ========== SECTION 3: SHIPMENT LIST (CORE VIEW) ==========
    st.subheader("📦 Live Shipments")
    
    if len(filtered_shipments) > 0:
        # Display key columns
        display_df = filtered_shipments[[
            "shipment_id",
            "destination_city",
            "assigned_vehicle_type",
            "current_risk_score",
            "risk_bucket",
            "area_type",
            "address_confidence_score"
        ]].head(50)  # Show first 50 for performance
        
        st.dataframe(
            display_df,
            use_container_width=True,
            height=300
        )
        
        if len(filtered_shipments) > 50:
            st.info(f"Showing first 50 of {len(filtered_shipments)} shipments")
    else:
        st.warning("No shipments match the selected filters")
    
    st.markdown("---")
    
    # ========== SECTION 4: RISK HEATMAP ==========
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("🔥 Risk Heatmap by City")
        
        # Group by city and risk bucket
        risk_counts = filtered_shipments.groupby(
            ["destination_city", "risk_bucket"]
        ).size().unstack(fill_value=0)
        
        if not risk_counts.empty:
            st.bar_chart(risk_counts)
        else:
            st.info("No data for selected filters")
    
    # ========== SECTION 5: WEATHER ALERTS ==========
    with col_right:
        st.subheader("🌦️ Weather Alerts")
        
        # Aggregate weather by city
        weather_agg = weather.groupby('city').agg({
            'weather_severity': lambda x: x.mode()[0] if len(x.mode()) > 0 else x.iloc[0],
            'weather_impact_factor': 'mean'
        }).reset_index()
        
        # Filter for selected city
        if city_filter != "All":
            weather_display = weather_agg[weather_agg['city'] == city_filter]
        else:
            weather_display = weather_agg
        
        # High weather impact
        high_weather = weather_display[weather_display["weather_impact_factor"] > 60]
        
        if not high_weather.empty:
            st.warning(f"⚠️ High weather impact in {len(high_weather)} cities:")
            for _, row in high_weather.iterrows():
                st.write(f"**{row['city']}**: {row['weather_severity']} severity, Impact: {row['weather_impact_factor']:.0f}")
        else:
            st.success("✅ No major weather disruptions detected")
    
    st.markdown("---")
    
    # ========== SECTION 6: ADDRESS ISSUE FLAGS ==========
    st.subheader("📍 Address Intelligence Issues")
    
    # Low confidence addresses
    address_flags = filtered_shipments[filtered_shipments["address_confidence_score"] < 60]
    
    if not address_flags.empty:
        st.error(f"⚠️ {len(address_flags)} shipments with low-confidence addresses:")
        
        display_address = address_flags[[
            "shipment_id",
            "destination_city",
            "area_type",
            "road_accessibility",
            "address_confidence_score"
        ]].head(20)
        
        st.dataframe(display_address, use_container_width=True)
        
        if len(address_flags) > 20:
            st.info(f"Showing first 20 of {len(address_flags)} flagged addresses")
    else:
        st.success("✅ All addresses have acceptable confidence scores")
    
    st.markdown("---")
    
    # ========== SECTION 7: VEHICLE FEASIBILITY WARNINGS ==========
    st.subheader("🚚 Vehicle Feasibility Warnings")
    
    # Check vehicle feasibility for filtered shipments
    vehicle_issues = []
    
    for _, row in filtered_shipments.head(100).iterrows():  # Check first 100 for performance
        vehicle_capacity = get_vehicle_capacity(row["assigned_vehicle_type"])
        
        result = hyper_local_vehicle_check(
            area_type=row["area_type"],
            road_accessibility=row["road_accessibility"],
            assigned_vehicle=row["assigned_vehicle_type"],
            weight_kg=row["weight_kg"],
            volumetric_weight=row["volumetric_weight"],
            vehicle_capacity=vehicle_capacity
        )
        
        if result["vehicle_status"] == "REJECTED":
            vehicle_issues.append({
                "shipment_id": row["shipment_id"],
                "city": row["destination_city"],
                "assigned": row["assigned_vehicle_type"],
                "recommended": result["final_vehicle"],
                "reason": result["reason"]
            })
    
    if vehicle_issues:
        st.warning(f"⚠️ {len(vehicle_issues)} shipments with infeasible vehicle assignments:")
        
        issues_df = pd.DataFrame(vehicle_issues)
        st.dataframe(issues_df, use_container_width=True)
    else:
        st.success("✅ All vehicle assignments are feasible")
    
    st.markdown("---")
    
    # ========== SECTION 8: CO₂ vs SPEED TRADE-OFF ==========
    st.subheader("🌱 Sustainability: CO₂ vs Speed Trade-off")
    
    col_slider, col_results = st.columns([1, 2])
    
    with col_slider:
        st.write("**Select Vehicle Type:**")
        vehicle_type = st.radio(
            "Vehicle",
            ["Bike", "Van", "Truck"],
            index=1
        )
        
        emission_factor = get_vehicle_emission_factor(vehicle_type)
        st.info(f"Emission Factor: {emission_factor} g CO₂/km")
    
    with col_results:
        tradeoff = co2_speed_tradeoff(emission_factor)
        
        st.write("**Route Comparison:**")
        
        col_fast, col_green = st.columns(2)
        
        with col_fast:
            st.metric(
                "🚀 Fast Route",
                f"{tradeoff['fast_route']['co2_kg']} kg CO₂",
                delta=f"{tradeoff['fast_route']['eta_hours']} hours ETA"
            )
        
        with col_green:
            st.metric(
                "🌍 Green Route",
                f"{tradeoff['green_route']['co2_kg']} kg CO₂",
                delta=f"{tradeoff['green_route']['eta_hours']} hours ETA"
            )
        
        if tradeoff['co2_saved_kg'] > 0:
            st.success(f"✅ Green route saves {tradeoff['co2_saved_kg']} kg CO₂ ({(tradeoff['co2_saved_kg']/tradeoff['fast_route']['co2_kg']*100):.1f}%)")
        
        st.write(f"**Recommendation:** {tradeoff['recommendation']}")
    
    st.markdown("---")
    
    # ========== SECTION 9: HUMAN OVERRIDE SYSTEM ==========
    st.subheader("✋ Human Override (Decision Authority Layer)")
    
    st.info("🔒 **Philosophy**: AI must NEVER be the final authority. Managers can override AI decisions with accountability.")
    
    col_override_left, col_override_right = st.columns([1, 1])
    
    with col_override_left:
        st.write("**Apply Override:**")
        
        # Get shipments that have AI decisions
        available_shipments = filtered_shipments['shipment_id'].tolist()[:50]  # First 50 for performance
        
        if len(available_shipments) > 0:
            shipment_to_override = st.selectbox(
                "Select Shipment",
                available_shipments,
                key="override_shipment"
            )
            
            # Simulate getting AI decision from Step 9
            # In production, this would come from pre_dispatch_gate
            selected_shipment = filtered_shipments[filtered_shipments['shipment_id'] == shipment_to_override].iloc[0]
            risk_score = selected_shipment['current_risk_score']
            
            # Simple AI decision simulation based on risk
            if risk_score < 30:
                ai_decision_sim = "DISPATCH"
            elif risk_score < 60:
                ai_decision_sim = "DELAY"
            else:
                ai_decision_sim = "RESCHEDULE"
            
            st.write(f"**AI Recommendation:** `{ai_decision_sim}` (Risk: {risk_score:.1f})")
            
            # Check if already locked
            if is_locked(shipment_to_override):
                st.warning(f"🔒 This shipment is LOCKED by previous override")
            
            override_decision = st.selectbox(
                "Manager Decision",
                ["DISPATCH", "DELAY", "RESCHEDULE"],
                key="override_decision"
            )
            
            override_reason = st.selectbox(
                "Override Reason",
                OVERRIDE_REASONS,
                key="override_reason"
            )
            
            if st.button("Apply Override", key="apply_override_btn"):
                result = apply_human_override(
                    shipment_id=shipment_to_override,
                    ai_decision=ai_decision_sim,
                    override_decision=override_decision,
                    override_reason=override_reason
                )
                
                if result["status"] == "OVERRIDDEN":
                    st.success(f"✅ Override Applied: {result['final_decision']}")
                    st.info(f"🔒 Shipment locked. AI cannot re-evaluate.")
                elif result["status"] == "NO_OVERRIDE":
                    st.info(f"ℹ️ Manager agrees with AI. No override needed.")
                else:
                    st.error(f"❌ Error: {result.get('message', 'Unknown error')}")
        else:
            st.warning("No shipments available for override")
    
    with col_override_right:
        st.write("**Override Statistics:**")
        
        stats = get_override_stats()
        
        if stats["total_overrides"] > 0:
            col_stat1, col_stat2 = st.columns(2)
            with col_stat1:
                st.metric("Total Overrides", stats["total_overrides"])
            with col_stat2:
                st.metric("Most Common Reason", stats["most_common_reason"] or "N/A")
            
            st.write("**Override Distribution:**")
            st.write(f"- ✅ To DISPATCH: {stats['ai_to_dispatch']}")
            st.write(f"- ⏸️ To DELAY: {stats['ai_to_delay']}")
            st.write(f"- 🔄 To RESCHEDULE: {stats['ai_to_reschedule']}")
            
            if st.checkbox("Show Override History", key="show_history"):
                history = get_override_history()
                if not history.empty:
                    st.dataframe(
                        history[['shipment_id', 'ai_decision', 'override_decision', 
                                'override_reason', 'timestamp']].tail(10),
                        use_container_width=True
                    )
        else:
            st.info("No overrides recorded yet")
    
    st.markdown("---")
    
    # ========== SECTION 10: ACTIONABLE INSIGHTS ==========
    st.subheader("💡 Actionable Insights")
    
    insights = []
    
    # High risk concentration
    if city_filter == "All":
        city_risk = shipments_full.groupby('destination_city')['current_risk_score'].mean().sort_values(ascending=False)
        if len(city_risk) > 0:
            highest_risk_city = city_risk.index[0]
            insights.append(f"🔴 **{highest_risk_city}** has the highest average risk ({city_risk.iloc[0]:.1f}). Consider increased monitoring.")
    
    # Address issues
    if len(address_flags) > 0:
        insights.append(f"📍 **{len(address_flags)} shipments** need address clarification before dispatch. Trigger customer notification.")
    
    # Vehicle issues
    if len(vehicle_issues) > 0:
        insights.append(f"🚚 **{len(vehicle_issues)} shipments** have infeasible vehicle assignments. Reassign before dispatch.")
    
    # Weather impact
    if not high_weather.empty:
        insights.append(f"🌦️ **{len(high_weather)} cities** experiencing high weather impact. Consider delaying non-priority shipments.")
    
    if insights:
        for insight in insights:
            st.write(insight)
    else:
        st.success("✅ No critical issues detected. Operations running smoothly.")
    
    # ====================
    # 9. LIVE TRACKING EVENTS (Step 16)
    # ====================
    st.header("📍 Live Tracking Events")
    st.caption("Real-time execution monitoring and delivery status tracking")
    
    try:
        tracking_df = get_tracking_history()
        
        if len(tracking_df) > 0:
            # Execution statistics
            exec_stats = get_execution_stats()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Shipments", 
                    exec_stats['total_shipments'],
                    help="Shipments in execution phase"
                )
            
            with col2:
                st.metric(
                    "Delivered", 
                    exec_stats['delivered_count'],
                    delta=f"{exec_stats['delivery_rate']:.1f}%",
                    help="Successfully delivered shipments"
                )
            
            with col3:
                st.metric(
                    "Packing Delays", 
                    exec_stats['packing_delays'],
                    delta="Ops Alert" if exec_stats['packing_delays'] > 0 else "Normal",
                    delta_color="inverse",
                    help="Shipments with packing delays"
                )
            
            with col4:
                st.metric(
                    "Delivery Delays", 
                    exec_stats['delivery_delays'],
                    delta="Customer Alert" if exec_stats['delivery_delays'] > 0 else "Normal",
                    delta_color="inverse",
                    help="Shipments with delivery delays"
                )
            
            # Status distribution chart
            st.subheader("Status Distribution")
            status_dist = pd.DataFrame.from_dict(
                exec_stats['status_distribution'], 
                orient='index', 
                columns=['Count']
            ).sort_values('Count', ascending=False)
            
            st.bar_chart(status_dist)
            
            # Recent tracking events
            st.subheader("Recent Tracking Events (Last 50)")
            
            # Format timestamp for display
            display_df = tracking_df.tail(50).copy()
            display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Add status color coding
            def color_status(val):
                if 'DELAY' in val or 'FAILED' in val:
                    return 'background-color: #ffcccc'
                elif val == 'DELIVERED':
                    return 'background-color: #ccffcc'
                elif val in ['DISPATCHED', 'IN_TRANSIT', 'OUT_FOR_DELIVERY']:
                    return 'background-color: #ffffcc'
                return ''
            
            styled_df = display_df.style.applymap(color_status, subset=['status'])
            st.dataframe(styled_df, use_container_width=True, height=400)
            
            # Search specific shipment
            st.subheader("🔍 Track Specific Shipment")
            shipment_search = st.text_input("Enter Shipment ID", placeholder="e.g., SHP_EXEC_001")
            
            if shipment_search:
                shipment_history = get_tracking_history(shipment_search)
                
                if len(shipment_history) > 0:
                    current_status = get_current_status(shipment_search)
                    
                    st.success(f"**Current Status:** {current_status}")
                    
                    # Show complete journey
                    st.write("**Complete Journey:**")
                    journey_df = shipment_history[['status', 'timestamp', 'remarks']].copy()
                    journey_df['timestamp'] = pd.to_datetime(journey_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
                    st.dataframe(journey_df, use_container_width=True)
                else:
                    st.warning(f"No tracking events found for {shipment_search}")
        
        else:
            st.info("📦 No tracking events yet. Run delivery execution simulations to see live tracking.")
            st.caption("Use `test_delivery_execution.py` to generate sample tracking data.")
    
    except Exception as e:
        st.warning(f"⚠️ Tracking data unavailable: {str(e)}")
        st.caption("This is normal if Step 16 hasn't been executed yet.")
    
    # ====================
    # 10. LEARNING LOOP ANALYTICS (Step 17)
    # ====================
    st.header("🔄 Learning Loop Analytics")
    st.caption("Prediction vs Reality comparison for continuous improvement")
    
    try:
        eod_stats = get_eod_statistics()
        
        if "message" in eod_stats:
            st.info("📊 No learning data yet. Run end-of-day logging to see analytics.")
            st.caption("Execute deliveries (Step 16) and run EOD logging (Step 17) to generate data.")
        else:
            # Learning metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Prediction Accuracy",
                    f"{eod_stats['avg_prediction_accuracy']:.1f}%",
                    help="Average accuracy of AI predictions"
                )
            
            with col2:
                st.metric(
                    "Mismatch Rate",
                    f"{eod_stats['mismatch_rate']:.1f}%",
                    delta="Issue" if eod_stats['mismatch_rate'] > 15 else "Normal",
                    delta_color="inverse",
                    help="% of predictions that didn't match reality"
                )
            
            with col3:
                st.metric(
                    "Override Rate",
                    f"{eod_stats['override_rate']:.1f}%",
                    help="% of AI decisions overridden by humans"
                )
            
            with col4:
                st.metric(
                    "Success Rate",
                    f"{eod_stats['delivery_success_rate']:.1f}%",
                    help="% of deliveries completed successfully"
                )
            
            # Learning insights
            st.subheader("💡 Learning Insights")
            insights = get_learning_insights()
            
            for insight in insights:
                if "⚠️" in insight or "❌" in insight:
                    st.warning(insight)
                elif "✅" in insight:
                    st.success(insight)
                else:
                    st.info(insight)
            
            # Mismatch patterns
            st.subheader("🔍 Mismatch Patterns")
            patterns = get_top_mismatch_patterns()
            
            if len(patterns) > 0:
                st.write("**Common Prediction Errors:**")
                st.dataframe(patterns, use_container_width=True)
            else:
                st.success("✅ No significant mismatch patterns detected")
            
            # EOD summary table
            st.subheader("📋 Recent EOD Records (Last 20)")
            try:
                eod_df = pd.read_csv("logs/eod_summary.csv")
                recent_eod = eod_df.tail(20)
                
                # Format for display
                display_cols = [
                    "shipment_id", "log_date", "predicted_decision", 
                    "actual_status", "delay_minutes", "prediction_accuracy",
                    "mismatch_flag", "override_flag"
                ]
                
                available_cols = [col for col in display_cols if col in recent_eod.columns]
                st.dataframe(recent_eod[available_cols], use_container_width=True)
            except:
                st.info("No EOD records available yet")
    
    except Exception as e:
        st.warning(f"⚠️ Learning analytics unavailable: {str(e)}")
        st.caption("This is normal if Step 17 hasn't been executed yet.")
    
    # Footer
    st.markdown("---")
    st.caption("🧭 Logistics Control Tower | Real-Time Decision Support System")

if __name__ == "__main__":
    main()
