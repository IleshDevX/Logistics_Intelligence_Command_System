"""
Pydantic Schemas for FastAPI
Step 13: Request/Response models for API endpoints
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

# ==================== SHIPMENT SCHEMAS ====================

class ShipmentBase(BaseModel):
    """Base shipment information"""
    shipment_id: str
    destination_city: str
    product_name: str
    weight_kg: float
    assigned_vehicle_type: str
    current_risk_score: float

class ShipmentDetail(ShipmentBase):
    """Detailed shipment with additional fields"""
    order_id: str
    product_category: str
    declared_value: float
    priority_flag: int
    volumetric_weight: float

class ShipmentResponse(BaseModel):
    """Response for shipment queries"""
    shipment: ShipmentDetail
    message: str

# ==================== INTELLIGENCE SCHEMAS ====================

class RiskAssessmentRequest(BaseModel):
    """Request for risk assessment"""
    shipment_id: str

class RiskAssessmentResponse(BaseModel):
    """Risk assessment results"""
    shipment_id: str
    risk_score: float
    risk_bucket: str  # Low, Medium, High
    factors: Dict[str, float]
    timestamp: str

class AddressIntelligenceRequest(BaseModel):
    """Request for address intelligence"""
    address_text: str

class AddressIntelligenceResponse(BaseModel):
    """Address intelligence results"""
    address: str
    confidence_score: float
    matched_landmarks: List[str]
    is_verified: bool

class WeatherImpactRequest(BaseModel):
    """Request for weather impact"""
    city: str

class WeatherImpactResponse(BaseModel):
    """Weather impact results"""
    city: str
    weather_impact_score: float
    conditions: str
    risk_level: str
    timestamp: str

# ==================== DECISION SCHEMAS ====================

class PreDispatchRequest(BaseModel):
    """Request for pre-dispatch decision"""
    shipment_id: str
    risk_score: Optional[float] = None
    weather_impact_score: Optional[float] = None
    address_confidence_score: Optional[float] = None

class PreDispatchResponse(BaseModel):
    """Pre-dispatch decision results"""
    shipment_id: str
    decision: str  # DISPATCH, DELAY, RESCHEDULE
    reasons: List[str]
    action_items: List[str]
    risk_score: float
    weather_impact: float
    address_confidence: float
    timestamp: str

class VehicleFeasibilityRequest(BaseModel):
    """Request for vehicle feasibility check"""
    shipment_id: str
    vehicle_type: str
    destination_area: str
    road_type: str
    weight_kg: float
    volume_cm3: float

class VehicleFeasibilityResponse(BaseModel):
    """Vehicle feasibility results"""
    shipment_id: str
    vehicle_type: str
    is_allowed: bool
    capacity_ok: bool
    feasible: bool
    reasons: List[str]
    recommended_vehicle: Optional[str] = None

class CO2TradeoffRequest(BaseModel):
    """Request for CO₂ trade-off analysis"""
    vehicle_type: str = Field(..., description="Bike, Van, or Truck")
    distance_km: float = Field(..., ge=5, le=50, description="Route distance in km")

class CO2TradeoffResponse(BaseModel):
    """CO₂ trade-off results"""
    vehicle_type: str
    distance_km: float
    fast_route: Dict[str, float]
    green_route: Dict[str, float]
    time_saved_hours: float
    co2_saved_kg: float
    recommendation: str
    sustainability_score: str

# ==================== OVERRIDE SCHEMAS ====================

class OverrideRequest(BaseModel):
    """Request to apply human override"""
    shipment_id: str
    ai_decision: str = Field(..., description="DISPATCH, DELAY, or RESCHEDULE")
    override_decision: str = Field(..., description="DISPATCH, DELAY, or RESCHEDULE")
    override_reason: str = Field(..., description="Must be from reason catalog")

class OverrideResponse(BaseModel):
    """Override application results"""
    shipment_id: str
    status: str
    final_decision: str
    locked: bool
    message: str
    timestamp: str

class OverrideLockCheckRequest(BaseModel):
    """Request to check if shipment is locked"""
    shipment_id: str

class OverrideLockCheckResponse(BaseModel):
    """Lock check results"""
    shipment_id: str
    is_locked: bool

class OverrideHistoryResponse(BaseModel):
    """Override history for a shipment"""
    shipment_id: Optional[str] = None
    overrides: List[Dict]
    total_count: int

# ==================== STATISTICS SCHEMAS ====================

class SystemStatsResponse(BaseModel):
    """System-wide statistics"""
    total_shipments: int
    high_risk_count: int
    low_address_confidence_count: int
    avg_risk_score: float
    total_overrides: int
    override_rate: float

class OverrideStatsResponse(BaseModel):
    """Override statistics for learning loop"""
    total_overrides: int
    override_rate: float
    most_common_reason: Optional[str]
    ai_to_dispatch: int
    ai_to_delay: int
    ai_to_reschedule: int
    reason_distribution: Dict[str, int]

class DecisionStatsResponse(BaseModel):
    """Pre-dispatch decision statistics"""
    total_decisions: int
    dispatch_count: int
    delay_count: int
    reschedule_count: int
    dispatch_rate: float
    delay_rate: float
    reschedule_rate: float

# ==================== CUSTOMER NOTIFICATION SCHEMAS ====================

class NotificationRequest(BaseModel):
    """Request to send customer notification"""
    shipment_id: str
    decision: str  # DISPATCH, DELAY, RESCHEDULE
    reason: str
    customer_phone: str
    customer_name: str
    channels: List[str] = ["console"]  # console, whatsapp, sms, email

class NotificationResponse(BaseModel):
    """Notification sending results"""
    shipment_id: str
    message: str
    channels_used: List[str]
    status: str
    timestamp: str

# ==================== COMMON SCHEMAS ====================

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: str
    timestamp: str

class SuccessResponse(BaseModel):
    """Generic success response"""
    message: str
    data: Optional[Dict] = None
    timestamp: str
