"""
Phase 4.5: Authentication Middleware
====================================

FastAPI dependencies for JWT authentication and authorization
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.auth import decode_access_token, TokenData, UserRole
from database.connection import get_users_collection

# OAuth2 scheme (expects token in Authorization header)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Dependency to get current user from JWT token
    
    Raises HTTPException if token is invalid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode token
    token_data = decode_access_token(token)
    if token_data is None or token_data.username is None:
        raise credentials_exception
    
    # Get user from database
    users_collection = get_users_collection()
    user = users_collection.find_one({"username": token_data.username})
    
    if user is None:
        raise credentials_exception
    
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


def get_current_active_user(current_user: dict = Depends(get_current_user)):
    """
    Dependency to ensure user is active
    """
    if not current_user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


# ============================================================================
# ROLE-BASED ACCESS CONTROL (RBAC)
# ============================================================================

def require_role(required_role: str):
    """
    Dependency factory for role-based access
    
    Usage:
        @app.get("/admin", dependencies=[Depends(require_role(UserRole.SUPERVISOR))])
    """
    def role_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role")
        
        # Role hierarchy check
        role_hierarchy = {
            UserRole.SUPERVISOR: 4,
            UserRole.MANAGER: 3,
            UserRole.SELLER: 2,
            UserRole.CUSTOMER: 1
        }
        
        if role_hierarchy.get(user_role, 0) < role_hierarchy.get(required_role, 0):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {required_role}"
            )
        
        return current_user
    
    return role_checker


def require_manager_or_above(current_user: dict = Depends(get_current_user)):
    """Require manager, supervisor role"""
    return require_role(UserRole.MANAGER)(current_user)


def require_supervisor(current_user: dict = Depends(get_current_user)):
    """Require supervisor role"""
    return require_role(UserRole.SUPERVISOR)(current_user)


# ============================================================================
# OPTIONAL AUTHENTICATION
# ============================================================================

async def get_current_user_optional(token: Optional[str] = Depends(oauth2_scheme)):
    """
    Get current user if token is provided, otherwise return None
    Useful for endpoints that work with or without authentication
    """
    if token is None:
        return None
    
    try:
        return get_current_user(token)
    except HTTPException:
        return None
