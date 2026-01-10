"""
FastAPI Routes - API Endpoints
Step 13: REST endpoints for all system components
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
import pandas as pd
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.schemas import *
from models.risk_engine import calculate_risk_score, risk_bucket
from features.address_intelligence import calculate_address_confidence, extract_landmarks
from features.weather_impact import get_weather_impact
from rules.pre_dispatch_gate import pre_dispatch_decision, get_decision_explanation, get_action_items
from rules.vehicle_selector import hyper_local_vehicle_check
from features.carbon_tradeoff_engine import co2_speed_tradeoff, get_vehicle_emission_factor, sustainability_score
from rules.human_override import (
    apply_human_override,
    is_locked,
    get_override_history,
    get_override_stats,
    OVERRIDE_REASONS
)
from notifications.customer_notifier import generate_message, notify_customer
from execution.delivery_simulator import (
    run_execution_flow,
    get_tracking_history,
    get_execution_stats,
    get_current_status,
    simulate_failed_delivery_attempt,
    bulk_simulate_deliveries
)

# Initialize routers
shipments_router = APIRouter()
intelligence_router = APIRouter()
decisions_router = APIRouter()
overrides_router = APIRouter()
statistics_router = APIRouter()
execution_router = APIRouter()

# Load data
try:
    SHIPMENTS_DF = pd.read_csv("Data/shipments.csv")
    ADDRESSES_DF = pd.read_csv("Data/addresses.csv")
    WEATHER_DF = pd.read_csv("Data/weather_and_environment.csv")
except Exception as e:
    print(f"Warning: Could not load data files: {e}")
    SHIPMENTS_DF = pd.DataFrame()
    ADDRESSES_DF = pd.DataFrame()
    WEATHER_DF = pd.DataFrame()

# ==================== SHIPMENT ENDPOINTS ====================

@shipments_router.get("/", response_model=List[ShipmentDetail])
async def get_shipments(
    limit: int = Query(default=50, ge=1, le=500),
    city: Optional[str] = None,
    min_risk: Optional[float] = None
):
    """Get list of shipments with optional filters"""
    try:
        df = SHIPMENTS_DF.copy()
        
        if city:
            df = df[df['destination_city'] == city]
        
        if min_risk is not None:
            df = df[df['current_risk_score'] >= min_risk]
        
        df = df.head(limit)
        
        return df.to_dict('records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@shipments_router.get("/{shipment_id}", response_model=ShipmentDetail)
async def get_shipment(shipment_id: str):
    """Get specific shipment details"""
    try:
        shipment = SHIPMENTS_DF[SHIPMENTS_DF['shipment_id'] == shipment_id]
        
        if shipment.empty:
            raise HTTPException(status_code=404, detail=f"Shipment {shipment_id} not found")
        
        return shipment.iloc[0].to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== INTELLIGENCE ENDPOINTS ====================

@intelligence_router.post("/risk", response_model=RiskAssessmentResponse)
async def assess_risk(request: RiskAssessmentRequest):
    """Get risk assessment for a shipment"""
    try:
        shipment = SHIPMENTS_DF[SHIPMENTS_DF['shipment_id'] == request.shipment_id]
        
        if shipment.empty:
            raise HTTPException(status_code=404, detail=f"Shipment {request.shipment_id} not found")
        
        s = shipment.iloc[0]
        
        # Calculate risk (simplified - in production would use full risk engine)
        risk_score = float(s['current_risk_score'])
        bucket = risk_bucket(risk_score)
        
        return {
            "shipment_id": request.shipment_id,
            "risk_score": risk_score,
            "risk_bucket": bucket,
            "factors": {
                "weight": float(s.get('weight_kg', 0)),
                "value": float(s.get('declared_value', 0)),
                "priority": float(s.get('priority_flag', 0))
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@intelligence_router.post("/address", response_model=AddressIntelligenceResponse)
async def analyze_address(request: AddressIntelligenceRequest):
    """Get address intelligence analysis"""
    try:
        # Use calculate_address_confidence which returns a dict
        result = calculate_address_confidence(
            raw_address=request.address_text,
            road_accessibility=None,
            existing_area_type=None
        )
        
        confidence = result['confidence_score']
        landmarks = extract_landmarks(request.address_text)
        
        return {
            "address": request.address_text,
            "confidence_score": confidence,
            "matched_landmarks": landmarks,
            "is_verified": confidence >= 60
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@intelligence_router.post("/weather", response_model=WeatherImpactResponse)
async def check_weather(request: WeatherImpactRequest):
    """Get weather impact for a city"""
    try:
        weather_data = get_weather_impact(request.city, use_live_api=False)  # Use simulated for now
        
        impact_score = weather_data.get('weather_impact_factor', 0) * 100  # Convert to 0-100 scale
        severity = weather_data.get('weather_severity', 'Moderate')
        
        if impact_score >= 60:
            risk_level = "High"
            conditions = f"Severe weather conditions: {severity}"
        elif impact_score >= 30:
            risk_level = "Medium"
            conditions = f"Moderate weather impact: {severity}"
        else:
            risk_level = "Low"
            conditions = "Favorable weather"
        
        return {
            "city": request.city,
            "weather_impact_score": impact_score,
            "conditions": conditions,
            "risk_level": risk_level,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== DECISION ENDPOINTS ====================

@decisions_router.post("/pre-dispatch", response_model=PreDispatchResponse)
async def make_pre_dispatch_decision(request: PreDispatchRequest):
    """Make pre-dispatch decision (DISPATCH/DELAY/RESCHEDULE)"""
    try:
        # Get shipment data if scores not provided
        if not all([request.risk_score, request.weather_impact_score, request.address_confidence_score]):
            shipment = SHIPMENTS_DF[SHIPMENTS_DF['shipment_id'] == request.shipment_id]
            if shipment.empty:
                raise HTTPException(status_code=404, detail=f"Shipment {request.shipment_id} not found")
            
            s = shipment.iloc[0]
            risk_score = request.risk_score or float(s['current_risk_score'])
            weather_impact = request.weather_impact_score or 30.0  # Default
            address_confidence = request.address_confidence_score or 70.0  # Default
        else:
            risk_score = request.risk_score
            weather_impact = request.weather_impact_score
            address_confidence = request.address_confidence_score
        
        # Make decision
        decision = pre_dispatch_decision(
            risk_score=risk_score,
            weather_impact_score=weather_impact,
            address_confidence_score=address_confidence
        )
        
        reasons = get_decision_explanation(decision, risk_score, weather_impact, address_confidence)
        action_items = get_action_items(decision)
        
        return {
            "shipment_id": request.shipment_id,
            "decision": decision,
            "reasons": reasons,
            "action_items": action_items,
            "risk_score": risk_score,
            "weather_impact": weather_impact,
            "address_confidence": address_confidence,
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@decisions_router.post("/vehicle-feasibility", response_model=VehicleFeasibilityResponse)
async def check_vehicle_feasibility(request: VehicleFeasibilityRequest):
    """Check vehicle feasibility for shipment"""
    try:
        result = hyper_local_vehicle_check(
            vehicle_type=request.vehicle_type,
            destination_area=request.destination_area,
            road_type=request.road_type,
            weight_kg=request.weight_kg,
            volume_cm3=request.volume_cm3
        )
        
        return {
            "shipment_id": request.shipment_id,
            "vehicle_type": request.vehicle_type,
            "is_allowed": result["is_allowed"],
            "capacity_ok": result["capacity_ok"],
            "feasible": result["feasible"],
            "reasons": result["reasons"],
            "recommended_vehicle": result.get("recommended_vehicle")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@decisions_router.post("/co2-tradeoff", response_model=CO2TradeoffResponse)
async def analyze_co2_tradeoff(request: CO2TradeoffRequest):
    """Analyze CO₂ vs speed trade-off"""
    try:
        emission_factor = get_vehicle_emission_factor(request.vehicle_type)
        result = co2_speed_tradeoff(emission_factor, request.distance_km)
        
        # Calculate sustainability score
        co2_saved = result['co2_saved_kg']
        score = sustainability_score(co2_saved, request.distance_km)
        
        return {
            "vehicle_type": request.vehicle_type,
            "distance_km": request.distance_km,
            "fast_route": result['fast_route'],
            "green_route": result['green_route'],
            "time_saved_hours": result['time_saved_hours'],
            "co2_saved_kg": result['co2_saved_kg'],
            "recommendation": result['recommendation'],
            "sustainability_score": score
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== OVERRIDE ENDPOINTS ====================

@overrides_router.post("/apply", response_model=OverrideResponse)
async def apply_override(request: OverrideRequest):
    """Apply human override to AI decision"""
    try:
        # Validate reason
        if request.override_reason not in OVERRIDE_REASONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid override reason. Must be one of: {OVERRIDE_REASONS}"
            )
        
        result = apply_human_override(
            shipment_id=request.shipment_id,
            ai_decision=request.ai_decision,
            override_decision=request.override_decision,
            override_reason=request.override_reason
        )
        
        return {
            "shipment_id": request.shipment_id,
            "status": result["status"],
            "final_decision": result["final_decision"],
            "locked": result.get("locked", False),
            "message": result.get("message", ""),
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@overrides_router.post("/check-lock", response_model=OverrideLockCheckResponse)
async def check_lock(request: OverrideLockCheckRequest):
    """Check if shipment has manual lock"""
    try:
        locked = is_locked(request.shipment_id)
        
        return {
            "shipment_id": request.shipment_id,
            "is_locked": locked
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@overrides_router.get("/history", response_model=OverrideHistoryResponse)
async def get_history(shipment_id: Optional[str] = None):
    """Get override history"""
    try:
        history_df = get_override_history(shipment_id)
        
        return {
            "shipment_id": shipment_id,
            "overrides": history_df.to_dict('records'),
            "total_count": len(history_df)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@overrides_router.get("/reasons")
async def get_override_reasons():
    """Get list of valid override reasons"""
    return {
        "reasons": OVERRIDE_REASONS,
        "count": len(OVERRIDE_REASONS)
    }

# ==================== STATISTICS ENDPOINTS ====================

@statistics_router.get("/system", response_model=SystemStatsResponse)
async def get_system_stats():
    """Get system-wide statistics"""
    try:
        df = SHIPMENTS_DF
        
        total = len(df)
        high_risk = len(df[df['current_risk_score'] > 60])
        low_address = 0  # Would need address data
        avg_risk = df['current_risk_score'].mean() if total > 0 else 0
        
        override_stats = get_override_stats()
        total_overrides = override_stats.get('total_overrides', 0)
        override_rate = (total_overrides / total * 100) if total > 0 else 0
        
        return {
            "total_shipments": total,
            "high_risk_count": high_risk,
            "low_address_confidence_count": low_address,
            "avg_risk_score": float(avg_risk),
            "total_overrides": total_overrides,
            "override_rate": override_rate
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@statistics_router.get("/overrides", response_model=OverrideStatsResponse)
async def get_override_statistics():
    """Get override statistics for learning loop"""
    try:
        stats = get_override_stats()
        
        return {
            "total_overrides": stats.get('total_overrides', 0),
            "override_rate": stats.get('override_rate', 0),
            "most_common_reason": stats.get('most_common_reason'),
            "ai_to_dispatch": stats.get('ai_to_dispatch', 0),
            "ai_to_delay": stats.get('ai_to_delay', 0),
            "ai_to_reschedule": stats.get('ai_to_reschedule', 0),
            "reason_distribution": stats.get('reason_distribution', {})
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@statistics_router.get("/decisions", response_model=DecisionStatsResponse)
async def get_decision_stats():
    """Get pre-dispatch decision statistics"""
    try:
        # In production, would query decision log
        # For now, simulate based on shipments
        total = len(SHIPMENTS_DF)
        
        # Simulate decision distribution (would come from actual decision log)
        dispatch = int(total * 0.62)
        delay = int(total * 0.02)
        reschedule = total - dispatch - delay
        
        return {
            "total_decisions": total,
            "dispatch_count": dispatch,
            "delay_count": delay,
            "reschedule_count": reschedule,
            "dispatch_rate": (dispatch / total * 100) if total > 0 else 0,
            "delay_rate": (delay / total * 100) if total > 0 else 0,
            "reschedule_rate": (reschedule / total * 100) if total > 0 else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== EXECUTION ENDPOINTS (Step 16) ====================

@execution_router.post("/execute-delivery", response_model=dict)
async def execute_delivery(request: dict):
    """
    Execute delivery simulation for a shipment
    
    Request body:
    {
        "shipment_id": "SHP_001",
        "packing_delay": false,
        "delivery_delay": false
    }
    """
    try:
        shipment_id = request.get("shipment_id")
        packing_delay = request.get("packing_delay", False)
        delivery_delay = request.get("delivery_delay", False)
        
        if not shipment_id:
            raise HTTPException(status_code=400, detail="shipment_id is required")
        
        result = run_execution_flow(
            shipment_id,
            packing_delay=packing_delay,
            delivery_delay=delivery_delay
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@execution_router.get("/tracking/{shipment_id}", response_model=dict)
async def get_shipment_tracking(shipment_id: str):
    """
    Get tracking history for a specific shipment
    """
    try:
        history = get_tracking_history(shipment_id)
        
        if len(history) == 0:
            raise HTTPException(
                status_code=404,
                detail=f"No tracking events found for {shipment_id}"
            )
        
        current_status = get_current_status(shipment_id)
        
        return {
            "shipment_id": shipment_id,
            "current_status": current_status,
            "total_events": len(history),
            "events": history.to_dict(orient="records")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@execution_router.get("/tracking", response_model=dict)
async def get_all_tracking(limit: int = Query(50, ge=1, le=1000)):
    """
    Get recent tracking events for all shipments
    """
    try:
        history = get_tracking_history()
        
        if len(history) == 0:
            return {
                "total_events": 0,
                "events": []
            }
        
        # Get latest events
        recent_events = history.tail(limit)
        
        return {
            "total_events": len(history),
            "showing": len(recent_events),
            "events": recent_events.to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@execution_router.get("/statistics/execution", response_model=dict)
async def get_execution_statistics():
    """
    Get execution statistics for all deliveries
    """
    try:
        stats = get_execution_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@execution_router.post("/simulate-failed-attempt", response_model=dict)
async def simulate_failed_attempt(request: dict):
    """
    Simulate a failed delivery attempt
    
    Request body:
    {
        "shipment_id": "SHP_001",
        "reason": "Customer unavailable"
    }
    """
    try:
        shipment_id = request.get("shipment_id")
        reason = request.get("reason", "Customer unavailable")
        
        if not shipment_id:
            raise HTTPException(status_code=400, detail="shipment_id is required")
        
        simulate_failed_delivery_attempt(shipment_id, reason)
        
        return {
            "shipment_id": shipment_id,
            "action": "failed_attempt_simulated",
            "reason": reason,
            "next_action": "re_attempt_scheduled"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@execution_router.post("/bulk-simulate", response_model=dict)
async def bulk_simulate(request: dict):
    """
    Bulk simulate multiple deliveries
    
    Request body:
    {
        "count": 10,
        "delay_probability": 0.2
    }
    """
    try:
        count = request.get("count", 10)
        delay_probability = request.get("delay_probability", 0.2)
        
        if count < 1 or count > 100:
            raise HTTPException(
                status_code=400,
                detail="count must be between 1 and 100"
            )
        
        if delay_probability < 0 or delay_probability > 1:
            raise HTTPException(
                status_code=400,
                detail="delay_probability must be between 0 and 1"
            )
        
        results = bulk_simulate_deliveries(count, delay_probability)
        
        return {
            "simulated_count": len(results),
            "results": results
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
