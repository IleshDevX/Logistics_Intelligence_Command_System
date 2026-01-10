"""
Production FastAPI Backend for LICS
Complete backend server with authentication, database, and notifications
"""

import os
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, status, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from pydantic import BaseModel, EmailStr, validator
import asyncio
from dotenv import load_dotenv

# Import our custom modules
import sys
sys.path.append('.')
from database.mongodb import LICSDatabase
from auth.jwt_auth import AuthenticationSystem
from notifications.sms_notifier import LICSNotificationManager, NotificationType, Priority

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
db = None
auth_system = None
notifier = None
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    global db, auth_system, notifier
    
    try:
        # Initialize database connection
        db = LICSDatabase()
        await db.connect()
        logger.info("Database connected successfully")
        
        # Initialize authentication system
        auth_system = AuthenticationSystem()
        logger.info("Authentication system initialized")
        
        # Initialize notification manager
        notifier = LICSNotificationManager()
        logger.info("Notification manager initialized")
        
        yield
        
    except Exception as e:
        logger.error(f"Startup error: {str(e)}")
        raise
    finally:
        # Cleanup on shutdown
        if db:
            await db.close()
            logger.info("Database connection closed")

# Create FastAPI app
app = FastAPI(
    title="LICS Backend API",
    description="Production Logistics Intelligence & Command System Backend",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API requests/responses

class UserRegistration(BaseModel):
    """User registration request model"""
    username: str
    email: EmailStr
    password: str
    full_name: str
    role: str = "customer"
    phone: Optional[str] = None
    
    @validator('role')
    def validate_role(cls, v):
        allowed_roles = ['admin', 'dispatcher', 'driver', 'customer']
        if v not in allowed_roles:
            raise ValueError(f'Role must be one of: {allowed_roles}')
        return v

class UserLogin(BaseModel):
    """User login request model"""
    username: str
    password: str

class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    role: str

class UserProfile(BaseModel):
    """User profile response model"""
    user_id: str
    username: str
    email: str
    full_name: str
    role: str
    phone: Optional[str]
    created_at: datetime
    is_active: bool

class ShipmentCreate(BaseModel):
    """Shipment creation request model"""
    customer_id: str
    pickup_address: str
    delivery_address: str
    package_details: Dict[str, Any]
    special_instructions: Optional[str] = None
    priority: str = "normal"
    
    @validator('priority')
    def validate_priority(cls, v):
        allowed_priorities = ['low', 'normal', 'high', 'urgent']
        if v not in allowed_priorities:
            raise ValueError(f'Priority must be one of: {allowed_priorities}')
        return v

class ShipmentUpdate(BaseModel):
    """Shipment update request model"""
    status: Optional[str] = None
    current_location: Optional[str] = None
    estimated_delivery: Optional[datetime] = None
    actual_delivery: Optional[datetime] = None
    driver_notes: Optional[str] = None

class NotificationRequest(BaseModel):
    """Notification request model"""
    phone: str
    notification_type: str
    shipment_id: Optional[str] = None
    message_data: Dict[str, Any] = {}

# Dependency functions

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    token = credentials.credentials
    
    try:
        payload = auth_system.verify_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        user = await db.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
        
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

def require_role(required_role: str):
    """Dependency factory for role-based access control"""
    async def check_role(current_user = Depends(get_current_user)):
        if current_user['role'] != required_role and current_user['role'] != 'admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role}"
            )
        return current_user
    return check_role

