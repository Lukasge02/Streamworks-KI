# backend/app/models/database.py
import asyncio
import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, JSON, String, Text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base

from app.core.settings import settings

logger = logging.getLogger(__name__)

# Database Base
Base = declarative_base()

# Training Files Model
class TrainingFile(Base):
    __tablename__ = "training_files"
    
    
    # SQLAlchemy Column definitions
    id = Column(String, primary_key=True)
    filename = Column(String, nullable=False)        # Original filename (clean)
    display_name = Column(String, nullable=False)    # User-friendly display name
    category = Column(String, nullable=False)        # help_data, stream_templates
    file_path = Column(String, nullable=False)       # Path to original file
    upload_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    file_size = Column(Integer, nullable=False)
    status = Column(String, default="processing")  # uploading, processing, ready, error, indexed
    error_message = Column(Text, nullable=True)
    
    # ChromaDB Integration Fields
    is_indexed = Column(Boolean, default=False)
    indexed_at = Column(DateTime, nullable=True)
    chunk_count = Column(Integer, default=0)
    chromadb_ids = Column(JSON, nullable=True)  # Store ChromaDB document IDs
    index_status = Column(String, nullable=True)  # indexing, indexed, failed
    index_error = Column(Text, nullable=True)
    
    # Document Processing Fields (Enhanced)
    processed_file_path = Column(String, nullable=True)  # Pfad zur optimierten MD-Datei
    original_format = Column(String, nullable=True)      # txt, md, pdf, docx, etc.
    optimized_format = Column(String, nullable=True)     # md, processed
    conversion_status = Column(String, nullable=True)    # completed, failed, skipped, partial
    conversion_error = Column(Text, nullable=True)       # Konvertierungsfehler
    conversion_metadata = Column(Text, nullable=True)    # JSON mit Metadaten
    processing_error = Column(Text, nullable=True)       # Allgemeine Verarbeitungsfehler
    
    # Production Document Processing Fields (NEW)
    document_category = Column(String, nullable=True)    # help_docs, office_doc, code_script, etc.
    processing_method = Column(String, nullable=True)    # pypdf_loader, python_docx, etc.
    processing_quality = Column(String, nullable=True)   # excellent, good, acceptable, poor, failed
    extraction_confidence = Column(String, nullable=True) # 0.0-1.0 confidence score as string
    
    # Multi-Source Citation Fields
    source_type = Column(String, nullable=True)          # StreamWorks, JIRA, DDDS, Documentation
    source_title = Column(String, nullable=True)         # Human-readable source title
    source_url = Column(String, nullable=True)           # Optional URL to original source
    document_type = Column(String, nullable=True)        # FAQ, Guide, Tutorial, API, Reference
    author = Column(String, nullable=True)               # Document author/creator
    version = Column(String, nullable=True)              # Document version
    last_modified = Column(DateTime, nullable=True)      # Last modification date
    priority = Column(Integer, default=1)                # Priority for citation ranking (1=highest)
    tags = Column(JSON, nullable=True)                   # Tags for categorization
    language = Column(String, default="de")              # Document language
    
    # Manual Source Categorization Fields (NEW)
    manual_source_category = Column(String, nullable=True)  # Testdaten, StreamWorks Hilfe, SharePoint
    description = Column(Text, nullable=True)              # User-provided description
    upload_timestamp = Column(DateTime, nullable=True)     # Upload timestamp
    original_path = Column(String, nullable=True)          # Path to original uploaded file

# Database Engine & Session with enhanced configuration
# Production-ready configuration with optimized settings
engine_kwargs = {
    "echo": settings.ENV == "development",  # Log SQL in development only
    "future": True,  # Enable SQLAlchemy 2.0 style
}

# Add database-specific optimizations
if not settings.DATABASE_URL.startswith("sqlite"):
    # PostgreSQL/MySQL production settings
    engine_kwargs.update({
        "pool_size": 10,  # Base connections (reduced for efficiency)
        "max_overflow": 20,  # Additional connections when needed
        "pool_pre_ping": True,  # Verify connections before use
        "pool_recycle": 3600,  # Recycle connections every hour
        "pool_timeout": 30,  # Timeout for getting connection from pool
        "pool_reset_on_return": "commit",  # Reset connections on return
        "connect_args": {
            "server_settings": {
                "application_name": "streamworks-ki"
            },
            "command_timeout": 10
        }
    })
else:
    # SQLite-specific optimizations (no pooling parameters for SQLite)
    engine_kwargs.update({
        "connect_args": {
            "check_same_thread": False,
            "timeout": 20  # SQLite timeout
        }
    })

engine = create_async_engine(
    settings.DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://").replace("postgresql://", "postgresql+asyncpg://"),
    **engine_kwargs
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    autoflush=False  # Better control over flush timing
)

async def get_db():
    """Enhanced database dependency with proper error handling"""
    session = None
    try:
        session = AsyncSessionLocal()
        yield session
    except Exception as e:
        logger.error(f"❌ Database session error: {e}")
        if session is not None:
            await session.rollback()
        raise
    finally:
        if session is not None:
            await session.close()

async def get_db_session():
    """Get database session for direct use (not dependency)"""
    return AsyncSessionLocal()

