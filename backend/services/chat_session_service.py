"""
Chat Session Service - Persistence for RAG Chat Sessions
Enterprise-ready service for managing chat sessions in Supabase
"""

import json
from typing import Optional, Dict, List
from services.db import get_supabase


class ChatSessionService:
    """Service for managing chat sessions in Supabase"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChatSessionService, cls).__new__(cls)
        return cls._instance

    def _get_db(self):
        """Get Supabase client"""
        return get_supabase()

    # ===================
    # Session Operations
    # ===================

    def create_session(
        self, title: str = "Neuer Chat", user_id: str = None
    ) -> Optional[Dict]:
        """Create a new chat session"""
        db = self._get_db()
        if not db:
            return None

        try:
            data = {"title": title}
            if user_id:
                data["user_id"] = user_id

            response = db.table("chat_sessions").insert(data).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error creating chat session: {e}")
            return None

    def list_sessions(self, limit: int = 50, user_id: str = None) -> List[Dict]:
        """List chat sessions ordered by most recent"""
        db = self._get_db()
        if not db:
            return []

        try:
            query = (
                db.table("chat_sessions")
                .select("id, title, created_at, updated_at, metadata")
                .order("updated_at", desc=True)
                .limit(limit)
            )

            if user_id:
                query = query.eq("user_id", user_id)

            response = query.execute()

            # Add message count for each session
            sessions = []
            for session in response.data or []:
                # Get message count
                count_resp = (
                    db.table("chat_messages")
                    .select("id", count="exact")
                    .eq("session_id", session["id"])
                    .execute()
                )
                session["message_count"] = count_resp.count if count_resp.count else 0
                sessions.append(session)

            return sessions
        except Exception as e:
            print(f"Error listing chat sessions: {e}")
            return []

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get a chat session with all its messages"""
        db = self._get_db()
        if not db:
            return None

        try:
            # Get session
            session_resp = (
                db.table("chat_sessions").select("*").eq("id", session_id).execute()
            )

            if not session_resp.data:
                return None

            session = session_resp.data[0]

            # Get messages
            messages_resp = (
                db.table("chat_messages")
                .select("id, role, content, sources, created_at")
                .eq("session_id", session_id)
                .order("created_at", desc=False)
                .execute()
            )

            session["messages"] = messages_resp.data or []
            return session

        except Exception as e:
            print(f"Error getting chat session {session_id}: {e}")
            return None

    def update_session(self, session_id: str, updates: Dict) -> Optional[Dict]:
        """Update session title or metadata"""
        db = self._get_db()
        if not db:
            return None

        try:
            # Only allow updating certain fields
            allowed = {"title", "metadata"}
            filtered_updates = {k: v for k, v in updates.items() if k in allowed}

            if not filtered_updates:
                return None

            response = (
                db.table("chat_sessions")
                .update(filtered_updates)
                .eq("id", session_id)
                .execute()
            )

            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error updating chat session {session_id}: {e}")
            return None

    def delete_session(self, session_id: str) -> bool:
        """Delete a chat session (messages cascade delete)"""
        db = self._get_db()
        if not db:
            return False

        try:
            db.table("chat_sessions").delete().eq("id", session_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting chat session {session_id}: {e}")
            return False

    def delete_all_sessions(self, user_id: str = None) -> bool:
        """Delete all chat sessions (messages cascade delete)"""
        db = self._get_db()
        if not db:
            return False

        try:
            query = db.table("chat_sessions").delete()

            # If user_id provided, only delete their sessions
            # If not provided, delete ALL sessions (careful!)
            # For now, we assume single-user mode or handled by RLS if user_id is None
            if user_id:
                query = query.eq("user_id", user_id)
            else:
                # To delete all rows without a where clause, we might need a condition that is always true
                # or just not chain .eq() if the library allows it.
                # Supabase-py often requires a filter for delete unless explicitly allowed?
                # Usually .neq("id", "00000000-0000-0000-0000-000000000000") is a safe trick if needed.
                # But let's try direct delete first.
                pass

            # Ideally we want to prevent accidental full wipe if not intended.
            # But the requirement is "delete all sessions".
            # Safe safeguard: delete where id is not null
            query.neq("id", "00000000-0000-0000-0000-000000000000").execute()
            return True
        except Exception as e:
            print(f"Error deleting all chat sessions: {e}")
            return False

    # ===================
    # Message Operations
    # ===================

    def add_message(
        self, session_id: str, role: str, content: str, sources: List[Dict] = None
    ) -> Optional[Dict]:
        """Add a message to a chat session"""
        db = self._get_db()
        if not db:
            return None

        try:
            data = {
                "session_id": session_id,
                "role": role,
                "content": content,
                "sources": sources or [],
            }

            # Ensure sources is JSON serializable
            data["sources"] = json.loads(json.dumps(data["sources"], default=str))

            response = db.table("chat_messages").insert(data).execute()

            # Also update session's updated_at
            db.table("chat_sessions").update({"updated_at": "now()"}).eq(
                "id", session_id
            ).execute()

            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error adding message to session {session_id}: {e}")
            return None

    def get_messages(
        self, session_id: str, limit: int = 100, offset: int = 0
    ) -> List[Dict]:
        """Get messages for a session with pagination"""
        db = self._get_db()
        if not db:
            return []

        try:
            response = (
                db.table("chat_messages")
                .select("id, role, content, sources, created_at")
                .eq("session_id", session_id)
                .order("created_at", desc=False)
                .range(offset, offset + limit - 1)
                .execute()
            )

            return response.data or []
        except Exception as e:
            print(f"Error getting messages for session {session_id}: {e}")
            return []

    def generate_session_title(self, first_message: str) -> str:
        """Generate an intelligent title using AI"""
        try:
            from openai import OpenAI
            from config import config

            if not config.OPENAI_API_KEY:
                # Fallback to simple truncation
                return self._simple_title(first_message)

            client = OpenAI(api_key=config.OPENAI_API_KEY)

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Du bist ein Titel-Generator. Erstelle einen kurzen, prägnanten deutschen Titel (max. 5 Wörter) für eine Chat-Konversation basierend auf der ersten Nachricht. Nur den Titel ausgeben, keine Anführungszeichen.",
                    },
                    {"role": "user", "content": first_message},
                ],
                max_tokens=20,
                temperature=0.7,
            )

            title = response.choices[0].message.content.strip()
            # Remove any quotes that might be in the response
            title = title.strip("\"'")
            return title if title else self._simple_title(first_message)

        except Exception as e:
            print(f"AI title generation failed: {e}")
            return self._simple_title(first_message)

    def _simple_title(self, message: str) -> str:
        """Fallback: Generate simple title from message"""
        title = message[:40].strip()
        if len(message) > 40:
            # Try to cut at word boundary
            if " " in title:
                title = title.rsplit(" ", 1)[0]
            title += "..."
        return title or "Neuer Chat"


# Global singleton instance
chat_session_service = ChatSessionService()
