#!/usr/bin/env python3
"""
Development Environment Setup Script
Sets up the development environment with proper database initialization
"""
import os
import sys
import logging
import asyncio
from pathlib import Path
from typing import Optional

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.core.settings import settings
from app.models.database import DatabaseManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class DevEnvironmentSetup:
    """Development environment setup manager"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    async def setup_database(self) -> bool:
        """Initialize development database"""
        try:
            logger.info("🔧 Setting up development database...")
            
            # Initialize database tables
            await self.db_manager.create_tables()
            logger.info("✅ Database tables created successfully")
            
            # Verify connection
            async with self.db_manager.get_session() as session:
                result = await session.execute("SELECT 1")
                if result.fetchone():
                    logger.info("✅ Database connection verified")
                    return True
                    
        except Exception as e:
            logger.error(f"❌ Database setup failed: {e}")
            return False
    
    async def setup_directories(self) -> bool:
        """Create required directories"""
        try:
            logger.info("📁 Creating required directories...")
            
            directories = [
                settings.STORAGE_PATH,
                Path(settings.STORAGE_PATH) / "documents",
                Path(settings.STORAGE_PATH) / "converted",
                Path(settings.STORAGE_PATH) / "temp",
                Path(settings.STORAGE_PATH) / "vector_db"
            ]
            
            for directory in directories:
                Path(directory).mkdir(parents=True, exist_ok=True)
                logger.info(f"✅ Created directory: {directory}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Directory setup failed: {e}")
            return False
    
    async def verify_environment(self) -> bool:
        """Verify development environment"""
        try:
            logger.info("🔍 Verifying development environment...")
            
            # Check environment variables
            required_vars = ['DATABASE_URL', 'STORAGE_PATH']
            missing_vars = [var for var in required_vars if not getattr(settings, var, None)]
            
            if missing_vars:
                logger.error(f"❌ Missing environment variables: {missing_vars}")
                return False
            
            logger.info("✅ Environment variables verified")
            return True
            
        except Exception as e:
            logger.error(f"❌ Environment verification failed: {e}")
            return False


async def main():
    """Main setup process"""
    setup = DevEnvironmentSetup()
    
    try:
        logger.info("🚀 Starting development environment setup...")
        
        # Verify environment
        if not await setup.verify_environment():
            logger.error("❌ Environment verification failed")
            sys.exit(1)
        
        # Setup directories
        if not await setup.setup_directories():
            logger.error("❌ Directory setup failed")
            sys.exit(1)
        
        # Setup database
        if not await setup.setup_database():
            logger.error("❌ Database setup failed")
            sys.exit(1)
        
        logger.info("🎉 Development environment setup completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Setup failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())