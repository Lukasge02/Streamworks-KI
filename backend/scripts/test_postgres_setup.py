"""
Test PostgreSQL Setup und Analytics
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database_postgres import check_database_health, get_db_session
from app.services.analytics_service import analytics_service
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_postgres_setup():
    """Test complete PostgreSQL setup"""
    
    logger.info("🧪 Testing PostgreSQL setup...")
    
    # 1. Test database connectivity
    health_ok = await check_database_health()
    logger.info(f"Database Health: {'✅ OK' if health_ok else '❌ FAILED'}")
    
    # 2. Test table creation
    async with get_db_session() as session:
        try:
            result = await session.execute(text("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            logger.info(f"Tables created: {tables}")
        except Exception as e:
            logger.error(f"Failed to query tables: {e}")
    
    # 3. Test analytics views
    async with get_db_session() as session:
        try:
            result = await session.execute(text("""
            SELECT viewname FROM pg_views 
            WHERE schemaname = 'analytics'
            ORDER BY viewname
            """))
            views = [row[0] for row in result]
            logger.info(f"Analytics views: {views}")
        except Exception as e:
            logger.error(f"Failed to query views: {e}")
    
    # 4. Test analytics service
    try:
        performance_data = await analytics_service.get_performance_summary(7)
        logger.info(f"Analytics service: ✅ OK")
        logger.info(f"Sample data: {performance_data}")
    except Exception as e:
        logger.error(f"Analytics service: ❌ FAILED - {e}")
    
    logger.info("✅ PostgreSQL setup test completed!")

if __name__ == "__main__":
    asyncio.run(test_postgres_setup())