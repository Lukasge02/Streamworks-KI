"""
Q&A Pipeline Service for StreamWorks RAG MVP
Phase 3: Strukturierte RAG mit LangGraph, Confidence & Quellen-Zitaten
"""
import os
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json
import logging
import re
from dataclasses import dataclass

from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from services.langgraph_foundation import QAWorkflowState, get_langgraph_foundation
from services.vectorstore import VectorStoreService
from services.embeddings import EmbeddingService

logger = logging.getLogger(__name__)

# ===============================
# Q&A PIPELINE CONFIGURATION
# ===============================

@dataclass
class QAConfig:
    """Configuration for Q&A Pipeline"""
    confidence_threshold: float = 0.7
    top_k: int = 6
    max_sources: int = 6
    min_chunk_relevance: float = 0.5
    enable_reranking: bool = False
    
    # LLM settings
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.1
    max_tokens: int = 1500


# ===============================
# RAG PROMPT TEMPLATES
# ===============================

QA_SYSTEM_PROMPT = """Du bist ein Experte für StreamWorks Workload Automation von Arvato Systems.

**Deine Aufgabe:**
- Beantworte Fragen präzise basierend AUSSCHLIESSLICH auf den bereitgestellten Kontext-Dokumenten
- Zitiere IMMER die Quellen mit [Quelle: {doc_id}] format
- Sei ehrlich wenn der Kontext keine ausreichende Information enthält

**Antwortformat:**
1. Direkte, präzise Antwort auf die Frage
2. Quellenverweise in eckigen Klammern: [Quelle: {doc_id}]
3. Falls unvollständige Info: "Basierend auf den verfügbaren Dokumenten..."

**Wichtig:**
- Erfinde KEINE Informationen außerhalb des gegebenen Kontexts
- Halte Antworten fokussiert und relevant
- Bei technischen Details: Gib konkrete Schritte oder Konfigurationen an"""

QA_HUMAN_PROMPT = """**Frage:** {query}

**Verfügbare Kontext-Dokumente:**
{context}

**Antwort:"""

# Confidence assessment prompt
CONFIDENCE_PROMPT = """Bewerte die Qualität der folgenden Antwort auf einer Skala von 0.0 bis 1.0:

**Frage:** {query}
**Antwort:** {answer}
**Kontext-Dokumente:** {num_sources} Dokumente

Bewerte basierend auf:
- Relevanz zur Frage (0.4)
- Vollständigkeit der Antwort (0.3) 
- Qualität der Quellenverweise (0.3)

Antworte nur mit einem Dezimalwert zwischen 0.0 und 1.0."""


# ===============================
# Q&A PIPELINE SERVICE
# ===============================

class QAPipelineService:
    """
    LangGraph-based Q&A Pipeline für StreamWorks RAG
    Implementiert structured retrieval mit confidence scoring
    """
    
    def __init__(self, vectorstore: VectorStoreService, embeddings: EmbeddingService, config: QAConfig = None):
        self.vectorstore = vectorstore
        self.embeddings = embeddings
        self.config = config or QAConfig()
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=self.config.model_name,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )
        
        # Create prompts
        self.qa_prompt = ChatPromptTemplate.from_messages([
            ("system", QA_SYSTEM_PROMPT),
            ("human", QA_HUMAN_PROMPT)
        ])
        
        self.confidence_prompt = ChatPromptTemplate.from_messages([
            ("human", CONFIDENCE_PROMPT)
        ])
        
        # Compiled graph will be cached
        self._compiled_graph = None
        
        logger.info(f"QAPipelineService initialized with config: {self.config}")
    
    
    def _create_qa_graph(self) -> CompiledStateGraph:
        """
        Create the Q&A LangGraph workflow
        Nodes: retrieve → generate → confidence_gate → return_final
        """
        
        def retrieve_node(state: QAWorkflowState) -> QAWorkflowState:
            """Node 1: Retrieve relevant chunks from ChromaDB"""
            logger.info(f"🔍 Retrieving for query: {state['query']}")
            
            try:
                # Get query embedding
                query_embedding = self.embeddings.get_embedding(state['query'])
                
                # Search ChromaDB
                search_results = self.vectorstore.search(
                    query_embedding=query_embedding,
                    top_k=self.config.top_k,
                    filters=state.get('filters')
                )
                
                # Format retrieved chunks
                retrieved_chunks = []
                for result in search_results:
                    chunk = {
                        "id": result.get("id", "unknown"),
                        "text": result.get("document", ""),
                        "metadata": result.get("metadata", {}),
                        "distance": result.get("distance", 1.0),
                        "relevance_score": max(0.0, 1.0 - result.get("distance", 1.0))  # Convert distance to relevance
                    }
                    
                    # Filter by minimum relevance
                    if chunk["relevance_score"] >= self.config.min_chunk_relevance:
                        retrieved_chunks.append(chunk)
                
                logger.info(f"Retrieved {len(retrieved_chunks)} relevant chunks (filtered from {len(search_results)})")
                
                return {
                    **state,
                    "retrieved_chunks": retrieved_chunks,
                    "step": "retrieved",
                    "metadata": {
                        **state.get("metadata", {}),
                        "retrieval_time": datetime.now().isoformat(),
                        "chunks_found": len(retrieved_chunks),
                        "chunks_filtered": len(search_results) - len(retrieved_chunks)
                    }
                }
                
            except Exception as e:
                logger.error(f"Retrieval failed: {e}")
                return {
                    **state,
                    "step": "retrieval_error",
                    "error": f"Retrieval failed: {str(e)}",
                    "retrieved_chunks": []
                }
        
        
        def generate_node(state: QAWorkflowState) -> QAWorkflowState:
            """Node 2: Generate answer with source citations"""
            logger.info("🤖 Generating answer with LLM")
            
            try:
                chunks = state.get("retrieved_chunks", [])
                
                if not chunks:
                    return {
                        **state,
                        "step": "no_context",
                        "answer": "Entschuldigung, ich konnte keine relevanten Informationen in der Dokumentation finden, um Ihre Frage zu beantworten.",
                        "confidence_score": 0.0,
                        "sources": []
                    }
                
                # Format context for LLM
                context_parts = []
                source_map = {}
                
                for i, chunk in enumerate(chunks):
                    doc_id = chunk["metadata"].get("doc_id", f"doc_{i}")
                    source_map[doc_id] = chunk
                    
                    context_part = f"""Dokument {doc_id}:
{chunk['text']}
---"""
                    context_parts.append(context_part)
                
                context = "\n".join(context_parts)
                
                # Generate answer
                messages = self.qa_prompt.format_messages(
                    query=state['query'],
                    context=context
                )
                
                response = self.llm.invoke(messages)
                answer = response.content
                
                # Extract source citations from answer
                cited_sources = []
                source_pattern = r'\[Quelle:\s*([^\]]+)\]'
                citations = re.findall(source_pattern, answer)
                
                for citation in citations:
                    if citation in source_map:
                        chunk = source_map[citation]
                        cited_sources.append({
                            "id": citation,
                            "text": chunk["text"][:200] + "..." if len(chunk["text"]) > 200 else chunk["text"],
                            "metadata": chunk["metadata"],
                            "relevance_score": chunk["relevance_score"]
                        })
                
                # Limit sources to max_sources
                cited_sources = cited_sources[:self.config.max_sources]
                
                logger.info(f"Generated answer with {len(cited_sources)} cited sources")
                
                return {
                    **state,
                    "step": "generated",
                    "answer": answer,
                    "sources": cited_sources,
                    "metadata": {
                        **state.get("metadata", {}),
                        "generation_time": datetime.now().isoformat(),
                        "sources_cited": len(cited_sources),
                        "total_context_chars": len(context)
                    }
                }
                
            except Exception as e:
                logger.error(f"Generation failed: {e}")
                return {
                    **state,
                    "step": "generation_error",
                    "error": f"Generation failed: {str(e)}",
                    "answer": "Es ist ein Fehler bei der Antwortgenerierung aufgetreten.",
                    "sources": []
                }
        
        
        def confidence_gate_node(state: QAWorkflowState) -> QAWorkflowState:
            """Node 3: Assess confidence and filter low-quality responses"""
            logger.info("📊 Assessing answer confidence")
            
            try:
                answer = state.get("answer", "")
                sources = state.get("sources", [])
                
                if state.get("step") == "no_context":
                    # No context available - low confidence
                    confidence_score = 0.0
                elif state.get("error"):
                    # Error occurred - no confidence
                    confidence_score = 0.0
                else:
                    # Use LLM to assess confidence
                    confidence_messages = self.confidence_prompt.format_messages(
                        query=state['query'],
                        answer=answer,
                        num_sources=len(sources)
                    )
                    
                    confidence_response = self.llm.invoke(confidence_messages)
                    
                    # Extract confidence score
                    try:
                        confidence_score = float(confidence_response.content.strip())
                        confidence_score = max(0.0, min(1.0, confidence_score))  # Clamp to [0,1]
                    except ValueError:
                        logger.warning(f"Could not parse confidence score: {confidence_response.content}")
                        confidence_score = 0.5  # Default to medium confidence
                
                logger.info(f"Confidence score: {confidence_score} (threshold: {self.config.confidence_threshold})")
                
                # Apply confidence gate
                if confidence_score < self.config.confidence_threshold:
                    # Low confidence - provide fallback response
                    fallback_answer = ("Basierend auf den verfügbaren Dokumenten kann ich Ihre Frage nicht "
                                     "mit ausreichender Sicherheit beantworten. Möglicherweise fehlen relevante "
                                     "Informationen in der Dokumentation oder die Frage ist zu spezifisch.")
                    
                    return {
                        **state,
                        "step": "low_confidence",
                        "answer": fallback_answer,
                        "confidence_score": confidence_score,
                        "sources": [],  # No sources for fallback
                        "metadata": {
                            **state.get("metadata", {}),
                            "confidence_gate": "blocked",
                            "original_answer": answer,
                            "original_sources": sources
                        }
                    }
                else:
                    # High confidence - proceed with answer
                    return {
                        **state,
                        "step": "confidence_passed",
                        "confidence_score": confidence_score,
                        "metadata": {
                            **state.get("metadata", {}),
                            "confidence_gate": "passed"
                        }
                    }
                    
            except Exception as e:
                logger.error(f"Confidence assessment failed: {e}")
                return {
                    **state,
                    "step": "confidence_error",
                    "error": f"Confidence assessment failed: {str(e)}",
                    "confidence_score": 0.0
                }
        
        
        def return_final_node(state: QAWorkflowState) -> QAWorkflowState:
            """Node 4: Format final response"""
            logger.info("✅ Formatting final Q&A response")
            
            processing_time = datetime.now().isoformat()
            sources = state.get("sources", [])
            
            # Create final result
            final_result = {
                "answer": state.get("answer", ""),
                "sources": sources,
                "confidence_score": state.get("confidence_score", 0.0),
                "confidence_badge": _get_confidence_badge(state.get("confidence_score", 0.0)),
                "chunk_count": len(state.get("retrieved_chunks", [])),
                "processing_metadata": {
                    "retrieval_time": state.get("metadata", {}).get("retrieval_time"),
                    "generation_time": state.get("metadata", {}).get("generation_time"),
                    "completion_time": processing_time,
                    "chunks_found": state.get("metadata", {}).get("chunks_found", 0),
                    "sources_cited": len(sources),
                    "confidence_gate": state.get("metadata", {}).get("confidence_gate", "unknown")
                }
            }
            
            return {
                **state,
                "step": "completed",
                "result": final_result,
                "metadata": {
                    **state.get("metadata", {}),
                    "completion_time": processing_time
                }
            }
        
        # Build the graph
        graph_builder = StateGraph(QAWorkflowState)
        
        # Add nodes
        graph_builder.add_node("retrieve", retrieve_node)
        graph_builder.add_node("generate", generate_node)
        graph_builder.add_node("confidence_gate", confidence_gate_node)
        graph_builder.add_node("return_final", return_final_node)
        
        # Add edges
        graph_builder.add_edge(START, "retrieve")
        graph_builder.add_edge("retrieve", "generate")
        graph_builder.add_edge("generate", "confidence_gate")
        graph_builder.add_edge("confidence_gate", "return_final")
        graph_builder.add_edge("return_final", END)
        
        # Compile graph
        compiled_graph = graph_builder.compile()
        
        return compiled_graph
    
    
    async def run_qa_pipeline(self, query: str, filters: Dict[str, Any] = None, 
                             top_k: int = None, confidence_threshold: float = None,
                             thread_id: str = None) -> Dict[str, Any]:
        """
        Run the complete Q&A pipeline
        Returns structured response with answer, sources, and confidence
        """
        import uuid
        
        if thread_id is None:
            thread_id = str(uuid.uuid4())
        
        # Override config if provided
        if top_k is not None:
            self.config.top_k = top_k
        if confidence_threshold is not None:
            self.config.confidence_threshold = confidence_threshold
        
        # Get or create compiled graph
        if self._compiled_graph is None:
            self._compiled_graph = self._create_qa_graph()
        
        # Initial state
        initial_state: QAWorkflowState = {
            "request_id": str(uuid.uuid4()),
            "pipeline_type": "qa",
            "created_at": datetime.now().isoformat(),
            "user_id": None,
            "query": query,
            "filters": filters,
            "step": "init",
            "error": None,
            "result": None,
            "metadata": {
                "config": {
                    "top_k": self.config.top_k,
                    "confidence_threshold": self.config.confidence_threshold,
                    "model": self.config.model_name
                }
            },
            
            # QA-specific fields
            "retrieved_chunks": None,
            "top_k": self.config.top_k,
            "confidence_threshold": self.config.confidence_threshold,
            "answer": None,
            "sources": None,
            "confidence_score": None
        }
        
        try:
            logger.info(f"🚀 Starting Q&A pipeline for query: {query}")
            
            # Run the workflow
            config = {"configurable": {"thread_id": thread_id}}
            
            final_state = None
            async for state in self._compiled_graph.astream(initial_state, config=config):
                logger.debug(f"State update: {list(state.keys())}")
                final_state = state
            
            # Extract final result
            if final_state and "return_final" in final_state:
                result = final_state["return_final"].get("result", {})
                
                return {
                    "success": True,
                    "result": result,
                    "thread_id": thread_id,
                    "pipeline_metadata": final_state["return_final"].get("metadata", {})
                }
            else:
                return {
                    "success": False,
                    "error": "Pipeline did not complete successfully",
                    "thread_id": thread_id,
                    "final_state": final_state
                }
            
        except Exception as e:
            logger.error(f"Q&A pipeline failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "thread_id": thread_id
            }


def _get_confidence_badge(confidence: float) -> Dict[str, str]:
    """Get confidence badge for UI display"""
    if confidence >= 0.8:
        return {"level": "high", "text": "Hoch", "color": "green"}
    elif confidence >= 0.6:
        return {"level": "medium", "text": "Mittel", "color": "yellow"}
    else:
        return {"level": "low", "text": "Niedrig", "color": "red"}


# Global instance management
_qa_pipeline_instance = None

async def get_qa_pipeline() -> QAPipelineService:
    """Get or create global Q&A pipeline instance"""
    global _qa_pipeline_instance
    
    if _qa_pipeline_instance is None:
        # Import global instances from main.py
        import main
        
        # Initialize vectorstore if needed
        if main.vectorstore_service.collection is None:
            await main.vectorstore_service.initialize()
        
        _qa_pipeline_instance = QAPipelineService(
            vectorstore=main.vectorstore_service,
            embeddings=main.embedding_service
        )
    
    return _qa_pipeline_instance