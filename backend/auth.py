"""
Phase 4: JWT Authentication & User Management
=============================================

Implements:
- User roles (seller, manager, supervisor, customer)
- Password hashing with bcrypt
- JWT token generation and verification
- Authentication middleware
"""

from datetime import datetime, timedelta
from typing import Optional, Dict
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr
import secrets
import os

# ============================================================================
# CONFIGURATION
# ============================================================================

def _get_jwt_config():
    """Get JWT configuration from Streamlit secrets or environment"""
    try:
        # Try Streamlit secrets first (for Streamlit Cloud)
        import streamlit as st
        if hasattr(st, 'secrets') and 'jwt' in st.secrets:
            return (
                st.secrets["jwt"]["secret_key"],
                st.secrets["jwt"].get("algorithm", "HS256"),
                st.secrets["jwt"].get("access_token_expire_minutes", 1440)
            )
    except (ImportError, FileNotFoundError, KeyError):
        pass
    
    # Fallback to environment variables (for local/FastAPI)
    return (
        os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32)),
        "HS256",
        60 * 24  # 24 hours
    )

# JWT Configuration - Streamlit compatible
SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES = _get_jwt_config()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ============================================================================
# USER ROLES (Phase 4.1)
# ============================================================================

class UserRole:
    """User roles for RBAC (Role-Based Access Control)"""
    SELLER = "seller"        # Creates shipments, views own data
    MANAGER = "manager"      # Approves/overrides AI decisions
    SUPERVISOR = "supervisor"  # Full system access, analytics
    CUSTOMER = "customer"    # Views own shipment status


VALID_ROLES = [UserRole.SELLER, UserRole.MANAGER, UserRole.SUPERVISOR, UserRole.CUSTOMER]


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class UserBase(BaseModel):
    """Base user model"""
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    role: str


class UserCreate(UserBase):
    """User creation model (includes password)"""
    password: str


class UserInDB(UserBase):
    """User model as stored in database"""
    password_hash: str
    is_active: bool = True
    created_at: datetime
    last_login: Optional[datetime] = None


class User(UserBase):
    """User model for API responses (no password)"""
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user: User


class TokenData(BaseModel):
    """Data stored in JWT token"""
    username: Optional[str] = None
    role: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request model"""
    username: str
    password: str


# ============================================================================
# PASSWORD HASHING (Phase 4.3)
# ============================================================================

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Stored password hash
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


# ============================================================================
# JWT TOKEN MANAGEMENT (Phase 4.2)
# ============================================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Data to encode in token (username, role, etc.)
        expires_delta: Optional expiration time
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow()  # Issued at
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[TokenData]:
    """
    Decode and verify a JWT token
    
    Args:
        token: JWT token to decode
        
    Returns:
        TokenData if valid, None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        
        if username is None:
            return None
            
        return TokenData(username=username, role=role)
        
    except JWTError:
        return None


# ============================================================================
# USER AUTHENTICATION
# ============================================================================

def authenticate_user(users_collection, username: str, password: str) -> Optional[Dict]:
    """
    Authenticate a user with username and password
    
    Args:
        users_collection: MongoDB users collection
        username: Username to authenticate
        password: Plain text password
        
    Returns:
        User dict if authenticated, None otherwise
    """
    user = users_collection.find_one({"username": username})
    
    if not user:
        return None
    
    if not verify_password(password, user["password_hash"]):
        return None
    
    if not user.get("is_active", True):
        return None
    
    return user


def create_user(users_collection, user_data: UserCreate) -> Dict:
    """
    Create a new user in the database
    
    Args:
        users_collection: MongoDB users collection
        user_data: User data (UserCreate model)
        
    Returns:
        Created user dict
        
    Raises:
        ValueError: If username or email already exists
    """
    # Check if username exists
    if users_collection.find_one({"username": user_data.username}):
        raise ValueError("Username already exists")
    
    # Check if email exists
    if users_collection.find_one({"email": user_data.email}):
        raise ValueError("Email already exists")
    
    # Validate role
    if user_data.role not in VALID_ROLES:
        raise ValueError(f"Invalid role. Must be one of: {', '.join(VALID_ROLES)}")
    
    # Create user document
    user_doc = {
        "username": user_data.username,
        "email": user_data.email,
        "full_name": user_data.full_name,
        "role": user_data.role,
        "password_hash": hash_password(user_data.password),
        "is_active": True,
        "created_at": datetime.utcnow(),
        "last_login": None
    }
    
    # Insert into database
    result = users_collection.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id
    
    return user_doc


def update_last_login(users_collection, username: str):
    """Update user's last login timestamp"""
    users_collection.update_one(
        {"username": username},
        {"$set": {"last_login": datetime.utcnow()}}
    )


# ============================================================================
# ROLE PERMISSIONS
# ============================================================================

def check_permission(user_role: str, required_role: str) -> bool:
    """
    Check if user has required permission
    
    Role hierarchy: supervisor > manager > seller > customer
    """
    role_hierarchy = {
        UserRole.SUPERVISOR: 4,
        UserRole.MANAGER: 3,
        UserRole.SELLER: 2,
        UserRole.CUSTOMER: 1
    }
    
    return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)
