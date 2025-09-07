"""
Modern Database Configuration for StreamWorks
Clean Supabase integration with enterprise-grade connection pooling
"""

import os
import logging
from typing import AsyncGenerator
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from models.core import Base

logger = logging.getLogger(__name__)

# Supabase Database Configuration
SUPABASE_DB_URL = os.getenv(
    "SUPABASE_DB_URL",
    "postgresql://postgres:Specki2002!@db.snzxgfmewxbeevoywula.supabase.co:5432/postgres"
)

# For async operations, use asyncpg driver
SUPABASE_ASYNC_URL = SUPABASE_DB_URL.replace("postgresql://", "postgresql+asyncpg://")

# Async engine for application with optimized connection pooling
async_engine = create_async_engine(
    SUPABASE_ASYNC_URL,
    pool_pre_ping=True,
    pool_recycle=1800,  # Recycle connections every 30 minutes
    pool_size=10,        # Base pool size
    max_overflow=20,     # Additional connections when needed
    pool_timeout=30,     # Wait time for connection from pool
    pool_reset_on_return='commit',  # Reset connections on return
    echo=False,  # Set to True for SQL debugging
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
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


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
async def check_database_health() -> bool:
    """
    Check if database is healthy
    Used for health endpoints
    """
    try:
        async with AsyncSessionLocal() as session:
            from sqlalchemy import text
            await session.execute(text("SELECT 1"))
            return True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False