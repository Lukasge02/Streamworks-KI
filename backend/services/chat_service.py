"""
Chat Service for Streamworks RAG System
Handles chat sessions, messages, and RAG integration with Supabase
"""

import asyncio
import uuid
import time
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

from supabase import create_client, Client
from config import settings
from .unified_rag_service import UnifiedRAGService, RAGConfig
from .vectorstore import VectorStoreService
from .embeddings import EmbeddingService

logger = logging.getLogger(__name__)

class ChatService:
    """Service for managing chat sessions and RAG-powered conversations"""
    
    def __init__(self):
        self.supabase: Client = None
        self.rag_service: UnifiedRAGService = None
        self._initialized = False
    
    async def _initialize(self):
        """Initialize Supabase client and RAG service"""
        if self._initialized:
            return
            
        try:
            # Initialize Supabase client
            self.supabase = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_SERVICE_KEY
            )
            
            # Initialize RAG service
            vectorstore = VectorStoreService()
            await vectorstore.initialize()
            
            embeddings = EmbeddingService()
            await embeddings.initialize()
            
            self.rag_service = UnifiedRAGService(vectorstore, embeddings)
            
            self._initialized = True
            logger.info("ChatService initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChatService: {str(e)}")
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
            session_data = {
                "title": title,
                "user_id": user_id,
                "company_id": "00000000-0000-0000-0000-000000000001",  # Default company
                "message_count": 0,
                "rag_config": rag_config or {},
                "context_filters": context_filters or {},
                "is_active": True,
                "is_archived": False
            }
            
            result = self.supabase.table("chat_sessions").insert(session_data).execute()
            
            if not result.data:
                raise Exception("Failed to create session - no data returned")
            
            session_id = result.data[0]["id"]
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
            query = self.supabase.table("chat_sessions").select("*")
            
            # Filter by user
            query = query.eq("user_id", user_id)
            
            # Filter by active status
            if active_only:
                query = query.eq("is_active", True)
            
            # Order by most recent
            query = query.order("updated_at", desc=True)
            
            # Limit results
            query = query.limit(limit)
            
            result = query.execute()
            
            return result.data or []
            
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
            update_data = {"updated_at": datetime.utcnow().isoformat()}
            
            if title is not None:
                update_data["title"] = title
            if rag_config is not None:
                update_data["rag_config"] = rag_config
            if context_filters is not None:
                update_data["context_filters"] = context_filters
            
            result = self.supabase.table("chat_sessions")\
                .update(update_data)\
                .eq("id", session_id)\
                .eq("user_id", user_id)\
                .execute()
            
            if not result.data:
                raise Exception("Session not found or access denied")
                
        except Exception as e:
            logger.error(f"Failed to update session: {str(e)}")
            raise Exception(f"Session update failed: {str(e)}")
    
    async def delete_session(self, session_id: str, user_id: str):
        """Delete a chat session and all its messages"""
        await self._initialize()
        
        try:
            # Delete messages first (cascade should handle this, but being explicit)
            self.supabase.table("chat_messages")\
                .delete()\
                .eq("session_id", session_id)\
                .execute()
            
            # Delete session
            result = self.supabase.table("chat_sessions")\
                .delete()\
                .eq("id", session_id)\
                .eq("user_id", user_id)\
                .execute()
            
            if not result.data:
                raise Exception("Session not found or access denied")
                
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
            # Verify user has access to this session
            session_check = self.supabase.table("chat_sessions")\
                .select("id")\
                .eq("id", session_id)\
                .eq("user_id", user_id)\
                .execute()
            
            if not session_check.data:
                raise Exception("Session not found or access denied")
            
            # Get messages
            result = self.supabase.table("chat_messages")\
                .select("*")\
                .eq("session_id", session_id)\
                .order("sequence_number", desc=False)\
                .limit(limit)\
                .execute()
            
            return result.data or []
            
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
            message_data = {
                "session_id": session_id,
                "user_id": user_id,
                "role": role,
                "content": content,
                "confidence_score": confidence_score,
                "processing_time_ms": processing_time_ms,
                "sources": sources or [],
                "model_used": model_used
            }
            
            result = self.supabase.table("chat_messages").insert(message_data).execute()
            
            if not result.data:
                raise Exception("Failed to add message - no data returned")
            
            message_id = result.data[0]["id"]
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
            session_data = self.supabase.table("chat_sessions")\
                .select("context_filters, rag_config")\
                .eq("id", session_id)\
                .execute()
            
            context_filters = {}
            if session_data.data:
                context_filters = session_data.data[0].get("context_filters", {})
            
            # 6. Process with RAG
            rag_response = await self.rag_service.query(
                query=enhanced_query,
                filters=context_filters,
                mode=processing_mode,
                include_sources=True,
                enable_rerank=enable_rerank
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
            # Use the stored function
            result = self.supabase.rpc("get_user_chat_stats", {"p_user_id": user_id}).execute()
            
            if result.data:
                return result.data
            
            # Fallback to manual calculation if function doesn't exist
            sessions = await self.get_user_sessions(user_id, active_only=False, limit=1000)
            active_sessions = [s for s in sessions if s["is_active"]]
            
            total_messages = 0
            for session in sessions:
                total_messages += session.get("message_count", 0)
            
            return {
                "total_sessions": len(sessions),
                "active_sessions": len(active_sessions),
                "total_messages": total_messages,
                "last_session_date": max([s["created_at"] for s in sessions]) if sessions else None
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
            # Get user's sessions first
            sessions = await self.get_user_sessions(user_id, active_only=False, limit=1000)
            session_ids = [s["id"] for s in sessions]
            
            if not session_ids:
                return []
            
            # Search messages with text similarity
            result = self.supabase.table("chat_messages")\
                .select("*, chat_sessions!inner(title)")\
                .in_("session_id", session_ids)\
                .ilike("content", f"%{query}%")\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            
            return result.data or []
            
        except Exception as e:
            logger.error(f"Failed to search messages: {str(e)}")
            raise Exception(f"Message search failed: {str(e)}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if chat service is healthy"""
        try:
            await self._initialize()
            
            # Test Supabase connection
            supabase_healthy = False
            try:
                result = self.supabase.table("chat_sessions").select("count", count="exact").limit(1).execute()
                supabase_healthy = True
            except Exception as e:
                logger.error(f"Supabase health check failed: {str(e)}")
            
            # Test RAG service
            rag_healthy = False
            try:
                if self.rag_service:
                    cache_stats = self.rag_service.get_cache_stats()
                    rag_healthy = True
            except Exception as e:
                logger.error(f"RAG health check failed: {str(e)}")
            
            return {
                "status": "healthy" if (supabase_healthy and rag_healthy) else "unhealthy",
                "supabase": "connected" if supabase_healthy else "disconnected",
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