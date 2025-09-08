"""
SQLAlchemy-based Chat Service for Streamworks RAG System
Uses direct PostgreSQL connection like the document system
"""

import uuid
import time
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
from sqlalchemy import text, select, insert, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from database import AsyncSessionLocal
from .openai_rag_service import OpenAIRAGService
from .vectorstore import VectorStoreService
from .embeddings import EmbeddingService

logger = logging.getLogger(__name__)

class ChatServiceSQLAlchemy:
    """SQLAlchemy-based Chat Service - compatible with existing database setup"""
    
    def __init__(self):
        self.rag_service: OpenAIRAGService = None
        self._initialized = False
    
    async def _initialize(self):
        """Initialize RAG service (database connection is handled by SQLAlchemy)"""
        if self._initialized:
            return
            
        try:
            # Initialize RAG service
            vectorstore = VectorStoreService()
            await vectorstore.initialize()
            
            embeddings = EmbeddingService()
            await embeddings.initialize()
            
            self.rag_service = OpenAIRAGService(vectorstore, embeddings)
            
            self._initialized = True
            logger.info("ChatServiceSQLAlchemy initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChatServiceSQLAlchemy: {str(e)}")
            raise
    
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
        """Create a new chat session"""
        await self._initialize()
        
        try:
            async with AsyncSessionLocal() as session:
                # Generate UUID
                session_id = str(uuid.uuid4())
                
                # Insert session
                await session.execute(text("""
                    INSERT INTO chat_sessions (
                        id, title, user_id, company_id, message_count,
                        rag_config, context_filters, is_active, is_archived
                    ) VALUES (
                        :id, :title, :user_id, :company_id, :message_count,
                        :rag_config, :context_filters, :is_active, :is_archived
                    )
                """), {
                    "id": session_id,
                    "title": title,
                    "user_id": user_id,
                    "company_id": "00000000-0000-0000-0000-000000000001",
                    "message_count": 0,
                    "rag_config": json.dumps(rag_config or {}),
                    "context_filters": json.dumps(context_filters or {}),
                    "is_active": True,
                    "is_archived": False
                })
                
                await session.commit()
                logger.info(f"Created chat session {session_id} for user {user_id}")
                
                return session_id
                
        except Exception as e:
            logger.error(f"Failed to create session: {str(e)}")
            raise Exception(f"Session creation failed: {str(e)}")
    
    async def get_user_sessions(
        self,
        user_id: str,
        active_only: bool = True,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get all chat sessions for a user"""
        await self._initialize()
        
        try:
            async with AsyncSessionLocal() as session:
                query = """
                    SELECT id, title, user_id, company_id, message_count,
                           rag_config, context_filters, is_active, is_archived,
                           created_at, updated_at, last_message_at
                    FROM chat_sessions
                    WHERE user_id = :user_id
                """
                
                params = {"user_id": user_id}
                
                if active_only:
                    query += " AND is_active = true"
                
                query += " ORDER BY updated_at DESC LIMIT :limit"
                params["limit"] = limit
                
                result = await session.execute(text(query), params)
                rows = result.fetchall()
                
                # Convert to list of dicts
                sessions = []
                for row in rows:
                    sessions.append({
                        "id": str(row[0]),
                        "title": row[1],
                        "user_id": row[2],
                        "company_id": str(row[3]) if row[3] else None,
                        "message_count": row[4],
                        "rag_config": json.loads(row[5]) if row[5] else {},
                        "context_filters": json.loads(row[6]) if row[6] else {},
                        "is_active": row[7],
                        "is_archived": row[8],
                        "created_at": row[9],
                        "updated_at": row[10],
                        "last_message_at": row[11]
                    })
                
                return sessions
                
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
        """Update chat session"""
        await self._initialize()
        
        try:
            async with AsyncSessionLocal() as session:
                update_parts = ["updated_at = now()"]
                params = {"session_id": session_id, "user_id": user_id}
                
                if title is not None:
                    update_parts.append("title = :title")
                    params["title"] = title
                if rag_config is not None:
                    update_parts.append("rag_config = :rag_config")
                    params["rag_config"] = json.dumps(rag_config)
                if context_filters is not None:
                    update_parts.append("context_filters = :context_filters")
                    params["context_filters"] = json.dumps(context_filters)
                
                query = f"""
                    UPDATE chat_sessions 
                    SET {', '.join(update_parts)}
                    WHERE id = :session_id AND user_id = :user_id
                """
                
                result = await session.execute(text(query), params)
                
                if result.rowcount == 0:
                    raise Exception("Session not found or access denied")
                    
                await session.commit()
                
        except Exception as e:
            logger.error(f"Failed to update session: {str(e)}")
            raise Exception(f"Session update failed: {str(e)}")
    
    async def delete_session(self, session_id: str, user_id: str):
        """Delete a chat session and all its messages"""
        await self._initialize()
        
        try:
            async with AsyncSessionLocal() as session:
                # Delete messages first (should cascade, but being explicit)
                await session.execute(text("""
                    DELETE FROM chat_messages 
                    WHERE session_id = :session_id
                """), {"session_id": session_id})
                
                # Delete session
                result = await session.execute(text("""
                    DELETE FROM chat_sessions 
                    WHERE id = :session_id AND user_id = :user_id
                """), {"session_id": session_id, "user_id": user_id})
                
                if result.rowcount == 0:
                    raise Exception("Session not found or access denied")
                
                await session.commit()
                logger.info(f"Deleted session {session_id} for user {user_id}")
                
        except Exception as e:
            logger.error(f"Failed to delete session: {str(e)}")
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
                        "sources": json.loads(row[7]) if row[7] else [],
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
        """Add a message to a chat session"""
        await self._initialize()
        
        try:
            async with AsyncSessionLocal() as session:
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
        enable_rerank: bool = False
    ) -> Dict[str, Any]:
        """Process user message and generate RAG response"""
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
            
            # 2. Get session context (recent messages for conversation awareness)
            recent_messages = await self.get_session_messages(
                session_id=session_id,
                user_id=user_id,
                limit=10  # Last 10 messages for context
            )
            
            # 3. Build conversation context
            conversation_context = ""
            if len(recent_messages) > 1:  # More than just the current message
                context_messages = recent_messages[-6:-1]  # Last 5 messages before current
                conversation_context = "\\n".join([
                    f"{msg['role'].title()}: {msg['content']}"
                    for msg in context_messages
                ])
            
            # 4. Enhance query with conversation context
            enhanced_query = query
            if conversation_context:
                enhanced_query = f"Previous conversation:\\n{conversation_context}\\n\\nCurrent question: {query}"
            
            # 5. Get session filters (if any)
            async with AsyncSessionLocal() as session:
                result = await session.execute(text("""
                    SELECT context_filters, rag_config 
                    FROM chat_sessions 
                    WHERE id = :session_id
                """), {"session_id": session_id})
                
                row = result.fetchone()
                context_filters = json.loads(row[0]) if row and row[0] else {}
            
            # 6. Process with OpenAI RAG
            rag_response = await self.rag_service.query(
                query=enhanced_query,
                filters=context_filters,
                mode=processing_mode,
                include_sources=True
            )
            
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            # 7. Add assistant response to session
            assistant_message_id = await self.add_message(
                session_id=session_id,
                user_id=user_id,
                role="assistant",
                content=rag_response["answer"],
                confidence_score=rag_response.get("confidence"),
                processing_time_ms=processing_time_ms,
                sources=rag_response.get("sources", []),
                model_used=rag_response.get("metadata", {}).get("model_used")
            )
            
            return {
                "message_id": assistant_message_id,
                "answer": rag_response["answer"],
                "confidence_score": rag_response.get("confidence"),
                "sources": rag_response.get("sources", []),
                "processing_time_ms": processing_time_ms,
                "model_used": rag_response.get("metadata", {}).get("model_used")
            }
            
        except Exception as e:
            logger.error(f"Failed to process message: {str(e)}")
            
            # Add error message to session
            try:
                await self.add_message(
                    session_id=session_id,
                    user_id=user_id,
                    role="assistant",
                    content=f"Sorry, I encountered an error processing your message: {str(e)}",
                    confidence_score=0.0,
                    processing_time_ms=int((time.time() - start_time) * 1000)
                )
            except:
                pass  # Don't fail the main request if logging fails
            
            raise Exception(f"Message processing failed: {str(e)}")
    
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
                        "sources": json.loads(row[7]) if row[7] else [],
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
        """Check if chat service is healthy"""
        try:
            await self._initialize()
            
            # Test database connection
            db_healthy = False
            try:
                async with AsyncSessionLocal() as session:
                    await session.execute(text("SELECT 1"))
                    db_healthy = True
            except Exception as e:
                logger.error(f"Database health check failed: {str(e)}")
            
            # Test OpenAI RAG service
            rag_healthy = False
            try:
                if self.rag_service:
                    rag_health_result = await self.rag_service.health_check()
                    rag_healthy = rag_health_result.get("status") == "healthy"
            except Exception as e:
                logger.error(f"RAG health check failed: {str(e)}")
            
            return {
                "status": "healthy" if (db_healthy and rag_healthy) else "unhealthy",
                "database": "connected" if db_healthy else "disconnected",
                "rag_service": "ready" if rag_healthy else "not ready",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }