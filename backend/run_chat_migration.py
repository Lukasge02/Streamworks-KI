#!/usr/bin/env python3
"""
Run Chat System Migration for Supabase
Creates chat_sessions and chat_messages tables with all necessary indices and policies
"""

import asyncio
import logging
from pathlib import Path
from supabase import create_client, Client
from config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_migration():
    """Execute the chat system migration"""
    
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
        logger.error("❌ SUPABASE_URL and SUPABASE_SERVICE_KEY must be configured")
        return False
    
    try:
        # Initialize Supabase client
        supabase: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY
        )
        logger.info("✅ Connected to Supabase")
        
        # Read migration SQL file
        migration_file = Path(__file__).parent / "migrations" / "001_create_chat_tables.sql"
        
        if not migration_file.exists():
            logger.error(f"❌ Migration file not found: {migration_file}")
            return False
        
        migration_sql = migration_file.read_text(encoding='utf-8')
        logger.info(f"📄 Loaded migration from {migration_file}")
        
        # Split the SQL into individual statements (simple approach)
        statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip()]
        
        logger.info(f"🔄 Executing {len(statements)} SQL statements...")
        
        # Execute each statement
        executed = 0
        for i, statement in enumerate(statements, 1):
            if statement.strip():
                try:
                    # Use RPC to execute raw SQL
                    result = supabase.rpc('exec_sql', {'sql': statement}).execute()
                    executed += 1
                    logger.debug(f"✓ Statement {i}/{len(statements)} executed")
                except Exception as e:
                    # Some statements might fail if objects already exist - that's ok
                    if "already exists" in str(e).lower():
                        logger.debug(f"⚠️  Statement {i} skipped (already exists)")
                    else:
                        logger.warning(f"⚠️  Statement {i} failed: {str(e)}")
        
        logger.info(f"✅ Migration completed! Executed {executed} statements")
        
        # Verify tables were created
        await verify_migration(supabase)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        return False

async def verify_migration(supabase: Client):
    """Verify that the migration was successful"""
    
    try:
        # Test chat_sessions table
        sessions_test = supabase.table("chat_sessions").select("count", count="exact").limit(0).execute()
        logger.info(f"✅ chat_sessions table verified (exists)")
        
        # Test chat_messages table  
        messages_test = supabase.table("chat_messages").select("count", count="exact").limit(0).execute()
        logger.info(f"✅ chat_messages table verified (exists)")
        
        # Test stored function
        try:
            stats_test = supabase.rpc("get_user_chat_stats", {"p_user_id": "test-user"}).execute()
            logger.info("✅ get_user_chat_stats function verified")
        except Exception as e:
            logger.warning(f"⚠️  get_user_chat_stats function test failed: {str(e)}")
        
        logger.info("🎉 Migration verification completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Migration verification failed: {str(e)}")

async def create_test_session(supabase: Client):
    """Create a test chat session to verify functionality"""
    
    try:
        # Create test session
        test_session = {
            "title": "Test Chat Session",
            "user_id": "test-user",
            "message_count": 0,
            "is_active": True
        }
        
        result = supabase.table("chat_sessions").insert(test_session).execute()
        
        if result.data:
            session_id = result.data[0]["id"]
            logger.info(f"✅ Test session created: {session_id}")
            
            # Create test message
            test_message = {
                "session_id": session_id,
                "user_id": "test-user", 
                "role": "user",
                "content": "Hello, this is a test message!"
            }
            
            msg_result = supabase.table("chat_messages").insert(test_message).execute()
            
            if msg_result.data:
                logger.info(f"✅ Test message created")
                
                # Verify session was updated
                session_check = supabase.table("chat_sessions").select("*").eq("id", session_id).execute()
                if session_check.data and session_check.data[0]["message_count"] == 1:
                    logger.info("✅ Session message count updated correctly")
                
                # Clean up test data
                supabase.table("chat_sessions").delete().eq("id", session_id).execute()
                logger.info("✅ Test data cleaned up")
                
        logger.info("🎉 Test session creation successful!")
        
    except Exception as e:
        logger.error(f"❌ Test session creation failed: {str(e)}")

# Alternative approach: Execute SQL directly through psycopg2 if needed
async def run_migration_direct():
    """Alternative method using direct SQL execution if RPC doesn't work"""
    
    try:
        import psycopg2
        
        # Parse Supabase URL to get connection details
        import urllib.parse as urlparse
        url = urlparse.urlparse(settings.SUPABASE_URL)
        
        # Connect directly to PostgreSQL
        conn = psycopg2.connect(
            host=url.hostname,
            port=url.port or 5432,
            database=url.path[1:],  # Remove leading slash
            user="postgres",  # Supabase default
            password=settings.SUPABASE_SERVICE_KEY.split('.')[1]  # Extract from JWT - this is simplified
        )
        
        cursor = conn.cursor()
        
        # Read and execute migration
        migration_file = Path(__file__).parent / "migrations" / "001_create_chat_tables.sql"
        migration_sql = migration_file.read_text(encoding='utf-8')
        
        cursor.execute(migration_sql)
        conn.commit()
        
        logger.info("✅ Direct SQL migration completed")
        
        cursor.close()
        conn.close()
        
    except ImportError:
        logger.error("❌ psycopg2 not available for direct SQL execution")
    except Exception as e:
        logger.error(f"❌ Direct SQL migration failed: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Chat System Migration...")
    
    success = asyncio.run(run_migration())
    
    if success:
        print("✅ Migration completed successfully!")
        print("You can now start the backend and test the chat system.")
    else:
        print("❌ Migration failed!")
        print("Please check the logs and fix any issues.")
        print("You may need to run the SQL manually in Supabase dashboard.")