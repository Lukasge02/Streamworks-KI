"""
Enterprise Chat Service - Production Grade Implementation
Handles all chat-related business logic with proper separation of concerns
"""
import logging
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from ...infrastructure.llm.mistral_client import MistralClient
from ...infrastructure.vectordb.chromadb_client import ChromaDBClient
from ..qa.rag_service import RAGService

logger = logging.getLogger(__name__)

@dataclass
class ChatMessage:
    """Domain model for chat messages"""
    id: str
    conversation_id: str
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class ChatConversation:
    """Domain model for chat conversations"""
    id: str
    user_id: Optional[str]
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]
    messages: List[ChatMessage]

class ChatService:
    """
    Enterprise Chat Service with full conversation management
    """
    
    def __init__(self):
        self.mistral_client = MistralClient()
        self.chromadb_client = ChromaDBClient()
        self.rag_service = RAGService()
        self._conversations: Dict[str, ChatConversation] = {}
        
    async def create_conversation(
        self, 
        user_id: Optional[str] = None,
        title: Optional[str] = None
    ) -> ChatConversation:
        """Create a new chat conversation"""
        conversation_id = str(uuid.uuid4())
        conversation = ChatConversation(
            id=conversation_id,
            user_id=user_id,
            title=title or f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            metadata={},
            messages=[]
        )
        self._conversations[conversation_id] = conversation
        logger.info(f"Created new conversation: {conversation_id}")
        return conversation
    
    async def send_message(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        mode: str = "hybrid",  # 'chat', 'rag', 'hybrid'
        context_window: int = 5
    ) -> Dict[str, Any]:
        """
        Process a chat message with enterprise-grade features
        
        Args:
            message: User message
            conversation_id: Existing conversation ID or None for new
            mode: Processing mode (chat, rag, hybrid)
            context_window: Number of previous messages to include
            
        Returns:
            Response with message, sources, and metadata
        """
        try:
            # Create or get conversation
            if not conversation_id:
                conversation = await self.create_conversation()
                conversation_id = conversation.id
            else:
                conversation = self._conversations.get(conversation_id)
                if not conversation:
                    raise ValueError(f"Conversation {conversation_id} not found")
            
            # Create user message
            user_message = ChatMessage(
                id=str(uuid.uuid4()),
                conversation_id=conversation_id,
                role="user",
                content=message,
                timestamp=datetime.now(timezone.utc),
                metadata={"mode": mode}
            )
            conversation.messages.append(user_message)
            
            # Process based on mode
            response_content = ""
            sources = []
            processing_metadata = {}
            
            if mode in ["rag", "hybrid"]:
                # Get RAG context
                rag_response = await self.rag_service.query(
                    question=message,
                    top_k=5
                )
                sources = rag_response.get("sources", [])
                processing_metadata["rag_confidence"] = rag_response.get("confidence", 0)
                
                if mode == "rag":
                    response_content = rag_response.get("answer", "")
                else:
                    # Hybrid mode - use RAG context with LLM
                    context = self._build_context(conversation, context_window)
                    rag_context = rag_response.get("context", "")
                    
                    prompt = self._build_hybrid_prompt(
                        message=message,
                        context=context,
                        rag_context=rag_context
                    )
                    
                    llm_response = await self.mistral_client.generate(prompt)
                    response_content = llm_response.get("response", "")
            
            else:
                # Pure chat mode
                context = self._build_context(conversation, context_window)
                prompt = self._build_chat_prompt(message=message, context=context)
                
                llm_response = await self.mistral_client.generate(prompt)
                response_content = llm_response.get("response", "")
            
            # Create assistant message
            assistant_message = ChatMessage(
                id=str(uuid.uuid4()),
                conversation_id=conversation_id,
                role="assistant",
                content=response_content,
                timestamp=datetime.now(timezone.utc),
                metadata={
                    "mode": mode,
                    "sources": sources,
                    **processing_metadata
                }
            )
            conversation.messages.append(assistant_message)
            conversation.updated_at = datetime.now(timezone.utc)
            
            # Build response
            return {
                "response": response_content,
                "conversation_id": conversation_id,
                "message_id": assistant_message.id,
                "sources": sources,
                "mode_used": mode,
                "processing_time": (
                    assistant_message.timestamp - user_message.timestamp
                ).total_seconds(),
                "metadata": processing_metadata
            }
            
        except Exception as e:
            logger.error(f"Chat service error: {e}")
            raise
    
    async def get_conversation(
        self, 
        conversation_id: str
    ) -> Optional[ChatConversation]:
        """Get a conversation by ID"""
        return self._conversations.get(conversation_id)
    
    async def list_conversations(
        self,
        user_id: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[ChatConversation]:
        """List conversations with pagination"""
        conversations = list(self._conversations.values())
        
        if user_id:
            conversations = [c for c in conversations if c.user_id == user_id]
        
        # Sort by updated_at descending
        conversations.sort(key=lambda c: c.updated_at, reverse=True)
        
        return conversations[offset:offset + limit]
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation"""
        if conversation_id in self._conversations:
            del self._conversations[conversation_id]
            logger.info(f"Deleted conversation: {conversation_id}")
            return True
        return False
    
    def _build_context(
        self, 
        conversation: ChatConversation, 
        window_size: int
    ) -> str:
        """Build conversation context from recent messages"""
        recent_messages = conversation.messages[-window_size * 2:]  # Get last N exchanges
        
        context_lines = []
        for msg in recent_messages:
            role = "User" if msg.role == "user" else "Assistant"
            context_lines.append(f"{role}: {msg.content}")
        
        return "\n".join(context_lines)
    
    def _build_chat_prompt(self, message: str, context: str) -> str:
        """Build prompt for pure chat mode"""
        return f"""Du bist ein hilfreicher KI-Assistent für StreamWorks.

Bisheriger Gesprächsverlauf:
{context}

User: {message}

Bitte antworte auf Deutsch und sei präzise und hilfreich."""
    
    def _build_hybrid_prompt(
        self, 
        message: str, 
        context: str, 
        rag_context: str
    ) -> str:
        """Build prompt for hybrid mode with RAG context"""
        return f"""Du bist ein hilfreicher KI-Assistent für StreamWorks.

Relevante Informationen aus der Wissensdatenbank:
{rag_context}

Bisheriger Gesprächsverlauf:
{context}

User: {message}

Bitte antworte auf Deutsch basierend auf den bereitgestellten Informationen. 
Wenn die Informationen nicht ausreichen, nutze dein allgemeines Wissen, 
aber kennzeichne dies entsprechend."""

# Singleton instance
chat_service = ChatService()