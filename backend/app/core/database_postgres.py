"""
PostgreSQL Database Service - Enterprise Setup
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import event, text
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from app.core.postgres_config import settings

logger = logging.getLogger(__name__)

# Database Engine
engine = create_async_engine(
    settings.async_database_url,
    **settings.get_db_config()
)

# Session Factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Database Dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Database session dependency for FastAPI"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Connection Management
@asynccontextmanager
async def get_db_session():
    """Context manager for database sessions"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Database Initialization
async def init_database():
    """Initialize database with tables and indexes"""
    logger.info("🗄️ Initializing PostgreSQL database...")
    
    try:
        from app.models.postgres_models import Base
        
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # Create analytics views
        await create_analytics_views()
        
        logger.info("✅ Database initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

async def create_analytics_views():
    """Create analytics views for Bachelor thesis evaluation"""
    
    # Split SQL statements to work with asyncpg
    statements = [
        "CREATE SCHEMA IF NOT EXISTS analytics",
        
        """CREATE OR REPLACE VIEW analytics.performance_summary AS
        SELECT 
            DATE_TRUNC('hour', created_at) as hour,
            COUNT(*) as total_queries,
            AVG(total_processing_time) as avg_processing_time,
            PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY total_processing_time) as p95_processing_time,
            AVG(confidence_score) as avg_confidence,
            COUNT(*) FILTER (WHERE confidence_score > 0.8) as high_confidence_queries,
            AVG(chunks_retrieved) as avg_chunks_retrieved,
            AVG(chunks_used_in_answer) as avg_chunks_used
        FROM chat_sessions
        WHERE created_at > NOW() - INTERVAL '30 days'
        GROUP BY DATE_TRUNC('hour', created_at)
        ORDER BY hour DESC""",
        
        """CREATE OR REPLACE VIEW analytics.document_processing AS
        SELECT 
            DATE_TRUNC('day', uploaded_at) as day,
            COUNT(*) as documents_uploaded,
            COUNT(*) FILTER (WHERE status = 'indexed') as documents_indexed,
            AVG(file_size / 1024.0) as avg_file_size_kb,
            AVG(conversion_time_seconds) as avg_conversion_time,
            AVG(indexing_time_seconds) as avg_indexing_time,
            AVG(chunk_count) as avg_chunks_per_document
        FROM documents
        WHERE uploaded_at > NOW() - INTERVAL '30 days'
        GROUP BY DATE_TRUNC('day', uploaded_at)
        ORDER BY day DESC""",
        
        """CREATE OR REPLACE VIEW analytics.system_performance AS
        SELECT 
            metric_category,
            metric_name,
            DATE_TRUNC('hour', recorded_at) as hour,
            AVG(metric_value) as avg_value,
            MAX(metric_value) as max_value,
            MIN(metric_value) as min_value,
            COUNT(*) as measurement_count
        FROM system_metrics
        WHERE recorded_at > NOW() - INTERVAL '24 hours'
        GROUP BY metric_category, metric_name, DATE_TRUNC('hour', recorded_at)
        ORDER BY hour DESC, metric_category, metric_name""",
        
        """CREATE OR REPLACE VIEW analytics.rag_effectiveness AS
        SELECT 
            c.content_type,
            COUNT(*) as total_chunks,
            AVG(c.quality_score) as avg_quality_score,
            AVG(c.retrieval_count) as avg_retrieval_count,
            AVG(c.avg_relevance_score) as avg_relevance_score,
            COUNT(*) FILTER (WHERE c.retrieval_count > 0) as chunks_ever_retrieved
        FROM document_chunks c
        WHERE c.quality_score IS NOT NULL
        GROUP BY c.content_type
        ORDER BY avg_relevance_score DESC NULLS LAST"""
    ]
    
    async with engine.begin() as conn:
        for statement in statements:
            await conn.execute(text(statement))
    
    logger.info("📊 Analytics views created successfully")

# Health Check
async def check_database_health() -> bool:
    """Check database connectivity and performance"""
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            return result.scalar() == 1
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False

# Cleanup
async def close_database():
    """Close database connections"""
    await engine.dispose()
    logger.info("🔒 Database connections closed")