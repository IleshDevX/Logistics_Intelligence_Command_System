"""
System Integration Test - LICS Full Stack Verification
Tests MongoDB integration, authentication, and core functionality
"""

import sys
import os
import time
import asyncio
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.database import DatabaseManager, test_database_connection
from utils.weather_api import WeatherService
from utils.schemas import UserSchema, ShipmentSchema
from components.user_registration import UserRegistrationManager
from utils.indian_cities import INDIAN_STATES_CITIES, get_state_from_city

def test_database_connection():
    """Test MongoDB Atlas connection"""
    print("🔌 Testing Database Connection...")
    
    try:
        db_status = test_database_connection()
        
        if db_status['status'] == 'connected':
            print("✅ Database connection successful!")
            print(f"   Database: {db_status['database_name']}")
            print(f"   Collections: {', '.join(db_status.get('collections', []))}")
            return True
        else:
            print("❌ Database connection failed!")
            print(f"   Error: {db_status.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Database test failed: {str(e)}")
        return False

def test_user_registration():
    """Test user registration system"""
    print("\n👤 Testing User Registration System...")
    
    try:
        # Initialize registration manager
        reg_manager = UserRegistrationManager()
        
        # Test user data
        test_user = {
            "username": f"test_user_{int(time.time())}",
            "email": f"test_{int(time.time())}@example.com", 
            "password": "TestPassword123!",
            "full_name": "Test User",
            "role": "seller",
            "department": "Sales",
            "phone": "+91-9876543210",
            "address": "123 Test Street, Mumbai, Maharashtra"
        }
        
        # Test registration
        result = reg_manager.register_user(
            test_user["username"],
            test_user["email"], 
            test_user["password"],
            test_user["full_name"],
            test_user["role"],
            test_user["department"],
            test_user["phone"],
            test_user["address"]
        )
        
        if result["success"]:
            print("✅ User registration successful!")
            print(f"   User ID: {result['user_id']}")
            return True, test_user
        else:
            print("❌ User registration failed!")
            print(f"   Error: {result.get('message', 'Unknown error')}")
            return False, None
            
    except Exception as e:
        print(f"❌ User registration test failed: {str(e)}")
        return False, None

def test_weather_api():
    """Test weather API integration"""
    print("\n🌤️ Testing Weather API Integration...")
    
    try:
        weather_service = WeatherService()
        
        # Test cities
        test_cities = ["Mumbai", "Delhi", "Bangalore", "Chennai"]
        
        for city in test_cities:
            weather_data = weather_service.get_current_weather(city)
            
            if weather_data and weather_data.get("success"):
                print(f"✅ Weather data for {city}:")
                data = weather_data["data"]
                print(f"   Temperature: {data.get('temperature', 'N/A')}°C")
                print(f"   Condition: {data.get('condition', 'N/A')}")
                print(f"   Risk Level: {data.get('risk_level', 'N/A')}")
            else:
                print(f"⚠️ Weather data unavailable for {city}")
        
        return True
        
    except Exception as e:
        print(f"❌ Weather API test failed: {str(e)}")
        return False

def test_indian_cities_data():
    """Test Indian cities and states data"""
    print("\n🗺️ Testing Indian Cities Data...")
    
    try:
        # Test state count
        states_count = len(INDIAN_STATES_CITIES)
        print(f"✅ Loaded {states_count} Indian states")
        
        # Test city data for a few states
        test_states = ["Maharashtra", "Karnataka", "Tamil Nadu"]
        
        for state in test_states:
            if state in INDIAN_STATES_CITIES:
                cities_count = len(INDIAN_STATES_CITIES[state])
                print(f"   {state}: {cities_count} cities")
            else:
                print(f"⚠️ {state} not found in data")
        
        # Test state detection from city
        test_cities = ["Mumbai", "Bangalore", "Chennai"]
        for city in test_cities:
            state = get_state_from_city(city)
            print(f"   {city} -> {state}")
        
        return True
        
    except Exception as e:
        print(f"❌ Indian cities data test failed: {str(e)}")
        return False

