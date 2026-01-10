"""
JWT Authentication System - Production Implementation
Secure password hashing and token management
"""

import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthenticationSystem:
    """
    Production-grade authentication system with JWT tokens
    """
    
    def __init__(self):
        # Password hashing context
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # JWT configuration - support both formats
        self.secret_key = os.getenv("JWT_SECRET_KEY")
        self.algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        
        # Support both JWT_EXPIRATION_HOURS and ACCESS_TOKEN_EXPIRE_MINUTES for compatibility
        expire_minutes = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
        expire_hours = os.getenv("JWT_EXPIRATION_HOURS")
        
        if expire_minutes:
            self.expiration_hours = int(expire_minutes) / 60.0
        elif expire_hours:
            self.expiration_hours = int(expire_hours)
        else:
            self.expiration_hours = 24  # Default 24 hours
        
        if not self.secret_key:
            raise ValueError("JWT_SECRET_KEY not found in environment variables")
        
        logger.info("🔐 Authentication system initialized")
    
    # ==================== PASSWORD MANAGEMENT ====================
    
    def hash_password(self, password: str) -> str:
        """Hash a password securely"""
        try:
            hashed = self.pwd_context.hash(password)
            logger.info("🔒 Password hashed successfully")
            return hashed
        except Exception as e:
            logger.error(f"❌ Failed to hash password: {str(e)}")
            raise
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        try:
            is_valid = self.pwd_context.verify(plain_password, hashed_password)
            if is_valid:
                logger.info("✅ Password verification successful")
            else:
                logger.warning("❌ Password verification failed")
            return is_valid
        except Exception as e:
            logger.error(f"❌ Password verification error: {str(e)}")
            return False
    
    # ==================== JWT TOKEN MANAGEMENT ====================
    
    def create_access_token(self, user_data: Dict[str, Any]) -> str:
        """Create a JWT access token"""
        try:
            # Token payload
            expires = datetime.now(timezone.utc) + timedelta(hours=self.expiration_hours)
            
            token_data = {
                "sub": user_data["username"],  # Subject (username)
                "role": user_data["role"],
                "full_name": user_data["full_name"],
                "exp": expires,
                "iat": datetime.now(timezone.utc),
                "type": "access_token"
            }
            
            # Create token
            token = jwt.encode(token_data, self.secret_key, algorithm=self.algorithm)
            
            logger.info(f"🎫 Access token created for: {user_data['username']}")
            return token
            
        except Exception as e:
            logger.error(f"❌ Failed to create access token: {str(e)}")
            raise
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token"""
        try:
            # Decode token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check token type
            if payload.get("type") != "access_token":
                logger.warning("❌ Invalid token type")
                return None
            
            # Check expiration
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp, timezone.utc) < datetime.now(timezone.utc):
                logger.warning("❌ Token expired")
                return None
            
            logger.info(f"✅ Token verified for: {payload.get('sub')}")
            return payload
            
        except JWTError as e:
            logger.warning(f"❌ JWT error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"❌ Token verification error: {str(e)}")
            return None
    
    def refresh_token(self, token: str) -> Optional[str]:
        """Refresh an access token"""
        try:
            # Verify current token
            payload = self.verify_token(token)
            if not payload:
                return None
            
            # Create new token with same data
            user_data = {
                "username": payload["sub"],
                "role": payload["role"],
                "full_name": payload["full_name"]
            }
            
            new_token = self.create_access_token(user_data)
            logger.info(f"🔄 Token refreshed for: {user_data['username']}")
            
            return new_token
            
        except Exception as e:
            logger.error(f"❌ Failed to refresh token: {str(e)}")
            return None
    
    # ==================== USER AUTHENTICATION ====================
    
    async def authenticate_user(self, username: str, password: str, db_instance) -> Optional[Dict[str, Any]]:
        """Authenticate user with username and password"""
        try:
            # Get user from database
            user = await db_instance.get_user_by_username(username)
            if not user:
                logger.warning(f"❌ User not found: {username}")
                return None
            
            # Check if user is active
            if not user.get("is_active", True):
                logger.warning(f"❌ User account disabled: {username}")
                return None
            
            # Verify password
            if not self.verify_password(password, user["password_hash"]):
                logger.warning(f"❌ Invalid password for: {username}")
                return None
            
            # Update last login
            await db_instance.update_last_login(username)
            
            # Remove password hash from returned data
            user_data = {k: v for k, v in user.items() if k != "password_hash"}
            
            logger.info(f"✅ User authenticated successfully: {username}")
            return user_data
            
        except Exception as e:
            logger.error(f"❌ Authentication error: {str(e)}")
            return None
    
    def create_login_response(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """Create login response with token"""
        try:
            # Create access token
            access_token = self.create_access_token(user)
            
            # Calculate expiration time
            expires_at = datetime.now(timezone.utc) + timedelta(hours=self.expiration_hours)
            
            response = {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_at": expires_at.isoformat(),
                "user": {
                    "username": user["username"],
                    "role": user["role"],
                    "full_name": user["full_name"]
                }
            }
            
            logger.info(f"📤 Login response created for: {user['username']}")
            return response
            
        except Exception as e:
            logger.error(f"❌ Failed to create login response: {str(e)}")
            raise
    
    # ==================== ROLE-BASED ACCESS CONTROL ====================
    
    def check_permission(self, user_role: str, required_permissions: list) -> bool:
        """Check if user role has required permissions"""
        
        # Define role permissions
        role_permissions = {
            "Seller": [
                "create_shipment",
                "view_own_shipments",
                "update_own_shipments"
            ],
            "Manager": [
                "create_shipment",
                "view_own_shipments", 
                "update_own_shipments",
                "view_all_shipments",
                "approve_shipments",
                "override_decisions",
                "send_notifications",
                "view_team_analytics"
            ],
            "Supervisor": [
                "view_all_shipments",
                "view_analytics",
                "view_reports",
                "export_data"
            ]
        }
        
        user_permissions = role_permissions.get(user_role, [])
        
        # Check if user has all required permissions
        has_permission = all(perm in user_permissions for perm in required_permissions)
        
        if has_permission:
            logger.info(f"✅ Permission granted for {user_role}: {required_permissions}")
        else:
            logger.warning(f"❌ Permission denied for {user_role}: {required_permissions}")
        
        return has_permission
    
    def require_role(self, allowed_roles: list, user_role: str) -> bool:
        """Check if user role is in allowed roles"""
        has_role = user_role in allowed_roles
        
        if has_role:
            logger.info(f"✅ Role authorized: {user_role}")
        else:
            logger.warning(f"❌ Role not authorized: {user_role} (allowed: {allowed_roles})")
        
        return has_role
    
    # ==================== SESSION MANAGEMENT ====================
    
    def extract_user_from_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Extract user information from token"""
        try:
            payload = self.verify_token(token)
            if not payload:
                return None
            
            return {
                "username": payload["sub"],
                "role": payload["role"],
                "full_name": payload["full_name"]
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to extract user from token: {str(e)}")
            return None
    
    def is_token_expired(self, token: str) -> bool:
        """Check if token is expired"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            exp = payload.get("exp")
            
            if exp:
                expiration_time = datetime.fromtimestamp(exp, timezone.utc)
                return datetime.now(timezone.utc) > expiration_time
            
            return True  # No expiration means expired
            
        except JWTError:
            return True  # Invalid token is considered expired
        except Exception:
            return True
    
    def get_token_expiration(self, token: str) -> Optional[datetime]:
        """Get token expiration datetime"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            exp = payload.get("exp")
            
            if exp:
                return datetime.fromtimestamp(exp, timezone.utc)
            
            return None
            
        except JWTError:
            return None
        except Exception:
            return None

# Global authentication instance
auth = AuthenticationSystem()

# Export for easy importing
__all__ = ["auth", "AuthenticationSystem"]