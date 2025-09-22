"""
LangExtract Session Persistence Service
Handles saving and loading LangExtract sessions to/from Supabase
Ensures parameter extraction data persists across browser sessions
"""

import logging
import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from models.langextract_models import StreamWorksSession, SessionState

logger = logging.getLogger(__name__)


class LangExtractSessionPersistenceService:
    """
    Service for persisting LangExtract sessions to Supabase
    Provides session continuity and parameter recovery capabilities
    """

    def __init__(self):
        self.enabled = False
        self.supabase_client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Supabase client if credentials are available"""
        try:
            from supabase import create_client
            import os

            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_SERVICE_KEY")

            if supabase_url and supabase_key:
                self.supabase_client = create_client(supabase_url, supabase_key)
                self.enabled = True
                logger.info("✅ LangExtract session persistence service initialized successfully")
            else:
                logger.info("🔒 Supabase credentials not found - session persistence disabled")

        except ImportError:
            logger.info("📦 Supabase client not installed - session persistence disabled")
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize Supabase client for session persistence: {str(e)}")

    async def save_session(self, session: StreamWorksSession, retry_count: int = 3) -> bool:
        """
        Save session to Supabase with automatic retry

        Args:
            session: StreamWorksSession to save
            retry_count: Number of retry attempts

        Returns:
            Success status
        """
        if not self.enabled:
            logger.debug("Session persistence disabled - skipping save")
            return False

        for attempt in range(retry_count):
            try:
                # Prepare session data for Supabase
                session_data = {
                    "session_id": session.session_id,
                    "job_type": session.job_type,
                    "stream_parameters": session.stream_parameters,
                    "job_parameters": session.job_parameters,
                    "completion_percentage": session.completion_percentage,
                    "critical_missing": session.critical_missing or [],
                    "messages": [
                        {
                            "type": msg.type,
                            "content": msg.content,
                            "timestamp": msg.timestamp.isoformat() if hasattr(msg.timestamp, 'isoformat') else str(msg.timestamp)
                        } for msg in session.messages
                    ] if session.messages else [],
                    "session_state": session.state.value if hasattr(session.state, 'value') else str(session.state),
                    "created_at": session.created_at.isoformat() if hasattr(session.created_at, 'isoformat') else str(session.created_at),
                    "last_activity": session.last_activity.isoformat() if hasattr(session.last_activity, 'isoformat') else str(session.last_activity),
                    "updated_at": datetime.utcnow().isoformat()
                }

                # Insert/update session in Supabase
                logger.info(f"🔄 Attempting to save session {session.session_id} to Supabase (attempt {attempt + 1})")
                logger.debug(f"Session data: {session_data}")

                result = self.supabase_client.table("langextract_sessions").upsert(session_data).execute()

                logger.info(f"📊 Supabase result: data={result.data}, count={getattr(result, 'count', 'unknown')}")

                if result.data:
                    logger.info(f"💾 Session saved to Supabase: {session.session_id} (completion: {session.completion_percentage}%)")
                    return True
                else:
                    logger.warning(f"⚠️ No data returned from Supabase session save (attempt {attempt + 1}): {session.session_id}")
                    logger.warning(f"Full result object: {result}")

            except Exception as e:
                logger.error(f"❌ Failed to save session to Supabase (attempt {attempt + 1}/{retry_count}): {str(e)}")
                if attempt < retry_count - 1:
                    await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
                else:
                    return False

        return False

    async def load_session(self, session_id: str, retry_count: int = 3) -> Optional[StreamWorksSession]:
        """
        Load session from Supabase with automatic retry

        Args:
            session_id: Session ID to load
            retry_count: Number of retry attempts

        Returns:
            StreamWorksSession or None if not found
        """
        if not self.enabled:
            logger.debug("Session persistence disabled - skipping load")
            return None

        for attempt in range(retry_count):
            try:
                # Get session from Supabase
                result = self.supabase_client.table("langextract_sessions").select("*").eq("session_id", session_id).execute()

                if result.data and len(result.data) > 0:
                    session_data = result.data[0]
                    logger.info(f"📥 Session loaded from Supabase: {session_id}")

                    # Convert back to StreamWorksSession
                    session = StreamWorksSession(
                        session_id=session_data["session_id"],
                        job_type=session_data.get("job_type"),
                        stream_parameters=session_data.get("stream_parameters", {}),
                        job_parameters=session_data.get("job_parameters", {}),
                        completion_percentage=session_data.get("completion_percentage", 0),
                        critical_missing=session_data.get("critical_missing", []),
                        state=SessionState(session_data.get("session_state", "STREAM_CONFIGURATION")),
                        created_at=datetime.fromisoformat(session_data["created_at"].replace('Z', '+00:00')),
                        last_activity=datetime.fromisoformat(session_data["last_activity"].replace('Z', '+00:00'))
                    )

                    # Restore messages if available
                    if session_data.get("messages"):
                        from models.langextract_models import ChatMessage
                        session.messages = [
                            ChatMessage(
                                type=msg.get("type", "assistant"),
                                content=msg.get("content", ""),
                                timestamp=datetime.fromisoformat(msg["timestamp"].replace('Z', '+00:00')) if msg.get("timestamp") else datetime.now()
                            ) for msg in session_data["messages"]
                        ]

                    return session
                else:
                    logger.debug(f"Session not found in Supabase: {session_id}")
                    return None

            except Exception as e:
                logger.error(f"❌ Failed to load session from Supabase (attempt {attempt + 1}/{retry_count}): {str(e)}")
                if attempt < retry_count - 1:
                    await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
                else:
                    return None

        return None

    async def delete_session(self, session_id: str, retry_count: int = 3) -> bool:
        """
        Delete session from Supabase with automatic retry

        Args:
            session_id: Session ID to delete
            retry_count: Number of retry attempts

        Returns:
            Success status
        """
        if not self.enabled:
            logger.debug("Session persistence disabled - skipping delete")
            return False

        for attempt in range(retry_count):
            try:
                # Delete session from Supabase
                result = self.supabase_client.table("langextract_sessions").delete().eq("session_id", session_id).execute()

                logger.info(f"🗑️ Session deleted from Supabase: {session_id}")
                return True

            except Exception as e:
                logger.error(f"❌ Failed to delete session from Supabase (attempt {attempt + 1}/{retry_count}): {str(e)}")
                if attempt < retry_count - 1:
                    await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
                else:
                    return False

        return False

    async def list_user_sessions(self, limit: int = 50, retry_count: int = 3) -> List[Dict[str, Any]]:
        """
        List recent sessions from Supabase

        Args:
            limit: Maximum number of sessions to return
            retry_count: Number of retry attempts

        Returns:
            List of session summaries
        """
        if not self.enabled:
            logger.debug("Session persistence disabled - skipping list")
            return []

        for attempt in range(retry_count):
            try:
                # Get recent sessions ordered by last activity
                result = self.supabase_client.table("langextract_sessions")\
                    .select("session_id, job_type, completion_percentage, created_at, last_activity, stream_parameters")\
                    .order("last_activity", desc=True)\
                    .limit(limit).execute()

                if result.data:
                    sessions = []
                    for session_data in result.data:
                        # Extract StreamName for display
                        stream_name = session_data.get("stream_parameters", {}).get("StreamName", "Unnamed Stream")

                        sessions.append({
                            "session_id": session_data["session_id"],
                            "stream_name": stream_name,
                            "job_type": session_data.get("job_type"),
                            "completion_percentage": session_data.get("completion_percentage", 0),
                            "created_at": session_data["created_at"],
                            "last_activity": session_data["last_activity"]
                        })

                    logger.info(f"📋 Listed {len(sessions)} sessions from Supabase")
                    return sessions
                else:
                    return []

            except Exception as e:
                logger.error(f"❌ Failed to list sessions from Supabase (attempt {attempt + 1}/{retry_count}): {str(e)}")
                if attempt < retry_count - 1:
                    await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
                else:
                    return []

        return []

    async def update_session_activity(self, session_id: str, retry_count: int = 3) -> bool:
        """
        Update session last_activity timestamp

        Args:
            session_id: Session ID to update
            retry_count: Number of retry attempts

        Returns:
            Success status
        """
        if not self.enabled:
            return False

        for attempt in range(retry_count):
            try:
                # Update last_activity timestamp
                result = self.supabase_client.table("langextract_sessions")\
                    .update({"last_activity": datetime.utcnow().isoformat()})\
                    .eq("session_id", session_id).execute()

                return True

            except Exception as e:
                logger.error(f"❌ Failed to update session activity (attempt {attempt + 1}/{retry_count}): {str(e)}")
                if attempt < retry_count - 1:
                    await asyncio.sleep(0.5 * (attempt + 1))
                else:
                    return False

        return False

    def is_enabled(self) -> bool:
        """Check if session persistence is enabled"""
        return self.enabled


# Global service instance
_session_persistence_service = None


def get_session_persistence_service() -> LangExtractSessionPersistenceService:
    """Get or create session persistence service instance"""
    global _session_persistence_service

    if _session_persistence_service is None:
        _session_persistence_service = LangExtractSessionPersistenceService()

    return _session_persistence_service


# Convenience functions
async def save_session(session: StreamWorksSession, retry_count: int = 3) -> bool:
    """Convenience function to save session"""
    service = get_session_persistence_service()
    return await service.save_session(session, retry_count)


async def load_session(session_id: str, retry_count: int = 3) -> Optional[StreamWorksSession]:
    """Convenience function to load session"""
    service = get_session_persistence_service()
    return await service.load_session(session_id, retry_count)


async def delete_session(session_id: str, retry_count: int = 3) -> bool:
    """Convenience function to delete session"""
    service = get_session_persistence_service()
    return await service.delete_session(session_id, retry_count)


async def list_user_sessions(limit: int = 50, retry_count: int = 3) -> List[Dict[str, Any]]:
    """Convenience function to list sessions"""
    service = get_session_persistence_service()
    return await service.list_user_sessions(limit, retry_count)