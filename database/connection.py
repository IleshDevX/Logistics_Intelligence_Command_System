"""
Phase 3.2: MongoDB Connection Module
====================================

Handles MongoDB connections with:
- Connection pooling
- Error handling
- Health checks
- Database operations
- Streamlit Cloud compatibility
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from typing import Optional
import os
from datetime import datetime

class DatabaseConnection:
    """MongoDB connection handler with pooling and error handling"""
    
    _instance = None
    _client: Optional[MongoClient] = None
    _db = None
    
    # MongoDB Configuration - Streamlit compatible
    @staticmethod
    def _get_mongo_config():
        """Get MongoDB configuration from Streamlit secrets or environment"""
        try:
            # Try Streamlit secrets first (for Streamlit Cloud)
            import streamlit as st
            if hasattr(st, 'secrets') and 'mongodb' in st.secrets:
                return (
                    st.secrets["mongodb"]["uri"],
                    st.secrets["mongodb"].get("database", "lics_db")
                )
        except (ImportError, FileNotFoundError, KeyError):
            pass
        
        # Fallback to environment variables (for local/FastAPI)
        return (
            os.getenv("MONGO_URI", "mongodb://localhost:27017/"),
            os.getenv("DATABASE_NAME", "lics_db")
        )
    
    MONGO_URI, DATABASE_NAME = _get_mongo_config()
    
    def __new__(cls):
        """Singleton pattern - only one connection instance"""
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
    
    def connect(self):
        """
        Establish connection to MongoDB
        Returns: True if successful, False otherwise
        """
        try:
            if self._client is None:
                self._client = MongoClient(
                    self.MONGO_URI,
                    serverSelectionTimeoutMS=5000,  # 5 second timeout
                    maxPoolSize=50,  # Connection pool size
                    minPoolSize=10,
                    maxIdleTimeMS=60000  # 60 seconds
                )
                
                # Test connection
                self._client.admin.command('ping')
                self._db = self._client[self.DATABASE_NAME]
                
                print(f"✅ Connected to MongoDB: {self.DATABASE_NAME}")
                return True
                
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"❌ MongoDB Connection Failed: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error connecting to MongoDB: {e}")
            return False
    
    def get_database(self):
        """Get database instance"""
        if self._db is None:
            self.connect()
        return self._db
    
    def get_collection(self, collection_name: str):
        """Get a specific collection"""
        db = self.get_database()
        return db[collection_name] if db else None
    
    def health_check(self) -> dict:
        """
        Check MongoDB health status
        Returns: dict with status and details
        """
        try:
            if self._client is None:
                return {"status": "disconnected", "message": "Not connected to MongoDB"}
            
            # Ping MongoDB
            self._client.admin.command('ping')
            
            # Get collection stats
            db = self.get_database()
            collections = db.list_collection_names()
            
            return {
                "status": "healthy",
                "database": self.DATABASE_NAME,
                "collections": len(collections),
                "collection_names": collections,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def close(self):
        """Close MongoDB connection"""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            print("✅ MongoDB connection closed")
    
    # Collection accessors
    @property
    def users(self):
        """Users collection"""
        return self.get_collection("users")
    
    @property
    def shipments(self):
        """Shipments collection"""
        return self.get_collection("shipments")
    
    @property
    def risk_scores(self):
        """Risk scores collection"""
        return self.get_collection("risk_scores")
    
    @property
    def decisions(self):
        """Decisions collection"""
        return self.get_collection("decisions")
    
    @property
    def notifications(self):
        """Notifications collection"""
        return self.get_collection("notifications")
    
    @property
    def learning_logs(self):
        """Learning logs collection"""
        return self.get_collection("learning_logs")


# Global database instance
db_connection = DatabaseConnection()


def get_db():
    """
    Dependency injection for FastAPI
    Usage: db = Depends(get_db)
    """
    return db_connection.get_database()


def get_users_collection():
    """Get users collection"""
    return db_connection.users


def get_shipments_collection():
    """Get shipments collection"""
    return db_connection.shipments
