"""
Modern Database Configuration for StreamWorks
Clean Supabase integration with enterprise-grade connection pooling
"""

import os
import logging
from datetime import datetime
from typing import AsyncGenerator
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from models.core import Base
from supabase import create_client, Client

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Supabase Database Configuration
SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_DB_URL:
    raise ValueError("SUPABASE_DB_URL environment variable is required")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables are required")

# For async operations, use asyncpg driver
SUPABASE_ASYNC_URL = SUPABASE_DB_URL.replace("postgresql://", "postgresql+asyncpg://")

# Async engine for application with optimized connection pooling
async_engine = create_async_engine(
    SUPABASE_ASYNC_URL,
    pool_pre_ping=True,
    pool_recycle=3600,  # Recycle connections every 60 minutes (increased)
    pool_size=20,        # Base pool size (increased for better concurrency)
    max_overflow=30,     # Additional connections when needed (increased)
    pool_timeout=60,     # Wait time for connection from pool (increased)
    pool_reset_on_return='commit',  # Reset connections on return
    echo=False,  # Set to True for SQL debugging
    # SSL configuration for Supabase
    connect_args={
        "ssl": "require",
        "server_settings": {
            "application_name": "streamworks_backend"
        }
    }
)

# Session makers
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=True,
    autocommit=False
)

# Sync engine for migrations and admin tasks
sync_engine = create_engine(
    SUPABASE_DB_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database sessions
    Used in FastAPI endpoints with proper state management
    """
    session = AsyncSessionLocal()
    try:
        yield session

        # Check if session is still active before committing
        if not session.is_active:
            logger.warning("Session is not active, skipping commit")
            return

        # Always attempt commit - SQLAlchemy handles if no transaction
        await session.commit()

    except Exception as e:
        logger.error(f"Session error: {str(e)}")

        # Only rollback if session is still active
        try:
            if session.is_active:
                await session.rollback()
        except Exception as rollback_error:
            logger.error(f"Rollback failed: {str(rollback_error)}")
        raise

    finally:
        # Ensure session is safely closed
        try:
            if session.is_active:
                await session.close()
        except Exception as close_error:
            logger.error(f"Session close failed: {str(close_error)}")
            # Don't re-raise close errors to avoid masking original exceptions


async def init_database():
    """
    Initialize database tables
    Creates all tables defined in models
    """
    try:
        async with async_engine.begin() as conn:
            # Create all tables (only creates if they don't exist)
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables ready")
            
        # Test connection
        async with AsyncSessionLocal() as session:
            from sqlalchemy import text
            await session.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise


async def close_database():
    """
    Close database connections
    Called on application shutdown
    """
    try:
        await async_engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database: {str(e)}")


# Health check function
async def check_database_health() -> dict:
    """
    Check if database is healthy
    Used for health endpoints
    """
    try:
        start_time = datetime.utcnow()
        async with AsyncSessionLocal() as session:
            from sqlalchemy import text
            result = await session.execute(text("SELECT 1"))
            end_time = datetime.utcnow()
            response_time = (end_time - start_time).total_seconds() * 1000  # in milliseconds

            return {
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
                "pool_size": async_engine.pool.size(),
                "pool_checked_in": async_engine.pool.checkedin(),
                "pool_checked_out": async_engine.pool.checkedout(),
                "timestamp": end_time.isoformat()
            }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


# Supabase Client for direct table operations
_supabase_client: Client = None

def get_supabase_client() -> Client:
    """Get Supabase client for direct table operations"""
    global _supabase_client

    if _supabase_client is None:
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

    return _supabase_client