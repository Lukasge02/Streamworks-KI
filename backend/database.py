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

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Supabase Database Configuration
SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")

if not SUPABASE_DB_URL:
    raise ValueError("SUPABASE_DB_URL environment variable is required")

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
    Used in FastAPI endpoints
    """
    session = None
    try:
        session = AsyncSessionLocal()
        yield session
        # Commit only if session is still active and has changes
        if session and hasattr(session, '_transaction') and session._transaction:
            await session.commit()
    except Exception as e:
        logger.error(f"Session error: {str(e)}")
        if session:
            try:
                await session.rollback()
            except Exception as rollback_error:
                logger.warning(f"Session rollback failed (non-critical): {str(rollback_error)}")
        raise
    finally:
        if session:
            try:
                # Ensure session is properly closed
                await session.close()
            except Exception as close_error:
                logger.warning(f"Session close error (non-critical): {str(close_error)}")


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
        async with AsyncSessionLocal() as session:
            from sqlalchemy import text
            result = await session.execute(text("SELECT 1"))
            
            # Get connection pool stats
            pool = async_engine.pool
            pool_stats = {
                "pool_size": pool.size(),
                "pool_overflow": pool.overflow(),
                "pool_checked_in": pool.checkedin(),
                "pool_checked_out": pool.checkedout()
            }
            
            return {
                "status": "healthy",
                "connection_test": "successful",
                "pool_stats": pool_stats,
                "timestamp": datetime.utcnow().isoformat()
            }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }