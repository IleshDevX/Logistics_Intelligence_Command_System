"""
MongoDB Database Layer - Production Implementation
LICS Database Schema and Connection Management
"""

import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING
from datetime import datetime, timezone
from typing import Optional, Dict, List, Any
from dotenv import load_dotenv
import sys
sys.path.append('.')

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LICSDatabase:
    """
    Production MongoDB Database Layer for LICS
    Handles all database operations with async motor driver
    """
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database = None
        self.users_collection = None
        self.shipments_collection = None
        self.is_demo_mode = False
        self._demo_collections = None
        
    async def connect(self):
        """Initialize database connection with demo fallback"""
        try:
            # Check if demo mode is forced
            if os.getenv("USE_DEMO_MODE", "false").lower() == "true":
                logger.info("🎭 Demo mode enabled via environment variable")
                await self._init_demo_mode()
                return
            
            # Get MongoDB URL from environment
            mongodb_url = os.getenv("MONGODB_URL")
            database_name = os.getenv("MONGODB_DATABASE", "lics_db")
            
            if not mongodb_url:
                logger.warning("MONGODB_URL not found, falling back to demo mode")
                await self._init_demo_mode()
                return
            
            # Create async client
            self.client = AsyncIOMotorClient(mongodb_url, serverSelectionTimeoutMS=5000)
            self.database = self.client[database_name]
            
            # Test connection
            await self.client.admin.command('ping')
            
            # Initialize collections
            self.users_collection = self.database.users
            self.shipments_collection = self.database.shipments
            
            # Create indexes
            await self._create_indexes()
            
            logger.info(f"✅ Connected to MongoDB: {database_name}")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to connect to MongoDB: {str(e)}")
            logger.info("🎭 Falling back to demo mode")
            await self._init_demo_mode()
    
    async def _init_demo_mode(self):
        """Initialize demo mode with fake data"""
        try:
            from utils.demo_mode import get_demo_collections, get_demo_users, get_demo_shipments
            
            self.is_demo_mode = True
            self._demo_collections = get_demo_collections()
            
            # Create mock async collections
            class MockAsyncCollection:
                def __init__(self, demo_collection):
                    self._demo = demo_collection
                
                async def find_one(self, query):
                    return self._demo.find_one(query)
                
                async def find(self, query=None):
                    class MockCursor:
                        def __init__(self, data):
                            self.data = data
                            self.index = 0
                        
                        async def to_list(self, length=None):
                            return self.data[:length] if length else self.data
                        
                        def __aiter__(self):
                            return self
                        
                        async def __anext__(self):
                            if self.index < len(self.data):
                                result = self.data[self.index]
                                self.index += 1
                                return result
                            raise StopAsyncIteration
                    
                    results = self._demo.find(query)
                    return MockCursor(results)
                
                async def insert_one(self, document):
                    # For demo mode, just return a mock result
                    class MockInsertResult:
                        def __init__(self):
                            self.inserted_id = f"demo_{len(self._demo.data) + 1}"
                    
                    # Add to demo data
                    document['_id'] = f"demo_{len(self._demo.data) + 1}"
                    self._demo.data.append(document)
                    return MockInsertResult()
                
                async def update_one(self, query, update):
                    # For demo mode, just return a mock result
                    class MockUpdateResult:
                        def __init__(self):
                            self.matched_count = 1
                            self.modified_count = 1
                    return MockUpdateResult()
                
                async def delete_one(self, query):
                    # For demo mode, just return a mock result
                    class MockDeleteResult:
                        def __init__(self):
                            self.deleted_count = 1
                    return MockDeleteResult()
            
            self.users_collection = MockAsyncCollection(self._demo_collections["users"])
            self.shipments_collection = MockAsyncCollection(self._demo_collections["shipments"])
            
            logger.info("✅ Demo mode initialized successfully")
            logger.info(f"   📊 Demo users: {len(get_demo_users())}")
            logger.info(f"   📦 Demo shipments: {len(get_demo_shipments())}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize demo mode: {str(e)}")
            raise
    
    async def disconnect(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("🔌 Disconnected from MongoDB")
    
    async def _create_indexes(self):
        """Create database indexes for optimal performance"""
        try:
            # Users collection indexes
            await self.users_collection.create_index([("username", ASCENDING)], unique=True)
            await self.users_collection.create_index([("role", ASCENDING)])
            
            # Shipments collection indexes  
            await self.shipments_collection.create_index([("seller_id", ASCENDING)])
            await self.shipments_collection.create_index([("status", ASCENDING)])
            await self.shipments_collection.create_index([("created_at", DESCENDING)])
            await self.shipments_collection.create_index([("risk_analysis.score", DESCENDING)])
            
            logger.info("📊 Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to create indexes: {str(e)}")
    
    # ==================== USER OPERATIONS ====================
    
    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new user
        Schema: {username, password_hash, role, full_name, created_at}
        """
        try:
            # Add timestamp
            user_data['created_at'] = datetime.now(timezone.utc)
            user_data['last_login'] = None
            user_data['is_active'] = True
            
            # Insert user
            result = await self.users_collection.insert_one(user_data)
            
            # Return user without password
            user = await self.users_collection.find_one(
                {"_id": result.inserted_id},
                {"password_hash": 0}
            )
            
            logger.info(f"👤 User created: {user_data['username']}")
            return self._format_document(user)
            
        except Exception as e:
            logger.error(f"❌ Failed to create user: {str(e)}")
            raise
    
    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username (includes password hash for authentication)"""
        try:
            user = await self.users_collection.find_one({"username": username})
            return self._format_document(user) if user else None
        except Exception as e:
            logger.error(f"❌ Failed to get user: {str(e)}")
            return None
    
    async def get_user_profile(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user profile (excludes password hash)"""
        try:
            user = await self.users_collection.find_one(
                {"username": username},
                {"password_hash": 0}
            )
            return self._format_document(user) if user else None
        except Exception as e:
            logger.error(f"❌ Failed to get user profile: {str(e)}")
            return None
    
    async def update_last_login(self, username: str):
        """Update user's last login timestamp"""
        try:
            await self.users_collection.update_one(
                {"username": username},
                {"$set": {"last_login": datetime.now(timezone.utc)}}
            )
        except Exception as e:
            logger.error(f"❌ Failed to update last login: {str(e)}")
    
    async def get_all_users(self, role: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all users (optionally filtered by role)"""
        try:
            query = {"role": role} if role else {}
            cursor = self.users_collection.find(query, {"password_hash": 0})
            users = await cursor.to_list(length=None)
            return [self._format_document(user) for user in users]
        except Exception as e:
            logger.error(f"❌ Failed to get users: {str(e)}")
            return []
    
    # ==================== SHIPMENT OPERATIONS ====================
    
    async def create_shipment(self, shipment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new shipment
        Schema: {seller_id, product_details, delivery_info, risk_analysis, status, customer_phone, created_at}
        """
        try:
            # Add timestamps and default values
            shipment_data['created_at'] = datetime.now(timezone.utc)
            shipment_data['updated_at'] = datetime.now(timezone.utc)
            shipment_data.setdefault('status', 'Pending')
            shipment_data.setdefault('notifications_sent', [])
            shipment_data.setdefault('status_history', [])
            
            # Add initial status to history
            shipment_data['status_history'].append({
                'status': shipment_data['status'],
                'timestamp': datetime.now(timezone.utc),
                'updated_by': shipment_data['seller_id']
            })
            
            # Insert shipment
            result = await self.shipments_collection.insert_one(shipment_data)
            
            # Return created shipment
            shipment = await self.shipments_collection.find_one({"_id": result.inserted_id})
            
            logger.info(f"📦 Shipment created: {result.inserted_id}")
            return self._format_document(shipment)
            
        except Exception as e:
            logger.error(f"❌ Failed to create shipment: {str(e)}")
            raise
    
    async def get_shipment_by_id(self, shipment_id: str) -> Optional[Dict[str, Any]]:
        """Get shipment by ID"""
        try:
            from bson import ObjectId
            shipment = await self.shipments_collection.find_one({"_id": ObjectId(shipment_id)})
            return self._format_document(shipment) if shipment else None
        except Exception as e:
            logger.error(f"❌ Failed to get shipment: {str(e)}")
            return None
    
    async def get_shipments_by_seller(self, seller_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get shipments by seller ID"""
        try:
            cursor = self.shipments_collection.find({"seller_id": seller_id}).sort("created_at", -1).limit(limit)
            shipments = await cursor.to_list(length=None)
            return [self._format_document(shipment) for shipment in shipments]
        except Exception as e:
            logger.error(f"❌ Failed to get shipments by seller: {str(e)}")
            return []
    
    async def get_shipments_by_status(self, status: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get shipments by status"""
        try:
            cursor = self.shipments_collection.find({"status": status}).sort("created_at", -1).limit(limit)
            shipments = await cursor.to_list(length=None)
            return [self._format_document(shipment) for shipment in shipments]
        except Exception as e:
            logger.error(f"❌ Failed to get shipments by status: {str(e)}")
            return []
    
    async def update_shipment_status(self, shipment_id: str, new_status: str, updated_by: str, reason: Optional[str] = None) -> bool:
        """Update shipment status with history tracking"""
        try:
            from bson import ObjectId
            
            # Create status history entry
            status_entry = {
                'status': new_status,
                'timestamp': datetime.now(timezone.utc),
                'updated_by': updated_by,
                'reason': reason
            }
            
            # Update shipment
            result = await self.shipments_collection.update_one(
                {"_id": ObjectId(shipment_id)},
                {
                    "$set": {
                        "status": new_status,
                        "updated_at": datetime.now(timezone.utc)
                    },
                    "$push": {"status_history": status_entry}
                }
            )
            
            success = result.modified_count > 0
            if success:
                logger.info(f"📦 Shipment {shipment_id} status updated to {new_status}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Failed to update shipment status: {str(e)}")
            return False
    
    async def add_notification_log(self, shipment_id: str, notification_data: Dict[str, Any]) -> bool:
        """Add notification to shipment log"""
        try:
            from bson import ObjectId
            
            notification_data['timestamp'] = datetime.now(timezone.utc)
            
            result = await self.shipments_collection.update_one(
                {"_id": ObjectId(shipment_id)},
                {"$push": {"notifications_sent": notification_data}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"❌ Failed to add notification log: {str(e)}")
            return False
    
    # ==================== ANALYTICS OPERATIONS ====================
    
    async def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Get real-time dashboard metrics"""
        try:
            # Get counts by status
            pending_count = await self.shipments_collection.count_documents({"status": "Pending"})
            approved_count = await self.shipments_collection.count_documents({"status": "Approved"})
            dispatched_count = await self.shipments_collection.count_documents({"status": "Dispatched"})
            delayed_count = await self.shipments_collection.count_documents({"status": "Delayed"})
            
            # Get total shipments
            total_shipments = await self.shipments_collection.count_documents({})
            
            # Get average risk score
            pipeline = [
                {"$group": {"_id": None, "avg_risk": {"$avg": "$risk_analysis.score"}}}
            ]
            avg_risk_result = await self.shipments_collection.aggregate(pipeline).to_list(1)
            avg_risk_score = avg_risk_result[0]["avg_risk"] if avg_risk_result else 0
            
            # Get high risk shipments count
            high_risk_count = await self.shipments_collection.count_documents({"risk_analysis.score": {"$gt": 70}})
            
            return {
                "total_shipments": total_shipments,
                "pending_count": pending_count,
                "approved_count": approved_count,
                "dispatched_count": dispatched_count,
                "delayed_count": delayed_count,
                "avg_risk_score": round(avg_risk_score, 1) if avg_risk_score else 0,
                "high_risk_count": high_risk_count,
                "timestamp": datetime.now(timezone.utc)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get dashboard metrics: {str(e)}")
            return {}
    
    async def get_risk_analytics(self) -> List[Dict[str, Any]]:
        """Get risk analytics data"""
        try:
            pipeline = [
                {
                    "$project": {
                        "risk_score": "$risk_analysis.score",
                        "status": 1,
                        "created_date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}}
                    }
                },
                {
                    "$group": {
                        "_id": "$created_date",
                        "avg_risk": {"$avg": "$risk_score"},
                        "total_shipments": {"$sum": 1},
                        "high_risk": {"$sum": {"$cond": [{"$gt": ["$risk_score", 70]}, 1, 0]}}
                    }
                },
                {"$sort": {"_id": -1}},
                {"$limit": 30}  # Last 30 days
            ]
            
            result = await self.shipments_collection.aggregate(pipeline).to_list(30)
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to get risk analytics: {str(e)}")
            return []
    
    # ==================== UTILITY METHODS ====================
    
    def _format_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Convert ObjectId to string for JSON serialization"""
        if document and "_id" in document:
            document["id"] = str(document["_id"])
            del document["_id"]
        return document
    
    async def health_check(self) -> bool:
        """Check database connection health"""
        try:
            await self.client.admin.command('ping')
            return True
        except Exception:
            return False

# Global database instance
db = LICSDatabase()

# Startup and shutdown functions for FastAPI
async def startup_database():
    """Initialize database connection"""
    await db.connect()

async def shutdown_database():
    """Close database connection"""
    await db.disconnect()

# Export for easy importing
__all__ = ["db", "startup_database", "shutdown_database", "LICSDatabase"]