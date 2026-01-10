"""
Configuration Validation Script for LICS
Checks environment configuration without external dependencies
"""

import os

def check_env_file():
    """Check if .env file exists and contains required variables"""
    env_file = '.env'
    
    if not os.path.exists(env_file):
        print("❌ .env file not found!")
        return False
    
    print("✅ .env file found")
    
    # Read .env file content
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Required environment variables
    required_vars = {
        'MONGODB_URL': 'MongoDB connection string',
        'JWT_SECRET_KEY': 'JWT secret key for authentication',
        'JWT_ALGORITHM': 'JWT algorithm (should be HS256)',
        'TWILIO_ACCOUNT_SID': 'Twilio Account SID',
        'TWILIO_AUTH_TOKEN': 'Twilio Auth Token',
        'WEATHER_API_KEY': 'Weather API key',
        'WEATHER_API_URL': 'Weather API base URL'
    }
    
    # Optional variables (check if at least one exists)
    optional_vars = {
        'token_expiration': ['JWT_EXPIRATION_HOURS', 'ACCESS_TOKEN_EXPIRE_MINUTES'],
        'twilio_phone': ['TWILIO_PHONE_NUMBER', 'TWILIO_FROM_PHONE'],
        'mongodb_database': ['MONGODB_DATABASE']
    }
    
    print("\n📋 Configuration Check:")
    all_present = True
    
    # Check required variables
    for var, description in required_vars.items():
        if f'{var}=' in content:
            # Extract value (simple parsing)
            lines = content.split('\n')
            value = None
            for line in lines:
                if line.strip().startswith(f'{var}='):
                    value = line.split('=', 1)[1].strip()
                    break
            
            if value and not value.startswith('your-') and not value.startswith('username:'):
                print(f"✅ {var}: Set")
            else:
                print(f"⚠️ {var}: Placeholder value (needs update)")
                all_present = False
        else:
            print(f"❌ {var}: Missing")
            all_present = False
    
    # Check optional variable groups
    for group_name, var_list in optional_vars.items():
        found = False
        for var in var_list:
            if f'{var}=' in content:
                # Extract value
                lines = content.split('\n')
                value = None
                for line in lines:
                    if line.strip().startswith(f'{var}='):
                        value = line.split('=', 1)[1].strip()
                        break
                if value and not value.startswith('your-'):
                    print(f"✅ {var}: Set")
                    found = True
                    break
        
        if not found:
            print(f"⚠️ {group_name}: None of {var_list} found")
    
    return all_present

def check_production_readiness():
    """Check if system is ready for production"""
    print("🚀 LICS Production Readiness Check")
    print("=" * 50)
    
    # Check environment file
    env_ok = check_env_file()
    
    # Check key files exist
    print("\n📁 System Files Check:")
    required_files = [
        'main.py',
        'database/mongodb.py',
        'auth/jwt_auth.py',
        'notifications/sms_notifier.py',
        'webapp/app.py',
        'requirements.txt',
        'start_lics.py'
    ]
    
    files_ok = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - Missing!")
            files_ok = False
    
    # Overall status
    print("\n🎯 Overall Status:")
    if env_ok and files_ok:
        print("✅ System is PRODUCTION READY!")
        print("🚀 Run 'python start_lics.py' to start the system")
        print("\n📱 Access URLs:")
        print("   - Streamlit Frontend: http://localhost:8501")
        print("   - FastAPI Backend: http://localhost:8000")
        print("   - API Documentation: http://localhost:8000/docs")
    else:
        print("⚠️ System needs configuration updates before production deployment")
        if not env_ok:
            print("   - Update .env file with real production credentials")
        if not files_ok:
            print("   - Ensure all required files are present")
    
    return env_ok and files_ok

if __name__ == "__main__":
    check_production_readiness()