"""
LlamaIndex Chat Service

Conversational RAG with session management:
- Multi-turn conversations with memory
- Integration with Supabase chat sessions
- Streaming support (optional)
- API-compatible response format
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict

from .query_service import QueryService, get_query_service
from .settings import LlamaIndexSettings


@dataclass
class ChatResponse:
    """
    Chat response matching existing API contract

    This dataclass mirrors the ChatResponseModel in the router
    for seamless frontend compatibility.
    """

    answer: str
    sources: List[Dict[str, Any]]
    has_context: bool
    chunks_found: int
    session_id: Optional[str] = None
    confidence: Optional[float] = None
    confidence_level: Optional[str] = None
    query_type: Optional[str] = None
    warnings: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
        return asdict(self)


class ChatService:
    """
    Conversational RAG Chat Service

    Features:
    - Multi-turn conversations with context
    - Session-based message history
    - Integration with existing chat session service
    - API-compatible response format
    """

    def __init__(self):
        self._query_service = None
        self._session_service = None

    @property
    def query_service(self) -> QueryService:
        """Lazy-loaded query service"""
        if self._query_service is None:
            self._query_service = get_query_service()
        return self._query_service

    @property
    def session_service(self):
        """Lazy-loaded chat session service (existing implementation)"""
        if self._session_service is None:
            from services.chat_session_service import chat_session_service

            self._session_service = chat_session_service
        return self._session_service

    def chat(
        self,
        query: str,
        session_id: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        num_chunks: int = 5,
        filters: Dict[str, Any] = None,
        doc_ids: List[str] = None,
    ) -> ChatResponse:
        """
        Process a chat message with RAG

        Args:
            query: User's question
            session_id: Optional session ID for persistence
            conversation_history: Previous messages for context
            num_chunks: Number of chunks to retrieve
            filters: Metadata filters
            doc_ids: Specific document IDs to search

        Returns:
            ChatResponse with answer and sources
        """
        # Auto-create session if not provided
        actual_session_id = session_id
        if not actual_session_id:
            session = self.session_service.create_session(
                title=self.session_service.generate_session_title(query)
            )
            if session:
                actual_session_id = session["id"]

        # Save user message to session
        if actual_session_id:
            self.session_service.add_message(
                session_id=actual_session_id,
                role="user",
                content=query,
            )

        # Build context-aware query if conversation history exists
        enhanced_query = self._enhance_query_with_history(query, conversation_history)

        # Execute RAG query
        result = self.query_service.query(
            query_text=enhanced_query,
            top_k=num_chunks,
            filters=filters,
            doc_ids=doc_ids,
        )

        # Save assistant response to session
        if actual_session_id:
            self.session_service.add_message(
                session_id=actual_session_id,
                role="assistant",
                content=result.answer,
                sources=result.sources,
            )

        return ChatResponse(
            answer=result.answer,
            sources=result.sources,
            has_context=result.has_context,
            chunks_found=result.chunks_found,
            session_id=actual_session_id,
            confidence=result.confidence,
            confidence_level=result.confidence_level,
            query_type=result.query_type,
            warnings=result.warnings,
        )

    def chat_simple(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        num_chunks: int = 5,
    ) -> Dict[str, Any]:
        """
        Simplified chat endpoint (API compatibility layer)

        Returns dict instead of dataclass for backward compatibility
        with existing router code.
        """
        response = self.chat(
            query=query,
            session_id=None,
            conversation_history=conversation_history,
            num_chunks=num_chunks,
        )

        return {
            "answer": response.answer,
            "sources": response.sources,
            "has_context": response.has_context,
            "chunks_found": response.chunks_found,
            "confidence": response.confidence,
            "confidence_level": response.confidence_level,
            "query_type": response.query_type,
            "warnings": response.warnings or [],
        }

    def chat_with_access_control(
        self,
        query: str,
        user_id: Optional[str] = None,
        user_roles: Optional[List[str]] = None,
        session_id: Optional[str] = None,
        num_chunks: int = 5,
    ) -> ChatResponse:
        """
        Chat with document access control

        Filters documents based on user permissions before querying.
        """
        from services.rag.access_service import get_access_service

        access_service = get_access_service()

        # Get accessible document IDs for user
        accessible_docs = access_service.get_accessible_documents(
            user_id=user_id,
            user_roles=user_roles,
        )

        if not accessible_docs:
            return ChatResponse(
                answer="Sie haben keinen Zugriff auf Dokumente, die diese Frage beantworten könnten.",
                sources=[],
                has_context=False,
                chunks_found=0,
                session_id=session_id,
                confidence=0.0,
                confidence_level="no_access",
                query_type="unknown",
                warnings=["Keine zugänglichen Dokumente"],
            )

        return self.chat(
            query=query,
            session_id=session_id,
            num_chunks=num_chunks,
            doc_ids=accessible_docs,
        )

    def _enhance_query_with_history(
        self,
        query: str,
        history: Optional[List[Dict[str, str]]],
    ) -> str:
        """Type-safe wrapper for shared utility"""
        from .context_utils import enhance_query_with_history

        return enhance_query_with_history(query, history)

    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        # Get vector store stats from existing VectorStore
        try:
            from services.rag.vector_store import vector_store

            vs_stats = {
                "collection": "streamworks_documents",
                "status": "connected",
            }
            try:
                info = vector_store.client.get_collection("streamworks_documents")
                vs_stats["points_count"] = info.points_count
                vs_stats["vectors_count"] = info.vectors_count
            except Exception:
                pass
        except Exception:
            vs_stats = {"status": "error"}

        return {
            "ready": True,
            "model": LlamaIndexSettings.LLM_MODEL,
            "embedding_model": LlamaIndexSettings.EMBEDDING_MODEL,
            "framework": "LlamaIndex",
            "vector_store": vs_stats,
            "enhancements": {
                "hybrid_search": True,
                "reranking": False,  # TODO: Add reranking
                "caching": True,
                "confidence_scoring": True,
            },
        }


# Singleton instance
_chat_service: Optional[ChatService] = None


def get_chat_service() -> ChatService:
    """Get singleton ChatService instance"""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service
