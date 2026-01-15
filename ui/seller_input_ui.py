# ui/seller_input_ui.py

from unittest import result
import streamlit as st

from engines.input_validation_engine import validate_and_normalize
from engines.area_feasibility_engine import evaluate_area_feasibility
from engines.weather_impact_engine import get_weather_risk
from engines.vehicle_feasibility_engine import evaluate_vehicle_feasibility
from engines.priority_classification_engine import classify_priority
from engines.risk_scoring_engine import compute_risk_score
from engines.delay_explanation_engine import generate_delay_explanation
from engines.manager_decision_engine import record_manager_decision
from engines.supervisor_analytics_engine import load_governance_metrics
from engines.supervisor_analytics_engine import (
    load_governance_metrics,
    load_override_records
)
from utils.id_generator import generate_parcel_id


def seller_input_form():

    active_view = st.session_state.get("active_view", "Seller View")

    # ==================================================
    # SELLER VIEW
    # ==================================================
    if active_view == "Seller View":

        st.subheader("📦 Seller Shipment Input")

        with st.form("shipment_form"):
            weight = st.number_input("Weight (kg)", min_value=0.0)
            length = st.number_input("Length (cm)", min_value=0.0)
            width = st.number_input("Width (cm)", min_value=0.0)
            height = st.number_input("Height (cm)", min_value=0.0)
            distance = st.number_input("Distance (km)", min_value=0.0)

            source_city = st.text_input("Source City (Pickup)")
            destination_city = st.text_input("Destination City (Delivery)")

            area_type = st.selectbox("Area Type", ["URBAN", "RURAL", "OLD_CITY"])
            address_type = st.selectbox("Address Type", ["RESIDENTIAL", "COMMERCIAL"])
            delivery_date = st.date_input("Delivery Date")
            urgency = st.selectbox("Delivery Urgency", ["NORMAL", "EXPRESS"])

            submitted = st.form_submit_button("Run Pre-Dispatch Analysis")

        if submitted:
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

            parcel_id = generate_parcel_id()
            result["parcel_id"] = parcel_id

            if not success:
                st.error("Validation failed:")
                for err in result:
                    st.write(f"- {err}")
                return

            # ---------------- RUN ALL ENGINES ----------------
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

            # Persist analysis for other views
            st.session_state["analysis"] = {
                "parcel_id": parcel_id,
                "shipment": result,
                "feasibility": feasibility,
                "weather": weather_risk,
                "vehicle": vehicle_result,
                "priority": priority_result,
                "risk": risk_result,
                "explanation": explanation
            }


            from config import RISK_UI

            risk_ui = RISK_UI[risk_result["risk_band"]]

            st.divider()
            st.subheader("🧭 AI Pre-Dispatch Recommendation")

            st.markdown(
                f"""
                **Overall Risk:** {risk_ui['emoji']} **{risk_ui['label']}**  
                **Risk Score:** {risk_result['risk_score']} / 100
                """
            )

            st.markdown("**Why this matters:**")
            st.write(explanation["summary"])

            with st.expander("See detailed risk reasons"):
                for idx, reason in enumerate(explanation["top_reasons"], start=1):
                    st.write(f"{idx}. {reason}")

            with st.expander("See technical analysis (advanced)"):
                st.write("Area Feasibility")
                st.json(feasibility)
                st.write("Weather Impact")
                st.json(weather_risk)
                st.write("Vehicle Feasibility")
                st.json(vehicle_result)
                st.write("Priority Classification")
                st.json(priority_result)
                st.write("Risk Breakdown")
                st.json(risk_result)

            st.info("If required, switch to **Manager View** to take action.")


    # ==================================================
    # MANAGER VIEW
    # ==================================================
    elif active_view == "Manager View":

        st.subheader("🧑‍💼 Manager Decision Panel")

        st.caption(
        "Review AI recommendation and explanation before taking action. "
        "Overrides require justification."
    )


        if "analysis" not in st.session_state:
            st.warning("No analysis found. Run Seller View first.")
            return

        risk = st.session_state["analysis"]["risk"]
        explanation = st.session_state["analysis"]["explanation"]

        from config import RISK_UI

        risk_ui = RISK_UI[risk["risk_band"]]

        st.markdown(
            f"""
            **AI Risk Assessment:** {risk_ui['emoji']} **{risk_ui['label']}**  
            **Risk Score:** {risk['risk_score']} / 100
            """
        )

        st.write("**AI Explanation:**")
        st.write(explanation["summary"])

        st.divider()


        st.write(f"**Risk Band:** {risk['risk_band']}")
        st.write(f"**Risk Score:** {risk['risk_score']}")
        st.write("**Explanation:**")
        st.write(explanation["summary"])

        decision = st.radio("Manager Decision", ["ACCEPT", "HOLD", "OVERRIDE"])
        override_reason = ""

        if decision == "OVERRIDE":
            override_reason = st.text_area(
                "Override Justification (Required)",
                placeholder="Explain why AI recommendation is overridden..."
            )

        if st.button("Submit Decision"):
            if decision == "OVERRIDE" and not override_reason.strip():
                st.error("Override justification is mandatory.")
            else:
                record_manager_decision(
                    parcel_id=st.session_state["analysis"]["parcel_id"],
                    decision=decision,
                    risk_band=risk["risk_band"],
                    override_reason=override_reason
                )

                st.success("Manager decision recorded successfully.")

    # ==================================================
    # SUPERVISOR VIEW 
    # ==================================================
    else:
        st.subheader("📊 Supervisor Governance Dashboard")

        metrics = load_governance_metrics()

        # 🔹 KPIs (always visible)
        st.metric("Total Decisions", metrics["total_decisions"])
        st.metric("Override Rate (%)", metrics["override_rate"])
        st.metric("High-Risk Acceptances", metrics["high_risk_accepts"])

        st.divider()
        st.subheader("🔴 AI Overrides (Supervisor Visibility)")

        overrides_df = load_override_records()

        if overrides_df.empty:
            st.success("No AI overrides recorded.")
        else:
            st.warning(f"{len(overrides_df)} AI override(s) detected.")

            display_df = overrides_df[[
                "parcel_id",
                "timestamp",
                "risk_band",
                "override_reason"
            ]].copy()


            display_df["status"] = "OVERRIDDEN"

            st.dataframe(display_df, use_container_width=True)


        st.divider()

        # 🔹 Details (only if supervisor wants)
        with st.expander("Decision Breakdown (details)"):
            st.json(metrics["decision_counts"])

        with st.expander("Risk Band Distribution (details)"):
            st.json(metrics["risk_distribution"])

