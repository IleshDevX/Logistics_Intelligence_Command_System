"""
MongoDB Database Schemas for LICS Application
Defines data models and validation rules
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import uuid
from pydantic import BaseModel, Field, validator
from bson import ObjectId

class PyObjectId(ObjectId):
    """Custom ObjectId for Pydantic compatibility"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

# Enums for consistent data
class UserRole(str, Enum):
    SELLER = "seller"
    MANAGER = "manager" 
    SUPERVISOR = "supervisor"
    ADMIN = "admin"

class ShipmentStatus(str, Enum):
    PENDING = "pending"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    DELAYED = "delayed"
    CANCELLED = "cancelled"
    RETURNED = "returned"

class PaymentType(str, Enum):
    PREPAID = "prepaid"
    COD = "cod"

class Priority(str, Enum):
    STANDARD = "standard"
    EXPRESS = "express"
    URGENT = "urgent"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class DecisionType(str, Enum):
    DISPATCH = "dispatch"
    DELAY = "delay"
    RESCHEDULE = "reschedule"

# User Schema
class UserSchema(BaseModel):
    """User document schema"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    password_hash: str = Field(...)
    full_name: str = Field(..., min_length=2, max_length=100)
    phone: Optional[str] = Field(None, regex=r'^\+91[0-9]{10}$')
    role: UserRole = Field(...)
    department: Optional[str] = Field(None, max_length=50)
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    preferences: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "username": "john_seller",
                "email": "john@company.com",
                "full_name": "John Kumar",
                "phone": "+919876543210",
                "role": "seller",
                "department": "Sales"
            }
        }

# Address Schema
class AddressSchema(BaseModel):
    """Address information schema"""
    full_address: str = Field(..., min_length=10, max_length=500)
    landmark: Optional[str] = Field(None, max_length=200)
    city: str = Field(..., min_length=2, max_length=50)
    state: str = Field(..., min_length=2, max_length=50)
    postal_code: str = Field(..., regex=r'^\d{6}$')
    country: str = Field(default="India")
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    address_type: str = Field(default="delivery")  # delivery, pickup, warehouse
    confidence_score: Optional[float] = Field(None, ge=0, le=100)
    
    class Config:
        schema_extra = {
            "example": {
                "full_address": "House No. 123, Sector 15, Noida",
                "landmark": "Near Metro Station",
                "city": "Noida",
                "state": "Uttar Pradesh", 
                "postal_code": "201301",
                "country": "India"
            }
        }

# Product Schema
class ProductSchema(BaseModel):
    """Product information schema"""
    name: str = Field(..., min_length=2, max_length=200)
    category: str = Field(..., min_length=2, max_length=50)
    weight_kg: float = Field(..., gt=0, le=1000)
    dimensions: Dict[str, float] = Field(...)  # length, width, height in cm
    declared_value: float = Field(..., gt=0, le=10000000)
    is_fragile: bool = Field(default=False)
    is_liquid: bool = Field(default=False)
    is_perishable: bool = Field(default=False)
    is_hazardous: bool = Field(default=False)
    special_instructions: Optional[str] = Field(None, max_length=1000)
    
    @validator('dimensions')
    def validate_dimensions(cls, v):
        required_keys = ['length', 'width', 'height']
        if not all(key in v for key in required_keys):
            raise ValueError('Dimensions must include length, width, and height')
        if any(val <= 0 for val in v.values()):
            raise ValueError('All dimensions must be positive')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Samsung Galaxy S24",
                "category": "Electronics",
                "weight_kg": 2.5,
                "dimensions": {"length": 30, "width": 20, "height": 10},
                "declared_value": 50000,
                "is_fragile": True
            }
        }

# Risk Analysis Schema
class RiskAnalysisSchema(BaseModel):
    """Risk analysis result schema"""
    overall_score: float = Field(..., ge=0, le=100)
    risk_level: RiskLevel = Field(...)
    factors: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    weather_impact: Dict[str, Any] = Field(default_factory=dict)
    address_confidence: float = Field(..., ge=0, le=100)
    delivery_complexity: str = Field(default="standard")
    ai_recommendation: DecisionType = Field(...)
    confidence_score: float = Field(..., ge=0, le=100)
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)
    model_version: str = Field(default="1.0")
    
    class Config:
        schema_extra = {
            "example": {
                "overall_score": 35.5,
                "risk_level": "low",
                "address_confidence": 85.2,
                "ai_recommendation": "dispatch",
                "confidence_score": 92.1
            }
        }

# Shipment Schema
class ShipmentSchema(BaseModel):
    """Main shipment document schema"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    shipment_id: str = Field(...)  # Unique business ID
    seller_id: PyObjectId = Field(...)
    
    # Product and delivery info
    product: ProductSchema = Field(...)
    pickup_address: AddressSchema = Field(...)
    delivery_address: AddressSchema = Field(...)
    recipient_name: str = Field(..., min_length=2, max_length=100)
    recipient_phone: str = Field(..., regex=r'^\+91[0-9]{10}$')
    
    # Business details
    payment_type: PaymentType = Field(...)
    cod_amount: Optional[float] = Field(None, ge=0)
    priority: Priority = Field(default=Priority.STANDARD)
    preferred_delivery_date: Optional[datetime] = None
    preferred_time_slot: Optional[str] = None
    
    # Status tracking
    current_status: ShipmentStatus = Field(default=ShipmentStatus.PENDING)
    status_history: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Risk and AI analysis
    risk_analysis: Optional[RiskAnalysisSchema] = None
    ai_decisions: List[Dict[str, Any]] = Field(default_factory=list)
    human_overrides: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Logistics
    assigned_vehicle: Optional[Dict[str, Any]] = None
    estimated_delivery: Optional[datetime] = None
    actual_pickup: Optional[datetime] = None
    actual_delivery: Optional[datetime] = None
    tracking_updates: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Financial
    total_cost: Optional[float] = Field(None, ge=0)
    cost_breakdown: Dict[str, float] = Field(default_factory=dict)
    
    # System metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: PyObjectId = Field(...)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Audit Log Schema
