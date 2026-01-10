"""
FastAPI Backend - Main Application
Phase 3 & 4: REST API with MongoDB and JWT Authentication

Endpoints:
- Authentication (register, login, JWT)
- Shipment intelligence (risk, address, weather)
- Pre-dispatch decisions
- Vehicle recommendations
- CO₂ trade-offs
- Human overrides
- System statistics
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import database connection
from database.connection import db_connection

# Import authentication routes
from auth_routes import router as auth_router

try:
    from routes import (
        shipments_router,
        intelligence_router,
        decisions_router,
        overrides_router,
        statistics_router,
        execution_router
    )
except ImportError:
    # Fallback: Create minimal routers if routes.py not available
    from fastapi import APIRouter
    shipments_router = APIRouter()
    intelligence_router = APIRouter()
    decisions_router = APIRouter()
    overrides_router = APIRouter()
    statistics_router = APIRouter()
    execution_router = APIRouter()

# Initialize FastAPI app
app = FastAPI(
    title="Logistics Intelligence & Command System API",
    description="AI-assisted logistics decision support system with human oversight",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event - Connect to MongoDB
@app.on_event("startup")
async def startup_event():
    """Initialize MongoDB connection on startup"""
    db_connection.connect()
    print("✅ FastAPI application started with MongoDB connection")

# Shutdown event - Close MongoDB connection
@app.on_event("shutdown")
async def shutdown_event():
    """Close MongoDB connection on shutdown"""
    db_connection.close()
    print("✅ FastAPI application shut down")

# Include routers
app.include_router(auth_router)  # Authentication routes (register, login, JWT)
app.include_router(shipments_router, prefix="/api/shipments", tags=["Shipments"])
app.include_router(intelligence_router, prefix="/api/intelligence", tags=["Intelligence"])
app.include_router(decisions_router, prefix="/api/decisions", tags=["Decisions"])
app.include_router(overrides_router, prefix="/api/overrides", tags=["Overrides"])
app.include_router(statistics_router, prefix="/api/statistics", tags=["Statistics"])
app.include_router(execution_router, prefix="/api/execution", tags=["Execution"])

@app.get("/")
async def root():
    """Root endpoint - API health check"""
    # Get MongoDB health
    db_health = db_connection.health_check()
    
    return {
        "message": "Logistics Intelligence & Command System API",
        "version": "1.0.0",
        "status": "operational",
        "authentication": "JWT enabled",
        "database": db_health,
        "docs": "/docs",
        "endpoints": {
            "auth": "/api/auth",
            "shipments": "/api/shipments",
            "intelligence": "/api/intelligence",
            "decisions": "/api/decisions",
            "overrides": "/api/overrides",
            "statistics": "/api/statistics",
            "execution": "/api/execution"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "LICS API",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
