#!/usr/bin/env python3
"""
Initialize PostgreSQL database with tables and views
"""
import asyncio
import logging
from app.core.database_postgres import init_database

logging.basicConfig(level=logging.INFO)

async def main():
    """Initialize the database"""
    try:
        await init_database()
        print("✅ PostgreSQL database initialized successfully!")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())