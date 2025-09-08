#!/usr/bin/env python3
"""
Create Chat Tables Synchronous
Erstellt Chat-Tabellen über synchrone PostgreSQL-Verbindung
"""

import os
import logging
from pathlib import Path
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_chat_tables():
    """Create chat tables via direct PostgreSQL connection"""
    
    # Database URL from environment or hardcoded
    db_url = os.getenv(
        "SUPABASE_DB_URL",
        "postgresql://postgres:Specki2002!@db.snzxgfmewxbeevoywula.supabase.co:5432/postgres"
    )
    
    try:
        # Connect to database
        conn = psycopg2.connect(db_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        logger.info("✅ Connected to PostgreSQL")
        
        # Read SQL script
        sql_file = Path(__file__).parent / "create_chat_tables.sql"
        if not sql_file.exists():
            logger.error(f"❌ SQL file not found: {sql_file}")
            return False
        
        sql_script = sql_file.read_text(encoding='utf-8')
        logger.info("📄 Loaded SQL script")
        
        # Execute script
        cursor.execute(sql_script)
        logger.info("✅ SQL script executed successfully")
        
        # Verify tables were created
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name IN ('chat_sessions', 'chat_messages')
            ORDER BY table_name
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        logger.info(f"📋 Created tables: {', '.join(tables)}")
        
        if 'chat_sessions' in tables and 'chat_messages' in tables:
            logger.info("🎉 Both chat tables created successfully!")
            
            # Test insert
            cursor.execute("""
                INSERT INTO chat_sessions (title, user_id) 
                VALUES ('Test Session', 'test-user') 
                RETURNING id
            """)
            session_id = cursor.fetchone()[0]
            logger.info(f"✅ Test session created: {session_id}")
            
            # Clean up test data
            cursor.execute("DELETE FROM chat_sessions WHERE id = %s", (session_id,))
            logger.info("✅ Test data cleaned up")
            
            return True
        else:
            logger.error("❌ Not all tables were created")
            return False
            
    except Exception as e:
        logger.error(f"❌ Failed to create tables: {str(e)}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        logger.info("🔌 Database connection closed")

def test_chat_endpoint():
    """Test the chat endpoint after table creation"""
    
    try:
        import requests
        
        # Test health endpoint
        response = requests.get("http://localhost:8000/api/chat/health")
        health = response.json()
        logger.info(f"🏥 Chat health: {health}")
        
        # Test sessions endpoint
        response = requests.get(
            "http://localhost:8000/api/chat/sessions",
            headers={"X-User-ID": "test-user"}
        )
        
        if response.status_code == 200:
            sessions = response.json()
            logger.info(f"✅ Sessions endpoint working! Found {len(sessions)} sessions")
            return True
        else:
            logger.error(f"❌ Sessions endpoint failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Endpoint test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Creating Chat Tables...")
    
    success = create_chat_tables()
    
    if success:
        print("\n🧪 Testing Chat Endpoint...")
        endpoint_test = test_chat_endpoint()
        
        if endpoint_test:
            print("\n🎉 SUCCESS! Chat system is now fully functional!")
            print("✅ Tables created")
            print("✅ Endpoint responding")
            print("✅ Ready for frontend integration")
        else:
            print("\n⚠️  Tables created but endpoint still has issues.")
            print("Check backend logs for more details.")
    else:
        print("\n❌ Failed to create tables.")
        print("You may need to run the SQL manually in Supabase dashboard.")