class DatabaseManager:
    """Production-Ready Database Manager with enhanced error handling and monitoring"""
    
    def __init__(self):
        self.engine = engine
        self.session_factory = AsyncSessionLocal
        self.is_initialized = False
        self.connection_retries = 0
        self.max_retries = 3
        self.retry_delay = 1.0  # seconds
        
        # Performance tracking
        self.performance_stats = {
            "total_queries": 0,
            "failed_queries": 0,
            "avg_response_time": 0.0,
            "connection_pool_size": 0,
            "active_connections": 0
        }
    
    async def init_db(self):
        """Initialize database with comprehensive error handling and retry logic"""
        for attempt in range(self.max_retries):
            try:
                logger.info(f"🚀 Initializing database (attempt {attempt + 1}/{self.max_retries})...")
                
                # Test connection with timeout
                start_time = time.time()
                async with self.engine.begin() as conn:
                    # Test basic connectivity
                    from sqlalchemy import text
                    await conn.execute(text("SELECT 1"))
                    connection_time = time.time() - start_time
                    logger.info(f"✅ Database connection verified ({connection_time:.3f}s)")
                    
                    # Create all tables
                    await conn.run_sync(Base.metadata.create_all)
                    logger.info("✅ Database tables created successfully")
                
                # Reset retry counter on success
                self.connection_retries = 0
                break
                
            except Exception as e:
                self.connection_retries += 1
                logger.warning(f"⚠️ Database init attempt {attempt + 1} failed: {e}")
                
                if attempt < self.max_retries - 1:
                    logger.info(f"🔄 Retrying in {self.retry_delay}s...")
                    await asyncio.sleep(self.retry_delay)
                    self.retry_delay *= 2  # Exponential backoff
                else:
                    logger.error("❌ Database initialization failed after all retries")
                    raise DatabaseInitializationError(f"Failed to initialize database after {self.max_retries} attempts: {e}")
        
        # Import and create evaluation tables if needed (outside the retry loop)
        try:
            from app.models.evaluation import create_evaluation_tables
            await self._run_in_session(create_evaluation_tables)
            logger.info("✅ Evaluation tables created successfully")
        except ImportError:
            logger.warning("⚠️ Evaluation tables module not found, skipping")
        except Exception as e:
            logger.warning(f"⚠️ Could not create evaluation tables: {e}")
        
        self.is_initialized = True
        logger.info("✅ Database initialization completed")
    
    @asynccontextmanager
    async def get_session_with_retry(self):
        """Get database session with automatic retry and performance tracking"""
        session = None
        start_time = time.time()
        
        for attempt in range(self.max_retries):
            try:
                session = self.session_factory()
                self.performance_stats["total_queries"] += 1
                yield session
                if session is not None:
                    await session.commit()
                
                # Track performance
                response_time = time.time() - start_time
                self._update_performance_stats(response_time)
                return
                
            except Exception as e:
                self.performance_stats["failed_queries"] += 1
                if session is not None:
                    await session.rollback()
                
                if attempt < self.max_retries - 1:
                    logger.warning(f"⚠️ Database operation failed (attempt {attempt + 1}), retrying: {e}")
                    await asyncio.sleep(0.5 * (attempt + 1))  # Progressive delay
                else:
                    logger.error(f"❌ Database operation failed after {self.max_retries} attempts: {e}")
                    raise
            finally:
                if session is not None:
                    await session.close()
    
    async def _run_in_session(self, func, *args, **kwargs):
        """Run function in database session with error handling"""
        async with self.get_session_with_retry() as session:
            if asyncio.iscoroutinefunction(func):
                return await func(session, *args, **kwargs)
            else:
                return func(session, *args, **kwargs)
    
    def _update_performance_stats(self, response_time: float):
        """Update performance statistics"""
        current_avg = self.performance_stats["avg_response_time"]
        total_queries = self.performance_stats["total_queries"]
        
        # Calculate new average
        new_avg = ((current_avg * (total_queries - 1)) + response_time) / total_queries
        self.performance_stats["avg_response_time"] = new_avg
    
    async def test_connection(self) -> bool:
        """Test database connectivity"""
        try:
            async with self.engine.begin() as conn:
                from sqlalchemy import text
                await conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"❌ Database connection test failed: {e}")
            return False
    
    async def get_health_status(self) -> dict:
        """Get database health status"""
        try:
            # Test basic connectivity
            connection_ok = await self.test_connection()
            
            if not connection_ok:
                return {
                    "status": "unhealthy",
                    "connection": False,
                    "error": "Cannot connect to database"
                }
            
            # Get table information
            async with self.engine.begin() as conn:
                # Check if tables exist
                from sqlalchemy import text
                result = await conn.execute(
                    text("SELECT name FROM sqlite_master WHERE type='table'")
                )
                tables = [row[0] for row in result.fetchall()]
            
            return {
                "status": "healthy",
                "connection": True,
                "tables_count": len(tables),
                "tables": tables,
                "is_initialized": self.is_initialized,
                "pool_size": self.engine.pool.size() if hasattr(self.engine.pool, 'size') else "unknown",
                "checked_out": self.engine.pool.checkedout() if hasattr(self.engine.pool, 'checkedout') else "unknown"
            }
            
        except Exception as e:
            logger.error(f"❌ Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "connection": False,
                "error": str(e),
                "is_initialized": self.is_initialized
            }
    
    async def cleanup(self):
        """Cleanup database connections"""
        try:
            await self.engine.dispose()
            logger.info("✅ Database connections cleaned up")
        except Exception as e:
            logger.error(f"❌ Database cleanup failed: {e}")

class DatabaseInitializationError(Exception):
    """Custom exception for database initialization errors"""
    pass

# Global database manager instance
db_manager = DatabaseManager()

# Legacy function for backward compatibility
async def init_db():
    """Initialize database tables (legacy function)"""
    await db_manager.init_db()