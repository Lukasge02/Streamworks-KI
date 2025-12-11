"""
RAG Chat Service
Retrieval-Augmented Generation for document-based Q&A
"""

from typing import List, Dict, Any, Optional
import openai
from config import config


class RAGChatService:
    """
    RAG Chat Service
    - Sucht relevante Dokument-Chunks via VectorStore
    - Sendet Kontext + Query an OpenAI GPT
    - Gibt Antwort mit Quellenangaben zurück
    """
    
    SYSTEM_PROMPT = """Du bist ein hilfreicher Assistent für Streamworks-Dokumentation.
Beantworte Fragen basierend auf den bereitgestellten Dokumenten.
Wenn du die Antwort nicht in den Dokumenten findest, sage das ehrlich.
Antworte auf Deutsch und sei präzise."""

    def __init__(self, vector_store=None):
        self._vector_store = vector_store
        self.openai_client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = getattr(config, 'LLM_MODEL', 'gpt-4o-mini')
    
    @property
    def vector_store(self):
        if self._vector_store is None:
            from .vector_store import vector_store
            self._vector_store = vector_store
        return self._vector_store
    
    def chat(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        num_chunks: int = 5,
        score_threshold: float = 0.3
    ) -> Dict[str, Any]:
        """
        Process a chat query with RAG
        
        Args:
            query: User's question
            conversation_history: Previous messages [{"role": "user/assistant", "content": "..."}]
            num_chunks: Number of relevant chunks to retrieve
            score_threshold: Minimum similarity score
            
        Returns:
            {
                "answer": str,
                "sources": [{"filename": str, "content": str, "score": float}],
                "has_context": bool
            }
        """
        # 1. Search for relevant documents
        search_results = self.vector_store.search(
            query=query,
            limit=num_chunks,
            score_threshold=score_threshold
        )
        
        # 2. Build context from results
        context_parts = []
        sources = []
        
        for i, result in enumerate(search_results):
            content = result.get("content", "")
            filename = result.get("filename", "Unknown")
            score = result.get("score", 0)
            
            context_parts.append(f"[Dokument {i+1}: {filename}]\n{content}")
            sources.append({
                "filename": filename,
                "content": content[:300] + "..." if len(content) > 300 else content,
                "score": round(score, 3),
                "doc_type": result.get("doc_type", "unknown")
            })
        
        context = "\n\n---\n\n".join(context_parts) if context_parts else ""
        has_context = len(context_parts) > 0
        
        # 3. Build messages for OpenAI
        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]
        
        # Add context if available
        if context:
            context_message = f"""Hier sind relevante Dokumente zur Beantwortung der Frage:

{context}

---

Nutze diese Informationen um die folgende Frage zu beantworten."""
            messages.append({"role": "system", "content": context_message})
        
        # Add conversation history (last 6 messages)
        if conversation_history:
            messages.extend(conversation_history[-6:])
        
        # Add current query
        messages.append({"role": "user", "content": query})
        
        # 4. Call OpenAI
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1500
            )
            answer = response.choices[0].message.content
        except Exception as e:
            answer = f"Fehler bei der KI-Anfrage: {str(e)}"
        
        return {
            "answer": answer,
            "sources": sources,
            "has_context": has_context,
            "chunks_found": len(sources)
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get service stats"""
        vs_stats = self.vector_store.get_stats()
        return {
            "model": self.model,
            "vector_store": vs_stats,
            "ready": bool(config.OPENAI_API_KEY)
        }


# Singleton instance
rag_chat_service = RAGChatService()
