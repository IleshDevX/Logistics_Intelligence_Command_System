"""
Demo Mode Utilities for LICS
Fallback data when MongoDB is unavailable
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any

def get_demo_users() -> List[Dict[str, Any]]:
    """Get demo user data"""
    return [
        {
            "_id": "user_001",
            "username": "admin",
            "email": "admin@lics.com",
            "full_name": "System Administrator",
            "role": "admin",
            "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewHgjPg.3QyLvEWu",
            "created_at": datetime.now() - timedelta(days=30),
            "last_login": datetime.now() - timedelta(hours=2),
            "is_active": True
        },
        {
            "_id": "user_002", 
            "username": "manager1",
            "email": "manager@lics.com",
            "full_name": "John Manager",
            "role": "manager",
            "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewHgjPg.3QyLvEWu",
            "created_at": datetime.now() - timedelta(days=20),
            "last_login": datetime.now() - timedelta(hours=1),
            "is_active": True
        },
        {
            "_id": "user_003",
            "username": "seller1",
            "email": "seller@lics.com", 
            "full_name": "Alice Seller",
            "role": "seller",
            "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewHgjPg.3QyLvEWu",
            "created_at": datetime.now() - timedelta(days=15),
            "last_login": datetime.now() - timedelta(minutes=30),
            "is_active": True
        }
    ]

def get_demo_shipments() -> List[Dict[str, Any]]:
    """Get demo shipment data"""
    return [
        {
            "_id": "shipment_001",
            "tracking_number": "LICS2026001",
            "seller_id": "user_003",
            "customer_name": "Customer One",
            "customer_phone": "+919876543210",
            "origin": "Mumbai",
            "destination": "Delhi",
            "weight": 2.5,
            "dimensions": {"length": 30, "width": 20, "height": 15},
            "value": 5000.0,
            "service_type": "express",
            "status": "in_transit",
            "created_at": datetime.now() - timedelta(days=2),
            "pickup_date": datetime.now() - timedelta(days=1),
            "expected_delivery": datetime.now() + timedelta(days=1),
            "risk_assessment": {
                "overall_risk": 3,
                "weather_risk": 2,
                "route_risk": 4,
                "traffic_risk": 3
            },
            "current_location": "Agra",
            "events": [
                {
                    "timestamp": datetime.now() - timedelta(days=1),
                    "status": "picked_up",
                    "location": "Mumbai",
                    "description": "Package picked up from seller"
                },
                {
                    "timestamp": datetime.now() - timedelta(hours=12),
                    "status": "in_transit",
                    "location": "Agra", 
                    "description": "Package in transit to destination"
                }
            ]
        },
        {
            "_id": "shipment_002",
            "tracking_number": "LICS2026002",
            "seller_id": "user_003",
            "customer_name": "Customer Two",
            "customer_phone": "+919876543211",
            "origin": "Bangalore",
            "destination": "Chennai",
            "weight": 1.2,
            "dimensions": {"length": 25, "width": 15, "height": 10},
            "value": 3000.0,
            "service_type": "standard",
            "status": "delivered",
            "created_at": datetime.now() - timedelta(days=5),
            "pickup_date": datetime.now() - timedelta(days=4),
            "expected_delivery": datetime.now() - timedelta(days=1),
            "delivered_at": datetime.now() - timedelta(hours=6),
            "risk_assessment": {
                "overall_risk": 2,
                "weather_risk": 1,
                "route_risk": 2,
                "traffic_risk": 3
            },
            "current_location": "Chennai",
            "events": [
                {
                    "timestamp": datetime.now() - timedelta(days=4),
                    "status": "picked_up",
                    "location": "Bangalore",
                    "description": "Package picked up from seller"
                },
                {
                    "timestamp": datetime.now() - timedelta(days=2),
                    "status": "in_transit",
                    "location": "Bangalore Hub",
                    "description": "Package processed at sorting facility"
                },
                {
                    "timestamp": datetime.now() - timedelta(hours=6),
                    "status": "delivered",
                    "location": "Chennai",
                    "description": "Package delivered to customer"
                }
            ]
        },
        {
            "_id": "shipment_003",
            "tracking_number": "LICS2026003",
            "seller_id": "user_003",
            "customer_name": "Customer Three",
            "customer_phone": "+919876543212",
            "origin": "Kolkata",
            "destination": "Pune", 
            "weight": 5.0,
            "dimensions": {"length": 40, "width": 30, "height": 25},
            "value": 8000.0,
            "service_type": "express",
            "status": "pending",
            "created_at": datetime.now() - timedelta(hours=3),
            "pickup_date": datetime.now() + timedelta(hours=6),
            "expected_delivery": datetime.now() + timedelta(days=2),
            "risk_assessment": {
                "overall_risk": 7,
                "weather_risk": 8,
                "route_risk": 6,
                "traffic_risk": 7
            },
            "current_location": "Kolkata",
            "events": [
                {
                    "timestamp": datetime.now() - timedelta(hours=3),
                    "status": "created",
                    "location": "Kolkata",
                    "description": "Shipment created and scheduled for pickup"
                }
            ]
        }
    ]

def get_demo_collections() -> Dict[str, Any]:
    """Get demo collections for database operations"""
    users = get_demo_users()
    shipments = get_demo_shipments()
    
    # Simple in-memory collection simulation
    class DemoCollection:
        def __init__(self, data):
            self.data = data
        
        def find(self, query=None):
            if not query:
                return self.data.copy()
            
            results = []
            for item in self.data:
                if self._matches_query(item, query):
                    results.append(item)
            return results
        
        def find_one(self, query):
            for item in self.data:
                if self._matches_query(item, query):
                    return item
            return None
        
        def _matches_query(self, item, query):
            for key, value in query.items():
                if '.' in key:
                    # Handle nested queries like 'risk_assessment.overall_risk'
                    keys = key.split('.')
                    obj = item
                    for k in keys:
                        if isinstance(obj, dict) and k in obj:
                            obj = obj[k]
                        else:
                            return False
                    
                    if isinstance(value, dict):
                        # Handle operators like $gte
                        for op, val in value.items():
                            if op == '$gte' and obj < val:
                                return False
                            elif op == '$lte' and obj > val:
                                return False
                            elif op == '$eq' and obj != val:
                                return False
                    else:
                        if obj != value:
                            return False
                else:
                    if key not in item or item[key] != value:
                        return False
            return True
    
    return {
        "users": DemoCollection(users),
        "shipments": DemoCollection(shipments)
    }

def is_demo_mode() -> bool:
    """Check if demo mode is enabled"""
    return os.getenv("USE_DEMO_MODE", "false").lower() == "true"