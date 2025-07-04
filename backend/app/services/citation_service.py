"""
Citation Service for Multi-Source Citation Management
Handles source attribution, relevance ranking, and citation formatting
"""
import logging
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.database import TrainingFile
from app.models.schemas import Citation, CitationSummary, SourceType, DocumentType
from langchain.schema import Document

logger = logging.getLogger(__name__)


class CitationService:
    """Service for managing citations and source attribution"""
    
    def __init__(self, db: AsyncSession = None):
        self.db = db
        self.source_type_mapping = {
            "faq": SourceType.FAQ,  # Check FAQ first before streamworks
            "streamworks_": SourceType.STREAMWORKS,
            "training_data": SourceType.DOCUMENTATION,
            "batch": SourceType.STREAMWORKS,
            "powershell": SourceType.STREAMWORKS,
            "csv": SourceType.STREAMWORKS,
        }
        
        self.document_type_mapping = {
            "faq": DocumentType.FAQ,
            "anleitung": DocumentType.GUIDE,
            "tipps": DocumentType.BEST_PRACTICES,
            "hilfe": DocumentType.TROUBLESHOOTING,
            "training": DocumentType.TUTORIAL,
            "template": DocumentType.TEMPLATE,
        }
        
        logger.info("🔗 Citation Service initialized")
    
    def _determine_source_type(self, filename: str) -> SourceType:
        """Determine source type from filename"""
        filename_lower = filename.lower()
        
        for keyword, source_type in self.source_type_mapping.items():
            if keyword in filename_lower:
                return source_type
        
        return SourceType.DOCUMENTATION
    
    def _determine_document_type(self, filename: str, content: str = "") -> DocumentType:
        """Determine document type from filename and content"""
        filename_lower = filename.lower()
        content_lower = content.lower()
        
        # Check filename patterns
        for keyword, doc_type in self.document_type_mapping.items():
            if keyword in filename_lower:
                return doc_type
        
        # Check content patterns
        if "f:" in content_lower and "a:" in content_lower:
            return DocumentType.FAQ
        elif "schritt" in content_lower or "anleitung" in content_lower:
            return DocumentType.GUIDE
        elif "beispiel" in content_lower or "template" in content_lower:
            return DocumentType.TEMPLATE
        elif "fehler" in content_lower or "problem" in content_lower:
            return DocumentType.TROUBLESHOOTING
        
        return DocumentType.GUIDE
    
    def _extract_source_title(self, filename: str, content: str = "") -> str:
        """Extract human-readable title from filename or content"""
        # Try to extract title from content first
        lines = content.split('\n')[:5]  # First 5 lines
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and len(line) > 10:
                # Clean up the line
                title = re.sub(r'^[^\w]*', '', line)
                if len(title) > 5:
                    return title[:100]  # Limit length
        
        # Fallback to filename cleanup
        title = filename.replace('.txt', '').replace('.md', '')
        title = re.sub(r'[_-]', ' ', title)
        title = ' '.join(word.capitalize() for word in title.split())
        
        return title
    
    def _calculate_relevance_score(self, doc: Document, query: str) -> float:
        """Calculate relevance score based on content similarity"""
        if not hasattr(doc, 'metadata') or 'score' not in doc.metadata:
            # Simple word overlap scoring as fallback
            query_words = set(query.lower().split())
            content_words = set(doc.page_content.lower().split())
            
            if not query_words:
                return 0.0
            
            overlap = len(query_words.intersection(content_words))
            return min(overlap / len(query_words), 1.0)
        
        # Use ChromaDB similarity score if available
        return min(doc.metadata.get('score', 0.0), 1.0)
    
    async def create_citations_from_documents(
        self, 
        documents: List[Document], 
        query: str = ""
    ) -> List[Citation]:
        """Create citation objects from retrieved documents"""
        citations = []
        
        for doc in documents:
            try:
                # Extract metadata
                metadata = doc.metadata if hasattr(doc, 'metadata') else {}
                filename = metadata.get('source', 'unknown_source.txt')
                
                # Determine source and document types
                source_type = self._determine_source_type(filename)
                document_type = self._determine_document_type(filename, doc.page_content)
                source_title = self._extract_source_title(filename, doc.page_content)
                
                # Calculate relevance
                relevance_score = self._calculate_relevance_score(doc, query)
                
                # Create citation
                citation = Citation(
                    source_type=source_type,
                    source_title=source_title,
                    document_type=document_type,
                    filename=filename,
                    chunk_id=metadata.get('chunk_id'),
                    relevance_score=relevance_score,
                    page_content=doc.page_content[:500],  # Limit content length
                    source_url=metadata.get('source_url'),
                    author=metadata.get('author'),
                    version=metadata.get('version'),
                    last_modified=metadata.get('last_modified'),
                    tags=metadata.get('tags', [])
                )
                
                citations.append(citation)
                
            except Exception as e:
                logger.warning(f"⚠️ Failed to create citation for document: {e}")
                continue
        
        # Sort by relevance score (highest first)
        citations.sort(key=lambda x: x.relevance_score, reverse=True)
        
        logger.info(f"🔗 Created {len(citations)} citations")
        return citations
    
    def create_citation_summary(self, citations: List[Citation]) -> CitationSummary:
        """Create a summary of citations"""
        if not citations:
            return CitationSummary(
                total_citations=0,
                source_breakdown={},
                highest_relevance=0.0,
                coverage_score=0.0
            )
        
        # Count by source type
        source_breakdown = {}
        for citation in citations:
            source_type = citation.source_type.value
            source_breakdown[source_type] = source_breakdown.get(source_type, 0) + 1
        
        # Calculate metrics
        highest_relevance = max(c.relevance_score for c in citations)
        avg_relevance = sum(c.relevance_score for c in citations) / len(citations)
        
        # Coverage score: diversity of sources + average relevance
        source_diversity = len(source_breakdown) / len(SourceType)
        coverage_score = (source_diversity * 0.3 + avg_relevance * 0.7)
        
        return CitationSummary(
            total_citations=len(citations),
            source_breakdown=source_breakdown,
            highest_relevance=highest_relevance,
            coverage_score=min(coverage_score, 1.0)
        )
    
    def format_citations_for_response(self, citations: List[Citation], max_citations: int = 3) -> str:
        """Format citations for inclusion in response text"""
        if not citations:
            return ""
        
        # Take top citations
        top_citations = citations[:max_citations]
        
        citation_text = "\n\n**Quellen:**\n"
        for i, citation in enumerate(top_citations, 1):
            citation_text += f"{i}. **{citation.source_title}** ({citation.source_type.value}"
            if citation.document_type:
                citation_text += f" - {citation.document_type.value}"
            if citation.relevance_score:
                citation_text += f", Relevanz: {citation.relevance_score:.1%}"
            citation_text += ")\n"
        
        return citation_text
    
    async def get_source_metadata(self, filename: str) -> Optional[Dict[str, Any]]:
        """Get additional metadata for a source file from database"""
        if not self.db:
            return None
        
        try:
            result = await self.db.execute(
                select(TrainingFile).where(TrainingFile.filename == filename)
            )
            training_file = result.scalar_one_or_none()
            
            if training_file:
                return {
                    'source_type': training_file.source_type,
                    'source_title': training_file.source_title,
                    'document_type': training_file.document_type,
                    'author': training_file.author,
                    'version': training_file.version,
                    'last_modified': training_file.last_modified,
                    'priority': training_file.priority,
                    'tags': training_file.tags
                }
        except Exception as e:
            logger.warning(f"⚠️ Failed to get source metadata for {filename}: {e}")
        
        return None
    
    def enhance_documents_with_metadata(self, documents: List[Document]) -> List[Document]:
        """Enhance documents with citation metadata"""
        enhanced_docs = []
        
        for doc in documents:
            # Copy the document
            enhanced_doc = Document(
                page_content=doc.page_content,
                metadata=doc.metadata.copy() if hasattr(doc, 'metadata') else {}
            )
            
            # Add citation metadata
            filename = enhanced_doc.metadata.get('source', '')
            enhanced_doc.metadata.update({
                'citation_source_type': self._determine_source_type(filename).value,
                'citation_document_type': self._determine_document_type(filename, doc.page_content).value,
                'citation_title': self._extract_source_title(filename, doc.page_content)
            })
            
            enhanced_docs.append(enhanced_doc)
        
        return enhanced_docs


# Global instance
citation_service = CitationService()