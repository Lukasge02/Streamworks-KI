"""
SQLAlchemy-based Chat Service for Streamworks RAG System
Uses direct PostgreSQL connection like the document system
"""

import uuid
import time
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
from sqlalchemy import text, select, insert, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from database import AsyncSessionLocal
from enum import Enum
from models.core import ChatSession, ChatMessage, MessageRole
from sqlalchemy.orm import selectinload

class RAGMode(Enum):
    """RAG operation modes"""
    FAST = "fast"
    ACCURATE = "accurate"
    COMPREHENSIVE = "comprehensive"
from .di_container import get_service
from .chat_title_generator import chat_title_generator
from services.rag_metrics_service import (
    get_rag_metrics_service,
    SourceReference as MetricsSourceReference,
)

logger = logging.getLogger(__name__)

class ChatServiceSQLAlchemy:
    """SQLAlchemy-based Chat Service - compatible with existing database setup"""

    def __init__(self):
        self.rag_service = None
        self._initialized = False
        self._retry_config = {
            "max_retries": 3,
            "base_delay": 1.0,  # seconds
            "max_delay": 30.0,  # seconds
            "backoff_factor": 2.0
        }
    
    async def _initialize(self):
        """Initialize chat service with timeout protection"""
        if self._initialized:
            return

        try:
            # Initialize Qdrant RAG service from DI container with timeout protection
            import asyncio

            logger.info("Initializing Qdrant RAG Service with 30s timeout...")

            # Use asyncio.wait_for to add timeout protection
            rag_service_task = asyncio.create_task(self._initialize_rag_service())
            self.rag_service = await asyncio.wait_for(rag_service_task, timeout=30.0)

            self._initialized = True
            logger.info("ChatServiceSQLAlchemy initialized successfully with Qdrant RAG Service")

        except asyncio.TimeoutError:
            logger.error("RAG service initialization timed out after 30 seconds")
            self.rag_service = None
            self._initialized = True
            logger.warning("ChatServiceSQLAlchemy initialized without RAG service (timeout)")

        except Exception as e:
            logger.error(f"Failed to initialize ChatServiceSQLAlchemy: {str(e)}")
            # Fallback to no RAG service
            self.rag_service = None
            self._initialized = True
            logger.warning("ChatServiceSQLAlchemy initialized without RAG service")

    async def _initialize_rag_service(self):
        """Helper method to initialize Qdrant RAG service from DI container with proper error handling"""

        rag_service = await get_service("rag_service")

        # Qdrant service is already initialized through DI container
        return rag_service

    async def _execute_with_retry(self, operation, operation_name: str, timeout: float = 30.0):
        """Execute operation with retry logic and exponential backoff"""
        last_exception = None

        for attempt in range(self._retry_config["max_retries"] + 1):
            try:
                # Add timeout protection
                if timeout > 0:
                    return await asyncio.wait_for(operation(), timeout=timeout)
                else:
                    return await operation()

            except asyncio.TimeoutError as e:
                last_exception = e
                logger.warning(f"{operation_name} timeout (attempt {attempt + 1}/{self._retry_config['max_retries'] + 1})")

            except Exception as e:
                last_exception = e
                logger.warning(f"{operation_name} failed (attempt {attempt + 1}/{self._retry_config['max_retries'] + 1}): {str(e)}")

            # Calculate delay with exponential backoff
            if attempt < self._retry_config["max_retries"]:
                delay = min(
                    self._retry_config["base_delay"] * (self._retry_config["backoff_factor"] ** attempt),
                    self._retry_config["max_delay"]
                )
                logger.info(f"Retrying {operation_name} in {delay:.1f}s...")
                await asyncio.sleep(delay)

        # All retries failed
        raise last_exception or Exception(f"{operation_name} failed after all retries")

    async def _execute_db_operation_with_retry(self, operation, operation_name: str):
        """Execute database operation with retry logic"""
        return await self._execute_with_retry(operation, operation_name, timeout=15.0)

    async def _execute_rag_operation_with_retry(self, operation, operation_name: str):
        """Execute RAG operation with retry logic and longer timeout"""
        return await self._execute_with_retry(operation, operation_name, timeout=60.0)

    @staticmethod
    def _handle_background_task_result(task: asyncio.Task, label: str) -> None:
        """Log unexpected exceptions from background tasks."""
        if task.cancelled():
            logger.debug(f"Background task {label} was cancelled")
            return

        exception = task.exception()
        if exception:
            logger.warning(f"Background task {label} failed: {exception}")

    def _schedule_title_generation(self, *, session_id: str, user_message: str) -> None:
        """Trigger chat title generation without blocking the main request."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            logger.debug("No running event loop available for title generation task")
            return

        async def _generate_and_store_title() -> None:
            try:
                title = await chat_title_generator.generate_title_from_user_message(user_message)
                if not title or title.strip() == "" or title == "Neue Unterhaltung":
                    return

                async with AsyncSessionLocal() as session:
                    result = await session.execute(
                        text("""
                            UPDATE chat_sessions
                            SET title = :title, updated_at = now()
                            WHERE id = :session_id AND title = 'Neue Unterhaltung'
                        """),
                        {"session_id": session_id, "title": title}
                    )

                    await session.commit()

                    if result.rowcount:
                        logger.info(f"Auto-generated title '{title}' for session {session_id}")
                    else:
                        logger.debug(
                            "Skipped title update for session %s because it already changed",
                            session_id,
                        )
            except Exception as exc:
                logger.warning(f"Failed to auto-generate title for session {session_id}: {exc}")

        task = loop.create_task(
            _generate_and_store_title(),
            name=f"generate_chat_title:{session_id}"
        )
        task.add_done_callback(
            lambda completed: self._handle_background_task_result(
                completed, f"title_generation:{session_id}"
            )
        )

    async def _record_rag_metrics(
        self,
        *,
        query: str,
        processing_mode: str,
        session_id: str,
        sources_payload,
        response_time_ms: int,
        cache_hit: bool = False,
        error: Optional[str] = None,
    ) -> None:
        """Normalize RAG response metadata and forward it to the metrics service."""
        try:
            metrics_service = await get_rag_metrics_service()

            source_refs: List[MetricsSourceReference] = []
            for source in sources_payload or []:
                parsed_ref = self._convert_to_metrics_source(source)
                if parsed_ref:
                    source_refs.append(parsed_ref)

            await metrics_service.track_rag_query(
                query=query,
                sources=source_refs,
                response_time_ms=max(response_time_ms, 0),
                cache_hit=cache_hit,
                mode=processing_mode,
                session_id=session_id,
                error=error,
            )

        except Exception as metrics_error:
            logger.warning(f"Failed to track RAG metrics: {metrics_error}")

    # ================================
    # METRICS NORMALIZATION HELPERS
    # ================================

    @staticmethod
    def _safe_float(value: Any) -> Optional[float]:
        try:
            if value is None:
                return None
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _safe_int(value: Any) -> Optional[int]:
        try:
            if value is None:
                return None
            return int(value)
        except (TypeError, ValueError):
            return None

    def _convert_to_metrics_source(self, source: Any) -> Optional[MetricsSourceReference]:
        """Convert various RAG source payloads into a metrics reference."""
        if isinstance(source, MetricsSourceReference):
            return source

        if not isinstance(source, dict):
            return None

        metadata = source.get("metadata")
        if not isinstance(metadata, dict):
            metadata = {}

        def first_value(*candidates: Any) -> Optional[Any]:
            for candidate in candidates:
                if candidate is None:
                    continue
                if isinstance(candidate, str) and not candidate.strip():
                    continue
                return candidate
            return None

        doc_id = first_value(
            source.get("document_id"),
            source.get("doc_id"),
            metadata.get("document_id"),
            metadata.get("doc_id"),
            metadata.get("source_id"),
            metadata.get("id"),
        )
        document_id = str(doc_id) if doc_id is not None else "unknown"

        filename = first_value(
            source.get("filename"),
            metadata.get("filename"),
            metadata.get("original_filename"),
            metadata.get("document_name"),
            metadata.get("title"),
        ) or "Unknown Document"

        page_number = self._safe_int(
            first_value(
                source.get("page_number"),
                source.get("page"),
                metadata.get("page_number"),
                metadata.get("page"),
                metadata.get("page_num"),
            )
        )

        chunk_index = self._safe_int(
            first_value(
                source.get("chunk_index"),
                source.get("index"),
                metadata.get("chunk_index"),
                metadata.get("chunk"),
            )
        )
        if chunk_index is None:
            chunk_index = 0

        chunk_id = first_value(
            source.get("chunk_id"),
            metadata.get("chunk_id"),
            metadata.get("id"),
        )

        section = first_value(
            source.get("section"),
            source.get("heading"),
            metadata.get("section"),
            metadata.get("heading"),
            metadata.get("title"),
        )

        snippet = first_value(
            source.get("snippet"),
            metadata.get("snippet"),
            metadata.get("text_preview"),
            metadata.get("content_preview"),
        )
        if snippet is None:
            snippet = source.get("content") or metadata.get("text") or ""
        snippet = str(snippet)
        if len(snippet) > 200:
            snippet = snippet[:200]

        relevance = self._safe_float(
            first_value(
                source.get("relevance_score"),
                metadata.get("relevance_score"),
                metadata.get("quality_score"),
                source.get("score"),
                metadata.get("score"),
            )
        )
        if relevance is None:
            relevance = 0.0
        else:
            if relevance < 0:
                relevance = 0.0
            if relevance > 1.0:
                relevance = min(relevance, 1.0)

        confidence = self._safe_float(
            first_value(
                source.get("confidence"),
                metadata.get("confidence"),
                metadata.get("quality_score"),
            )
        )
        if confidence is None:
            confidence = relevance
        else:
            if confidence < 0:
                confidence = 0.0
            if confidence > 1.0:
                confidence = min(confidence, 1.0)

        doc_type = first_value(
            source.get("doc_type"),
            metadata.get("doc_type"),
            metadata.get("mime_type"),
            metadata.get("document_type"),
        )

        return MetricsSourceReference(
            document_id=document_id,
            filename=str(filename),
            page_number=page_number,
            section=section,
            relevance_score=relevance,
            snippet=snippet,
            chunk_index=chunk_index,
            confidence=confidence,
            doc_type=doc_type,
            chunk_id=chunk_id,
        )

    # ================================
    # SESSION MANAGEMENT
    # ================================
    
    async def create_session(
        self,
        user_id: str,
        title: str,
        rag_config: Optional[Dict[str, Any]] = None,
        context_filters: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new chat session using ORM"""
        await self._initialize()

        async def _create_session_operation():
            async with AsyncSessionLocal() as db_session:
                # Create new session using ORM
                new_session = ChatSession(
                    title=title,
                    user_id=user_id,
                    company_id=uuid.UUID('00000000-0000-0000-0000-000000000001'),
                    message_count=0,
                    rag_config=rag_config or {},
                    context_filters=context_filters or {},
                    is_active=True,
                    is_archived=False
                )

                db_session.add(new_session)
                await db_session.commit()
                await db_session.refresh(new_session)  # Get the generated ID

                session_id = str(new_session.id)
                logger.info(f"Created chat session {session_id} (title: '{title}') for user {user_id}")
                return session_id

        try:
            return await self._execute_db_operation_with_retry(
                _create_session_operation,
                "create_session"
            )
        except Exception as e:
            logger.error(f"Failed to create session after retries: {str(e)}")
            raise Exception(f"Session creation failed: {str(e)}")
    
    async def get_user_sessions(
        self,
        user_id: str,
        active_only: bool = True,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get all chat sessions for a user using ORM"""
        await self._initialize()

        try:
            async with AsyncSessionLocal() as db_session:
                # Build query using ORM
                stmt = select(ChatSession).where(ChatSession.user_id == user_id)

                if active_only:
                    stmt = stmt.where(ChatSession.is_active == True)

                stmt = stmt.order_by(ChatSession.updated_at.desc()).limit(limit)

                result = await db_session.execute(stmt)
                sessions = result.scalars().all()

                # Convert to list of dicts
                session_list = []
                for session in sessions:
                    session_list.append({
                        "id": str(session.id),
                        "title": session.title,
                        "user_id": session.user_id,
                        "company_id": str(session.company_id) if session.company_id else None,
                        "message_count": session.message_count,
                        "rag_config": session.rag_config,
                        "context_filters": session.context_filters,
                        "is_active": session.is_active,
                        "is_archived": session.is_archived,
                        "created_at": session.created_at,
                        "updated_at": session.updated_at,
                        "last_message_at": session.last_message_at
                    })

                logger.info(f"Retrieved {len(session_list)} sessions for user {user_id}")
                return session_list

        except Exception as e:
            logger.error(f"Failed to get user sessions: {str(e)}")
            raise Exception(f"Failed to get sessions: {str(e)}")
    
    async def update_session(
        self,
        session_id: str,
        user_id: str,
        title: Optional[str] = None,
        rag_config: Optional[Dict[str, Any]] = None,
        context_filters: Optional[Dict[str, Any]] = None
    ):
        """Update chat session using ORM"""
        await self._initialize()

        try:
            async with AsyncSessionLocal() as db_session:
                # Find the session to update
                # Convert session_id string to UUID for proper comparison
                try:
                    session_uuid = uuid.UUID(session_id)
                except ValueError:
                    logger.warning(f"Invalid UUID format for session_id: {session_id}")
                    raise Exception("Session not found or access denied")

                stmt = select(ChatSession).where(
                    ChatSession.id == session_uuid,
                    ChatSession.user_id == user_id
                )
                result = await db_session.execute(stmt)
                chat_session = result.scalar_one_or_none()

                if chat_session is None:
                    logger.warning(f"Update attempt failed: Session {session_id} not found for user {user_id}")
                    raise Exception("Session not found or access denied")

                # Update fields if provided
                if title is not None:
                    chat_session.title = title
                if rag_config is not None:
                    chat_session.rag_config = rag_config
                if context_filters is not None:
                    chat_session.context_filters = context_filters

                # updated_at will be automatically updated by the model
                await db_session.commit()

                logger.info(f"Updated session {session_id} for user {user_id}")

        except Exception as e:
            logger.error(f"Failed to update session: {str(e)}")
            if "Session not found or access denied" in str(e):
                raise  # Re-raise specific errors
            raise Exception(f"Session update failed: {str(e)}")
    
    async def delete_session(self, session_id: str, user_id: str):
        """Delete a chat session and all its messages using ORM"""
        await self._initialize()

        try:
            async with AsyncSessionLocal() as db_session:
                # First, find the session to ensure it exists and user has access
                # Convert session_id string to UUID for proper comparison
                try:
                    session_uuid = uuid.UUID(session_id)
                except ValueError:
                    logger.warning(f"Invalid UUID format for session_id: {session_id}")
                    raise Exception("Session not found or access denied")

                stmt = select(ChatSession).where(
                    ChatSession.id == session_uuid,
                    ChatSession.user_id == user_id
                )
                result = await db_session.execute(stmt)
                chat_session = result.scalar_one_or_none()

                if chat_session is None:
                    logger.warning(f"Delete attempt failed: Session {session_id} not found for user {user_id}")
                    raise Exception("Session not found or access denied")

                # Log details for debugging
                logger.info(f"Deleting session {session_id} (title: '{chat_session.title}') for user {user_id}")

                # Delete the session (messages will cascade due to relationship configuration)
                await db_session.delete(chat_session)
                await db_session.commit()

                logger.info(f"Successfully deleted session {session_id} for user {user_id}")

        except Exception as e:
            logger.error(f"Failed to delete session {session_id} for user {user_id}: {str(e)}")
            if "Session not found or access denied" in str(e):
                raise  # Re-raise specific errors
            raise Exception(f"Session deletion failed: {str(e)}")
    
    # ================================
    # MESSAGE MANAGEMENT
    # ================================
    
    async def get_session_messages(
        self,
        session_id: str,
        user_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get all messages for a session"""
        await self._initialize()
        
        try:
            async with AsyncSessionLocal() as session:
                # Verify user has access to this session
                session_check = await session.execute(text("""
                    SELECT id FROM chat_sessions 
                    WHERE id = :session_id AND user_id = :user_id
                """), {"session_id": session_id, "user_id": user_id})
                
                if not session_check.fetchone():
                    raise Exception("Session not found or access denied")
                
                # Get messages
                result = await session.execute(text("""
                    SELECT id, session_id, user_id, role, content,
                           confidence_score, processing_time_ms, sources,
                           model_used, created_at, sequence_number
                    FROM chat_messages
                    WHERE session_id = :session_id
                    ORDER BY sequence_number, created_at
                    LIMIT :limit
                """), {"session_id": session_id, "limit": limit})
                
                rows = result.fetchall()
                
                # Convert to list of dicts
                messages = []
                for row in rows:
                    messages.append({
                        "id": str(row[0]),
                        "session_id": str(row[1]),
                        "user_id": row[2],
                        "role": row[3],
                        "content": row[4],
                        "confidence_score": float(row[5]) if row[5] else None,
                        "processing_time_ms": row[6],
                        "sources": json.loads(row[7]) if isinstance(row[7], str) and row[7] else (row[7] if row[7] else []),
                        "model_used": row[8],
                        "created_at": row[9],
                        "sequence_number": row[10]
                    })
                
                return messages
                
        except Exception as e:
            logger.error(f"Failed to get session messages: {str(e)}")
            raise Exception(f"Failed to get messages: {str(e)}")
    
    async def add_message(
        self,
        session_id: str,
        user_id: str,
        role: str,
        content: str,
        confidence_score: Optional[float] = None,
        processing_time_ms: Optional[int] = None,
        sources: Optional[List[Dict[str, Any]]] = None,
        model_used: Optional[str] = None
    ) -> str:
        """Add a message to a chat session with session validation"""
        await self._initialize()

        try:
            async with AsyncSessionLocal() as session:
                # First validate session exists and user has access
                session_check = await session.execute(text("""
                    SELECT id FROM chat_sessions
                    WHERE id = :session_id AND user_id = :user_id
                """), {"session_id": session_id, "user_id": user_id})

                if not session_check.fetchone():
                    raise Exception(f"Session not found or access denied for session {session_id}")

                message_id = str(uuid.uuid4())

                await session.execute(text("""
                    INSERT INTO chat_messages (
                        id, session_id, user_id, role, content,
                        confidence_score, processing_time_ms, sources, model_used
                    ) VALUES (
                        :id, :session_id, :user_id, :role, :content,
                        :confidence_score, :processing_time_ms, :sources, :model_used
                    )
                """), {
                    "id": message_id,
                    "session_id": session_id,
                    "user_id": user_id,
                    "role": role,
                    "content": content,
                    "confidence_score": confidence_score,
                    "processing_time_ms": processing_time_ms,
                    "sources": json.dumps(sources or []),
                    "model_used": model_used
                })

                await session.commit()
                logger.debug(f"Added {role} message to session {session_id}")

                # Auto-generate title if this is the first user message
                if role == "user":
                    try:
                        # Check if this is the first user message in session
                        result = await session.execute(text("""
                            SELECT title FROM chat_sessions
                            WHERE id = :session_id AND title = 'Neue Unterhaltung'
                        """), {"session_id": session_id})

                        if result.fetchone():
                            # Defer expensive title generation so we don't block the response
                            self._schedule_title_generation(session_id=session_id, user_message=content)
                    except Exception as e:
                        logger.warning(f"Failed to auto-generate title: {str(e)}")

                return message_id

        except Exception as e:
            logger.error(f"Failed to add message: {str(e)}")
            raise Exception(f"Message creation failed: {str(e)}")
    
    # ================================
    # RAG PROCESSING
    # ================================
    
    async def process_message(
        self,
        session_id: str,
        user_id: str,
        query: str,
        processing_mode: str = "accurate",
        include_sources: bool = True
    ) -> Dict[str, Any]:
        """Process user message and generate RAG response with enhanced error handling and retry logic"""
        await self._initialize()

        start_time = time.time()

        try:
            # 1. Add user message to session with retry
            async def _add_user_message():
                return await self.add_message(
                    session_id=session_id,
                    user_id=user_id,
                    role="user",
                    content=query
                )

            user_message_id = await self._execute_db_operation_with_retry(
                _add_user_message,
                "add_user_message"
            )

            # 2. Get session context with retry
            async def _get_session_context():
                return await self.get_session_messages(
                    session_id=session_id,
                    user_id=user_id,
                    limit=10  # Last 10 messages for context
                )

            recent_messages = await self._execute_db_operation_with_retry(
                _get_session_context,
                "get_session_context"
            )

            # 3. Build conversation context
            conversation_context = []
            if len(recent_messages) > 1:  # More than just the current message
                context_messages = recent_messages[-6:-1]  # Last 5 messages before current
                conversation_context = [
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in context_messages
                ]

            # 4. Get session filters with retry
            async def _get_session_filters():
                async with AsyncSessionLocal() as session:
                    result = await session.execute(text("""
                        SELECT context_filters, rag_config
                        FROM chat_sessions
                        WHERE id = :session_id
                    """), {"session_id": session_id})

                    row = result.fetchone()
                    return json.loads(row[0]) if row and isinstance(row[0], str) and row[0] else (row[0] if row and row[0] else {})

            context_filters = await self._execute_db_operation_with_retry(
                _get_session_filters,
                "get_session_filters"
            )

            # 5. Process with UnifiedRAGService with enhanced retry logic
            rag_response_dict = await self._process_rag_query_with_retry(
                query=query,
                processing_mode=processing_mode,
                context_filters=context_filters,
                conversation_context=conversation_context,
                session_id=session_id,
                user_id=user_id
            )

            processing_time_ms = int((time.time() - start_time) * 1000)

            # 6. Add assistant response to session with retry
            async def _add_assistant_message():
                return await self.add_message(
                    session_id=session_id,
                    user_id=user_id,
                    role="assistant",
                    content=rag_response_dict["answer"],
                    confidence_score=rag_response_dict.get("confidence"),
                    processing_time_ms=processing_time_ms,
                    sources=rag_response_dict.get("sources", []),
                    model_used=rag_response_dict.get("metadata", {}).get("model_used")
                )

            assistant_message_id = await self._execute_db_operation_with_retry(
                _add_assistant_message,
                "add_assistant_message"
            )

            await self._record_rag_metrics(
                query=query,
                processing_mode=processing_mode,
                session_id=session_id,
                sources_payload=rag_response_dict.get("sources", []),
                response_time_ms=processing_time_ms,
                cache_hit=bool(rag_response_dict.get("metadata", {}).get("cache_hit", False)),
            )

            # Title is now auto-generated in add_message when first user message is added
            return {
                "message_id": assistant_message_id,
                "answer": rag_response_dict["answer"],
                "confidence_score": rag_response_dict.get("confidence"),
                "sources": rag_response_dict.get("sources", []),
                "processing_time_ms": processing_time_ms,
                "model_used": rag_response_dict.get("metadata", {}).get("model_used"),
                "retry_attempts": getattr(rag_response_dict, "retry_attempts", 0)
            }

        except Exception as e:
            logger.error(f"Failed to process message after retries: {str(e)}")
            fallback_answer = (
                "Entschuldigung, ein interner Fehler ist aufgetreten. "
                "Unser Team wurde informiert und arbeitet an einer Lösung."
            )

            # Persist a sanitized error response in the conversation history
            fallback_message_id = await self._add_error_message_with_fallback(
                session_id=session_id,
                user_id=user_id,
                error_message=fallback_answer,
                start_time=start_time
            )

            if not fallback_message_id:
                fallback_message_id = f"error-{uuid.uuid4()}"

            return {
                "message_id": fallback_message_id,
                "answer": fallback_answer,
                "confidence_score": 0.0,
                "sources": [],
                "processing_time_ms": int((time.time() - start_time) * 1000),
                "model_used": "unified-rag-service",
                "retry_attempts": self._retry_config["max_retries"]
            }

    async def _process_rag_query_with_retry(
        self,
        query: str,
        processing_mode: str,
        context_filters: Dict[str, Any],
        conversation_context: List[Dict[str, str]],
        session_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Process RAG query with enhanced retry logic and graceful fallbacks"""

        if not self.rag_service:
            return {
                "answer": "Entschuldigung, der RAG-Service ist derzeit nicht verfügbar. Bitte versuchen Sie es später erneut.",
                "confidence": 0.0,
                "sources": [],
                "metadata": {"error": "RAG service unavailable", "fallback": True}
            }

        # Convert string mode to RAGMode enum
        try:
            from .rag import RAGMode
            rag_mode = RAGMode.ACCURATE
            if processing_mode.upper() == "FAST":
                rag_mode = RAGMode.FAST
            elif processing_mode.upper() == "COMPREHENSIVE":
                rag_mode = RAGMode.COMPREHENSIVE
        except ImportError as e:
            logger.warning(f"Failed to import RAGMode, using fallback: {str(e)}")
            # Use string mode directly as fallback
            rag_mode = processing_mode

        async def _rag_query_operation():
            try:
                rag_response = await self.rag_service.query(
                    query=query,
                    mode=rag_mode,
                    filters=context_filters,
                    conversation_context=conversation_context,
                    session_id=session_id,
                    user_id=user_id
                )

                # Debug: Log response type and structure
                logger.debug(f"RAG response type: {type(rag_response)}")
                logger.debug(f"RAG response keys: {rag_response.keys() if isinstance(rag_response, dict) else 'Not a dict'}")

                # Qdrant RAG service returns dict format directly
                # Check if it's already a dict or if it needs conversion
                if isinstance(rag_response, dict):
                    result = {
                        "answer": rag_response.get("answer", ""),
                        "confidence": rag_response.get("metadata", {}).get("confidence_score", 0.0),
                        "sources": rag_response.get("metadata", {}).get("sources", []),
                        "metadata": rag_response.get("metadata", {})
                    }
                    logger.debug(f"Successfully converted dict response to result format")
                    return result
                else:
                    # Handle RAGResponse objects (if they exist)
                    logger.debug(f"Handling non-dict response type: {type(rag_response)}")
                    result = {
                        "answer": getattr(rag_response, 'answer', ''),
                        "confidence": getattr(rag_response, 'confidence_score', 0.0),
                        "sources": getattr(rag_response, 'sources', []),
                        "metadata": getattr(rag_response, 'metadata', {})
                    }
                    logger.debug(f"Successfully converted object response to result format")
                    return result
            except Exception as e:
                logger.error(f"Error in _rag_query_operation: {type(e).__name__}: {str(e)}")
                logger.error(f"RAG response type at error: {type(rag_response) if 'rag_response' in locals() else 'undefined'}")
                raise

        try:
            # Execute RAG query with retry
            result = await self._execute_rag_operation_with_retry(
                _rag_query_operation,
                "rag_query"
            )
            result["metadata"]["retry_attempts"] = 0  # No retries needed
            return result

        except Exception as rag_error:
            logger.error(f"RAG query failed after retries: {str(rag_error)}")

            # Try fallback to fast mode with reduced context
            if rag_mode != RAGMode.FAST:
                try:
                    logger.info("Attempting fallback to fast mode...")
                    fallback_result = await self._try_fallback_query(
                        query=query,
                        context_filters=context_filters,
                        conversation_context=conversation_context[-2:],  # Reduced context
                        session_id=session_id,
                        user_id=user_id
                    )
                    fallback_result["metadata"]["fallback_reason"] = "fast_mode_fallback"
                    fallback_result["metadata"]["original_error"] = str(rag_error)
                    return fallback_result

                except Exception as fallback_error:
                    logger.error(f"Fast mode fallback also failed: {str(fallback_error)}")

            # Ultimate fallback response
            return {
                "answer": "Entschuldigung, bei der Verarbeitung Ihrer Anfrage ist ein Problem aufgetreten. Bitte versuchen Sie es später erneut oder formulieren Sie Ihre Frage anders.",
                "confidence": 0.0,
                "sources": [],
                "metadata": {
                    "error": str(rag_error),
                    "fallback": True,
                    "original_mode": processing_mode,
                    "retry_attempts": self._retry_config["max_retries"]
                }
            }

    async def _try_fallback_query(
        self,
        query: str,
        context_filters: Dict[str, Any],
        conversation_context: List[Dict[str, str]],
        session_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Try fallback query with fast mode and minimal context"""

        if not self.rag_service:
            raise Exception("RAG service not available for fallback")

        from .rag import RAGMode

        async def _fallback_query_operation():
            rag_response = await self.rag_service.query(
                query=query,
                mode=RAGMode.FAST,
                filters=context_filters,
                conversation_context=conversation_context,
                session_id=session_id,
                user_id=user_id
            )

            # Qdrant RAG service returns dict format directly
            if isinstance(rag_response, dict):
                return {
                    "answer": rag_response.get("answer", ""),
                    "confidence": rag_response.get("metadata", {}).get("confidence_score", 0.0),
                    "sources": rag_response.get("metadata", {}).get("sources", []),
                    "metadata": rag_response.get("metadata", {})
                }
            else:
                return {
                    "answer": getattr(rag_response, 'answer', ''),
                    "confidence": getattr(rag_response, 'confidence_score', 0.0),
                    "sources": getattr(rag_response, 'sources', []),
                    "metadata": getattr(rag_response, 'metadata', {})
                }

        return await self._execute_rag_operation_with_retry(
            _fallback_query_operation,
            "fallback_rag_query"
        )

    async def _add_error_message_with_fallback(
        self,
        session_id: str,
        user_id: str,
        error_message: str,
        start_time: float
    ):
        """Add error message to session with fallback handling"""

        async def _add_error():
            return await self.add_message(
                session_id=session_id,
                user_id=user_id,
                role="assistant",
                content=(
                    error_message
                    if error_message
                    else "Sorry, I encountered an error processing your message."
                ),
                confidence_score=0.0,
                processing_time_ms=int((time.time() - start_time) * 1000)
            )

        try:
            return await self._execute_db_operation_with_retry(_add_error, "add_error_message")
        except Exception as fallback_error:
            logger.error(f"Failed to add error message: {str(fallback_error)}")
            # Continue without failing the main operation
            return None
    
    # ================================
    # UTILITY METHODS
    # ================================
    
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get chat statistics for a user"""
        await self._initialize()
        
        try:
            async with AsyncSessionLocal() as session:
                # Try to use the stored function if it exists
                try:
                    result = await session.execute(text("""
                        SELECT * FROM get_user_chat_stats(:user_id)
                    """), {"user_id": user_id})
                    
                    row = result.fetchone()
                    if row:
                        return {
                            "total_sessions": row[0],
                            "active_sessions": row[1],
                            "total_messages": row[2],
                            "last_session_date": row[3]
                        }
                except Exception:
                    # Fallback to manual calculation
                    pass
                
                # Manual calculation
                result = await session.execute(text("""
                    SELECT 
                        COUNT(*) as total_sessions,
                        COUNT(*) FILTER (WHERE is_active = true) as active_sessions,
                        COALESCE(SUM(message_count), 0) as total_messages,
                        MAX(created_at) as last_session_date
                    FROM chat_sessions 
                    WHERE user_id = :user_id
                """), {"user_id": user_id})
                
                row = result.fetchone()
                return {
                    "total_sessions": row[0],
                    "active_sessions": row[1], 
                    "total_messages": row[2],
                    "last_session_date": row[3]
                }
            
        except Exception as e:
            logger.error(f"Failed to get user stats: {str(e)}")
            raise Exception(f"Stats retrieval failed: {str(e)}")
    
    async def search_messages(
        self,
        user_id: str,
        query: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search through user's chat messages"""
        await self._initialize()
        
        try:
            async with AsyncSessionLocal() as session:
                # Search messages with ILIKE
                result = await session.execute(text("""
                    SELECT m.*, s.title as session_title
                    FROM chat_messages m
                    JOIN chat_sessions s ON m.session_id = s.id
                    WHERE m.user_id = :user_id 
                      AND m.content ILIKE :search_query
                    ORDER BY m.created_at DESC
                    LIMIT :limit
                """), {
                    "user_id": user_id,
                    "search_query": f"%{query}%",
                    "limit": limit
                })
                
                rows = result.fetchall()
                
                # Convert to list of dicts
                messages = []
                for row in rows:
                    messages.append({
                        "id": str(row[0]),
                        "session_id": str(row[1]),
                        "user_id": row[2],
                        "role": row[3],
                        "content": row[4],
                        "confidence_score": float(row[5]) if row[5] else None,
                        "processing_time_ms": row[6],
                        "sources": json.loads(row[7]) if isinstance(row[7], str) and row[7] else (row[7] if row[7] else []),
                        "model_used": row[8],
                        "created_at": row[9],
                        "sequence_number": row[10],
                        "session_title": row[11]
                    })
                
                return messages
            
        except Exception as e:
            logger.error(f"Failed to search messages: {str(e)}")
            raise Exception(f"Message search failed: {str(e)}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Enhanced health check with detailed component status and retry information"""
        try:
            await self._initialize()

            health_components = {
                "service_initialized": self._initialized,
                "retry_config": self._retry_config,
                "components": {},
                "performance": {},
                "timestamp": datetime.utcnow().isoformat()
            }

            # Test database connection with retry
            db_healthy = False
            db_response_time = None
            try:
                db_start = time.time()
                async with AsyncSessionLocal() as session:
                    await session.execute(text("SELECT 1"))
                db_response_time = int((time.time() - db_start) * 1000)
                db_healthy = True
            except Exception as e:
                logger.error(f"Database health check failed: {str(e)}")

            health_components["components"]["database"] = {
                "status": "healthy" if db_healthy else "unhealthy",
                "response_time_ms": db_response_time,
                "error": None if db_healthy else "Connection failed"
            }

            # Test RAG service with timeout protection and detailed status
            rag_healthy = False
            rag_details = {}
            try:
                if self.rag_service:
                    import asyncio
                    rag_start = time.time()
                    # Add timeout for RAG health check
                    health_task = asyncio.create_task(self.rag_service.health_check())
                    rag_health_result = await asyncio.wait_for(health_task, timeout=10.0)
                    rag_response_time = int((time.time() - rag_start) * 1000)

                    rag_healthy = rag_health_result.get("status") == "healthy"
                    rag_details = {
                        "status": rag_health_result.get("status"),
                        "response_time_ms": rag_response_time,
                        "details": rag_health_result.get("components", {}),
                        "available_modes": rag_health_result.get("available_modes", []),
                        "query_processor": rag_health_result.get("query_processor", {}),
                        "adaptive_retriever": rag_health_result.get("adaptive_retriever", {})
                    }
                else:
                    rag_details = {
                        "status": "not_initialized",
                        "error": "RAG service not available"
                    }
            except asyncio.TimeoutError:
                logger.error("RAG health check timed out after 10 seconds")
                rag_details = {
                    "status": "timeout",
                    "error": "Health check timed out after 10 seconds"
                }
            except Exception as e:
                logger.error(f"RAG health check failed: {str(e)}")
                rag_details = {
                    "status": "error",
                    "error": str(e)
                }

            health_components["components"]["rag_service"] = rag_details

            # Overall status determination
            critical_components_healthy = db_healthy and (rag_healthy or not self.rag_service)
            overall_status = "healthy" if critical_components_healthy else "degraded"

            # Performance metrics
            health_components["performance"] = {
                "database_response_time_ms": db_response_time,
                "rag_response_time_ms": rag_details.get("response_time_ms"),
                "retry_configuration": {
                    "max_retries": self._retry_config["max_retries"],
                    "base_delay_s": self._retry_config["base_delay"],
                    "max_delay_s": self._retry_config["max_delay"],
                    "backoff_factor": self._retry_config["backoff_factor"]
                }
            }

            # Build final response
            final_response = {
                "status": overall_status,
                "service": "ChatServiceSQLAlchemy",
                "version": "enterprise-ready",
                "components": health_components["components"],
                "performance": health_components["performance"],
                "timestamp": health_components["timestamp"]
            }

            # Add detailed error information if unhealthy
            if overall_status != "healthy":
                errors = []
                if not db_healthy:
                    errors.append("Database connection failed")
                if self.rag_service and not rag_healthy:
                    errors.append("RAG service not healthy")
                final_response["errors"] = errors
                final_response["fallback_mode"] = "operational_with_limitations"

            return final_response

        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "service": "ChatServiceSQLAlchemy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "fallback_mode": "limited_functionality"
            }
    
    # ================================
    # TITLE MANAGEMENT
    # ================================
    
    async def regenerate_session_title(
        self,
        session_id: str,
        user_id: str
    ) -> str:
        """Regenerate title for a chat session"""
        await self._initialize()
        
        try:
            # Verify session ownership
            async with AsyncSessionLocal() as session:
                result = await session.execute(text("""
                    SELECT id FROM chat_sessions 
                    WHERE id = :session_id AND user_id = :user_id
                """), {"session_id": session_id, "user_id": user_id})
                
                if not result.fetchone():
                    raise Exception("Session not found or access denied")
            
            # Generate new title
            new_title = await chat_title_generator.generate_title_for_session(
                session_id, force_refresh=True
            )
            
            logger.info(f"Regenerated title '{new_title}' for session {session_id}")
            return new_title
            
        except Exception as e:
            logger.error(f"Failed to regenerate title: {str(e)}")
            raise Exception(f"Title regeneration failed: {str(e)}")
    
    async def update_session_title(
        self,
        session_id: str,
        user_id: str,
        title: str
    ) -> str:
        """Update session title with custom title"""
        await self._initialize()
        
        try:
            return await chat_title_generator.update_session_title(
                session_id=session_id,
                user_id=user_id,
                custom_title=title
            )
            
        except Exception as e:
            logger.error(f"Failed to update title: {str(e)}")
            raise Exception(f"Title update failed: {str(e)}")

    async def process_message_stream(
        self,
        session_id: str,
        user_id: str,
        query: str,
        processing_mode: str = "accurate"
    ):
        """
        Process user message with streaming response
        Returns async generator that yields chunks of the response
        """
        await self._initialize()

        start_time = time.time()

        try:
            # 1. Add user message to session
            user_message_id = await self.add_message(
                session_id=session_id,
                user_id=user_id,
                role="user",
                content=query
            )

            # 2. Get session context
            recent_messages = await self.get_session_messages(
                session_id=session_id,
                user_id=user_id,
                limit=10
            )

            # 3. Build conversation context
            conversation_context = []
            if len(recent_messages) > 1:
                context_messages = recent_messages[-6:-1]
                conversation_context = [
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in context_messages
                ]

            # 4. Get filters and process with RAG
            context_filters = {"session_id": session_id}

            if self.rag_service:
                # Use LLM factory for streaming
                from .llm_factory import get_llm_service
                llm_service = await get_llm_service()

                # Get relevant documents first
                rag_response = await self.rag_service.query(
                    query=query,
                    mode=processing_mode,
                    filters=context_filters,
                    conversation_context=conversation_context,
                    max_sources=5
                )

                if rag_response.get("answer") and hasattr(llm_service, 'chat_completion'):
                    # Stream the response using OpenAI
                    messages = [
                        {"role": "system", "content": "Du bist ein hilfsreicher Assistent. Beantworte Fragen basierend auf dem bereitgestellten Kontext."},
                        {"role": "user", "content": f"Kontext:\n{rag_response.get('answer', '')}\n\nFrage: {query}"}
                    ]

                    # Start streaming
                    complete_response = ""
                    async for chunk in await llm_service.chat_completion(
                        messages=messages,
                        stream=True
                    ):
                        if chunk.get("choices") and chunk["choices"][0].get("delta", {}).get("content"):
                            content = chunk["choices"][0]["delta"]["content"]
                            complete_response += content
                            yield {
                                "type": "content",
                                "content": content,
                                "session_id": session_id
                            }

                        if chunk.get("done"):
                            break

                    # Save complete response to database
                    await self.add_message(
                        session_id=session_id,
                        user_id=user_id,
                        role="assistant",
                        content=complete_response,
                        metadata={
                            "processing_mode": processing_mode,
                            "sources": rag_response.get("metadata", {}).get("sources", []),
                            "streaming": True
                        }
                    )

                    processing_time_ms = int((time.time() - start_time) * 1000)
                    await self._record_rag_metrics(
                        query=query,
                        processing_mode=processing_mode,
                        session_id=session_id,
                        sources_payload=rag_response.get("metadata", {}).get("sources", []),
                        response_time_ms=processing_time_ms,
                        cache_hit=bool(rag_response.get("metadata", {}).get("cache_hit", False)),
                    )

                    yield {
                        "type": "done",
                        "session_id": session_id,
                        "sources": rag_response.get("metadata", {}).get("sources", [])
                    }
                else:
                    # Fallback to non-streaming
                    answer = rag_response.get("answer", "Entschuldigung, ich konnte keine Antwort finden.")

                    await self.add_message(
                        session_id=session_id,
                        user_id=user_id,
                        role="assistant",
                        content=answer,
                        metadata={
                            "processing_mode": processing_mode,
                            "sources": rag_response.get("metadata", {}).get("sources", []),
                            "streaming": False
                        }
                    )

                    processing_time_ms = int((time.time() - start_time) * 1000)
                    await self._record_rag_metrics(
                        query=query,
                        processing_mode=processing_mode,
                        session_id=session_id,
                        sources_payload=rag_response.get("metadata", {}).get("sources", []),
                        response_time_ms=processing_time_ms,
                        cache_hit=bool(rag_response.get("metadata", {}).get("cache_hit", False)),
                    )

                    yield {
                        "type": "content",
                        "content": answer,
                        "session_id": session_id
                    }

                    yield {
                        "type": "done",
                        "session_id": session_id,
                        "sources": rag_response.get("metadata", {}).get("sources", [])
                    }
            else:
                # No RAG service available
                fallback_response = "Entschuldigung, der RAG-Service ist derzeit nicht verfügbar."

                await self.add_message(
                    session_id=session_id,
                    user_id=user_id,
                    role="assistant",
                    content=fallback_response
                )

                processing_time_ms = int((time.time() - start_time) * 1000)
                await self._record_rag_metrics(
                    query=query,
                    processing_mode=processing_mode,
                    session_id=session_id,
                    sources_payload=[],
                    response_time_ms=processing_time_ms,
                    cache_hit=False,
                    error="rag_service_unavailable",
                )

                yield {
                    "type": "content",
                    "content": fallback_response,
                    "session_id": session_id
                }

                yield {
                    "type": "done",
                    "session_id": session_id,
                    "sources": []
                }

        except Exception as e:
            logger.error(f"Streaming chat error: {str(e)}")
            processing_time_ms = int((time.time() - start_time) * 1000)
            await self._record_rag_metrics(
                query=query,
                processing_mode=processing_mode,
                session_id=session_id,
                sources_payload=[],
                response_time_ms=processing_time_ms,
                cache_hit=False,
                error=str(e),
            )
            yield {
                "type": "error",
                "content": f"Chat-Fehler: {str(e)}",
                "session_id": session_id
            }