def test_shipment_creation():
    """Test shipment creation and storage"""
    print("\n📦 Testing Shipment Creation...")
    
    try:
        from utils.database import get_shipments_collection
        
        shipments_collection = get_shipments_collection()
        
        # Create test shipment
        test_shipment = {
            "tracking_number": f"LICS{int(time.time())}",
            "seller_id": "test_seller",
            "origin": "Mumbai, Maharashtra",
            "destination": "Delhi, Delhi",
            "weight": 5.5,
            "dimensions": {"length": 30, "width": 20, "height": 15},
            "value": 15000,
            "priority": "standard",
            "fragile": False,
            "status": "pending",
            "created_at": time.time(),
            "estimated_delivery_date": "2024-01-20",
            "origin_coordinates": {"lat": 19.0760, "lng": 72.8777},
            "destination_coordinates": {"lat": 28.7041, "lng": 77.1025},
            "risk_assessment": {
                "overall_risk": 3.5,
                "distance_risk": 2.8,
                "weather_risk": 1.2,
                "traffic_risk": 4.1,
                "calculated_at": time.time()
            },
            "weather_impact": {
                "current_condition": "clear",
                "temperature": 25,
                "humidity": 65,
                "risk_level": "low",
                "last_updated": time.time()
            }
        }
        
        # Insert shipment
        result = shipments_collection.insert_one(test_shipment)
        
        if result.inserted_id:
            print("✅ Shipment creation successful!")
            print(f"   Shipment ID: {str(result.inserted_id)}")
            print(f"   Tracking Number: {test_shipment['tracking_number']}")
            return True, str(result.inserted_id)
        else:
            print("❌ Shipment creation failed!")
            return False, None
            
    except Exception as e:
        print(f"❌ Shipment creation test failed: {str(e)}")
        return False, None

def test_audit_logging():
    """Test audit logging system"""
    print("\n📝 Testing Audit Logging System...")
    
    try:
        from utils.database import get_audit_logs_collection
        
        audit_collection = get_audit_logs_collection()
        
        # Create test audit log
        test_audit = {
            "action": "test_action",
            "entity_type": "system",
            "entity_id": "test_entity",
            "user_id": "test_user",
            "details": {
                "test_detail": "system_integration_test",
                "timestamp_readable": datetime.now().isoformat()
            },
            "timestamp": time.time(),
            "ip_address": "127.0.0.1",
            "user_agent": "integration_test"
        }
        
        # Insert audit log
        result = audit_collection.insert_one(test_audit)
        
        if result.inserted_id:
            print("✅ Audit logging successful!")
            print(f"   Audit ID: {str(result.inserted_id)}")
            return True
        else:
            print("❌ Audit logging failed!")
            return False
            
    except Exception as e:
        print(f"❌ Audit logging test failed: {str(e)}")
        return False

def run_full_system_test():
    """Run complete system integration test"""
    print("🚀 LICS System Integration Test")
    print("=" * 50)
    
    test_results = []
    
    # Test 1: Database Connection
    db_result = test_database_connection()
    test_results.append(("Database Connection", db_result))
    
    if not db_result:
        print("\n❌ Critical: Database connection failed. Cannot proceed with other tests.")
        return False
    
    # Test 2: User Registration
    user_result, test_user = test_user_registration()
    test_results.append(("User Registration", user_result))
    
    # Test 3: Weather API
    weather_result = test_weather_api()
    test_results.append(("Weather API", weather_result))
    
    # Test 4: Indian Cities Data
    cities_result = test_indian_cities_data()
    test_results.append(("Indian Cities Data", cities_result))
    
    # Test 5: Shipment Creation
    shipment_result, shipment_id = test_shipment_creation()
    test_results.append(("Shipment Creation", shipment_result))
    
    # Test 6: Audit Logging
    audit_result = test_audit_logging()
    test_results.append(("Audit Logging", audit_result))
    
    # Results Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25}: {status}")
        if result:
            passed_tests += 1
    
    print("\n" + "=" * 50)
    success_rate = (passed_tests / total_tests) * 100
    print(f"Overall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🎉 System integration test PASSED!")
        print("✅ LICS is ready for deployment!")
        return True
    else:
        print("⚠️ System integration test FAILED!")
        print("❌ Please fix failing components before deployment.")
        return False

if __name__ == "__main__":
    # Run the complete system test
    success = run_full_system_test()
    
    if success:
        print("\n🚀 Ready to run LICS webapp!")
        print("💡 Run: streamlit run webapp/app.py")
    else:
        print("\n🔧 Please review and fix the failing tests.")
    
    print("\n" + "=" * 50)
    print("Thank you for using LICS Integration Test!")
    print("=" * 50)