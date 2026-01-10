"""
Production API Client for LICS
Handles all backend communication with authentication and error handling
"""

import requests
import streamlit as st
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime, timedelta
import json
import time
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LICSAPIClient:
    """Production API client for LICS backend"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize API client with base URL"""
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.timeout = 30
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
            
            # Log request for debugging
            logger.info(f"{method} {endpoint} - Status: {response.status_code}")
            
            # Handle different response types
            if response.status_code == 204:  # No content
                return {"success": True}
            
            # Try to parse JSON response
            try:
                data = response.json()
            except ValueError:
                data = {"message": response.text}
            
            # Check for success
            if 200 <= response.status_code < 300:
                return {"success": True, "data": data}
            else:
                error_msg = data.get('error', data.get('detail', f'HTTP {response.status_code}'))
                return {"success": False, "error": error_msg, "status_code": response.status_code}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            return {"success": False, "error": f"Connection error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {"success": False, "error": f"Unexpected error: {str(e)}"}
    
    def set_auth_token(self, token: str):
        """Set authentication token for requests"""
        self.session.headers.update({
            'Authorization': f'Bearer {token}'
        })
    
    def clear_auth_token(self):
        """Clear authentication token"""
        self.session.headers.pop('Authorization', None)
    
    # Health and status endpoints
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health status"""
        return self._make_request('GET', '/health')
    
    # Authentication endpoints
    
    def register(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new user"""
        return self._make_request('POST', '/auth/register', json=user_data)
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login user and get JWT token"""
        login_data = {
            "username": username,
            "password": password
        }
        return self._make_request('POST', '/auth/login', json=login_data)
    
    def get_profile(self) -> Dict[str, Any]:
        """Get current user profile"""
        return self._make_request('GET', '/auth/profile')
    
    # Shipment endpoints
    
    def create_shipment(self, shipment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new shipment"""
        return self._make_request('POST', '/shipments', json=shipment_data)
    
    def get_shipments(self, skip: int = 0, limit: int = 50, status: Optional[str] = None) -> Dict[str, Any]:
        """Get list of shipments"""
        params = {"skip": skip, "limit": limit}
        if status:
            params["status"] = status
        return self._make_request('GET', '/shipments', params=params)
    
    def get_shipment(self, shipment_id: str) -> Dict[str, Any]:
        """Get specific shipment by ID"""
        return self._make_request('GET', f'/shipments/{shipment_id}')
    
    def update_shipment(self, shipment_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update shipment status and details"""
        return self._make_request('PUT', f'/shipments/{shipment_id}', json=update_data)
    
    # Notification endpoints
    
    def send_notification(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send manual SMS notification"""
        return self._make_request('POST', '/notifications/send', json=notification_data)
    
    def get_notification_history(self, limit: int = 50) -> Dict[str, Any]:
        """Get notification history"""
        params = {"limit": limit}
        return self._make_request('GET', '/notifications/history', params=params)
    
    # Analytics endpoints
    
    def get_dashboard_analytics(self) -> Dict[str, Any]:
        """Get dashboard analytics data"""
        return self._make_request('GET', '/analytics/dashboard')
    
    def get_shipment_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get shipment trends over time"""
        params = {"days": days}
        return self._make_request('GET', '/analytics/shipment-trends', params=params)

class MockAPIClient:
    """Mock API client for demo purposes"""
    
    def __init__(self, base_url="http://localhost:8000/api"):
        self.base_url = base_url
        
    def get_shipment_analysis(self, shipment_data):
        """Mock shipment analysis API call"""
        time.sleep(0.5)  # Simulate API delay
        
        # Simulate risk calculation
        risk_score = min(100, max(0, 
            shipment_data.get('weight', 1) * 3 +
            shipment_data.get('declared_value', 1000) / 100 +
            (15 if shipment_data.get('payment_mode') == 'Cash on Delivery (COD)' else 5) +
            random.randint(0, 20)
        ))
        
        return {
            "risk_score": int(risk_score),
            "weather_impact": random.uniform(0.1, 0.8),
            "address_confidence": random.uniform(0.7, 0.95),
            "recommended_action": "DISPATCH" if risk_score < 70 else "DELAY",
            "factors": {
                "weight_risk": min(15, shipment_data.get('weight', 1) * 3),
                "value_risk": min(20, shipment_data.get('declared_value', 1000) / 100),
                "payment_risk": 15 if shipment_data.get('payment_mode') == 'Cash on Delivery (COD)' else 5,
                "area_risk": random.randint(5, 15)
            }
        }
    
    def get_weather_data(self, pincode, date):
        """Mock weather API call"""
        time.sleep(0.3)  # Simulate API delay
        
        conditions = ["Clear", "Cloudy", "Light Rain", "Heavy Rain", "Overcast"]
        condition = random.choice(conditions)
        
        return {
            "condition": condition,
            "temperature": random.randint(20, 35),
            "humidity": random.randint(40, 80),
            "wind_speed": random.randint(5, 25),
            "precipitation_chance": random.randint(0, 80),
            "impact_factor": random.uniform(0.1, 0.9),
            "forecast": f"Weather for {pincode} on {date}"
        }
    
    def validate_address(self, address, pincode):
        """Mock address validation API call"""
        time.sleep(0.2)  # Simulate API delay
        
        return {
            "is_valid": True,
            "confidence": random.uniform(0.7, 0.95),
            "standardized_address": address,
            "landmark_found": random.choice([True, False]),
            "delivery_difficulty": random.choice(["Easy", "Moderate", "Difficult"])
        }
    
    def get_route_optimization(self, origin, destination, traffic_data=None):
        """Mock route optimization API call"""
        time.sleep(0.4)  # Simulate API delay
        
        return {
            "optimal_route": f"Route from {origin} to {destination}",
            "estimated_time": random.randint(30, 180),  # minutes
            "distance": random.uniform(5, 50),  # km
            "traffic_factor": random.uniform(1.0, 2.5),
            "alternative_routes": 2,
            "toll_charges": random.randint(0, 100)
        }
    
    def send_notification(self, customer_phone, message, notification_type="SMS"):
        """Mock notification API call"""
        time.sleep(0.1)  # Simulate API delay
        
        return {
            "success": True,
            "message_id": f"MSG{int(time.time())}{random.randint(100, 999)}",
            "delivery_status": "Sent",
            "timestamp": datetime.now().isoformat()
        }
    
    def track_shipment(self, shipment_id):
        """Mock shipment tracking API call"""
        time.sleep(0.3)  # Simulate API delay
        
        # Generate mock tracking data
        stages = ["order_placed", "processing", "dispatched", "in_transit", "out_for_delivery"]
        current_stage = random.choice(stages)
        
        locations = [
            "Order Processing Center", 
            "Distribution Hub - Zone A",
            "In Transit - Highway Route",
            "Local Distribution Center",
            "Out for Delivery"
        ]
        
        return {
            "shipment_id": shipment_id,
            "current_stage": current_stage,
            "current_location": random.choice(locations),
            "estimated_delivery": (datetime.now() + timedelta(hours=random.randint(2, 24))).isoformat(),
            "tracking_history": [
                {
                    "timestamp": (datetime.now() - timedelta(hours=i*2)).isoformat(),
                    "location": locations[min(i, len(locations)-1)],
                    "status": stages[min(i, len(stages)-1)]
                }
                for i in range(3)
            ]
        }
    
    def create_override(self, shipment_id, original_decision, new_decision, reason, manager_id):
        """Mock override creation API call"""
        time.sleep(0.2)  # Simulate API delay
        
        return {
            "override_id": f"OVR{int(time.time())}",
            "shipment_id": shipment_id,
            "original_decision": original_decision,
            "new_decision": new_decision,
            "reason": reason,
            "manager_id": manager_id,
            "timestamp": datetime.now().isoformat(),
            "status": "Applied"
        }
    
    def get_analytics_data(self, date_range, filters=None):
        """Mock analytics data API call"""
        time.sleep(0.8)  # Simulate API delay
        
        # Generate mock analytics data
        days = (date_range[1] - date_range[0]).days + 1
        data = []
        
        for i in range(days):
            date = date_range[0] + timedelta(days=i)
            daily_shipments = random.randint(20, 100)
            
            data.append({
                "date": date.isoformat(),
                "total_shipments": daily_shipments,
                "successful_deliveries": int(daily_shipments * random.uniform(0.85, 0.98)),
                "average_risk_score": random.randint(20, 80),
                "weather_delays": random.randint(0, 10),
                "overrides_count": random.randint(0, 5),
                "customer_satisfaction": random.uniform(4.0, 5.0)
            })
        
        return data
    
    def get_real_time_metrics(self):
        """Mock real-time metrics API call"""
        time.sleep(0.1)  # Simulate API delay
        
        return {
            "active_shipments": random.randint(30, 100),
            "pending_decisions": random.randint(0, 15),
            "high_risk_alerts": random.randint(0, 8),
            "system_health": {
                "risk_engine": random.choice(["Online", "Degraded", "Offline"]),
                "weather_api": random.choice(["Online", "Slow", "Offline"]),
                "notification_service": random.choice(["Online", "Degraded"]),
                "tracking_system": random.choice(["Online", "Slow"])
            },
            "performance_metrics": {
                "avg_processing_time": random.uniform(1.0, 5.0),
                "api_response_time": random.uniform(0.1, 2.0),
                "success_rate": random.uniform(0.9, 0.99)
            }
        }

# Singleton API client instance
@st.cache_resource
def get_api_client():
    """Get cached API client instance - returns production client by default"""
    # Try production client first, fallback to mock
    try:
        client = LICSAPIClient()
        # Test connection
        result = client.health_check()
        if result['success']:
            return client
    except:
        pass
    
    # Fallback to mock client
    return MockAPIClient()

# Authentication helper functions

def is_logged_in() -> bool:
    """Check if user is currently logged in"""
    return 'auth_token' in st.session_state and st.session_state.auth_token is not None

def get_current_user() -> Optional[Dict[str, Any]]:
    """Get current logged in user data"""
    return st.session_state.get('current_user')

def login_user(username: str, password: str) -> Dict[str, Any]:
    """Login user and store session data"""
    api_client = get_api_client()
    
    # Check if this is a production client
    if isinstance(api_client, LICSAPIClient):
        # Clear any existing auth
        api_client.clear_auth_token()
        
        # Attempt login
        result = api_client.login(username, password)
        
        if result['success']:
            token_data = result['data']
            
            # Store auth token
            st.session_state.auth_token = token_data['access_token']
            st.session_state.user_id = token_data['user_id']
            st.session_state.user_role = token_data['role']
            
            # Set token for API client
            api_client.set_auth_token(token_data['access_token'])
            
            # Get user profile
            profile_result = api_client.get_profile()
            if profile_result['success']:
                st.session_state.current_user = profile_result['data']
            
            logger.info(f"User logged in: {username}")
            return {"success": True, "message": "Login successful"}
        else:
            return result
    else:
        # Mock authentication for demo
        mock_users = {
            "admin": {"password": "admin123", "role": "admin", "name": "Administrator"},
            "dispatcher": {"password": "dispatch123", "role": "dispatcher", "name": "Dispatcher"},
            "driver": {"password": "driver123", "role": "driver", "name": "Driver"},
            "customer": {"password": "customer123", "role": "customer", "name": "Customer"}
        }
        
        if username in mock_users and mock_users[username]["password"] == password:
            user_data = mock_users[username]
            st.session_state.current_user = {
                "user_id": f"mock_{username}",
                "username": username,
                "role": user_data["role"],
                "full_name": user_data["name"],
                "email": f"{username}@example.com"
            }
            st.session_state.user_role = user_data["role"]
            return {"success": True, "message": "Login successful (Demo Mode)"}
        else:
            return {"success": False, "error": "Invalid credentials"}

def logout_user():
    """Logout current user and clear session"""
    api_client = get_api_client()
    
    # Clear API client auth if production
    if isinstance(api_client, LICSAPIClient):
        api_client.clear_auth_token()
    
    # Clear session state
    keys_to_clear = ['auth_token', 'user_id', 'user_role', 'current_user']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    logger.info("User logged out")

def register_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Register new user"""
    api_client = get_api_client()
    
    if isinstance(api_client, LICSAPIClient):
        result = api_client.register(user_data)
        
        if result['success']:
            # Auto-login after registration
            token_data = result['data']
            
            # Store auth token
            st.session_state.auth_token = token_data['access_token']
            st.session_state.user_id = token_data['user_id']
            st.session_state.user_role = token_data['role']
            
            # Set token for API client
            api_client.set_auth_token(token_data['access_token'])
            
            # Get user profile
            profile_result = api_client.get_profile()
            if profile_result['success']:
                st.session_state.current_user = profile_result['data']
            
            logger.info(f"User registered: {user_data['username']}")
        
        return result
    else:
        # Mock registration for demo
        return {"success": True, "message": "Registration successful (Demo Mode)"}

def ensure_authenticated():
    """Ensure user is authenticated, redirect to login if not"""
    if not is_logged_in():
        st.error("Please login to access this page")
        st.stop()
    
    # Set auth token for API client if logged in and production
    api_client = get_api_client()
    if isinstance(api_client, LICSAPIClient) and 'auth_token' in st.session_state:
        api_client.set_auth_token(st.session_state.auth_token)

def require_role(required_role: str) -> bool:
    """Check if current user has required role"""
    if not is_logged_in():
        return False
    
    user_role = st.session_state.get('user_role')
    return user_role == required_role or user_role == 'admin'

# Error handling helpers

def handle_api_error_new(result: Dict[str, Any], default_message: str = "Operation failed") -> None:
    """Handle API error responses with user-friendly messages"""
    if not result['success']:
        error_msg = result.get('error', default_message)
        status_code = result.get('status_code')
        
        if status_code == 401:
            st.error("Authentication failed. Please login again.")
            logout_user()
        elif status_code == 403:
            st.error("Access denied. You don't have permission for this action.")
        elif status_code == 404:
            st.error("Resource not found.")
        elif status_code == 400:
            st.error(f"Invalid request: {error_msg}")
        else:
            st.error(f"Error: {error_msg}")

def show_api_success(message: str = "Operation completed successfully") -> None:
    """Show success message for API operations"""
    st.success(message)

# Data formatting helpers

def format_datetime(dt_str: str) -> str:
    """Format datetime string for display"""
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return str(dt_str)

def format_shipment_status(status: str) -> str:
    """Format shipment status for display"""
    status_map = {
        'created': '📦 Created',
        'dispatch_ready': '🚚 Ready for Dispatch',
        'in_transit': '🚛 In Transit',
        'delivered': '✅ Delivered',
        'delayed': '⏰ Delayed',
        'cancelled': '❌ Cancelled',
        'exception': '⚠️ Exception'
    }
    return status_map.get(status, status.title())

def format_user_role(role: str) -> str:
    """Format user role for display"""
    role_map = {
        'admin': '👑 Administrator',
        'dispatcher': '📋 Dispatcher',
        'driver': '🚛 Driver',
        'customer': '👤 Customer'
    }
    return role_map.get(role, role.title())

# Testing function
def test_api_connection():
    """Test API connection and display status"""
    api_client = get_api_client()
    
    if isinstance(api_client, LICSAPIClient):
        with st.spinner("Testing API connection..."):
            result = api_client.health_check()
        
        if result['success']:
            health_data = result['data']
            st.success("✅ Production API connection successful!")
            
            with st.expander("API Health Details"):
                st.json(health_data)
        else:
            st.error(f"❌ Production API connection failed: {result['error']}")
            st.info("Falling back to demo mode. Make sure the FastAPI backend is running on http://localhost:8000")
    else:
        st.warning("⚠️ Running in Demo Mode - Using mock data")
        st.info("Start the FastAPI backend to use production mode")

def get_mock_api_client():
    """Get mock API client instance"""
    return MockAPIClient()

# Legacy utility functions for API integration
def handle_api_error(error, operation="API operation"):
    """Handle API errors gracefully"""
    st.error(f"❌ {operation} failed: {str(error)}")
    st.info("💡 This is a demo environment. In production, this would connect to real APIs.")

def show_api_loading(operation_name):
    """Show loading state for API operations"""
    with st.spinner(f"🔄 {operation_name}..."):
        time.sleep(0.5)  # Visual feedback
        return True

@st.cache_data(ttl=300)  # Cache for 5 minutes
def cached_weather_data(pincode, date):
    """Cached weather data to reduce API calls"""
    client = get_api_client()
    return client.get_weather_data(pincode, date)

@st.cache_data(ttl=60)  # Cache for 1 minute
def cached_real_time_metrics():
    """Cached real-time metrics"""
    client = get_api_client()
    return client.get_real_time_metrics()

def simulate_real_backend_calls():
    """Simulate calls to real backend APIs (for demo documentation)"""
    
    backend_apis = {
        "Risk Analysis": "POST /api/v1/shipments/analyze",
        "Weather Impact": "GET /api/v1/weather/impact/{pincode}",
        "Address Validation": "POST /api/v1/addresses/validate", 
        "Route Optimization": "POST /api/v1/routes/optimize",
        "Notification Send": "POST /api/v1/notifications/send",
        "Shipment Tracking": "GET /api/v1/shipments/{id}/track",
        "Override Create": "POST /api/v1/overrides",
        "Analytics Data": "GET /api/v1/analytics/data",
        "Real-time Metrics": "GET /api/v1/metrics/realtime"
    }
    
    return backend_apis

class DataCache:
    """Data caching utility for improved performance"""
    
    @staticmethod
    def cache_shipment_data(shipment_id, data, ttl_seconds=3600):
        """Cache shipment data"""
        cache_key = f"shipment_{shipment_id}"
        if 'data_cache' not in st.session_state:
            st.session_state['data_cache'] = {}
        
        st.session_state['data_cache'][cache_key] = {
            'data': data,
            'timestamp': time.time(),
            'ttl': ttl_seconds
        }
    
    @staticmethod
    def get_cached_shipment_data(shipment_id):
        """Get cached shipment data"""
        cache_key = f"shipment_{shipment_id}"
        
        if 'data_cache' not in st.session_state:
            return None
        
        cached_item = st.session_state['data_cache'].get(cache_key)
        if not cached_item:
            return None
        
        # Check if cache is expired
        if time.time() - cached_item['timestamp'] > cached_item['ttl']:
            del st.session_state['data_cache'][cache_key]
            return None
        
        return cached_item['data']
    
    @staticmethod
    def clear_cache():
        """Clear all cached data"""
        if 'data_cache' in st.session_state:
            st.session_state['data_cache'] = {}

def validate_api_response(response, required_fields):
    """Validate API response contains required fields"""
    if not isinstance(response, dict):
        return False
    
    for field in required_fields:
        if field not in response:
            return False
    
    return True

def format_api_error(error_response):
    """Format API error response for user display"""
    if isinstance(error_response, dict):
        error_message = error_response.get('message', 'Unknown error')
        error_code = error_response.get('code', 'ERR_UNKNOWN')
        return f"Error {error_code}: {error_message}"
    else:
        return str(error_response)

# Test functions for API connectivity
def test_api_connectivity():
    """Test API connectivity and response times"""
    client = get_api_client()
    
    tests = [
        ("Risk Analysis", lambda: client.get_shipment_analysis({"weight": 1, "declared_value": 1000})),
        ("Weather Data", lambda: client.get_weather_data("400001", "2024-01-15")),
        ("Address Validation", lambda: client.validate_address("Test Address", "400001")),
        ("Real-time Metrics", lambda: client.get_real_time_metrics())
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            start_time = time.time()
            response = test_func()
            end_time = time.time()
            
            results[test_name] = {
                "status": "✅ Success",
                "response_time": f"{(end_time - start_time)*1000:.0f}ms",
                "data_received": len(str(response)) > 0
            }
        except Exception as e:
            results[test_name] = {
                "status": "❌ Failed", 
                "response_time": "N/A",
                "error": str(e)
            }
    
    return results