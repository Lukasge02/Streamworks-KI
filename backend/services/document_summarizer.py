"""
Document Summarization Service using Ollama - Qdrant Integration
Provides intelligent document summarization using local AI models with Qdrant vector store
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from services.ollama_service import ollama_service
from services.qdrant_vectorstore import get_qdrant_service
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.core import Document

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

            # Get document chunks from Qdrant vector store
            try:
                qdrant_service = await get_qdrant_service()
                chunks_data = await qdrant_service.get_document_chunks(
                    doc_id=document_id,
                    limit=20  # Limit to first 20 chunks for performance
                )

                if not chunks_data:
                    summary = "Keine Textinhalte verfügbar - Dokument wird möglicherweise noch verarbeitet."
                    key_points = []
                    await self._save_summary_to_db(db, document, summary, key_points)
                    return {
                        "summary": summary,
                        "key_points": key_points,
                        "status": "no_content",
                        "generated_at": datetime.utcnow().isoformat()
                    }

                # Combine chunk contents for summary generation
                content_parts = []
                for chunk_data in chunks_data:
                    content = chunk_data.get('content', '')
                    if content:
                        content_parts.append(content)

                combined_content = "\n\n".join(content_parts)

                logger.info(f"✅ Retrieved {len(chunks_data)} chunks from Qdrant for summary generation")

            except Exception as e:
                logger.error(f"Failed to retrieve chunks from Qdrant: {str(e)}")
                summary = "Zusammenfassung nicht verfügbar - Fehler beim Laden der Dokumentinhalte."
                key_points = []
                await self._save_summary_to_db(db, document, summary, key_points)
                return {
                    "summary": summary,
                    "key_points": key_points,
                    "status": "error",
                    "error": str(e),
                    "generated_at": datetime.utcnow().isoformat()
                }

            # Truncate content for faster processing
            max_chars = 4000  # Reduced for speed
            if len(combined_content) > max_chars:
                combined_content = combined_content[:max_chars] + "..."

            # Generate summary with Ollama
            summary, key_points = await self._generate_summary_with_ollama(
                combined_content, document.original_filename
            )

            # Cache summary in database
            await self._save_summary_to_db(db, document, summary, key_points)

            return {
                "summary": summary,
                "key_points": key_points,
                "status": "generated",
                "source": "qdrant",
                "chunks_processed": len(chunks_data),
                "generated_at": datetime.utcnow().isoformat(),
                "cached": False
            }

        except Exception as e:
            logger.error(f"Summary generation failed: {str(e)}")
            raise


    async def _generate_summary_with_ollama(
        self, content: str, filename: str
    ) -> tuple[str, List[str]]:
        """Generate summary and key points using Ollama"""

        prompt = f"""Du bist ein Experte für Dokumentenanalyse. Analysiere das folgende deutsche Dokument und erstelle eine präzise Zusammenfassung.

DOKUMENT: {filename}

INHALT:
{content}

Aufgabe:
- Erstelle eine kompakte, aber informative deutsche Zusammenfassung (2-3 Sätze)
- Identifiziere die 3-4 wichtigsten Kernaussagen
- Antworte NUR mit dem gewünschten JSON-Format, ohne zusätzliche Erklärungen

