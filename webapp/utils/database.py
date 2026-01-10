"""
Database Connection Module for LICS
MongoDB Atlas Integration with Connection Pooling
"""

import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from typing import Optional, Dict, Any
import asyncio
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB Configuration
MONGODB_URI = "mongodb+srv://ileshpatel666_db_user:wd4BU1pADhIdDohY@lics-cluster.1r5cdmy.mongodb.net/?appName=lics-cluster"
DATABASE_NAME = "lics_production"

# Global variables for connections
_sync_client: Optional[MongoClient] = None
_async_client: Optional[AsyncIOMotorClient] = None
_database = None
_async_database = None

class DatabaseManager:
    """Database manager for LICS application"""
    
    def __init__(self):
        self.client = None
        self.database = None
        self.is_connected = False
    
    def connect(self) -> bool:
        """Establish connection to MongoDB"""
        try:
            # Create client with connection options
            self.client = MongoClient(
                MONGODB_URI,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=10000,         # 10 second connection timeout
                maxPoolSize=10,                 # Maximum 10 connections
                retryWrites=True
            )
            
            # Test connection
            self.client.admin.command('ping')
            self.database = self.client[DATABASE_NAME]
            self.is_connected = True
            
            logger.info("✅ Successfully connected to MongoDB Atlas")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {str(e)}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            self.is_connected = False
            logger.info("🔌 Disconnected from MongoDB")
    
    def get_collection(self, collection_name: str):
        """Get collection from database"""
        if not self.is_connected:
            if not self.connect():
                raise Exception("Failed to connect to database")
        
        return self.database[collection_name]
    
    def test_connection(self) -> Dict[str, Any]:
        """Test database connection and return status"""
        try:
            if not self.is_connected:
                self.connect()
            
            # Get server info
            server_info = self.client.server_info()
            
            # Get database stats
            db_stats = self.database.command("dbstats")
            
            # List collections
            collections = self.database.list_collection_names()
            
            return {
                "status": "connected",
                "server_version": server_info.get("version", "unknown"),
                "database_name": DATABASE_NAME,
                "collections": collections,
                "database_size": db_stats.get("dataSize", 0),
                "connection_time": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "connection_time": datetime.utcnow().isoformat()
            }

# Global database instance
db_manager = DatabaseManager()

def get_database():
    """Get database instance"""
    global db_manager
    
    if not db_manager.is_connected:
        db_manager.connect()
    
    return db_manager.database

def get_collection(collection_name: str):
    """Get specific collection"""
    db = get_database()
    return db[collection_name]

# Collection helpers
def get_users_collection():
    """Get users collection"""
    return get_collection("users")

def get_shipments_collection():
    """Get shipments collection"""
    return get_collection("shipments")

def get_audit_logs_collection():
    """Get audit logs collection"""
    return get_collection("audit_logs")

def get_notifications_collection():
    """Get notifications collection"""
    return get_collection("notifications")

def get_system_config_collection():
    """Get system configuration collection"""
    return get_collection("system_config")

def get_analytics_collection():
    """Get analytics collection"""
    return get_collection("analytics")

# Async database functions for future use
class AsyncDatabaseManager:
    """Async database manager for high-performance operations"""
    
    def __init__(self):
        self.client = None
        self.database = None
        self.is_connected = False
    
    async def connect(self) -> bool:
        """Establish async connection to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(
                MONGODB_URI,
                serverSelectionTimeoutMS=5000,
                maxPoolSize=10
            )
            
            # Test connection
            await self.client.admin.command('ping')
            self.database = self.client[DATABASE_NAME]
            self.is_connected = True
            
            logger.info("✅ Successfully connected to MongoDB Atlas (Async)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB (Async): {str(e)}")
            self.is_connected = False
            return False
    
    async def disconnect(self):
        """Close async database connection"""
        if self.client:
            self.client.close()
            self.is_connected = False
            logger.info("🔌 Disconnected from MongoDB (Async)")
    
    async def get_collection(self, collection_name: str):
        """Get collection from async database"""
        if not self.is_connected:
            await self.connect()
        
        return self.database[collection_name]

# Initialize database connection on module import
def initialize_database():
    """Initialize database connection"""
    try:
        success = db_manager.connect()
        if success:
            logger.info("🚀 Database initialized successfully")
            
            # Create indexes for better performance
            create_indexes()
            
        return success
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {str(e)}")
        return False

def create_indexes():
    """Create database indexes for better performance"""
    try:
        # Users collection indexes
        users_collection = get_users_collection()
        users_collection.create_index("username", unique=True)
        users_collection.create_index("email", unique=True)
        users_collection.create_index("role")
        
        # Shipments collection indexes
        shipments_collection = get_shipments_collection()
        shipments_collection.create_index("shipment_id", unique=True)
        shipments_collection.create_index("seller_id")
        shipments_collection.create_index("current_status")
        shipments_collection.create_index("destination_city")
        shipments_collection.create_index("created_at")
        shipments_collection.create_index("risk_score")
        
        # Audit logs indexes
        audit_collection = get_audit_logs_collection()
        audit_collection.create_index("user_id")
        audit_collection.create_index("action")
        audit_collection.create_index("timestamp")
        
        logger.info("📊 Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to create indexes: {str(e)}")

# Test function
def test_database_connection():
    """Test database connection"""
    return db_manager.test_connection()

# Auto-initialize on import
if not db_manager.is_connected:
    initialize_database()