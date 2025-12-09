import os
import json
from typing import Optional, Dict, List, Any
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class DatabaseService:
    _instance = None
    client: Optional[Client] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseService, cls).__new__(cls)
            cls._instance._init_client()
        return cls._instance

    def _init_client(self):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        if url and key:
            try:
                self.client = create_client(url, key)
            except Exception as e:
                print(f"Error connecting to Supabase: {e}")
        else:
             print("Warning: SUPABASE_URL or SUPABASE_KEY not found in environment.")

    def get_client(self) -> Optional[Client]:
        return self.client

    def save_session(self, session_id: str, data: dict):
        """Save or update a wizard session."""
        if not self.client: return None
        try:
            # Upsert session data
            data_copy = json.loads(json.dumps(data, default=str)) # Ensure JSON serializable
            return self.client.table("sessions").upsert({
                "id": session_id,
                "data": data_copy,
                "updated_at": "now()"
            }).execute()
        except Exception as e:
            print(f"Error saving session {session_id}: {e}")
            return None

    def get_session(self, session_id: str) -> Optional[dict]:
        """Retrieve a wizard session."""
        if not self.client: return None
        try:
            response = self.client.table("sessions").select("data").eq("id", session_id).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]["data"]
            return None
        except Exception as e:
            print(f"Error getting session {session_id}: {e}")
            return None

    def save_stream(self, filename: str, content: str, metadata: dict = None, job_type: str = "STANDARD"):
        """Save a generated stream."""
        if not self.client: return None
        
        dataset = {
            "filename": filename,
            "content": content,
            "metadata": metadata or {},
        }
        
        # Check if schema supports job_type directly or inside metadata
        # Based on migration, we have metadata jsonb. job_type can go there.
        if metadata is None:
            metadata = {}
        metadata["job_type"] = job_type
        dataset["metadata"] = metadata

        try:
            return self.client.table("streams").insert(dataset).execute()
        except Exception as e:
            print(f"Error saving stream {filename}: {e}")
            raise e

    def get_dropdown_options(self, category: str):
        """Fetch dropdown options for a specific category."""
        if not self.client: return []
        try:
            response = self.client.table("dropdown_options")\
                .select("label, value")\
                .eq("category", category)\
                .eq("is_active", True)\
                .execute()
            return response.data
        except Exception as e:
            print(f"Error fetching dropdown options for {category}: {e}")
            return []

    def get_user_streams(self, user_id: str = None, limit: int = 50):
        """Get recent streams (optionally filtered by user)"""
        if not self.client: return []
        try:
            query = self.client.table("streams")\
                .select("id, filename, created_at, metadata")\
                .order("created_at", desc=True)\
                .limit(limit)
                
            # If user_id provided (future)
            if user_id:
                query = query.eq("user_id", user_id)
                
            response = query.execute()
            return response.data
        except Exception as e:
            print(f"Error fetching streams: {e}")
            return []

    def get_stream(self, stream_id: str):
        """Get full stream details including content"""
        if not self.client: return None
        try:
            response = self.client.table("streams")\
                .select("*")\
                .eq("id", stream_id)\
                .execute()
                
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error fetching stream {stream_id}: {e}")
            return None

    def list_sessions(self, limit: int = 50):
        """List all sessions with their status and params for dashboard"""
        if not self.client: return []
        try:
            response = self.client.table("sessions")\
                .select("id, data, created_at, updated_at")\
                .order("updated_at", desc=True)\
                .limit(limit)\
                .execute()
            
            # Transform data for frontend
            sessions = []
            for row in response.data or []:
                data = row.get("data", {})
                params = data.get("params", {})
                sessions.append({
                    "id": row["id"],
                    "name": params.get("stream_name") or "Entwurf",
                    "status": data.get("status", "draft"),
                    "job_type": data.get("detected_job_type") or params.get("job_type", "STANDARD"),
                    "current_step": data.get("current_step", "basic_info"),
                    "completion_percent": data.get("completion_percent", 0),
                    "created_at": row.get("created_at"),
                    "updated_at": row.get("updated_at"),
                    "params": params
                })
            return sessions
        except Exception as e:
            print(f"Error listing sessions: {e}")
            return []

    def update_session_status(self, session_id: str, status: str):
        """Update session status (draft/complete)"""
        if not self.client: return None
        try:
            # Get existing session
            session = self.get_session(session_id)
            if session:
                session["status"] = status
                return self.save_session(session_id, session)
            return None
        except Exception as e:
            print(f"Error updating session status: {e}")
            return None

    def delete_session(self, session_id: str):
        """Delete a session"""
        if not self.client: return False
        try:
            self.client.table("sessions").delete().eq("id", session_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting session {session_id}: {e}")
            return False


# Global instance
db = DatabaseService()

# Backward compatibility
def get_supabase() -> Optional[Client]:
    return db.get_client()