{{
    "summary": "Hier die kompakte Zusammenfassung des Dokumentinhalts...",
    "key_points": ["Erster wichtiger Punkt", "Zweiter wichtiger Punkt", "Dritter wichtiger Punkt"]
}}"""

        try:
            response = await self.ollama.generate(
                model=self.default_model,
                prompt=prompt,
                temperature=0.1  # Low temperature for consistent results
            )

            if not response:
                raise ValueError("Empty response from Ollama")

            logger.info(f"Raw Ollama response: {response[:500]}...")  # Log first 500 chars for debugging

            # Clean response - remove potential markdown formatting
            cleaned_response = response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]  # Remove ```json
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]  # Remove ```
            cleaned_response = cleaned_response.strip()

            # Parse JSON response
            import json
            try:
                result = json.loads(cleaned_response)
                summary = result.get("summary", "Zusammenfassung konnte nicht generiert werden.")
                key_points = result.get("key_points", [])

                # Ensure key_points is a list
                if not isinstance(key_points, list):
                    key_points = []

                # Filter out empty key points
                key_points = [point for point in key_points if point and point.strip()]

                logger.info(f"Successfully parsed summary: {summary[:100]}... with {len(key_points)} key points")

            except json.JSONDecodeError as json_error:
                logger.warning(f"JSON parsing failed: {json_error}. Response: {cleaned_response[:200]}...")

                # Improved fallback: try to extract content even from malformed responses
                summary = self._extract_summary_fallback(cleaned_response)
                key_points = self._extract_key_points_fallback(cleaned_response)

            return summary, key_points[:5]  # Limit to 5 key points

        except Exception as e:
            logger.error(f"Ollama generation failed: {str(e)}")
            return "Automatische Zusammenfassung nicht verfügbar.", []

    def _extract_summary_fallback(self, response: str) -> str:
        """Extract summary from malformed response"""
        try:
            # Look for "summary" key in the response
            if '"summary"' in response:
                start = response.find('"summary"')
                colon_pos = response.find(':', start)
                if colon_pos != -1:
                    # Find the start of the summary value
                    quote_start = response.find('"', colon_pos)
                    if quote_start != -1:
                        # Find the end quote
                        quote_end = response.find('"', quote_start + 1)
                        if quote_end != -1:
                            return response[quote_start + 1:quote_end]

            # Fallback: use first meaningful line
            lines = response.strip().split('\n')
            for line in lines:
                line = line.strip()
                if len(line) > 20 and not line.startswith('{') and not line.startswith('['):
                    return line

            return "Zusammenfassung konnte aus der Antwort nicht extrahiert werden."

        except:
            return "Zusammenfassung nicht verfügbar."

    def _extract_key_points_fallback(self, response: str) -> List[str]:
        """Extract key points from malformed response"""
        try:
            key_points = []

            # Look for "key_points" array in the response
            if '"key_points"' in response:
                start = response.find('"key_points"')
                bracket_start = response.find('[', start)
                if bracket_start != -1:
                    bracket_end = response.find(']', bracket_start)
                    if bracket_end != -1:
                        array_content = response[bracket_start + 1:bracket_end]
                        # Simple parsing of array elements
                        import re
                        matches = re.findall(r'"([^"]+)"', array_content)
                        key_points = matches

            # Fallback: look for bullet points or numbered lists
            if not key_points:
                lines = response.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                        key_points.append(line[1:].strip())
                    elif len(line) > 10 and (line[0].isdigit() and line[1] == '.'):
                        key_points.append(line[2:].strip())

            return key_points[:4]  # Limit to 4

        except:
            return []

    async def _save_summary_to_db(
        self, db: AsyncSession, document: Document, summary: str, key_points: List[str]
    ):
        """Save summary to database with fallback for missing fields"""
        try:
            # Try to save to AI summary fields if available
            if hasattr(document, 'ai_summary'):
                document.ai_summary = summary
                document.summary_key_points = key_points
                document.summary_generated_at = datetime.utcnow()
                await db.commit()
                logger.info(f"✅ Summary cached in database for document {document.id}")
            else:
                logger.warning("AI summary fields not available - summary not cached")
        except Exception as e:
            logger.warning(f"Failed to cache summary in database: {str(e)}")
            # Don't raise - summary generation succeeded, caching failed

    async def generate_bulk_summaries(
        self, document_ids: List[str], db: AsyncSession, concurrency: int = 3
    ) -> Dict[str, Dict[str, Any]]:
        """Generate summaries for multiple documents with concurrency control"""

        semaphore = asyncio.Semaphore(concurrency)

        async def generate_single(doc_id: str) -> tuple[str, Dict[str, Any]]:
            async with semaphore:
                try:
                    result = await self.generate_summary(doc_id, db, force_refresh=False)
                    return doc_id, result
                except Exception as e:
                    return doc_id, {"status": "error", "error": str(e)}

        # Execute in parallel with concurrency limit
        tasks = [generate_single(doc_id) for doc_id in document_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Format results
        summaries = {}
        for result in results:
            if isinstance(result, tuple):
                doc_id, summary_data = result
                summaries[doc_id] = summary_data
            else:
                # Handle exception
                summaries["unknown"] = {"status": "error", "error": str(result)}

        return summaries

# Global instance
document_summarizer = DocumentSummarizer()