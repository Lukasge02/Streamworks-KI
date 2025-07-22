"""
Cleanup Script - Entfernt alle alten chaotischen Config-Dateien
"""
import os
import shutil
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def cleanup_config_chaos():
    """Entfernt alle alten, chaotischen Config-Dateien"""
    
    logger.info("🧹 Cleaning up config chaos...")
    
    # Config-Dateien die entfernt werden sollen
    config_files_to_remove = [
        "backend/app/core/config.py",  # Alte unified config
        "backend/app/core/production_config.py",  # Parallel production config
        "backend/app/core/storage_config.py",  # Alte storage config
        "backend/app/core/service_container.py",  # Over-engineered DI
        "backend/requirements_postgres.txt",  # Separate postgres requirements
    ]
    
    removed_files = []
    for config_file in config_files_to_remove:
        config_path = Path(config_file)
        if config_path.exists():
            config_path.unlink()
            removed_files.append(config_file)
            logger.info(f"🗑️ Removed: {config_file}")
    
    # Service-Dateien die durch PostgreSQL obsolet werden
    obsolete_services = [
        "backend/app/services/enterprise_intelligent_chunker.py",
        "backend/app/services/enterprise_chromadb_indexer.py", 
        "backend/app/services/production_document_processor.py",
    ]
    
    for service_file in obsolete_services:
        service_path = Path(service_file)
        if service_path.exists():
            service_path.unlink()
            removed_files.append(service_file)
            logger.info(f"🗑️ Removed obsolete service: {service_file}")
    
    logger.info(f"✅ Removed {len(removed_files)} chaotic config/service files")
    return removed_files

def cleanup_storage_paths():
    """Konsolidiert chaotische Storage-Pfade"""
    
    logger.info("📁 Consolidating storage paths...")
    
    # Alte chaotische Pfade die bereinigt werden
    old_paths_to_cleanup = [
        "./backend/data/",  # Doppelte data Ordner
        "./backend/streamworks.db",  # Alte SQLite DBs
        "./backend/streamworks_ki.db",
    ]
    
    cleaned_paths = []
    for old_path in old_paths_to_cleanup:
        path_obj = Path(old_path)
        if path_obj.exists():
            try:
                if path_obj.is_file():
                    path_obj.unlink()
                else:
                    shutil.rmtree(path_obj)
                cleaned_paths.append(old_path)
                logger.info(f"🗑️ Removed path: {old_path}")
            except Exception as e:
                logger.warning(f"⚠️ Could not remove {old_path}: {e}")
    
    logger.info(f"✅ Cleaned {len(cleaned_paths)} storage paths")
    return cleaned_paths

def update_main_app():
    """Update main.py to use only PostgreSQL config"""
    
    main_py_content = '''"""
Streamworks-KI Backend - Clean PostgreSQL Architecture
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.postgres_config import settings
from app.core.database_postgres import init_database, close_database
from app.api.v1.qa_api import router as qa_router
from app.api.v1.training import router as training_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.xml import router as xml_router

# Setup logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Clean startup/shutdown with PostgreSQL"""
    
    # Startup
    logger.info("🚀 Starting Streamworks-KI (PostgreSQL)")
    logger.info(f"🔧 Environment: {'Development' if settings.DEBUG else 'Production'}")
    
    try:
        # Initialize PostgreSQL
        await init_database()
        logger.info("✅ PostgreSQL initialized")
        
        yield
        
    finally:
        # Shutdown
        await close_database()
        logger.info("🔒 Application shutdown complete")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(qa_router, prefix=settings.API_PREFIX)
app.include_router(training_router, prefix=settings.API_PREFIX)
app.include_router(analytics_router, prefix=settings.API_PREFIX)
app.include_router(xml_router, prefix=settings.API_PREFIX)

@app.get("/")
async def root():
    return {
        "message": "Streamworks-KI API",
        "version": settings.VERSION,
        "database": "PostgreSQL",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "database": "postgresql"
    }
'''
    
    main_path = Path("backend/app/main.py")
    with open(main_path, 'w') as f:
        f.write(main_py_content)
    
    logger.info("✅ Updated main.py for clean PostgreSQL setup")

def complete_cleanup():
    """Führt komplette Bereinigung durch"""
    
    logger.info("🧹 Starting complete config & storage cleanup...")
    
    # 1. Config cleanup
    removed_configs = cleanup_config_chaos()
    
    # 2. Storage cleanup  
    cleaned_paths = cleanup_storage_paths()
    
    # 3. Update main app
    update_main_app()
    
    logger.info("✅ Complete cleanup finished!")
    logger.info(f"📊 Cleanup Summary:")
    logger.info(f"   Configs removed: {len(removed_configs)}")
    logger.info(f"   Paths cleaned: {len(cleaned_paths)}")
    logger.info(f"   Main app updated for PostgreSQL")

if __name__ == "__main__":
    complete_cleanup()