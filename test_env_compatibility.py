"""
Test Environment Variable Compatibility
Tests both JWT_EXPIRATION_HOURS and ACCESS_TOKEN_EXPIRE_MINUTES formats
"""

import os
import sys
sys.path.append('.')

def test_jwt_config():
    """Test JWT configuration with different formats"""
    print("🧪 Testing JWT Configuration Compatibility")
    print("=" * 50)
    
    # Save original env vars
    original_expire_minutes = os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES')
    original_expire_hours = os.environ.get('JWT_EXPIRATION_HOURS')
    
    try:
        # Test 1: ACCESS_TOKEN_EXPIRE_MINUTES only
        os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'] = '60'
        if 'JWT_EXPIRATION_HOURS' in os.environ:
            del os.environ['JWT_EXPIRATION_HOURS']
        
        from auth.jwt_auth import AuthenticationSystem
        auth1 = AuthenticationSystem()
        print(f"✅ Test 1 (60 minutes): {auth1.expiration_hours} hours")
        
        # Test 2: JWT_EXPIRATION_HOURS only  
        if 'ACCESS_TOKEN_EXPIRE_MINUTES' in os.environ:
            del os.environ['ACCESS_TOKEN_EXPIRE_MINUTES']
        os.environ['JWT_EXPIRATION_HOURS'] = '24'
        
        # Reload the module to test new config
        import importlib
        import auth.jwt_auth
        importlib.reload(auth.jwt_auth)
        auth2 = auth.jwt_auth.AuthenticationSystem()
        print(f"✅ Test 2 (24 hours): {auth2.expiration_hours} hours")
        
        # Test 3: Both set (should prefer ACCESS_TOKEN_EXPIRE_MINUTES)
        os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'] = '120'
        os.environ['JWT_EXPIRATION_HOURS'] = '48'
        
        importlib.reload(auth.jwt_auth)
        auth3 = auth.jwt_auth.AuthenticationSystem()
        print(f"✅ Test 3 (both set, 120 min priority): {auth3.expiration_hours} hours")
        
        print("\n🎯 All JWT configuration tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Restore original environment
        if original_expire_minutes:
            os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'] = original_expire_minutes
        elif 'ACCESS_TOKEN_EXPIRE_MINUTES' in os.environ:
            del os.environ['ACCESS_TOKEN_EXPIRE_MINUTES']
            
        if original_expire_hours:
            os.environ['JWT_EXPIRATION_HOURS'] = original_expire_hours
        elif 'JWT_EXPIRATION_HOURS' in os.environ:
            del os.environ['JWT_EXPIRATION_HOURS']

def test_twilio_config():
    """Test Twilio phone number configuration"""
    print("\n🧪 Testing Twilio Configuration Compatibility")
    print("=" * 50)
    
    # Save original env vars
    original_phone_number = os.environ.get('TWILIO_PHONE_NUMBER')
    original_from_phone = os.environ.get('TWILIO_FROM_PHONE')
    
    try:
        # Test 1: TWILIO_FROM_PHONE only
        os.environ['TWILIO_FROM_PHONE'] = '+18159085835'
        if 'TWILIO_PHONE_NUMBER' in os.environ:
            del os.environ['TWILIO_PHONE_NUMBER']
        
        # Set required Twilio vars for testing
        os.environ['TWILIO_ACCOUNT_SID'] = 'test_sid'
        os.environ['TWILIO_AUTH_TOKEN'] = 'test_token'
        
        from notifications.sms_notifier import TwilioSMSService
        sms1 = TwilioSMSService()
        print(f"✅ Test 1 (TWILIO_FROM_PHONE): {sms1.from_phone}")
        
        # Test 2: TWILIO_PHONE_NUMBER only
        if 'TWILIO_FROM_PHONE' in os.environ:
            del os.environ['TWILIO_FROM_PHONE']
        os.environ['TWILIO_PHONE_NUMBER'] = '+18159085835'
        
        import importlib
        import notifications.sms_notifier
        importlib.reload(notifications.sms_notifier)
        sms2 = notifications.sms_notifier.TwilioSMSService()
        print(f"✅ Test 2 (TWILIO_PHONE_NUMBER): {sms2.from_phone}")
        
        print("\n🎯 All Twilio configuration tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Restore original environment
        if original_phone_number:
            os.environ['TWILIO_PHONE_NUMBER'] = original_phone_number
        elif 'TWILIO_PHONE_NUMBER' in os.environ:
            del os.environ['TWILIO_PHONE_NUMBER']
            
        if original_from_phone:
            os.environ['TWILIO_FROM_PHONE'] = original_from_phone
        elif 'TWILIO_FROM_PHONE' in os.environ:
            del os.environ['TWILIO_FROM_PHONE']

if __name__ == "__main__":
    test_jwt_config()
    test_twilio_config()
    print("\n🚀 Environment compatibility tests completed!")