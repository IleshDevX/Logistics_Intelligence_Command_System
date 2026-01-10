"""
MongoDB Atlas Database Setup Script
Creates 6 collections with proper schemas and indexes in MongoDB Atlas
"""

from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import CollectionInvalid
from datetime import datetime

# MongoDB Atlas connection - reads from secrets
def get_mongo_uri():
    """Get MongoDB URI from Streamlit secrets or use Atlas directly"""
    try:
        # Try reading from .streamlit/secrets.toml
        import toml
        secrets = toml.load('.streamlit/secrets.toml')
        return secrets['mongodb']['uri'], secrets['mongodb']['database']
    except:
        # Fallback to direct Atlas connection
        return (
            "mongodb+srv://ileshpatel666_db_user:clNrihAWgGXMB3ea@lics-cluster.1r5cdmy.mongodb.net/?appName=lics-cluster",
            "lics_db"
        )

MONGO_URI, DATABASE_NAME = get_mongo_uri()

def setup_database():
    """Create database and collections with schemas"""
    print("\n" + "="*80)
    print("  MONGODB ATLAS: Collections Setup")
    print("="*80 + "\n")
    
    try:
        # Connect to MongoDB Atlas
        print(f"🔗 Connecting to MongoDB Atlas...")
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000)
        
        # Test connection
        client.admin.command('ping')
        print(f"✅ Connected to MongoDB Atlas")
        
        db = client[DATABASE_NAME]
        print(f"📁 Database: {DATABASE_NAME}\n")
        
        collections_created = 0
        
        # ============================================================================
        # 1. USERS COLLECTION
        # ============================================================================
        print("Creating collection: users")
        try:
            db.create_collection("users", validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["username", "email", "hashed_password", "role", "created_at"],
                    "properties": {
                        "username": {"bsonType": "string"},
                        "email": {"bsonType": "string"},
                        "hashed_password": {"bsonType": "string"},
                        "role": {"enum": ["seller", "manager", "supervisor", "customer"]},
                        "full_name": {"bsonType": "string"},
                        "is_active": {"bsonType": "bool"},
                        "created_at": {"bsonType": "date"},
                        "last_login": {"bsonType": "date"}
                    }
                }
            })
            db.users.create_index([("username", ASCENDING)], unique=True)
            db.users.create_index([("email", ASCENDING)], unique=True)
            print("  ✅ users (with indexes: username, email)")
            collections_created += 1
        except CollectionInvalid:
            print("  ⚠️  users already exists")
        
        # ============================================================================
        # 2. SHIPMENTS COLLECTION
        # ============================================================================
        print("Creating collection: shipments")
        try:
            db.create_collection("shipments", validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["shipment_id", "origin", "destination", "status", "created_at"],
                    "properties": {
                        "shipment_id": {"bsonType": "string"},
                        "seller_id": {"bsonType": "string"},
                        "customer_id": {"bsonType": "string"},
                        "origin": {"bsonType": "string"},
                        "destination": {"bsonType": "string"},
                        "priority": {"enum": ["low", "medium", "high", "critical"]},
                        "weight": {"bsonType": "number"},
                        "status": {"enum": ["pending", "assigned", "in_transit", "delivered", "delayed", "cancelled"]},
                        "created_at": {"bsonType": "date"},
                        "updated_at": {"bsonType": "date"}
                    }
                }
            })
            db.shipments.create_index([("shipment_id", ASCENDING)], unique=True)
            db.shipments.create_index([("status", ASCENDING)])
            db.shipments.create_index([("created_at", DESCENDING)])
            print("  ✅ shipments (with indexes: shipment_id, status, created_at)")
            collections_created += 1
        except CollectionInvalid:
            print("  ⚠️  shipments already exists")
        
        # ============================================================================
        # 3. RISK_SCORES COLLECTION
        # ============================================================================
        print("Creating collection: risk_scores")
        try:
            db.create_collection("risk_scores", validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["shipment_id", "risk_score", "calculated_at"],
                    "properties": {
                        "shipment_id": {"bsonType": "string"},
                        "risk_score": {"bsonType": "number", "minimum": 0, "maximum": 100},
                        "weather_risk": {"bsonType": "number"},
                        "traffic_risk": {"bsonType": "number"},
                        "address_risk": {"bsonType": "number"},
                        "vehicle_risk": {"bsonType": "number"},
                        "calculated_at": {"bsonType": "date"}
                    }
                }
            })
            db.risk_scores.create_index([("shipment_id", ASCENDING)])
            db.risk_scores.create_index([("risk_score", DESCENDING)])
            db.risk_scores.create_index([("calculated_at", DESCENDING)])
            print("  ✅ risk_scores (with indexes: shipment_id, risk_score, calculated_at)")
            collections_created += 1
        except CollectionInvalid:
            print("  ⚠️  risk_scores already exists")
        
        # ============================================================================
        # 4. DECISIONS COLLECTION
        # ============================================================================
        print("Creating collection: decisions")
        try:
            db.create_collection("decisions", validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["shipment_id", "decision_type", "made_by", "timestamp"],
                    "properties": {
                        "shipment_id": {"bsonType": "string"},
                        "decision_type": {"enum": ["dispatch", "delay", "reschedule", "cancel"]},
                        "made_by": {"enum": ["ai", "manager", "supervisor"]},
                        "confidence": {"bsonType": "number", "minimum": 0, "maximum": 100},
                        "reasoning": {"bsonType": "string"},
                        "human_override": {"bsonType": "bool"},
                        "override_reason": {"bsonType": "string"},
                        "timestamp": {"bsonType": "date"}
                    }
                }
            })
            db.decisions.create_index([("shipment_id", ASCENDING)])
            db.decisions.create_index([("made_by", ASCENDING)])
            db.decisions.create_index([("timestamp", DESCENDING)])
            print("  ✅ decisions (with indexes: shipment_id, made_by, timestamp)")
            collections_created += 1
        except CollectionInvalid:
            print("  ⚠️  decisions already exists")
        
        # ============================================================================
        # 5. NOTIFICATIONS COLLECTION
        # ============================================================================
        print("Creating collection: notifications")
        try:
            db.create_collection("notifications", validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["user_id", "message", "status", "created_at"],
                    "properties": {
                        "user_id": {"bsonType": "string"},
                        "shipment_id": {"bsonType": "string"},
                        "notification_type": {"enum": ["delay", "dispatch", "delivered", "alert"]},
                        "message": {"bsonType": "string"},
                        "status": {"enum": ["sent", "delivered", "failed"]},
                        "channel": {"enum": ["email", "sms", "push", "in_app"]},
                        "created_at": {"bsonType": "date"},
                        "sent_at": {"bsonType": "date"}
                    }
                }
            })
            db.notifications.create_index([("user_id", ASCENDING)])
            db.notifications.create_index([("status", ASCENDING)])
            db.notifications.create_index([("created_at", DESCENDING)])
            print("  ✅ notifications (with indexes: user_id, status, created_at)")
            collections_created += 1
        except CollectionInvalid:
            print("  ⚠️  notifications already exists")
        
        # ============================================================================
        # 6. LEARNING_LOGS COLLECTION
        # ============================================================================
        print("Creating collection: learning_logs")
        try:
            db.create_collection("learning_logs", validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["shipment_id", "feedback_type", "timestamp"],
                    "properties": {
                        "shipment_id": {"bsonType": "string"},
                        "feedback_type": {"enum": ["success", "failure", "override"]},
                        "decision_id": {"bsonType": "string"},
                        "outcome": {"bsonType": "string"},
                        "weight_adjustments": {"bsonType": "object"},
                        "timestamp": {"bsonType": "date"}
                    }
                }
            })
            db.learning_logs.create_index([("shipment_id", ASCENDING)])
            db.learning_logs.create_index([("feedback_type", ASCENDING)])
            db.learning_logs.create_index([("timestamp", DESCENDING)])
            print("  ✅ learning_logs (with indexes: shipment_id, feedback_type, timestamp)")
            collections_created += 1
        except CollectionInvalid:
            print("  ⚠️  learning_logs already exists")
        
        # Summary
        print("\n" + "="*80)
        print(f"✅ Database setup complete!")
        print(f"📊 Collections created/verified: {collections_created}/6")
        print(f"🗄️  Database: {DATABASE_NAME}")
        print(f"☁️  MongoDB Atlas: Connected")
        print("="*80 + "\n")
        
        # List all collections
        all_collections = db.list_collection_names()
        print("📋 All collections in database:")
        for coll in all_collections:
            count = db[coll].count_documents({})
            print(f"   - {coll}: {count} documents")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = setup_database()
    if success:
        print("\n🎉 Ready to use! You can now run the Streamlit app.")
        print("   Run: streamlit run dashboard/control_tower_streamlit.py")
    else:
        print("\n⚠️  Setup encountered errors. Please check the output above.")
