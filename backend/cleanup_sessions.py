"""
Cleanup Script for Empty/Draft Sessions

Run this script to delete empty sessions that were created before the lazy-creation fix.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from supabase import create_client

def cleanup_empty_sessions():
    """Delete sessions with no meaningful data (empty params)"""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ SUPABASE_URL or SUPABASE_KEY not found")
        return False
    
    client = create_client(url, key)
    
    # Get all sessions
    response = client.table("sessions").select("id, data").execute()
    sessions = response.data or []
    
    deleted_count = 0
    kept_count = 0
    
    for session in sessions:
        session_id = session["id"]
        data = session.get("data", {})
        params = data.get("params", {})
        
        # Check if session has any meaningful data
        has_name = bool(params.get("stream_name"))
        has_description = bool(params.get("short_description"))
        has_contact = bool(params.get("contact_first_name") or params.get("contact_last_name"))
        
        if not (has_name or has_description or has_contact):
            # Delete empty session
            try:
                client.table("sessions").delete().eq("id", session_id).execute()
                print(f"🗑️  Deleted empty session: {session_id[:8]}...")
                deleted_count += 1
            except Exception as e:
                print(f"❌ Error deleting {session_id}: {e}")
        else:
            kept_count += 1
            print(f"✓  Kept session: {session_id[:8]}... (name: {params.get('stream_name', '-')})")
    
    print(f"\n📊 Summary: Deleted {deleted_count} empty sessions, kept {kept_count} sessions")
    return True


if __name__ == "__main__":
    print("🧹 Starting session cleanup...\n")
    cleanup_empty_sessions()
    print("\n✅ Cleanup complete!")
