# app.py - Unified Control Tower UI for LICS
# Light Theme Professional Design

import streamlit as st
import pandas as pd
from datetime import datetime
from config import APP_TITLE, RISK_UI, DATA_PATH

# Import all engines
from engines.input_validation_engine import validate_and_normalize
from engines.area_feasibility_engine import evaluate_area_feasibility
from engines.weather_impact_engine import get_weather_risk
from engines.vehicle_feasibility_engine import evaluate_vehicle_feasibility
from engines.priority_classification_engine import classify_priority
from engines.risk_scoring_engine import compute_risk_score
from engines.delay_explanation_engine import generate_delay_explanation
from engines.manager_decision_engine import record_manager_decision
from engines.supervisor_analytics_engine import load_governance_metrics, load_override_records
from utils.id_generator import generate_parcel_id


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title=APP_TITLE,
    layout="wide",
    initial_sidebar_state="expanded"
)


# =============================================================================
# CUSTOM CSS - LIGHT THEME ONLY
# =============================================================================

st.markdown("""
<style>
    /* Global Light Theme */
    :root {
        --bg-color: #FAFAFA;
        --card-bg: #FFFFFF;
        --text-primary: #2E2E2E;
        --text-secondary: #6B7280;
        --border-color: #E5E7EB;
        --shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    
    /* Remove default padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Card styling */
    .light-card {
        background: var(--card-bg);
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow);
        margin-bottom: 1rem;
    }
    
    /* Section headers */
    .section-header {
        color: var(--text-primary);
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--border-color);
    }
    
    /* Risk badges - soft colors */
    .risk-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .risk-low {
        background: #D1FAE5;
        color: #065F46;
    }
    
    .risk-medium {
        background: #FEF3C7;
        color: #92400E;
    }
    
    .risk-high {
        background: #FEE2E2;
        color: #991B1B;
    }
    
    /* Info tiles */
    .info-tile {
        background: #F9FAFB;
        padding: 1rem;
        border-radius: 6px;
        border-left: 3px solid #60A5FA;
        margin-bottom: 0.5rem;
    }
    
    /* Metric card */
    .metric-card {
        background: var(--card-bg);
        padding: 1.25rem;
        border-radius: 8px;
        border: 1px solid var(--border-color);
        text-align: center;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-primary);
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: var(--text-secondary);
        margin-top: 0.25rem;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: #F5F7F9;
        border-right: 1px solid #E5E7EB;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 2rem;
    }
    
    /* Sidebar header */
    .sidebar-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 8px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .sidebar-title {
        font-size: 1.25rem;
        font-weight: 700;
        margin: 0;
        color: white;
    }
    
    .sidebar-subtitle {
        font-size: 0.8rem;
        margin-top: 0.25rem;
        opacity: 0.9;
        color: white;
    }
    
    /* Sidebar info box */
    .sidebar-info {
        background: #EFF6FF;
        border-left: 3px solid #3B82F6;
        padding: 1rem;
        border-radius: 6px;
        margin: 1rem 0;
        font-size: 0.85rem;
        color: #1E40AF;
    }
    
    /* Sidebar help section */
    .sidebar-help {
        background: #FEFCE8;
        border-left: 3px solid #EAB308;
        padding: 0.875rem;
        border-radius: 6px;
        margin: 1rem 0;
        font-size: 0.8rem;
        color: #854D0E;
    }
    
    /* Radio button styling */
    .stRadio > label {
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
    }
    
    .stRadio > div {
        gap: 0.75rem;
    }
    
    /* Button styling */
    .stButton>button {
        border-radius: 6px;
        font-weight: 500;
    }
    
    /* Form elements */
    .stTextInput>div>div>input,
    .stNumberInput>div>div>input,
    .stSelectbox>div>div>select {
        border-radius: 6px;
        border: 1px solid var(--border-color);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: #F9FAFB;
        border-radius: 6px;
        font-weight: 500;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Table styling */
    .dataframe {
        font-size: 0.9rem;
    }
    
    /* Governance hint */
    .governance-hint {
        font-size: 0.8rem;
        color: var(--text-secondary);
        font-style: italic;
        margin-top: 0.5rem;
    }
    
    /* Intelligence overview cards */
    .engine-card {
        background: #FFFFFF;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #E5E7EB;
        margin-bottom: 0.75rem;
        border-left: 3px solid #8B5CF6;
    }
    
    .engine-header {
        font-weight: 600;
        color: #2E2E2E;
        font-size: 1rem;
        margin-bottom: 0.5rem;
    }
    
    .engine-meta {
        font-size: 0.8rem;
        color: #6B7280;
        margin-bottom: 0.25rem;
    }
    
    /* Transparency badge */
    .transparency-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 600;
        background: #DBEAFE;
        color: #1E40AF;
        margin-right: 0.5rem;
    }
    
    /* Composition bar */
    .composition-bar {
        height: 40px;
        border-radius: 8px;
        overflow: hidden;
        display: flex;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .composition-segment {
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.85rem;
        font-weight: 600;
        color: white;
        transition: all 0.3s;
    }
    
    /* Disclaimer box */
    .disclaimer-box {
        background: #FEF3C7;
        border-left: 4px solid #F59E0B;
        padding: 1.25rem;
        border-radius: 6px;
        margin: 1.5rem 0;
    }
    
    .disclaimer-title {
        font-weight: 700;
        color: #92400E;
        margin-bottom: 0.5rem;
    }
    
    .disclaimer-text {
        color: #78350F;
        font-size: 0.9rem;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# SIDEBAR NAVIGATION
# =============================================================================

with st.sidebar:
    # Header with gradient
    st.markdown("""
    <div class="sidebar-header">
        <div class="sidebar-title">🚚 LICS Control Tower</div>
        <div class="sidebar-subtitle">AI-Assisted, Human-Controlled Logistics</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation
    st.markdown("**🧭 Select Your Role**")
    active_view = st.radio(
        "Navigation",
        ["📦 Seller View", "🧑‍💼 Manager View", "📊 Supervisor View", "🧠 Intelligence & Transparency"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # Contextual help based on active view
    if active_view == "📦 Seller View":
        st.markdown("""
        <div class="sidebar-info">
            <strong>📦 Seller View</strong><br>
            Submit shipment details and receive AI-powered risk analysis before dispatch.
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="sidebar-help">
            <strong>💡 Quick Tip</strong><br>
            Fill in all shipment details accurately for best risk assessment.
        </div>
        """, unsafe_allow_html=True)
    
    elif active_view == "🧑‍💼 Manager View":
        st.markdown("""
        <div class="sidebar-info">
            <strong>🧑‍💼 Manager View</strong><br>
            Review AI recommendations and make final decisions with full audit trail.
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="sidebar-help">
            <strong>⚖️ Governance Note</strong><br>
            All overrides require justification and are visible to supervisors.
        </div>
        """, unsafe_allow_html=True)
    
    elif active_view == "📊 Supervisor View":
        st.markdown("""
        <div class="sidebar-info">
            <strong>📊 Supervisor View</strong><br>
            Monitor decisions, track overrides, and ensure compliance across all operations.
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="sidebar-help">
            <strong>🔍 Oversight Focus</strong><br>
            Pay attention to override rates and high-risk acceptances.
        </div>
        """, unsafe_allow_html=True)
    
    else:  # Intelligence & Transparency View
        st.markdown("""
        <div class="sidebar-info">
            <strong>🧠 Intelligence & Transparency</strong><br>
            Understand the models, data, and trends behind risk intelligence.
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="sidebar-help">
            <strong>🔍 Transparency Goal</strong><br>
            This section is read-only and purely informational.
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # System status indicator
    st.markdown("""
    <div style="text-align: center; padding: 0.75rem; background: #D1FAE5; border-radius: 6px; margin: 1rem 0;">
        <div style="font-size: 0.75rem; color: #065F46; font-weight: 600;">
            ✅ SYSTEM ONLINE
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Footer
    st.caption("© 2026 LICS System v2.0")
    st.caption("Built for Indian Logistics")
    st.caption("Made by IleshDevX with 🧡 & Python") 

# =============================================================================
# SELLER VIEW - INPUT + AI INTELLIGENCE
# =============================================================================

if active_view == "📦 Seller View":
    
    st.title("Pre-Dispatch Intelligence")
    st.caption("Submit shipment details for AI-powered risk analysis")
    
    st.markdown("---")
    
    # SECTION 1: SHIPMENT INPUT FORM
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="section-header">📦 Shipment Basics</div>', unsafe_allow_html=True)
        
        # Auto-generate Parcel ID
        if "current_parcel_id" not in st.session_state:
            st.session_state["current_parcel_id"] = generate_parcel_id()
        
        parcel_id_display = st.text_input("Parcel ID", value=st.session_state["current_parcel_id"], disabled=True)
        
        col_w, col_d = st.columns(2)
        with col_w:
            weight = st.number_input("Weight (kg)", min_value=0.0, step=0.1, help="Shipment weight")
        with col_d:
            distance = st.number_input("Distance (km)", min_value=0.0, step=1.0, help="Route distance")
        
        col_l, col_wi, col_h = st.columns(3)
        with col_l:
            length = st.number_input("Length (cm)", min_value=0.0, step=1.0)
        with col_wi:
            width = st.number_input("Width (cm)", min_value=0.0, step=1.0)
        with col_h:
            height = st.number_input("Height (cm)", min_value=0.0, step=1.0)
        
        st.markdown('<div class="section-header">📍 Route Details</div>', unsafe_allow_html=True)
        
        col_src, col_dest = st.columns(2)
        with col_src:
            source_city = st.text_input("Source City", placeholder="e.g., Mumbai")
        with col_dest:
            destination_city = st.text_input("Destination City", placeholder="e.g., Delhi")
        
        st.markdown('<div class="section-header">🏙️ Delivery Context</div>', unsafe_allow_html=True)
        
        col_area, col_addr = st.columns(2)
        with col_area:
            area_type = st.selectbox("Area Type", ["URBAN", "RURAL", "OLD_CITY"])
        with col_addr:
            address_type = st.selectbox("Address Type", ["RESIDENTIAL", "COMMERCIAL"])
        
        st.markdown('<div class="section-header">⏱️ Time Constraints</div>', unsafe_allow_html=True)
        
        col_date, col_urg = st.columns(2)
        with col_date:
            delivery_date = st.date_input("Delivery Date")
        with col_urg:
            urgency = st.selectbox("Urgency", ["NORMAL", "EXPRESS"])
        
        st.markdown("")
        analyze_button = st.button("🚀 Run Pre-Dispatch Analysis", type="primary", use_container_width=True)
    
    with col2:
        st.info("**How it works:**\n\n1. Enter shipment details\n2. AI analyzes risks\n3. Get recommendations\n4. Manager reviews\n5. Decision logged")
    
    # SECTION 2: AI PRE-DISPATCH RECOMMENDATION
    if analyze_button:
        input_data = {
            "weight_kg": weight,
            "length_cm": length,
            "width_cm": width,
            "height_cm": height,
            "distance_km": distance,
            "source_city": source_city,
            "destination_city": destination_city,
            "area_type": area_type,
            "address_type": address_type,
            "delivery_date": delivery_date,
            "delivery_urgency": urgency
        }
        
        success, result = validate_and_normalize(input_data)
        
        if not success:
            st.error("❌ **Validation Failed**")
            for err in result:
                st.write(f"• {err}")
        else:
            result["parcel_id"] = st.session_state["current_parcel_id"]
            
            with st.spinner("Analyzing shipment..."):
                # Run all engines
                feasibility = evaluate_area_feasibility(result)
                weather_risk = get_weather_risk(result["destination_city"])
                vehicle_result = evaluate_vehicle_feasibility(result)
                priority_result = classify_priority(result)
                
                risk_result = compute_risk_score(
                    shipment=result,
                    area_result=feasibility,
                    weather_result=weather_risk,
                    vehicle_result=vehicle_result,
                    priority_result=priority_result
                )
                
                explanation = generate_delay_explanation(
                    risk_result=risk_result,
                    area_result=feasibility,
                    weather_result=weather_risk,
                    vehicle_result=vehicle_result,
                    priority_result=priority_result
                )
            
            # Store in session
            st.session_state["analysis"] = {
                "parcel_id": st.session_state["current_parcel_id"],
                "shipment": result,
                "feasibility": feasibility,
                "weather": weather_risk,
                "vehicle": vehicle_result,
                "priority": priority_result,
                "risk": risk_result,
                "explanation": explanation
            }
            
            # Generate new ID for next submission
            st.session_state["current_parcel_id"] = generate_parcel_id()
            
            st.markdown("---")
            st.markdown("## 🧭 AI Pre-Dispatch Recommendation")
            
            # Summary Card
            risk_band = risk_result["risk_band"]
            risk_score = risk_result["risk_score"]
            risk_class = f"risk-{risk_band.lower()}"
            
            col_summary1, col_summary2 = st.columns([3, 1])
            
            with col_summary1:
                st.markdown(f"""
                <div class="light-card">
                    <div style="display: flex; align-items: center; gap: 1rem;">
                        <span class="risk-badge {risk_class}">{RISK_UI[risk_band]['emoji']} {RISK_UI[risk_band]['label']}</span>
                        <div>
                            <div style="font-size: 1.5rem; font-weight: 700; color: var(--text-primary);">{risk_score}/100</div>
                            <div style="font-size: 0.875rem; color: var(--text-secondary);">Risk Score</div>
                        </div>
                    </div>
                    <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--border-color);">
                        <strong>Parcel ID:</strong> {result["parcel_id"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_summary2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{priority_result['priority']}</div>
                    <div class="metric-label">Priority</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Explanation-First Layout
            st.markdown("### Why This Matters")
            st.markdown(f"**{explanation['summary']}**")
            
            st.markdown("### Top Risk Factors")
            for idx, reason in enumerate(explanation["top_reasons"][:5], start=1):
                st.markdown(f"**{idx}.** {reason}")
            
            # Progressive Disclosure
            st.markdown("---")
            st.markdown("### Technical Details (Optional)")
            
            with st.expander("🔍 Area Feasibility Analysis"):
                st.write(f"**Status:** {feasibility.get('feasible', 'N/A')}")
                st.write(f"**Reason:** {feasibility.get('reason', 'N/A')}")
                if feasibility.get('delay_minutes', 0) > 0:
                    st.write(f"**Expected Delay:** {feasibility['delay_minutes']} minutes")
            
            with st.expander("🌤️ Weather Impact"):
                st.write(f"**Condition:** {weather_risk.get('weather_condition', 'N/A')}")
                st.write(f"**Severity:** {weather_risk.get('severity', 'N/A')}")
                st.write(f"**Risk Adjustment:** +{weather_risk.get('risk_adjustment', 0)} points")
                st.write(f"**Impact:** {weather_risk.get('reason', 'N/A')}")
            
            with st.expander("🚚 Vehicle Feasibility"):
                st.write(f"**Status:** {vehicle_result.get('vehicle_status', 'N/A')}")
                st.write(f"**Selected Vehicle:** {vehicle_result.get('selected_vehicle', 'N/A')}")
                st.write(f"**Suggested Vehicle:** {vehicle_result.get('suggested_vehicle', 'N/A')}")
                st.write(f"**Rationale:** {vehicle_result.get('reason', 'N/A')}")
            
            with st.expander("🎯 Priority Classification Logic"):
                st.write(f"**Priority:** {priority_result.get('priority', 'N/A')}")
                st.write(f"**Reason:** {priority_result.get('reason', 'N/A')}")
            
            with st.expander("📊 Risk Score Breakdown"):
                st.json(risk_result)
            
            with st.expander("🔧 Raw JSON (Advanced)"):
                st.json({
                    "area": feasibility,
                    "weather": weather_risk,
                    "vehicle": vehicle_result,
                    "priority": priority_result,
                    "risk": risk_result
                })
            
            st.success("✅ Analysis complete. Switch to **Manager View** to take action.")


# =============================================================================
# MANAGER VIEW - DECISION DASHBOARD
# =============================================================================

elif active_view == "🧑‍💼 Manager View":
    
    st.title("Manager Decision Dashboard")
    st.caption("Review AI recommendations and make informed decisions")
    
    st.markdown("---")
    
    if "analysis" not in st.session_state:
        st.warning("⚠️ No analysis available. Please run analysis in **Seller View** first.")
    else:
        analysis = st.session_state["analysis"]
        risk = analysis["risk"]
        explanation = analysis["explanation"]
        shipment = analysis["shipment"]
        
        # SECTION 1: SHIPMENT SNAPSHOT
        st.markdown("### 📋 Shipment Snapshot")
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            st.markdown(f"""
            <div class="info-tile">
                <div style="font-size: 0.75rem; color: var(--text-secondary);">Parcel ID</div>
                <div style="font-weight: 600; color: var(--text-primary);">{analysis["parcel_id"]}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="info-tile">
                <div style="font-size: 0.75rem; color: var(--text-secondary);">Route</div>
                <div style="font-weight: 600; color: var(--text-primary);">{shipment['source_city']} → {shipment['destination_city']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            risk_class = f"risk-{risk['risk_band'].lower()}"
            st.markdown(f"""
            <div class="info-tile">
                <div style="font-size: 0.75rem; color: var(--text-secondary);">Risk Band</div>
                <div><span class="risk-badge {risk_class}">{risk['risk_band']}</span></div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="info-tile">
                <div style="font-size: 0.75rem; color: var(--text-secondary);">Urgency</div>
                <div style="font-weight: 600; color: var(--text-primary);">{shipment['delivery_urgency']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            st.markdown(f"""
            <div class="info-tile">
                <div style="font-size: 0.75rem; color: var(--text-secondary);">Area Type</div>
                <div style="font-weight: 600; color: var(--text-primary);">{shipment['area_type']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col6:
            st.markdown(f"""
            <div class="info-tile">
                <div style="font-size: 0.75rem; color: var(--text-secondary);">Vehicle</div>
                <div style="font-weight: 600; color: var(--text-primary);">{analysis['vehicle'].get('selected_vehicle', 'N/A')}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # SECTION 2: AI INSIGHT PANEL (BEFORE DECISION)
        st.markdown("### 🧠 AI Risk Assessment")
        
        risk_band = risk["risk_band"]
        risk_score = risk["risk_score"]
        risk_class = f"risk-{risk_band.lower()}"
        
        st.markdown(f"""
        <div class="light-card" style="background: #FEF3C7; border-left: 4px solid #F59E0B;">
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                <span class="risk-badge {risk_class}">{RISK_UI[risk_band]['emoji']} {RISK_UI[risk_band]['label']}</span>
                <div>
                    <div style="font-size: 1.75rem; font-weight: 700;">{risk_score}/100</div>
                    <div style="font-size: 0.875rem; color: var(--text-secondary);">AI Risk Score</div>
                </div>
            </div>
            <div style="padding: 1rem; background: white; border-radius: 6px;">
                <strong>AI Explanation:</strong>
                <p style="margin: 0.5rem 0 0 0; color: var(--text-primary);">{explanation['summary']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("**Key Contributing Factors:**")
        for idx, reason in enumerate(explanation["top_reasons"][:3], start=1):
            st.markdown(f"**{idx}.** {reason}")
        
        st.markdown("---")
        
        # SECTION 3: MANAGER DECISION PANEL
        st.markdown("### ✅ Manager Decision")
        
        col_dec1, col_dec2 = st.columns([2, 1])
        
        with col_dec1:
            decision = st.radio(
                "Select Decision",
                ["ACCEPT", "HOLD", "OVERRIDE"],
                help="Choose action based on AI recommendation and business context"
            )
            
            override_reason = ""
            
            if decision == "OVERRIDE":
                st.warning("⚠️ **Override Mode Active**")
                override_reason = st.text_area(
                    "Override Justification (Required)",
                    placeholder="Explain why you are overriding the AI recommendation...",
                    help="This will be logged and visible to supervisors",
                    height=100
                )
                st.markdown('<div class="governance-hint">⚖️ All overrides are logged and visible to supervisors for governance review.</div>', unsafe_allow_html=True)
            
            submit_button = st.button("📝 Submit Decision", type="primary", use_container_width=True)
        
        with col_dec2:
            st.info("""
            **Decision Guide:**
            
            **ACCEPT** - Proceed with dispatch
            
            **HOLD** - Delay for further review
            
            **OVERRIDE** - Proceed against AI advice (requires justification)
            """)
        
        if submit_button:
            if decision == "OVERRIDE" and not override_reason.strip():
                st.error("❌ Override justification is mandatory for governance compliance.")
            else:
                record_manager_decision(
                    parcel_id=analysis["parcel_id"],
                    decision=decision,
                    risk_band=risk["risk_band"],
                    override_reason=override_reason
                )
                
                st.success(f"✅ Decision **{decision}** recorded successfully for Parcel ID: {analysis['parcel_id']}")
                
                if decision == "OVERRIDE":
                    st.warning("⚠️ Override logged. Supervisor will be notified.")
                
                # Clear analysis after decision
                del st.session_state["analysis"]
                st.balloons()


# =============================================================================
# SUPERVISOR VIEW - GOVERNANCE DASHBOARD
# =============================================================================

elif active_view == "📊 Supervisor View":
    
    st.title("Supervisor Governance Dashboard")
    st.caption("Monitor decisions, track overrides, and ensure system compliance")
    
    st.markdown("---")
    
    metrics = load_governance_metrics()
    
    # SECTION 1: GOVERNANCE METRICS
    st.markdown("### 📊 Key Governance Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['total_decisions']}</div>
            <div class="metric-label">Total Shipments Reviewed</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        override_rate = metrics['override_rate']
        override_color = "#991B1B" if override_rate > 15 else "#92400E" if override_rate > 5 else "#065F46"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: {override_color};">{override_rate}%</div>
            <div class="metric-label">Override Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        high_risk_accepts = metrics['high_risk_accepts']
        high_risk_color = "#991B1B" if high_risk_accepts > 10 else "#92400E" if high_risk_accepts > 5 else "#065F46"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: {high_risk_color};">{high_risk_accepts}</div>
            <div class="metric-label">High-Risk Acceptances</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        decision_counts = metrics['decision_counts']
        disagree_count = decision_counts.get('OVERRIDE', 0)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{disagree_count}</div>
            <div class="metric-label">AI Disagreements</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # SECTION 2: VISUAL ANALYTICS
    st.markdown("### 📈 Decision Analytics")
    
    if metrics['total_decisions'] > 0:
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.markdown("**Decision Type Distribution**")
            decision_df = pd.DataFrame(
                list(metrics['decision_counts'].items()),
                columns=['Decision', 'Count']
            )
            st.bar_chart(decision_df.set_index('Decision'), color="#60A5FA")
        
        with col_chart2:
            st.markdown("**Risk Band Distribution**")
            risk_df = pd.DataFrame(
                list(metrics['risk_distribution'].items()),
                columns=['Risk Band', 'Count']
            )
            st.bar_chart(risk_df.set_index('Risk Band'), color="#F59E0B")
    else:
        st.info("No decision data available yet.")
    
    st.markdown("---")
    
    # SECTION 3: OVERRIDDEN SHIPMENTS TABLE
    st.markdown("### 🔴 Overridden Shipments (Audit Trail)")
    
    overrides_df = load_override_records()
    
    if overrides_df.empty:
        st.success("✅ No AI overrides recorded. System recommendations are being followed.")
    else:
        st.warning(f"⚠️ **{len(overrides_df)} override(s) detected** – Review for compliance")
        
        display_df = overrides_df[[
            "parcel_id",
            "timestamp",
            "risk_band",
            "override_reason"
        ]].copy()
        
        display_df.columns = ["Parcel ID", "Timestamp", "Risk Band", "Override Reason"]
        display_df["Status"] = "🔴 OVERRIDDEN"
        
        # Format timestamp
        if "Timestamp" in display_df.columns:
            display_df["Timestamp"] = pd.to_datetime(display_df["Timestamp"]).dt.strftime("%Y-%m-%d %H:%M")
        
        st.dataframe(
            display_df,
            use_container_width=True,
            height=300
        )
    
    st.markdown("---")
    
    # SECTION 4: MODEL & DATA TRANSPARENCY
    st.markdown("### 🔍 Model & Data Transparency")
    
    col_trans1, col_trans2 = st.columns(2)
    
    with col_trans1:
        st.markdown("""
        <div class="light-card">
            <h4>Model Information</h4>
            <ul>
                <li><strong>Type:</strong> Hybrid (Rule-Based + ML)</li>
                <li><strong>ML Algorithm:</strong> Decision Tree Classifier</li>
                <li><strong>Training Data:</strong> Historical shipment records</li>
                <li><strong>Last Updated:</strong> January 2026</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col_trans2:
        st.markdown("""
        <div class="light-card">
            <h4>Feature Set</h4>
            <ul>
                <li>Shipment weight & dimensions</li>
                <li>Route distance & area type</li>
                <li>Weather conditions (live API)</li>
                <li>Vehicle availability</li>
                <li>Delivery urgency</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Additional Details (Expandable)
    with st.expander("📋 Detailed Decision Breakdown"):
        st.json(metrics['decision_counts'])
    
    with st.expander("📊 Risk Band Distribution Details"):
        st.json(metrics['risk_distribution'])
    
    st.markdown("---")
    st.caption("💡 This dashboard ensures transparency, accountability, and governance compliance.")


# =============================================================================
# INTELLIGENCE & TRANSPARENCY VIEW - MODEL & TREND ANALYSIS
# =============================================================================

else:  # Intelligence & Transparency View
    
    st.title("Intelligence & Model Transparency")
    st.caption("Understand the models, data, and trends behind LICS risk intelligence")
    
    st.markdown("---")
    
    # SECTION 1: SYSTEM INTELLIGENCE OVERVIEW
    st.markdown("### 🧠 System Intelligence Overview")
    st.markdown("LICS uses multiple intelligence engines to assess pre-dispatch risk. Each engine plays a specific role:")
    
    col_eng1, col_eng2 = st.columns(2)
    
    with col_eng1:
        st.markdown("""
        <div class="engine-card">
            <div class="engine-header">🔍 Input Validation Engine</div>
            <div class="engine-meta"><span class="transparency-badge">Rule-Based</span></div>
            <div class="engine-meta"><strong>Role:</strong> Data quality assurance</div>
            <div class="engine-meta"><strong>Contribution:</strong> Blocks invalid shipments</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="engine-card">
            <div class="engine-header">🌤️ Weather Impact Engine</div>
            <div class="engine-meta"><span class="transparency-badge">Rule-Based + Live API</span></div>
            <div class="engine-meta"><strong>Role:</strong> Real-time weather risk assessment</div>
            <div class="engine-meta"><strong>Contribution:</strong> Risk adjustment (+0 to +30)</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="engine-card">
            <div class="engine-header">🎯 Priority Classification Engine</div>
            <div class="engine-meta"><span class="transparency-badge">ML-Assisted</span></div>
            <div class="engine-meta"><strong>Role:</strong> Urgency detection</div>
            <div class="engine-meta"><strong>Contribution:</strong> Priority signal (HIGH/MEDIUM/LOW)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_eng2:
        st.markdown("""
        <div class="engine-card">
            <div class="engine-header">🏙️ Area Feasibility Engine</div>
            <div class="engine-meta"><span class="transparency-badge">Rule-Based</span></div>
            <div class="engine-meta"><strong>Role:</strong> Last-mile complexity assessment</div>
            <div class="engine-meta"><strong>Contribution:</strong> Delay estimation & risk modifier</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="engine-card">
            <div class="engine-header">🚚 Vehicle Feasibility Engine</div>
            <div class="engine-meta"><span class="transparency-badge">Rule-Based</span></div>
            <div class="engine-meta"><strong>Role:</strong> Vehicle-route compatibility</div>
            <div class="engine-meta"><strong>Contribution:</strong> Feasibility check & vehicle recommendation</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="engine-card">
            <div class="engine-header">📊 Risk Scoring Engine</div>
            <div class="engine-meta"><span class="transparency-badge">Composite Algorithm</span></div>
            <div class="engine-meta"><strong>Role:</strong> Final risk score calculation</div>
            <div class="engine-meta"><strong>Contribution:</strong> Combines all signals into 0-100 score</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # SECTION 2: DATA USED FOR RISK PREDICTION
    st.markdown("### 📁 Data Used for Risk Prediction")
    
    col_data1, col_data2 = st.columns(2)
    
    with col_data1:
        st.markdown("""
        <div class="light-card">
            <h4>Input Data Categories</h4>
            <ul>
                <li><strong>Shipment Attributes</strong> – Weight, dimensions, volume</li>
                <li><strong>Route Information</strong> – Source, destination, distance</li>
                <li><strong>Area Characteristics</strong> – Urban, rural, old city complexity</li>
                <li><strong>Weather Signals</strong> – Live weather conditions (API)</li>
                <li><strong>Operational Constraints</strong> – Vehicle availability, urgency</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col_data2:
        st.markdown("""
        <div class="light-card">
            <h4>Data Source Type</h4>
            <ul>
                <li><strong>User Input</strong> – Seller-provided shipment details</li>
                <li><strong>Static CSV</strong> – Area feasibility rules, vehicle master</li>
                <li><strong>External API</strong> – WeatherAPI.com (live data)</li>
                <li><strong>Derived Rules</strong> – Traffic profiles, risk thresholds</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.info("""
    **🔒 Privacy & Data Ethics**  
    • No personal customer data is collected or stored  
    • No customer profiling or tracking  
    • No learning from individual manager decisions  
    • Operational metrics only, fully anonymized
    """)
    
    st.markdown("---")
    
    # SECTION 3: MODEL & RULE COMPOSITION
    st.markdown("### ⚖️ Model & Rule Composition")
    st.markdown("LICS uses a **hybrid approach** that balances rule-based logic with machine learning signals:")
    
    # Composition bar
    st.markdown("""
    <div class="composition-bar">
        <div class="composition-segment" style="width: 70%; background: #3B82F6;">
            Rule-Based Logic (70%)
        </div>
        <div class="composition-segment" style="width: 30%; background: #8B5CF6;">
            ML Signal (30%)
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_comp1, col_comp2, col_comp3 = st.columns(3)
    
    with col_comp1:
        st.markdown("""
        <div class="metric-card" style="border-left: 3px solid #3B82F6;">
            <div class="metric-value" style="color: #3B82F6;">70%</div>
            <div class="metric-label">Rule-Based Logic</div>
            <div style="font-size: 0.75rem; color: #6B7280; margin-top: 0.5rem;">
                Area, weather, vehicle feasibility rules
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_comp2:
        st.markdown("""
        <div class="metric-card" style="border-left: 3px solid #8B5CF6;">
            <div class="metric-value" style="color: #8B5CF6;">30%</div>
            <div class="metric-label">ML Proxy Signal</div>
            <div style="font-size: 0.75rem; color: #6B7280; margin-top: 0.5rem;">
                Priority classification (urgency detection)
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_comp3:
        st.markdown("""
        <div class="metric-card" style="border-left: 3px solid #10B981;">
            <div class="metric-value" style="color: #10B981;">0%</div>
            <div class="metric-label">Explanation Layer</div>
            <div style="font-size: 0.75rem; color: #6B7280; margin-top: 0.5rem;">
                Interpretation only, non-scoring
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.success("✅ **ML does not dominate decisions.** Rule-based logic forms the primary foundation of risk assessment.")
    
    st.markdown("---")
    
    # SECTION 4: MODEL EFFECTIVENESS ON RISK MEASUREMENT
    st.markdown("### 📈 Model Effectiveness on Risk Measurement")
    st.markdown("These behavioral indicators show how the intelligence system is performing:")
    
    # Load historical data for analysis
    try:
        decisions_df = pd.read_csv(f"{DATA_PATH}/manager_decisions.csv")
        
        if not decisions_df.empty:
            # Metrics
            col_eff1, col_eff2, col_eff3, col_eff4 = st.columns(4)
            
            with col_eff1:
                avg_risk_band_dist = decisions_df['risk_band'].value_counts()
                total = len(decisions_df)
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{total}</div>
                    <div class="metric-label">Total Assessments</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_eff2:
                low_pct = (avg_risk_band_dist.get('LOW', 0) / total * 100) if total > 0 else 0
                st.markdown(f"""
                <div class="metric-card" style="border-left: 3px solid #10B981;">
                    <div class="metric-value" style="color: #10B981;">{low_pct:.1f}%</div>
                    <div class="metric-label">Low Risk Rate</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_eff3:
                med_pct = (avg_risk_band_dist.get('MEDIUM', 0) / total * 100) if total > 0 else 0
                st.markdown(f"""
                <div class="metric-card" style="border-left: 3px solid #F59E0B;">
                    <div class="metric-value" style="color: #F59E0B;">{med_pct:.1f}%</div>
                    <div class="metric-label">Medium Risk Rate</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_eff4:
                high_pct = (avg_risk_band_dist.get('HIGH', 0) / total * 100) if total > 0 else 0
                st.markdown(f"""
                <div class="metric-card" style="border-left: 3px solid #EF4444;">
                    <div class="metric-value" style="color: #EF4444;">{high_pct:.1f}%</div>
                    <div class="metric-label">High Risk Rate</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Charts
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.markdown("**Risk Band Distribution**")
                risk_chart_df = pd.DataFrame(
                    list(avg_risk_band_dist.items()),
                    columns=['Risk Band', 'Count']
                )
                st.bar_chart(risk_chart_df.set_index('Risk Band'), color="#8B5CF6")
            
            with col_chart2:
                st.markdown("**Override Rate by Risk Band**")
                override_by_risk = decisions_df[decisions_df['decision'] == 'OVERRIDE']['risk_band'].value_counts()
                override_chart_df = pd.DataFrame(
                    list(override_by_risk.items()),
                    columns=['Risk Band', 'Overrides']
                )
                if not override_chart_df.empty:
                    st.bar_chart(override_chart_df.set_index('Risk Band'), color="#EF4444")
                else:
                    st.info("No overrides recorded yet")
        
        else:
            st.info("📊 No assessment data available yet. Run analyses in Seller View to generate insights.")
    
    except FileNotFoundError:
        st.info("📊 No historical data found. Decision data will appear here once managers start making decisions.")
    
    st.markdown("---")
    
    # SECTION 5: TREND ANALYSIS (SYSTEM HEALTH)
    st.markdown("### 📊 Trend Analysis (System Health)")
    st.markdown("Monitor how the system behavior evolves over time:")
    
    try:
        decisions_df = pd.read_csv(f"{DATA_PATH}/manager_decisions.csv")
        
        if not decisions_df.empty and len(decisions_df) > 5:
            decisions_df['timestamp'] = pd.to_datetime(decisions_df['timestamp'])
            decisions_df = decisions_df.sort_values('timestamp')
            
            # Risk band trend
            st.markdown("**Risk Assessment Trend Over Time**")
            
            # Create daily aggregation
            decisions_df['date'] = decisions_df['timestamp'].dt.date
            daily_risk = decisions_df.groupby(['date', 'risk_band']).size().unstack(fill_value=0)
            
            if not daily_risk.empty:
                st.line_chart(daily_risk, color=["#10B981", "#F59E0B", "#EF4444"])
            
            st.markdown("---")
            
            # Override trend
            st.markdown("**Override Frequency Trend**")
            daily_overrides = decisions_df[decisions_df['decision'] == 'OVERRIDE'].groupby('date').size()
            
            if not daily_overrides.empty:
                st.line_chart(daily_overrides, color="#EF4444")
            else:
                st.success("✅ No overrides detected in the system")
        
        else:
            st.info("📊 Insufficient data for trend analysis. More decisions needed (minimum 5).")
    
    except FileNotFoundError:
        st.info("📊 No trend data available yet.")
    
    st.markdown("---")
    
    # SECTION 6: MODEL GOVERNANCE & LIMITS
    st.markdown("### 🔒 Model Governance & Limitations")
    
    col_gov1, col_gov2 = st.columns(2)
    
    with col_gov1:
        st.markdown("""
        <div class="light-card">
            <h4>What the Model Does</h4>
            <ul>
                <li>✅ Assesses pre-dispatch delivery risk</li>
                <li>✅ Provides explainable risk scores</li>
                <li>✅ Recommends vehicle and priority</li>
                <li>✅ Considers weather and area complexity</li>
                <li>✅ Supports human decision-making</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col_gov2:
        st.markdown("""
        <div class="light-card">
            <h4>What the Model Does NOT Do</h4>
            <ul>
                <li>❌ Does not make final dispatch decisions</li>
                <li>❌ Does not self-learn from overrides</li>
                <li>❌ Does not automatically retrain</li>
                <li>❌ Does not replace human judgment</li>
                <li>❌ Does not guarantee delivery outcomes</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Disclaimer
    st.markdown("""
    <div class="disclaimer-box">
        <div class="disclaimer-title">⚠️ Important Disclaimer</div>
        <div class="disclaimer-text">
            <strong>Risk scores indicate likelihood of delay, not certainty.</strong><br><br>
            
            LICS is a <strong>decision support system</strong>, not an automated decision-making system. 
            All risk assessments are <strong>advisory</strong> and subject to manager review and approval.
            <br><br>
            
            The system does not learn from individual decisions or adapt automatically. 
            Model updates require explicit retraining by authorized personnel.
            <br><br>
            
            Operational decisions remain the responsibility of human managers who have 
            the authority to accept, hold, or override any AI recommendation with appropriate justification.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # SECTION 7: PROJECT / MODEL OVERVIEW PANEL
    st.markdown("### 📋 System Information")
    
    col_sys1, col_sys2, col_sys3 = st.columns(3)
    
    with col_sys1:
        st.markdown("""
        <div class="light-card">
            <h4>Project Details</h4>
            <ul>
                <li><strong>Name:</strong> LICS</li>
                <li><strong>Version:</strong> 2.0</li>
                <li><strong>Engine Count:</strong> 6 active engines</li>
                <li><strong>Architecture:</strong> Hybrid (Rule + ML)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col_sys2:
        st.markdown("""
        <div class="light-card">
            <h4>Data & Storage</h4>
            <ul>
                <li><strong>Storage:</strong> CSV-based</li>
                <li><strong>Audit Trail:</strong> Complete</li>
                <li><strong>Data Privacy:</strong> No PII</li>
                <li><strong>Retention:</strong> Unlimited</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col_sys3:
        st.markdown("""
        <div class="light-card">
            <h4>Model Training</h4>
            <ul>
                <li><strong>Approach:</strong> Offline</li>
                <li><strong>Data Type:</strong> Historical operational</li>
                <li><strong>Last Update:</strong> January 2026</li>
                <li><strong>Next Update:</strong> Manual trigger</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # SECTION 8: DATA INSPECTION (CSV FILE VIEWER)
    st.markdown("### 📂 Data Inspection & CSV File Viewer")
    st.markdown("Inspect the raw data files used by the LICS system for complete transparency:")
    
    # CSV file selection
    csv_files = {
        "Area Feasibility Master": "area_feasibility_master.csv",
        "Manager Decisions (Audit Trail)": "manager_decisions.csv",
        "Shipments Input (Historical)": "shipments_input.csv",
        "Traffic Profile": "traffic_profile.csv",
        "Vehicle Master": "vehicle_master.csv",
        "Weather Risk Rules": "weather_risk_rules.csv"
    }
    
    col_select, col_info = st.columns([2, 1])
    
    with col_select:
        selected_file = st.selectbox(
            "**Select CSV File to Inspect**",
            list(csv_files.keys()),
            help="Choose a data file to view its contents"
        )
    
    with col_info:
        st.markdown("""
        <div style="background: #EFF6FF; padding: 1rem; border-radius: 6px; border-left: 3px solid #3B82F6;">
            <strong>📊 Data Transparency</strong><br>
            <span style="font-size: 0.85rem; color: #1E40AF;">
                All system data is stored in human-readable CSV format
            </span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Load and display selected CSV
    if selected_file:
        csv_path = f"{DATA_PATH}/{csv_files[selected_file]}"
        
        try:
            df = pd.read_csv(csv_path)
            
            # File metadata
            col_meta1, col_meta2, col_meta3, col_meta4 = st.columns(4)
            
            with col_meta1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="font-size: 1.5rem;">{len(df)}</div>
                    <div class="metric-label">Total Rows</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_meta2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="font-size: 1.5rem;">{len(df.columns)}</div>
                    <div class="metric-label">Total Columns</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_meta3:
                file_size = pd.io.common.file_exists(csv_path)
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="font-size: 1.5rem;">CSV</div>
                    <div class="metric-label">File Format</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_meta4:
                memory_usage = df.memory_usage(deep=True).sum() / 1024  # KB
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="font-size: 1.5rem;">{memory_usage:.1f} KB</div>
                    <div class="metric-label">Memory Size</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("")
            
            # Column information
            with st.expander("📋 Column Information", expanded=False):
                col_info_df = pd.DataFrame({
                    'Column Name': df.columns,
                    'Data Type': df.dtypes.values,
                    'Non-Null Count': df.count().values,
                    'Null Count': df.isnull().sum().values
                })
                st.dataframe(col_info_df, use_container_width=True)
            
            # Data preview
            st.markdown(f"**📊 Data Preview: {selected_file}**")
            st.caption(f"Showing first 100 rows of {len(df)} total records")
            
            # Display dataframe with pagination
            display_df = df.head(100)
            st.dataframe(
                display_df,
                use_container_width=True,
                height=400
            )
            
            # Summary statistics for numeric columns
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
            if len(numeric_cols) > 0:
                with st.expander("📈 Summary Statistics (Numeric Columns)", expanded=False):
                    st.dataframe(df[numeric_cols].describe(), use_container_width=True)
            
            # Sample records
            with st.expander("🔍 Random Sample Records", expanded=False):
                if len(df) > 5:
                    sample_df = df.sample(min(5, len(df)))
                    st.dataframe(sample_df, use_container_width=True)
                else:
                    st.dataframe(df, use_container_width=True)
            
            st.success(f"✅ Successfully loaded **{csv_files[selected_file]}** with {len(df)} records")
        
        except FileNotFoundError:
            st.error(f"❌ File not found: `{csv_files[selected_file]}`")
            st.info("This file may not exist yet. Some files are created during system operation.")
        
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")
    
    st.markdown("---")
    
    st.success("""
    **🎯 Transparency Mission**  
    This section exists to build trust through openness. LICS is designed to be explainable, 
    governable, and honest about its capabilities and limitations.
    """)
    
    st.caption("💡 This view is read-only and purely informational. No operational controls are available here.")
