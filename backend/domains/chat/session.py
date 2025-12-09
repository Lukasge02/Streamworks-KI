"""
Session Manager - Verwaltet Chat-Sessions in Supabase (mit Memory-Fallback)
"""
from typing import Dict, Any, Optional
import uuid
import json
from services.db import get_supabase


class SessionManager:
    """Manages chat sessions in Supabase"""
    
    def __init__(self):
        self._memory_fallback: Dict[str, Dict[str, Any]] = {}
    
    def _get_db(self):
        return get_supabase()
    
    def create_session(self) -> str:
        """Create a new session and return its ID"""
        session_id = str(uuid.uuid4())
        initial_data = {
            "params": {},
            "job_type": None,
            "messages": [],
            "extraction_complete": False
        }
        
        db = self._get_db()
        if db:
            try:
                db.table("sessions").insert({"id": session_id, "data": initial_data}).execute()
                return session_id
            except Exception as e:
                print(f"Supabase create error: {e}, using fallback")
        
        self._memory_fallback[session_id] = initial_data
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID"""
        db = self._get_db()
        if db:
            try:
                response = db.table("sessions").select("data").eq("id", session_id).execute()
                if response.data:
                    return response.data[0]["data"]
            except Exception as e:
                print(f"Supabase get error: {e}")
        
        return self._memory_fallback.get(session_id)
    
    def get_or_create(self, session_id: Optional[str]) -> tuple[str, Dict[str, Any]]:
        """Get existing session or create new one"""
        if session_id:
            data = self.get_session(session_id)
            if data:
                return session_id, data
        
        new_id = self.create_session()
        return new_id, self.get_session(new_id)
    
    def update_session(self, session_id: str, updates: Dict[str, Any]) -> None:
        """Update session data"""
        db = self._get_db()
        
        # Merge logic needed because we only have partial updates usually
        # But for Supabase JSONB, we typically update the whole object or need to fetch-merge-update
        # Optimization: Fetch first
        current = self.get_session(session_id)
        if not current:
            return
            
        current.update(updates)
        
        if db:
            try:
                db.table("sessions").update({"data": current}).eq("id", session_id).execute()
                return
            except Exception as e:
                print(f"Supabase update error: {e}")
        
        self._memory_fallback[session_id] = current
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        db = self._get_db()
        if db:
            try:
                db.table("sessions").delete().eq("id", session_id).execute()
                return True
            except Exception as e:
                print(f"Supabase delete error: {e}")
        
        if session_id in self._memory_fallback:
            del self._memory_fallback[session_id]
            return True
        return False
    
    def exists(self, session_id: str) -> bool:
        """Check if session exists"""
        return self.get_session(session_id) is not None


# Global session manager instance
session_manager = SessionManager()
