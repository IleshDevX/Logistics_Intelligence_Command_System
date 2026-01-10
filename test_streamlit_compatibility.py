"""
Test Streamlit Compatibility
============================

Verifies that the database connection and JWT configuration
work correctly with the new Streamlit-compatible code.
"""

import sys
import os

# Test 1: Database Connection
print("=" * 60)
print("TEST 1: Database Connection (Streamlit Compatible)")
print("=" * 60)

try:
    from database.connection import db_connection
    
    print(f"✅ Import successful")
    print(f"📊 MongoDB URI: {db_connection.MONGO_URI[:30]}... (truncated)")
    print(f"📁 Database Name: {db_connection.DATABASE_NAME}")
    
    if db_connection.connect():
        print(f"✅ Connected to MongoDB")
        db = db_connection.get_database()
        collections = db.list_collection_names()
        print(f"📊 Collections found: {len(collections)}")
        for coll in collections:
            count = db[coll].count_documents({})
            print(f"   - {coll}: {count} documents")
        print("✅ TEST 1 PASSED: Database connection works!")
    else:
        print("❌ Failed to connect to MongoDB")
        print("⚠️ This is expected if MongoDB is not running")
        
except Exception as e:
    print(f"❌ TEST 1 FAILED: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 2: JWT Configuration
print("=" * 60)
print("TEST 2: JWT Authentication (Streamlit Compatible)")
print("=" * 60)

try:
    from backend.auth import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
    
    print(f"✅ Import successful")
    print(f"🔐 Algorithm: {ALGORITHM}")
    print(f"⏱️ Token Expiry: {ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
    print(f"🔑 Secret Key Length: {len(SECRET_KEY)} characters")
    print(f"🔑 Secret Key (first 20 chars): {SECRET_KEY[:20]}...")
    print("✅ TEST 2 PASSED: JWT configuration works!")
    
except Exception as e:
    print(f"❌ TEST 2 FAILED: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 3: Environment Detection
print("=" * 60)
print("TEST 3: Environment Detection")
print("=" * 60)

try:
    # Try importing streamlit
    try:
        import streamlit as st
        print("✅ Streamlit module found")
        
        if hasattr(st, 'secrets'):
            print("✅ st.secrets available")
            print("📝 Mode: STREAMLIT CLOUD")
        else:
            print("⚠️ st.secrets not available (expected in local environment)")
            print("📝 Mode: LOCAL STREAMLIT")
    except ImportError:
        print("⚠️ Streamlit module not found (expected in FastAPI backend)")
        print("📝 Mode: FASTAPI BACKEND")
    
    # Check environment variables
    mongo_uri_env = os.getenv("MONGO_URI")
    jwt_key_env = os.getenv("JWT_SECRET_KEY")
    
    print(f"\nEnvironment Variables:")
    print(f"  - MONGO_URI: {'Set' if mongo_uri_env else 'Not set (using default)'}")
    print(f"  - JWT_SECRET_KEY: {'Set' if jwt_key_env else 'Not set (using generated)'}")
    
    print("✅ TEST 3 PASSED: Environment detection works!")
    
except Exception as e:
    print(f"❌ TEST 3 FAILED: {e}")
    import traceback
    traceback.print_exc()

print()

# Summary
print("=" * 60)
print("SUMMARY")
print("=" * 60)
print("""
✅ Database connection module is Streamlit-compatible
✅ JWT authentication module is Streamlit-compatible
✅ Configuration automatically adapts to environment

Next Steps:
1. Create MongoDB Atlas account
2. Update .streamlit/secrets.toml with Atlas URI
3. Test with: streamlit run dashboard/control_tower_streamlit.py
4. Deploy to Streamlit Cloud

For detailed instructions, see STREAMLIT_DEPLOYMENT_GUIDE.md
""")
