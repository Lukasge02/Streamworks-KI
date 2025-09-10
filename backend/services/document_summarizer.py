"""
Document Summarization Service using Ollama
Provides intelligent document summarization using local AI models
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from services.ollama_service import ollama_service
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.core import Document, DocumentChunk

logger = logging.getLogger(__name__)

class DocumentSummarizer:
    """Service for generating intelligent document summaries using local AI"""
    
    def __init__(self):
        self.ollama = ollama_service
        self.default_model = "qwen2.5:7b"  # Fast and good quality model
        
    async def generate_summary(
        self, 
        document_id: str,
        db: AsyncSession,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Generate an intelligent summary of a document with database caching
        
        Args:
            document_id: ID of the document to summarize
            db: Database session
            force_refresh: Force regeneration even if cached summary exists
            
        Returns:
            Dictionary containing summary and metadata
        """
        try:
            # Get document
            result = await db.execute(
                select(Document).where(Document.id == document_id)
            )
            document = result.scalar_one_or_none()
            
            if not document:
                raise ValueError(f"Document {document_id} not found")
            
            # Check for cached summary (with fallback for schema compatibility)
            try:
                if (not force_refresh and 
                    hasattr(document, 'ai_summary') and document.ai_summary and 
                    hasattr(document, 'summary_key_points') and document.summary_key_points):
                    return {
                        "summary": document.ai_summary,
                        "key_points": document.summary_key_points,
                        "status": "cached",
                        "generated_at": document.summary_generated_at.isoformat() if document.summary_generated_at else None,
                        "cached": True
                    }
            except AttributeError:
                # Fallback if schema is not updated yet
                logger.warning("AI summary fields not available, proceeding without caching")
            
            # Get document chunks
            chunks_result = await db.execute(
                select(DocumentChunk)
                .where(DocumentChunk.document_id == document_id)
                .order_by(DocumentChunk.chunk_index)
                .limit(30)  # Reduced for faster processing
            )
            chunks = chunks_result.scalars().all()
            
            if not chunks:
                summary = "Keine Textinhalte verfügbar."
                key_points = []
                await self._save_summary_to_db(db, document, summary, key_points)
                return {
                    "summary": summary,
                    "key_points": key_points,
                    "status": "no_content",
                    "generated_at": datetime.utcnow().isoformat()
                }
            
            # Combine chunk contents (prioritize titles and headers)
            content_parts = []
            for chunk in chunks[:20]:  # Further reduced for speed
                if chunk.chunk_type in ['title', 'section_header']:
                    content_parts.append(f"## {chunk.content}")
                else:
                    content_parts.append(chunk.content)
            
            combined_content = "\n\n".join(content_parts)
            
            # Truncate content for faster processing
            max_chars = 4000  # Reduced for speed
            if len(combined_content) > max_chars:
                combined_content = combined_content[:max_chars] + "..."
            
            # Generate compact key points directly (no separate summary)
            key_points_prompt = f"""Extrahiere die 3 wichtigsten Kernaussagen aus diesem Dokument. Jede Aussage max. 15 Wörter, kompakt und prägnant:

{combined_content}

3 Kernaussagen:
1.
2. 
3."""

            key_points_response = await self.ollama.generate_completion(
                prompt=key_points_prompt,
                model=self.default_model,
                temperature=0.2,
                max_tokens=150  # Reduced for speed
            )
            
            # Parse key points from response
            key_points_text = key_points_response.get("response", "")
            key_points = []
            for line in key_points_text.split('\n'):
                clean_line = line.strip().lstrip('•-*123456789. ')
                if clean_line and len(clean_line) > 5:
                    key_points.append(clean_line)
                if len(key_points) >= 3:  # Limit to exactly 3 key points
                    break
            
            # Create summary from key points (more consistent)
            if key_points:
                summary = " • ".join(key_points)
            else:
                summary = "Zusammenfassung konnte nicht erstellt werden."
            
            # Save to database
            await self._save_summary_to_db(db, document, summary, key_points)
            
            return {
                "summary": summary,
                "key_points": key_points,
                "status": "success",
                "generated_at": datetime.utcnow().isoformat(),
                "cached": False
            }
            
        except Exception as e:
            logger.error(f"Error generating summary for document {document_id}: {str(e)}")
            return {
                "summary": "Zusammenfassung konnte nicht generiert werden.",
                "key_points": [],
                "status": "error",
                "error": str(e),
                "generated_at": datetime.utcnow().isoformat()
            }
    
    async def _save_summary_to_db(
        self, 
        db: AsyncSession, 
        document: Document, 
        summary: str, 
        key_points: List[str]
    ):
        """Save generated summary to database for caching"""
        try:
            # Check if schema supports caching
            if (hasattr(document, 'ai_summary') and 
                hasattr(document, 'summary_key_points') and 
                hasattr(document, 'summary_generated_at')):
                
                document.ai_summary = summary
                document.summary_key_points = key_points
                document.summary_generated_at = datetime.utcnow()
                
                await db.commit()
                logger.info(f"Saved summary to database for document {document.id}")
            else:
                logger.warning("AI summary caching not available - schema not updated")
        except Exception as e:
            logger.error(f"Failed to save summary to database: {str(e)}")
            await db.rollback()
    
    async def generate_chunk_summary(
        self,
        chunks: List[DocumentChunk],
        context: Optional[str] = None
    ) -> str:
        """
        Generate a summary for a specific set of chunks
        
        Args:
            chunks: List of document chunks to summarize
            context: Optional context about the document
            
        Returns:
            Summary text
        """
        try:
            if not chunks:
                return "Keine Inhalte zum Zusammenfassen."
            
            # Combine chunk contents
            combined = "\n".join([chunk.content for chunk in chunks[:10]])
            
            prompt = f"""Fasse den folgenden Textabschnitt kurz zusammen (max. 100 Wörter):

{combined[:2000]}

Zusammenfassung:"""

            response = await self.ollama.generate_completion(
                prompt=prompt,
                model=self.default_model,
                temperature=0.3,
                max_tokens=150
            )
            
            return response.get("response", "").strip()
            
        except Exception as e:
            logger.error(f"Error generating chunk summary: {str(e)}")
            return "Zusammenfassung nicht verfügbar."
    
    async def analyze_document_tone(
        self,
        document_id: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Analyze the tone and style of a document
        
        Args:
            document_id: ID of the document
            db: Database session
            
        Returns:
            Dictionary with tone analysis
        """
        try:
            # Get some chunks for analysis
            chunks_result = await db.execute(
                select(DocumentChunk)
                .where(DocumentChunk.document_id == document_id)
                .order_by(DocumentChunk.chunk_index)
                .limit(10)
            )
            chunks = chunks_result.scalars().all()
            
            if not chunks:
                return {"tone": "neutral", "formality": "unknown"}
            
            sample_text = "\n".join([c.content for c in chunks[:5]])[:2000]
            
            prompt = f"""Analysiere den Ton und Stil dieses Textes. Antworte im JSON-Format:

Text: {sample_text}

Gib zurück:
- tone: "professional" | "casual" | "academic" | "technical" | "creative"
- formality: "formal" | "informal" | "neutral"
- sentiment: "positive" | "negative" | "neutral"

JSON:"""

            response = await self.ollama.generate_completion(
                prompt=prompt,
                model=self.default_model,
                temperature=0.1,
                max_tokens=50
            )
            
            # Parse response
            import json
            try:
                result = json.loads(response.get("response", "{}"))
                return result
            except:
                return {
                    "tone": "professional",
                    "formality": "formal",
                    "sentiment": "neutral"
                }
                
        except Exception as e:
            logger.error(f"Error analyzing document tone: {str(e)}")
            return {
                "tone": "unknown",
                "formality": "unknown",
                "sentiment": "neutral"
            }

# Singleton instance
document_summarizer = DocumentSummarizer()