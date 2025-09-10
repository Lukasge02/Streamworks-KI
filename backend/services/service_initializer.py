"""
Service Initialization Module
Handles proper startup and shutdown of all services using the DI container
"""

import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager

from .di_container import get_container, initialize_container, cleanup_container

logger = logging.getLogger(__name__)


async def initialize_services():
    """Initialize all services on application startup"""
    try:
        logger.info("🚀 Initializing StreamWorks services...")
        
        # Initialize dependency injection container
        await initialize_container()
        
        logger.info("✅ All services initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {str(e)}")
        raise


async def shutdown_services():
    """Cleanup all services on application shutdown"""
    try:
        logger.info("🛑 Shutting down StreamWorks services...")
        
        # Cleanup dependency injection container
        await cleanup_container()
        
        logger.info("✅ All services shutdown successfully")
        
    except Exception as e:
        logger.error(f"❌ Error during service shutdown: {str(e)}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for service initialization"""
    # Startup
    await initialize_services()
    
    yield
    
    # Shutdown
    await shutdown_services()


async def get_service_health():
    """Get health status for all services"""
    try:
        container = get_container()
        return await container.health_check()
    except Exception as e:
        logger.error(f"Failed to get service health: {str(e)}")
        return {"status": "unhealthy", "error": str(e)}