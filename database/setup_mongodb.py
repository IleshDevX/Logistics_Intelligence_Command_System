"""
MongoDB Database Setup Script
Phase 3.1: Create Collections for LICS

Creates 6 collections with proper schemas and indexes:
1. users - User authentication and RBAC
2. shipments - Shipment data
3. risk_scores - AI risk calculations
4. decisions - Dispatch/Delay/Reschedule decisions
5. notifications - Customer/Manager notifications
6. learning_logs - Learning loop weight adjustments
"""

from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import CollectionInvalid
from datetime import datetime
import json

# MongoDB connection
MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "lics_db"

def setup_database():
    """Create database and collections with schemas"""
    print("\n" + "="*80)
    print("  PHASE 3.1: MongoDB Collections Setup")
    print("="*80 + "\n")
    
    try:
        # Connect to MongoDB
        client = MongoClient(MONGO_URI)
        db = client[DATABASE_NAME]
        
        print(f"✅ Connected to MongoDB at {MONGO_URI}")
        print(f"✅ Database: {DATABASE_NAME}\n")
        
        # Collection 1: Users
        print("📋 Creating 'users' collection...")
        try:
            db.create_collection("users", validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["username", "email", "password_hash", "role", "created_at"],
                    "properties": {
                        "username": {"bsonType": "string", "description": "Unique username"},
                        "email": {"bsonType": "string", "description": "User email address"},
                        "password_hash": {"bsonType": "string", "description": "Hashed password"},
                        "role": {"enum": ["seller", "manager", "admin"], "description": "User role for RBAC"},
                        "full_name": {"bsonType": "string"},
                        "is_active": {"bsonType": "bool"},
                        "created_at": {"bsonType": "date"},
                        "last_login": {"bsonType": "date"}
                    }
                }
            })
            db.users.create_index([("username", ASCENDING)], unique=True)
            db.users.create_index([("email", ASCENDING)], unique=True)
            print("   ✅ 'users' collection created with indexes (username, email)")
        except CollectionInvalid:
            print("   ⚠️  'users' collection already exists")
        
        # Collection 2: Shipments
        print("\n📋 Creating 'shipments' collection...")
        try:
            db.create_collection("shipments", validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["shipment_id", "customer_name", "address", "created_at"],
                    "properties": {
                        "shipment_id": {"bsonType": "string", "description": "Unique shipment identifier"},
                        "customer_name": {"bsonType": "string"},
                        "address": {"bsonType": "string"},
                        "delivery_date": {"bsonType": "date"},
                        "priority": {"enum": ["low", "medium", "high", "urgent"]},
                        "status": {"enum": ["pending", "dispatched", "delayed", "rescheduled", "delivered", "cancelled"]},
                        "created_at": {"bsonType": "date"},
                        "updated_at": {"bsonType": "date"}
                    }
                }
            })
            db.shipments.create_index([("shipment_id", ASCENDING)], unique=True)
            db.shipments.create_index([("status", ASCENDING)])
            db.shipments.create_index([("delivery_date", ASCENDING)])
            print("   ✅ 'shipments' collection created with indexes (shipment_id, status, delivery_date)")
        except CollectionInvalid:
            print("   ⚠️  'shipments' collection already exists")
        
        # Collection 3: Risk Scores
        print("\n📋 Creating 'risk_scores' collection...")
        try:
            db.create_collection("risk_scores", validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["shipment_id", "risk_score", "calculated_at"],
                    "properties": {
                        "shipment_id": {"bsonType": "string"},
                        "risk_score": {"bsonType": "double", "minimum": 0, "maximum": 10},
                        "risk_factors": {"bsonType": "object"},
                        "weather_risk": {"bsonType": "double"},
                        "address_risk": {"bsonType": "double"},
                        "calculated_at": {"bsonType": "date"},
                        "calculated_by": {"bsonType": "string"}
                    }
                }
            })
            db.risk_scores.create_index([("shipment_id", ASCENDING)])
            db.risk_scores.create_index([("calculated_at", DESCENDING)])
            db.risk_scores.create_index([("risk_score", DESCENDING)])
            print("   ✅ 'risk_scores' collection created with indexes (shipment_id, calculated_at, risk_score)")
        except CollectionInvalid:
            print("   ⚠️  'risk_scores' collection already exists")
        
        # Collection 4: Decisions
        print("\n📋 Creating 'decisions' collection...")
        try:
            db.create_collection("decisions", validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["shipment_id", "decision_type", "ai_recommendation", "created_at"],
                    "properties": {
                        "shipment_id": {"bsonType": "string"},
                        "decision_type": {"enum": ["DISPATCH", "DELAY", "RESCHEDULE"]},
                        "ai_recommendation": {"bsonType": "string"},
                        "ai_confidence": {"bsonType": "double"},
                        "human_decision": {"bsonType": "string"},
                        "decided_by": {"bsonType": "string"},
                        "override_reason": {"bsonType": "string"},
                        "created_at": {"bsonType": "date"},
                        "approved_at": {"bsonType": "date"}
                    }
                }
            })
            db.decisions.create_index([("shipment_id", ASCENDING)])
            db.decisions.create_index([("decision_type", ASCENDING)])
            db.decisions.create_index([("created_at", DESCENDING)])
            print("   ✅ 'decisions' collection created with indexes (shipment_id, decision_type, created_at)")
        except CollectionInvalid:
            print("   ⚠️  'decisions' collection already exists")
        
        # Collection 5: Notifications
        print("\n📋 Creating 'notifications' collection...")
        try:
            db.create_collection("notifications", validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["shipment_id", "recipient_type", "message", "sent_at"],
                    "properties": {
                        "shipment_id": {"bsonType": "string"},
                        "recipient_type": {"enum": ["customer", "manager", "seller"]},
                        "recipient_email": {"bsonType": "string"},
                        "message": {"bsonType": "string"},
                        "notification_type": {"enum": ["sms", "email", "whatsapp", "app"]},
                        "status": {"enum": ["sent", "failed", "pending"]},
                        "sent_at": {"bsonType": "date"},
                        "delivered_at": {"bsonType": "date"}
                    }
                }
            })
            db.notifications.create_index([("shipment_id", ASCENDING)])
            db.notifications.create_index([("recipient_type", ASCENDING)])
            db.notifications.create_index([("sent_at", DESCENDING)])
            print("   ✅ 'notifications' collection created with indexes (shipment_id, recipient_type, sent_at)")
        except CollectionInvalid:
            print("   ⚠️  'notifications' collection already exists")
        
        # Collection 6: Learning Logs
        print("\n📋 Creating 'learning_logs' collection...")
        try:
            db.create_collection("learning_logs", validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["adjustment_date", "weight_changes"],
                    "properties": {
                        "adjustment_date": {"bsonType": "date"},
                        "weight_changes": {"bsonType": "object"},
                        "previous_weights": {"bsonType": "object"},
                        "new_weights": {"bsonType": "object"},
                        "decisions_analyzed": {"bsonType": "int"},
                        "overrides_count": {"bsonType": "int"},
                        "adjustment_reason": {"bsonType": "string"},
                        "created_at": {"bsonType": "date"}
                    }
                }
            })
            db.learning_logs.create_index([("adjustment_date", DESCENDING)])
            db.learning_logs.create_index([("created_at", DESCENDING)])
            print("   ✅ 'learning_logs' collection created with indexes (adjustment_date, created_at)")
        except CollectionInvalid:
            print("   ⚠️  'learning_logs' collection already exists")
        
        # Verify collections
        print("\n" + "="*80)
        print("  VERIFICATION")
        print("="*80 + "\n")
        
        collections = db.list_collection_names()
        print(f"📊 Total collections in '{DATABASE_NAME}': {len(collections)}\n")
        
        for col_name in collections:
            col = db[col_name]
            doc_count = col.count_documents({})
            indexes = col.list_indexes()
            index_count = len(list(indexes))
            print(f"   ✅ {col_name:<20} | Documents: {doc_count:<5} | Indexes: {index_count}")
        
        print("\n" + "="*80)
        print("  ✅ MongoDB Setup Complete!")
        print("="*80 + "\n")
        
        print("📌 Database URL: mongodb://localhost:27017/")
        print(f"📌 Database Name: {DATABASE_NAME}")
        print("📌 Collections: users, shipments, risk_scores, decisions, notifications, learning_logs")
        print("\n✅ Ready for Phase 3.2: Database Connection Module\n")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Error setting up MongoDB: {e}")
        return False

if __name__ == "__main__":
    success = setup_database()
    exit(0 if success else 1)
