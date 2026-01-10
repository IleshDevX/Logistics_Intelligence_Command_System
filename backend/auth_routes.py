"""
Phase 4: Authentication Routes
==============================

Endpoints:
- POST /api/auth/register - Register new user
- POST /api/auth/login - Login and get JWT token
- GET /api/auth/me - Get current user info
- POST /api/auth/logout - Logout (client-side only)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.auth import (
    UserCreate, User, Token, LoginRequest,
    create_access_token, authenticate_user, create_user,
    update_last_login, ACCESS_TOKEN_EXPIRE_MINUTES, UserRole
)
from backend.middleware import get_current_user
from database.connection import get_users_collection

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# ============================================================================
# REGISTRATION ENDPOINT (Phase 4.6)
# ============================================================================

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    """
    Register a new user
    
    **Roles:**
    - seller: Creates shipments, views own data
    - manager: Approves/overrides AI decisions
    - supervisor: Full system access, analytics
    - customer: Views own shipment status
    
    **Returns:**
    - User object (without password)
    """
    users_collection = get_users_collection()
    
    try:
        # Create user
        created_user = create_user(users_collection, user_data)
        
        # Return user without password
        return User(
            username=created_user["username"],
            email=created_user["email"],
            full_name=created_user.get("full_name"),
            role=created_user["role"],
            is_active=created_user["is_active"],
            created_at=created_user["created_at"],
            last_login=created_user.get("last_login")
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )


# ============================================================================
# LOGIN ENDPOINT (Phase 4.4)
# ============================================================================

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login with username and password
    
    **Returns:**
    - JWT access token
    - Token type (bearer)
    - User information
    
    **JWT Flow:**
    1. User sends username + password
    2. Backend verifies credentials
    3. Backend generates JWT token
    4. Frontend stores token
    5. Frontend sends token with every API request
    """
    users_collection = get_users_collection()
    
    # Authenticate user
    user = authenticate_user(users_collection, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    update_last_login(users_collection, user["username"])
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=access_token_expires
    )
    
    # Return token and user info
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=User(
            username=user["username"],
            email=user["email"],
            full_name=user.get("full_name"),
            role=user["role"],
            is_active=user["is_active"],
            created_at=user["created_at"],
            last_login=user.get("last_login")
        )
    )


# Alternative login endpoint (JSON body instead of form data)
@router.post("/login-json", response_model=Token)
async def login_json(credentials: LoginRequest):
    """
    Login with JSON body (alternative to form data)
    
    Useful for testing with Swagger UI or REST clients
    """
    users_collection = get_users_collection()
    
    user = authenticate_user(users_collection, credentials.username, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    update_last_login(users_collection, user["username"])
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=User(
            username=user["username"],
            email=user["email"],
            full_name=user.get("full_name"),
            role=user["role"],
            is_active=user["is_active"],
            created_at=user["created_at"],
            last_login=user.get("last_login")
        )
    )


# ============================================================================
# PROTECTED ENDPOINTS
# ============================================================================

@router.get("/me", response_model=User)
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Get current user information
    
    **Requires:** Valid JWT token in Authorization header
    
    **Returns:**
    - Current user details
    """
    return User(
        username=current_user["username"],
        email=current_user["email"],
        full_name=current_user.get("full_name"),
        role=current_user["role"],
        is_active=current_user["is_active"],
        created_at=current_user["created_at"],
        last_login=current_user.get("last_login")
    )


@router.post("/logout")
async def logout():
    """
    Logout endpoint (client-side token removal)
    
    **Note:** JWT tokens are stateless, so logout is handled client-side
    by removing the token from storage (localStorage, cookies, etc.)
    
    **Client should:**
    1. Remove token from storage
    2. Redirect to login page
    3. Clear any cached user data
    """
    return {
        "message": "Logout successful",
        "instructions": "Remove JWT token from client storage"
    }


@router.get("/health")
async def auth_health():
    """Authentication service health check"""
    return {
        "status": "healthy",
        "service": "Authentication",
        "jwt_enabled": True,
        "roles": [UserRole.SELLER, UserRole.MANAGER, UserRole.SUPERVISOR, UserRole.CUSTOMER]
    }
