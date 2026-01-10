"""
Test MongoDB Atlas Connection
=============================
Tests connection to MongoDB Atlas cloud database
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, OperationFailure

print("=" * 70)
print("TESTING MONGODB ATLAS CONNECTION")
print("=" * 70)

# MongoDB Atlas Connection String
MONGO_URI = "mongodb+srv://ileshpatel666_db_user:clNrihAWgGXMB3ea@lics-cluster.1r5cdmy.mongodb.net/?appName=lics-cluster"
DATABASE_NAME = "lics_db"

print("\nTEST 1: Connecting to MongoDB Atlas...")
print(f"URI: {MONGO_URI[:50]}... (truncated for security)")
print(f"Database: {DATABASE_NAME}")

try:
    # Create MongoDB client
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=10000,  # 10 second timeout
        connectTimeoutMS=10000,
        socketTimeoutMS=10000
    )
    
    # Test connection with ping
    print("\nAttempting to ping MongoDB Atlas...")
    client.admin.command('ping')
    
    print("✅ Successfully connected to MongoDB Atlas!")
    
    # Test database access
    print(f"\nTEST 2: Accessing database '{DATABASE_NAME}'...")
    db = client[DATABASE_NAME]
    
    # Try to list collections
    collections = db.list_collection_names()
    print(f"✅ Database '{DATABASE_NAME}' is accessible")
    print(f"📊 Collections found: {len(collections)}")
    
    if collections:
        print("📋 Collection names:")
        for coll in collections:
            try:
                count = db[coll].count_documents({})
                print(f"   - {coll}: {count} documents")
            except Exception as e:
                print(f"   - {coll}: (could not count documents)")
    else:
        print("ℹ️  No collections yet (database is empty)")
    
    # Test write permissions
    print(f"\nTEST 3: Testing write permissions...")
    test_collection = db['test_connection']
    
    # Try to insert a test document
    test_doc = {"test": "connection", "timestamp": "2026-01-10"}
    result = test_collection.insert_one(test_doc)
    print(f"✅ Write test successful! Document ID: {result.inserted_id}")
    
    # Clean up test document
    test_collection.delete_one({"_id": result.inserted_id})
    print("✅ Cleanup successful!")
    
    # Close connection
    client.close()
    
    print("\n" + "=" * 70)
    print("🎉 ALL TESTS PASSED! MongoDB Atlas is ready to use!")
    print("=" * 70)
    print("\nNext Steps:")
    print("1. ✅ MongoDB Atlas connection works")
    print("2. ✅ Database is accessible")
    print("3. ✅ Read/write permissions verified")
    print("4. 🚀 Ready to run Streamlit app!")
    print("\nRun: streamlit run dashboard/control_tower_streamlit.py")
    
except ConnectionFailure as e:
    print(f"\n❌ CONNECTION FAILURE: {e}")
    print("\nPossible causes:")
    print("1. Network connectivity issues")
    print("2. MongoDB Atlas cluster is paused or stopped")
    print("3. Firewall blocking connection")
    print("\nSolution:")
    print("- Check your internet connection")
    print("- Verify cluster is running in MongoDB Atlas")
    
except ServerSelectionTimeoutError as e:
    print(f"\n❌ SERVER SELECTION TIMEOUT: {e}")
    print("\nPossible causes:")
    print("1. Incorrect connection string")
    print("2. Network Access not configured in Atlas")
    print("3. Cluster endpoint incorrect")
    print("\nSolution:")
    print("- Verify connection string is correct")
    print("- Check Network Access allows 0.0.0.0/0 in Atlas")
    
except OperationFailure as e:
    print(f"\n❌ AUTHENTICATION FAILED: {e}")
    print("\nPossible causes:")
    print("1. ❌ Username or password is incorrect")
    print("2. ❌ Database user doesn't exist")
    print("3. ❌ User permissions insufficient")
    print("4. ❌ Special characters in password need URL encoding")
    print("\n🔧 SOLUTION:")
    print("=" * 70)
    print("1. Go to MongoDB Atlas → Database Access")
    print("2. Find user: ileshpatel666_db_user")
    print("3. Click 'Edit' → 'Edit Password'")
    print("4. Set new password: Test123456 (simple, no special chars)")
    print("5. Click 'Update User'")
    print("6. Wait 1-2 minutes")
    print("7. Update the connection string with new password")
    print("\nOR create a new user:")
    print("- Username: lics_admin")
    print("- Password: LicsTest123")
    print("- Role: Atlas admin")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ UNEXPECTED ERROR: {e}")
    print(f"Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    
print("\n")