class AuditLogSchema(BaseModel):
    """Audit log for tracking all system actions"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId = Field(...)
    action: str = Field(...)  # create_shipment, override_decision, etc.
    entity_type: str = Field(...)  # shipment, user, etc.
    entity_id: str = Field(...)
    old_value: Optional[Dict[str, Any]] = None
    new_value: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Notification Schema
class NotificationSchema(BaseModel):
    """Customer and internal notifications"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    shipment_id: str = Field(...)
    recipient_phone: str = Field(...)
    recipient_email: Optional[str] = None
    message: str = Field(..., max_length=1000)
    notification_type: str = Field(...)  # sms, email, whatsapp, push
    channel: str = Field(...)  # twilio, sendgrid, etc.
    status: str = Field(default="pending")  # pending, sent, delivered, failed
    attempts: int = Field(default=0)
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# System Configuration Schema
class SystemConfigSchema(BaseModel):
    """System configuration and settings"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    config_key: str = Field(..., unique=True)
    config_value: Dict[str, Any] = Field(...)
    description: Optional[str] = None
    is_active: bool = Field(default=True)
    created_by: PyObjectId = Field(...)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Analytics Schema
class AnalyticsSchema(BaseModel):
    """Analytics and reporting data"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    metric_name: str = Field(...)
    metric_value: float = Field(...)
    dimensions: Dict[str, str] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    period: str = Field(...)  # hourly, daily, weekly, monthly
    calculated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Database validation functions
def validate_shipment_data(data: Dict[str, Any]) -> ShipmentSchema:
    """Validate shipment data against schema"""
    return ShipmentSchema(**data)

def validate_user_data(data: Dict[str, Any]) -> UserSchema:
    """Validate user data against schema"""
    return UserSchema(**data)

# Collection names
COLLECTIONS = {
    "users": "users",
    "shipments": "shipments", 
    "audit_logs": "audit_logs",
    "notifications": "notifications",
    "system_config": "system_config",
    "analytics": "analytics"
}