# API Routes

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "LICS Backend API is running",
        "version": "1.0.0",
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    try:
        # Check database connection
        db_status = await db.health_check()
        
        return {
            "status": "healthy",
            "database": db_status,
            "timestamp": datetime.now().isoformat(),
            "services": {
                "authentication": "operational",
                "notifications": "operational",
                "database": "operational"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

# Authentication endpoints

@app.post("/auth/register", response_model=TokenResponse)
async def register_user(user_data: UserRegistration):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = await db.get_user_by_username(user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        existing_email = await db.get_user_by_email(user_data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = auth_system.hash_password(user_data.password)
        
        # Create user document
        user_doc = {
            "username": user_data.username,
            "email": user_data.email,
            "password_hash": hashed_password,
            "full_name": user_data.full_name,
            "role": user_data.role,
            "phone": user_data.phone,
            "is_active": True,
            "created_at": datetime.now(),
            "last_login": None
        }
        
        # Insert user into database
        user_id = await db.create_user(user_doc)
        
        # Generate JWT token
        token_data = {
            "sub": str(user_id),
            "username": user_data.username,
            "role": user_data.role
        }
        
        access_token = auth_system.create_access_token(token_data)
        
        # Update last login
        await db.users.update_one(
            {"_id": user_id},
            {"$set": {"last_login": datetime.now()}}
        )
        
        logger.info(f"User registered successfully: {user_data.username}")
        
        # Get token expiration from environment - support both formats
        expire_minutes = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
        expire_hours = os.getenv("JWT_EXPIRATION_HOURS")
        
        if expire_minutes:
            expires_in_seconds = int(expire_minutes) * 60
        elif expire_hours:
            expires_in_seconds = int(expire_hours) * 3600
        else:
            expires_in_seconds = 24 * 3600  # Default 24 hours
        
        return TokenResponse(
            access_token=access_token,
            expires_in=expires_in_seconds,
            user_id=str(user_id),
            role=user_data.role
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@app.post("/auth/login", response_model=TokenResponse)
async def login_user(login_data: UserLogin):
    """Authenticate user and return JWT token"""
    try:
        # Get user from database
        user = await db.get_user_by_username(login_data.username)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Verify password
        if not auth_system.verify_password(login_data.password, user['password_hash']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        if not user['is_active']:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated"
            )
        
        # Generate JWT token
        token_data = {
            "sub": str(user['_id']),
            "username": user['username'],
            "role": user['role']
        }
        
        access_token = auth_system.create_access_token(token_data)
        
        # Update last login
        await db.users.update_one(
            {"_id": user['_id']},
            {"$set": {"last_login": datetime.now()}}
        )
        
        logger.info(f"User logged in successfully: {login_data.username}")
        
        # Get token expiration from environment - support both formats
        expire_minutes = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
        expire_hours = os.getenv("JWT_EXPIRATION_HOURS")
        
        if expire_minutes:
            expires_in_seconds = int(expire_minutes) * 60
        elif expire_hours:
            expires_in_seconds = int(expire_hours) * 3600
        else:
            expires_in_seconds = 24 * 3600  # Default 24 hours
        
        return TokenResponse(
            access_token=access_token,
            expires_in=expires_in_seconds,
            user_id=str(user['_id']),
            role=user['role']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@app.get("/auth/profile", response_model=UserProfile)
async def get_user_profile(current_user = Depends(get_current_user)):
    """Get current user profile"""
    return UserProfile(
        user_id=str(current_user['_id']),
        username=current_user['username'],
        email=current_user['email'],
        full_name=current_user['full_name'],
        role=current_user['role'],
        phone=current_user.get('phone'),
        created_at=current_user['created_at'],
        is_active=current_user['is_active']
    )

# Shipment endpoints

@app.post("/shipments")
async def create_shipment(
    shipment_data: ShipmentCreate,
    current_user = Depends(get_current_user)
):
    """Create a new shipment"""
    try:
        # Create shipment document
        shipment_doc = {
            "customer_id": shipment_data.customer_id,
            "pickup_address": shipment_data.pickup_address,
            "delivery_address": shipment_data.delivery_address,
            "package_details": shipment_data.package_details,
            "special_instructions": shipment_data.special_instructions,
            "priority": shipment_data.priority,
            "status": "created",
            "created_by": str(current_user['_id']),
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "tracking_events": [{
                "status": "created",
                "timestamp": datetime.now(),
                "location": "System",
                "notes": "Shipment created"
            }]
        }
        
        # Insert shipment into database
        shipment_id = await db.create_shipment(shipment_doc)
        shipment_doc['_id'] = shipment_id
        
        # Send SMS notification if customer phone is available
        customer = await db.get_user_by_id(shipment_data.customer_id)
        if customer and customer.get('phone'):
            try:
                await notifier.notify_shipment_created(
                    phone=customer['phone'],
                    shipment_id=str(shipment_id)
                )
            except Exception as e:
                logger.warning(f"Failed to send SMS notification: {str(e)}")
        
        logger.info(f"Shipment created successfully: {shipment_id}")
        
        return {
            "shipment_id": str(shipment_id),
            "status": "created",
            "message": "Shipment created successfully"
        }
        
    except Exception as e:
        logger.error(f"Shipment creation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create shipment"
        )

@app.get("/shipments")
async def get_shipments(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    current_user = Depends(get_current_user)
):
    """Get shipments with filtering"""
    try:
        # Build filter based on user role
        filter_query = {}
        
        if current_user['role'] == 'customer':
            filter_query['customer_id'] = str(current_user['_id'])
        elif status:
            filter_query['status'] = status
        
        shipments = await db.get_shipments(filter_query, skip, limit)
        
        return {
            "shipments": shipments,
            "total": len(shipments),
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Error fetching shipments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch shipments"
        )

@app.get("/shipments/{shipment_id}")
async def get_shipment(
    shipment_id: str,
    current_user = Depends(get_current_user)
):
    """Get specific shipment by ID"""
    try:
        shipment = await db.get_shipment_by_id(shipment_id)
        
        if not shipment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shipment not found"
            )
        
        # Check access permissions
        if (current_user['role'] == 'customer' and 
            shipment['customer_id'] != str(current_user['_id'])):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return shipment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching shipment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch shipment"
        )

@app.put("/shipments/{shipment_id}")
async def update_shipment(
    shipment_id: str,
    update_data: ShipmentUpdate,
    current_user = Depends(require_role("dispatcher"))
):
    """Update shipment status and details"""
    try:
        # Get existing shipment
        shipment = await db.get_shipment_by_id(shipment_id)
        if not shipment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shipment not found"
            )
        
        # Prepare update document
        update_doc = {"updated_at": datetime.now()}
        
        if update_data.status:
            update_doc['status'] = update_data.status
            
            # Add tracking event
            tracking_event = {
                "status": update_data.status,
                "timestamp": datetime.now(),
                "location": update_data.current_location or "Unknown",
                "notes": update_data.driver_notes or f"Status updated to {update_data.status}",
                "updated_by": str(current_user['_id'])
            }
            update_doc['$push'] = {"tracking_events": tracking_event}
        
        if update_data.current_location:
            update_doc['current_location'] = update_data.current_location
        
        if update_data.estimated_delivery:
            update_doc['estimated_delivery'] = update_data.estimated_delivery
        
        if update_data.actual_delivery:
            update_doc['actual_delivery'] = update_data.actual_delivery
        
        # Update shipment in database
        await db.update_shipment(shipment_id, update_doc)
        
        # Send SMS notifications based on status
        customer = await db.get_user_by_id(shipment['customer_id'])
        if customer and customer.get('phone') and update_data.status:
            try:
                if update_data.status == 'in_transit':
                    await notifier.notify_in_transit(
                        phone=customer['phone'],
                        shipment_id=shipment_id,
                        current_location=update_data.current_location or "In Transit",
                        eta=update_data.estimated_delivery.strftime("%Y-%m-%d %H:%M") if update_data.estimated_delivery else "TBD"
                    )
                elif update_data.status == 'delivered':
                    await notifier.notify_delivered(
                        phone=customer['phone'],
                        shipment_id=shipment_id
                    )
            except Exception as e:
                logger.warning(f"Failed to send SMS notification: {str(e)}")
        
        logger.info(f"Shipment updated successfully: {shipment_id}")
        
        return {
            "shipment_id": shipment_id,
            "status": "updated",
            "message": "Shipment updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating shipment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update shipment"
        )

# Notification endpoints

@app.post("/notifications/send")
async def send_notification(
    notification_data: NotificationRequest,
    current_user = Depends(require_role("dispatcher"))
):
    """Send manual SMS notification"""
    try:
        # Map notification type to method
        notification_methods = {
            'shipment_created': notifier.notify_shipment_created,
            'dispatch_ready': notifier.notify_dispatch_ready,
            'in_transit': notifier.notify_in_transit,
            'delivered': notifier.notify_delivered,
            'delayed': notifier.notify_delayed,
            'exception': notifier.notify_exception,
            'weather_alert': notifier.notify_weather_alert,
            'emergency': notifier.notify_emergency
        }
        
        if notification_data.notification_type not in notification_methods:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid notification type"
            )
        
        # Send notification
        method = notification_methods[notification_data.notification_type]
        result = await method(
            phone=notification_data.phone,
            **notification_data.message_data
        )
        
        return {
            "status": "sent" if result.get('success') else "failed",
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending notification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send notification"
        )

@app.get("/notifications/history")
async def get_notification_history(
    limit: int = 50,
    current_user = Depends(require_role("dispatcher"))
):
    """Get notification history"""
    try:
        history = notifier.get_notification_history(limit)
        stats = notifier.get_notification_stats()
        
        return {
            "history": history,
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Error fetching notification history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch notification history"
        )

# Analytics endpoints

@app.get("/analytics/dashboard")
async def get_dashboard_analytics(
    current_user = Depends(require_role("admin"))
):
    """Get dashboard analytics data"""
    try:
        analytics = await db.get_analytics_summary()
        return analytics
        
    except Exception as e:
        logger.error(f"Error fetching analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch analytics"
        )

@app.get("/analytics/shipment-trends")
async def get_shipment_trends(
    days: int = 30,
    current_user = Depends(require_role("admin"))
):
    """Get shipment trends over time"""
    try:
        trends = await db.get_shipment_trends(days)
        return trends
        
    except Exception as e:
        logger.error(f"Error fetching shipment trends: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch shipment trends"
        )

# Error handlers

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler"""
    logger.warning(f"HTTP {exc.status_code}: {exc.detail} - {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler"""
    logger.error(f"Unhandled exception: {str(exc)} - {request.url}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    # Run the server
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )