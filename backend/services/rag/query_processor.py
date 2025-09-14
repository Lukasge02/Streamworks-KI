"""
Query Processing Service für Streamworks-KI RAG Pipeline
Phase 2: Erweiterte Query-Verarbeitung mit LlamaIndex

Verwendet LlamaIndex-Komponenten für:
- Query-Transformation und -Expansion
- HyDE (Hypothetical Document Embeddings)
- Sub-Query-Generierung für komplexe Fragen
- Konversationskontext-Integration
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from llama_index.core.query_engine import SubQuestionQueryEngine
from llama_index.core.tools import QueryEngineTool
from llama_index.core.response_synthesizers import TreeSummarize
from llama_index.core.schema import QueryBundle
from llama_index.core.prompts import PromptTemplate
from llama_index.core.base.llms.types import ChatMessage, MessageRole

from . import RAGMode, RAGResponse, QueryContext

logger = logging.getLogger(__name__)


class QueryProcessor:
    """
    Advanced Query Processing mit LlamaIndex-Integration

    Verarbeitet Benutzeranfragen durch:
    1. Query-Analyse und -Klassifizierung
    2. Query-Enhancement mit Konversationskontext
    3. HyDE-basierte hypothetische Dokumentgenerierung
    4. Sub-Query-Dekomposition für komplexe Fragen
    """

    def __init__(self, llm_service=None, embed_model=None):
        self.llm_service = llm_service
        self.embed_model = embed_model
        self._initialized = False

        # Query Enhancement Templates
        self.query_enhancement_template = PromptTemplate(
            """Du bist ein Experte für Streamworks XML-Konfigurationen und Enterprise-Systeme.

Konversationshistorie:
{conversation_context}

Aktuelle Benutzeranfrage: {original_query}

Aufgabe: Erweitere und präzisiere die Benutzeranfrage, um bessere Suchergebnisse zu erzielen.
Berücksichtige den Konversationskontext und füge relevante technische Begriffe hinzu.

Erweiterte Anfrage:"""
        )

        # HyDE Template für hypothetische Dokumente
        self.hyde_template = PromptTemplate(
            """Du bist ein Experte für Streamworks-Konfigurationen.

Benutzeranfrage: {query}

Erstelle ein hypothetisches Dokumentfragment, das eine ideale Antwort auf diese Frage enthalten würde.
Das Fragment sollte technische Details, XML-Beispiele und Konfigurationsparameter enthalten.

Hypothetisches Dokument:"""
        )

    async def initialize(self) -> bool:
        """Initialize Query Processor"""
        if self._initialized:
            return True

        try:
            logger.info("🚀 Initializing Query Processor...")

            # Validation
            if not self.llm_service:
                raise ValueError("LLM service required for query processing")

            if not self.embed_model:
                raise ValueError("Embedding model required for query processing")

            self._initialized = True
            logger.info("✅ Query Processor initialized successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize Query Processor: {str(e)}")
            raise e

    async def process_query(
        self,
        query_context: QueryContext,
        mode: RAGMode = RAGMode.ACCURATE
    ) -> Tuple[str, List[str], Dict[str, Any]]:
        """
        Process user query through enhancement pipeline

        Args:
            query_context: Context containing query and conversation history
            mode: Processing mode for different complexity levels

        Returns:
            Tuple of (enhanced_query, sub_queries, metadata)
        """
        if not await self.initialize():
            raise Exception("Failed to initialize Query Processor")

        start_time = time.time()

        try:
            logger.info(f"🔍 Processing query in {mode.value} mode: {query_context.original_query[:100]}...")

            # 1. Query Classification and Analysis
            query_analysis = await self._analyze_query(query_context.original_query)

            # 2. Context-aware Query Enhancement
            enhanced_query = await self._enhance_query_with_context(query_context)

            # 3. Generate sub-queries for complex questions (if needed)
            sub_queries = []
            if mode in [RAGMode.ACCURATE, RAGMode.COMPREHENSIVE]:
                sub_queries = await self._generate_sub_queries(enhanced_query, query_analysis)

            # 4. HyDE: Generate hypothetical documents for better retrieval
            hyde_queries = []
            if mode == RAGMode.COMPREHENSIVE:
                hyde_queries = await self._generate_hyde_queries(enhanced_query)
                sub_queries.extend(hyde_queries)

            processing_time = int((time.time() - start_time) * 1000)

            metadata = {
                "original_query": query_context.original_query,
                "enhanced_query": enhanced_query,
                "sub_queries_count": len(sub_queries),
                "hyde_queries_count": len(hyde_queries),
                "query_analysis": query_analysis,
                "processing_time_ms": processing_time,
                "mode": mode.value
            }

            logger.info(f"✅ Query processed: {len(sub_queries)} sub-queries generated in {processing_time}ms")

            return enhanced_query, sub_queries, metadata

        except Exception as e:
            logger.error(f"❌ Query processing failed: {str(e)}")
            # Return original query as fallback
            return query_context.original_query, [], {
                "error": str(e),
                "fallback": True,
                "original_query": query_context.original_query
            }

    async def _analyze_query(self, query: str) -> Dict[str, Any]:
        """
        Analyze query to determine complexity and type

        Returns:
            Dictionary with analysis results
        """
        try:
            # Basic analysis using heuristics
            analysis = {
                "length": len(query),
                "word_count": len(query.split()),
                "has_technical_terms": self._contains_technical_terms(query),
                "is_complex": len(query.split()) > 10 or "?" in query.count("?") > 1,
                "query_type": self._classify_query_type(query),
                "confidence": 0.8  # Base confidence
            }

            # Adjust confidence based on analysis
            if analysis["has_technical_terms"]:
                analysis["confidence"] += 0.1
            if analysis["is_complex"]:
                analysis["confidence"] -= 0.1

            return analysis

        except Exception as e:
            logger.warning(f"Query analysis failed: {str(e)}")
            return {
                "length": len(query),
                "word_count": len(query.split()),
                "has_technical_terms": False,
                "is_complex": False,
                "query_type": "general",
                "confidence": 0.5,
                "error": str(e)
            }

    async def _enhance_query_with_context(self, query_context: QueryContext) -> str:
        """
        Enhance query using conversation context
        """
        try:
            # Build conversation context string
            context_str = ""
            if query_context.conversation_context:
                context_messages = []
                for msg in query_context.conversation_context[-3:]:  # Last 3 messages
                    role = msg.get("role", "user")
                    content = msg.get("content", "")[:200]  # Limit length
                    context_messages.append(f"{role.title()}: {content}")
                context_str = "\n".join(context_messages)

            if not context_str:
                # No context, return original query with minor enhancement
                return self._add_technical_context(query_context.original_query)

            # Use LLM to enhance query with context
            enhanced_prompt = self.query_enhancement_template.format(
                conversation_context=context_str,
                original_query=query_context.original_query
            )

            response = await self.llm_service.acomplete(enhanced_prompt)
            enhanced_query = str(response).strip()

            # Fallback to original if enhancement fails
            if not enhanced_query or len(enhanced_query) < 5:
                enhanced_query = self._add_technical_context(query_context.original_query)

            logger.debug(f"Query enhanced: '{query_context.original_query}' → '{enhanced_query}'")
            return enhanced_query

        except Exception as e:
            logger.warning(f"Query enhancement failed: {str(e)}")
            return self._add_technical_context(query_context.original_query)

    async def _generate_sub_queries(self, enhanced_query: str, analysis: Dict[str, Any]) -> List[str]:
        """
        Generate sub-queries for complex questions
        """
        try:
            # Only generate sub-queries for complex queries
            if not analysis.get("is_complex", False):
                return []

            sub_query_prompt = f"""
Teile diese komplexe Frage in 2-3 spezifische Teilfragen auf, die einzeln beantwortet werden können:

Hauptfrage: {enhanced_query}

Teilfragen:
1."""

            response = await self.llm_service.acomplete(sub_query_prompt)
            response_text = str(response).strip()

            # Parse sub-queries from response
            sub_queries = []
            lines = response_text.split('\n')
            for line in lines:
                line = line.strip()
                if line and (line.startswith(('1.', '2.', '3.', '-', '•'))):
                    # Clean up the sub-query
                    sub_query = line.split('.', 1)[-1].strip() if '.' in line else line[1:].strip()
                    if len(sub_query) > 10:  # Valid sub-query
                        sub_queries.append(sub_query)

            # Limit to max 3 sub-queries
            return sub_queries[:3]

        except Exception as e:
            logger.warning(f"Sub-query generation failed: {str(e)}")
            return []

    async def _generate_hyde_queries(self, query: str) -> List[str]:
        """
        Generate HyDE (Hypothetical Document Embeddings) queries
        """
        try:
            hyde_prompt = self.hyde_template.format(query=query)

            response = await self.llm_service.acomplete(hyde_prompt)
            hyde_doc = str(response).strip()

            if len(hyde_doc) > 50:  # Valid hypothetical document
                return [hyde_doc]

            return []

        except Exception as e:
            logger.warning(f"HyDE generation failed: {str(e)}")
            return []

    def _contains_technical_terms(self, query: str) -> bool:
        """Check if query contains technical Streamworks terms"""
        technical_terms = [
            'xml', 'konfiguration', 'stream', 'job', 'scheduling',
            'parameter', 'property', 'template', 'connector',
            'database', 'sql', 'transformation', 'mapping'
        ]

        query_lower = query.lower()
        return any(term in query_lower for term in technical_terms)

    def _classify_query_type(self, query: str) -> str:
        """Classify the type of query"""
        query_lower = query.lower()

        if any(word in query_lower for word in ['wie', 'how', 'erstell', 'create', 'mach']):
            return 'how_to'
        elif any(word in query_lower for word in ['was', 'what', 'welch', 'which']):
            return 'definition'
        elif any(word in query_lower for word in ['warum', 'why', 'weshalb']):
            return 'explanation'
        elif any(word in query_lower for word in ['beispiel', 'example', 'zeig']):
            return 'example'
        else:
            return 'general'

    def _add_technical_context(self, query: str) -> str:
        """Add basic technical context to query if missing"""
        if not self._contains_technical_terms(query):
            return f"{query} (Streamworks-System Konfiguration)"
        return query


# Global instance
_query_processor = None

async def get_query_processor(llm_service=None, embed_model=None) -> QueryProcessor:
    """Get global Query Processor instance"""
    global _query_processor
    if _query_processor is None:
        _query_processor = QueryProcessor(llm_service, embed_model)
    return _query_processor