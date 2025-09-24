"""
SQLAlchemy-based LangExtract Session Persistence Service
Verwendet dieselbe PostgreSQL-Verbindung wie ChatService für guaranteed Reliability
"""

import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy import text, insert, update, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import AsyncSessionLocal
from models.langextract_models import StreamworksSession, SessionState

logger = logging.getLogger(__name__)


class SQLAlchemySessionPersistenceService:
    """
    SQLAlchemy-basierter Session Persistence Service
    Verwendet direkte PostgreSQL-Verbindung wie ChatService
    """

    def __init__(self):
        self.enabled = True
        logger.info("✅ SQLAlchemy LangExtract Session Persistence Service initialized")

    async def save_session(self, session: StreamworksSession, retry_count: int = 3) -> bool:
        """
        Save session to PostgreSQL using SQLAlchemy
        """
        for attempt in range(retry_count):
            try:
                logger.info(f"🔄 SQLAlchemy save attempt {attempt + 1}/{retry_count} for session: {session.session_id}")

                async with AsyncSessionLocal() as db:
                    logger.info(f"🔗 Database connection established for session: {session.session_id}")

                    # Prepare session data with proper JSON serialization for JSONB fields
                    session_data = {
                        "session_id": session.session_id,
                        "job_type": session.job_type,
                        "stream_parameters": json.dumps(session.stream_parameters or {}),
                        "job_parameters": json.dumps(session.job_parameters or {}),
                        "critical_missing": session.critical_missing or [],
                        "messages": json.dumps([
                            {
                                "type": msg.type,
                                "content": msg.content,
                                "timestamp": msg.timestamp.isoformat() if hasattr(msg.timestamp, 'isoformat') else str(msg.timestamp)
                            } for msg in getattr(session, 'messages', [])
                        ] if hasattr(session, 'messages') and session.messages else []),
                        "session_state": session.state.value if hasattr(session.state, 'value') else str(session.state),
                        "created_at": session.created_at,
                        "last_activity": session.last_activity,
                        "updated_at": datetime.utcnow()
                    }

                    logger.info(f"📊 Session data prepared for: {session.session_id} - {len(str(session_data))} chars")

                    # Use raw SQL for UPSERT since it's more reliable
                    upsert_sql = text("""
                        INSERT INTO langextract_sessions (
                            session_id, job_type, stream_parameters, job_parameters,
                            critical_missing, messages, session_state, created_at, last_activity, updated_at
                        ) VALUES (
                            :session_id, :job_type, :stream_parameters, :job_parameters,
                            :critical_missing, :messages, :session_state, :created_at, :last_activity, :updated_at
                        )
                        ON CONFLICT (session_id) DO UPDATE SET
                            job_type = EXCLUDED.job_type,
                            stream_parameters = EXCLUDED.stream_parameters,
                            job_parameters = EXCLUDED.job_parameters,
                            critical_missing = EXCLUDED.critical_missing,
                            messages = EXCLUDED.messages,
                            session_state = EXCLUDED.session_state,
                            last_activity = EXCLUDED.last_activity,
                            updated_at = EXCLUDED.updated_at
                    """)

                    logger.info(f"📝 Executing SQL UPSERT for session: {session.session_id}")
                    result = await db.execute(upsert_sql, session_data)

                    logger.info(f"📝 SQL executed, committing transaction for session: {session.session_id}")
                    await db.commit()

                    logger.info(f"✅ Transaction committed successfully for session: {session.session_id}")
                    logger.info(f"💾 Session saved via SQLAlchemy: {session.session_id} (completion: {session.completion_percentage}%)")
                    return True

            except Exception as e:
                error_type = type(e).__name__
                error_msg = str(e)
                logger.error(f"❌ SQLAlchemy save FAILED (attempt {attempt + 1}/{retry_count}): {error_type}: {error_msg}")
                logger.error(f"❌ Session ID: {session.session_id}")

                # Log specific database errors
                if "connection" in error_msg.lower():
                    logger.error(f"🔌 DATABASE CONNECTION ERROR for session {session.session_id}")
                elif "table" in error_msg.lower() or "relation" in error_msg.lower():
                    logger.error(f"📋 TABLE/RELATION ERROR for session {session.session_id}")
                elif "permission" in error_msg.lower() or "authentication" in error_msg.lower():
                    logger.error(f"🔐 PERMISSION/AUTH ERROR for session {session.session_id}")
                else:
                    logger.error(f"❓ UNKNOWN ERROR TYPE for session {session.session_id}")

                # Log full traceback for debugging
                import traceback
                logger.error(f"❌ Full traceback for session {session.session_id}: {traceback.format_exc()}")

                if attempt < retry_count - 1:
                    sleep_time = 1 * (attempt + 1)
                    logger.info(f"⏳ Retrying in {sleep_time} seconds for session: {session.session_id}")
                    import asyncio
                    await asyncio.sleep(sleep_time)  # Exponential backoff
                else:
                    logger.error(f"❌ All {retry_count} attempts FAILED for session: {session.session_id}")
                    return False

        return False

    async def load_session(self, session_id: str, retry_count: int = 3) -> Optional[StreamworksSession]:
        """
        Load session from PostgreSQL using SQLAlchemy
        """
        for attempt in range(retry_count):
            try:
                async with AsyncSessionLocal() as db:
                    # Get session from database
                    select_sql = text("""
                        SELECT * FROM langextract_sessions
                        WHERE session_id = :session_id
                    """)

                    result = await db.execute(select_sql, {"session_id": session_id})
                    session_data = result.fetchone()

                    if session_data:
                        logger.info(f"📥 Session loaded via SQLAlchemy: {session_id}")

                        # Convert row to dict
                        session_dict = dict(session_data._mapping)

                        # Convert back to StreamworksSession with JSON deserialization
                        session = StreamworksSession(
                            session_id=session_dict["session_id"],
                            job_type=session_dict.get("job_type"),
                            stream_parameters=json.loads(session_dict.get("stream_parameters", "{}")) if isinstance(session_dict.get("stream_parameters"), str) else session_dict.get("stream_parameters", {}),
                            job_parameters=json.loads(session_dict.get("job_parameters", "{}")) if isinstance(session_dict.get("job_parameters"), str) else session_dict.get("job_parameters", {}),
                            critical_missing=session_dict.get("critical_missing", []),
                            state=SessionState(session_dict.get("session_state", "STREAM_CONFIGURATION")),
                            created_at=session_dict["created_at"],
                            last_activity=session_dict["last_activity"]
                        )

                        # Restore messages if available
                        if session_dict.get("messages"):
                            from models.langextract_models import ChatMessage
                            messages_data = json.loads(session_dict["messages"]) if isinstance(session_dict["messages"], str) else session_dict["messages"]
                            session.messages = [
                                ChatMessage(
                                    type=msg.get("type", "assistant"),
                                    content=msg.get("content", ""),
                                    timestamp=datetime.fromisoformat(msg["timestamp"]) if msg.get("timestamp") else datetime.now()
                                ) for msg in messages_data
                            ]

                        return session
                    else:
                        logger.debug(f"Session not found via SQLAlchemy: {session_id}")
                        return None

            except Exception as e:
                logger.error(f"❌ Failed to load session via SQLAlchemy (attempt {attempt + 1}/{retry_count}): {str(e)}")
                if attempt < retry_count - 1:
                    import asyncio
                    await asyncio.sleep(1 * (attempt + 1))
                else:
                    return None

        return None

    async def delete_session(self, session_id: str, retry_count: int = 3) -> bool:
        """
        Delete session from PostgreSQL using SQLAlchemy
        """
        for attempt in range(retry_count):
            try:
                async with AsyncSessionLocal() as db:
                    delete_sql = text("""
                        DELETE FROM langextract_sessions
                        WHERE session_id = :session_id
                    """)

                    await db.execute(delete_sql, {"session_id": session_id})
                    await db.commit()

                    logger.info(f"🗑️ Session deleted via SQLAlchemy: {session_id}")
                    return True

            except Exception as e:
                logger.error(f"❌ Failed to delete session via SQLAlchemy (attempt {attempt + 1}/{retry_count}): {str(e)}")
                if attempt < retry_count - 1:
                    import asyncio
                    await asyncio.sleep(1 * (attempt + 1))
                else:
                    return False

        return False

    async def list_user_sessions(self, limit: int = 50, retry_count: int = 3) -> List[Dict[str, Any]]:
        """
        List recent sessions from PostgreSQL using SQLAlchemy
        """
        for attempt in range(retry_count):
            try:
                async with AsyncSessionLocal() as db:
                    list_sql = text("""
                        SELECT session_id, job_type, created_at, last_activity, stream_parameters
                        FROM langextract_sessions
                        ORDER BY last_activity DESC
                        LIMIT :limit
                    """)

                    result = await db.execute(list_sql, {"limit": limit})
                    sessions_data = result.fetchall()

                    if sessions_data:
                        sessions = []
                        for session_data in sessions_data:
                            session_dict = dict(session_data._mapping)

                            # Extract StreamName for display - handle JSON string or dict
                            stream_params = session_dict.get("stream_parameters", {})
                            if isinstance(stream_params, str):
                                try:
                                    stream_params = json.loads(stream_params)
                                except (json.JSONDecodeError, TypeError):
                                    stream_params = {}
                            stream_name = stream_params.get("StreamName", "Unnamed Stream")

                            sessions.append({
                                "session_id": session_dict["session_id"],
                                "stream_name": stream_name,
                                "job_type": session_dict.get("job_type"),
                                "created_at": session_dict["created_at"].isoformat() if session_dict.get("created_at") else "",
                                "last_activity": session_dict["last_activity"].isoformat() if session_dict.get("last_activity") else ""
                            })

                        logger.info(f"📋 Listed {len(sessions)} sessions via SQLAlchemy")
                        return sessions
                    else:
                        return []

            except Exception as e:
                logger.error(f"❌ Failed to list sessions via SQLAlchemy (attempt {attempt + 1}/{retry_count}): {str(e)}")
                if attempt < retry_count - 1:
                    import asyncio
                    await asyncio.sleep(1 * (attempt + 1))
                else:
                    return []

        return []

    def is_enabled(self) -> bool:
        """Check if session persistence is enabled (always True for SQLAlchemy)"""
        return self.enabled


# Global service instance
_sqlalchemy_session_persistence_service = None


def get_sqlalchemy_session_persistence_service() -> SQLAlchemySessionPersistenceService:
    """Get or create SQLAlchemy session persistence service instance"""
    global _sqlalchemy_session_persistence_service

    if _sqlalchemy_session_persistence_service is None:
        _sqlalchemy_session_persistence_service = SQLAlchemySessionPersistenceService()

    return _sqlalchemy_session_persistence_service