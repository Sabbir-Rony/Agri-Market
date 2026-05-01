"""
Main FastAPI application for Pre-Harvest Marketplace
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from pathlib import Path

from app.core.config import settings
from app.core.database import init_db
from app.api.routes import (
    routes_auth,
    routes_products,
    routes_orders,
    routes_payments,
    routes_deliveries,
    routes_claims,
    routes_dashboard,
    routes_upload
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown"""
    # Startup
    await init_db()
    yield
    # Shutdown
    pass


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="B2B/B2C Pre-Harvest Marketplace with escrow-like split payments",
    lifespan=lifespan
)

# Configure CORS - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(routes_auth.router, prefix="/api")
app.include_router(routes_products.router, prefix="/api")
app.include_router(routes_orders.router, prefix="/api")
app.include_router(routes_payments.router, prefix="/api")
app.include_router(routes_deliveries.router, prefix="/api")
app.include_router(routes_claims.router, prefix="/api")
app.include_router(routes_dashboard.router, prefix="/api")
app.include_router(routes_upload.router, prefix="/api")

# Serve uploaded files
if Path("uploads").exists():
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Pre-Harvest Marketplace API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Run with: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000