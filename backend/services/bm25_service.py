"""
BM25 Service für Sparse/Keyword-basierte Retrieval
Implementiert Best Match 25 Algorithmus für präzise Keyword-Suche
"""

import asyncio
import json
import logging
import math
import pickle
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict, Counter
import re
from dataclasses import dataclass
from datetime import datetime

from config import settings

logger = logging.getLogger(__name__)

@dataclass
class BM25Document:
    """Represents a document in BM25 index"""
    doc_id: str
    chunk_id: str
    content: str
    terms: List[str]
    metadata: Dict[str, Any]
    term_frequencies: Dict[str, int]

@dataclass 
class BM25SearchResult:
    """BM25 search result with scoring"""
    chunk_id: str
    doc_id: str
    content: str
    metadata: Dict[str, Any]
    bm25_score: float
    matched_terms: List[str]
    term_highlights: Dict[str, List[int]]  # term -> [positions]

class BM25Service:
    """
    State-of-the-art BM25 implementation for keyword-based retrieval
    Features:
    - German + English tokenization
    - Intelligent preprocessing 
    - Optimized scoring with tuned parameters
    - Incremental index updates
    - Persistent caching
    """
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        """
        Initialize BM25 Service
        
        Args:
            k1: Term frequency saturation parameter (1.2-2.0)
            b: Length normalization parameter (0.0-1.0)
        """
        self.k1 = k1
        self.b = b
        
        # Document storage
        self.documents: Dict[str, BM25Document] = {}
        self.document_frequencies: Dict[str, int] = defaultdict(int)
        self.average_doc_length: float = 0.0
        self.total_documents: int = 0
        
        # Performance tracking
        self.search_stats = {
            'total_searches': 0,
            'avg_search_time': 0.0,
            'cache_hits': 0
        }
        
        # Cache and persistence
        self.index_path = Path(settings.SYSTEM_PATH / "bm25")
        self.index_path.mkdir(parents=True, exist_ok=True)
        self._index_dirty = False
        
        logger.info(f"🔍 BM25Service initialized - k1: {k1}, b: {b}")
    
    def _tokenize_and_preprocess(self, text: str) -> List[str]:
        """
        Advanced tokenization for German/English text
        
        Features:
        - Multi-language support
        - Technical term preservation 
        - Smart punctuation handling
        - Stopword filtering
        """
        if not text or not text.strip():
            return []
        
        # Convert to lowercase
        text = text.lower().strip()
        
        # Preserve technical terms and codes
        technical_pattern = r'\b(?:api|http[s]?|ssl|tls|json|xml|sql|v\d+\.\d+|\w+-\d+)\b'
        technical_terms = re.findall(technical_pattern, text, re.I)
        
        # Basic tokenization - split on whitespace and punctuation
        tokens = re.findall(r'\b\w+\b', text)
        
        # Add back technical terms
        tokens.extend(technical_terms)
        
        # Basic German/English stopwords
        stopwords = {
            'der', 'die', 'das', 'und', 'oder', 'ein', 'eine', 'ist', 'sind',
            'the', 'and', 'or', 'a', 'an', 'is', 'are', 'in', 'on', 'at', 'to',
            'for', 'of', 'with', 'by'
        }
        
        # Filter tokens
        filtered_tokens = []
        for token in tokens:
            if (len(token) >= 2 and 
                token not in stopwords and
                not token.isdigit()):
                filtered_tokens.append(token)
        
        return filtered_tokens
    
    async def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """
        Add documents to BM25 index
        
        Expected document format:
        {
            'id': 'chunk_id',
            'doc_id': 'document_id', 
            'content': 'text content',
            'metadata': {...}
        }
        """
        if not documents:
            logger.warning("No documents provided for BM25 indexing")
            return
        
        try:
            new_docs = []
            total_length = 0
            
            for doc_data in documents:
                chunk_id = str(doc_data.get('id', doc_data.get('chunk_id', '')))
                doc_id = str(doc_data.get('doc_id', ''))
                content = str(doc_data.get('content', ''))
                metadata = doc_data.get('metadata', {})
                
                if not chunk_id or not content:
                    logger.warning(f"Skipping document with missing id or content: {doc_data}")
                    continue
                
                # Tokenize and preprocess
                terms = self._tokenize_and_preprocess(content)
                if not terms:
                    logger.debug(f"Document {chunk_id} tokenized to empty - skipping")
                    continue
                
                # Calculate term frequencies
                term_frequencies = Counter(terms)
                
                # Create BM25 document
                bm25_doc = BM25Document(
                    doc_id=doc_id,
                    chunk_id=chunk_id,
                    content=content,
                    terms=terms,
                    metadata=metadata,
                    term_frequencies=term_frequencies
                )
                
                # Update index
                if chunk_id in self.documents:
                    # Remove old document from frequency counts
                    old_doc = self.documents[chunk_id]
                    for term in set(old_doc.term_frequencies.keys()):
                        self.document_frequencies[term] -= 1
                        if self.document_frequencies[term] <= 0:
                            del self.document_frequencies[term]
                else:
                    self.total_documents += 1
                
                # Add new document
                self.documents[chunk_id] = bm25_doc
                new_docs.append(bm25_doc)
                total_length += len(terms)
                
                # Update document frequencies
                for term in set(term_frequencies.keys()):
                    self.document_frequencies[term] += 1
            
            # Update average document length
            if self.total_documents > 0:
                all_lengths = sum(len(doc.terms) for doc in self.documents.values())
                self.average_doc_length = all_lengths / self.total_documents
            
            self._index_dirty = True
            logger.info(f"✅ Added {len(new_docs)} documents. Total: {self.total_documents}, Avg length: {self.average_doc_length:.1f}")
            
        except Exception as e:
            logger.error(f"Failed to add documents to BM25 index: {str(e)}")
            raise
    
    async def search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        min_score: float = 0.1
    ) -> List[BM25SearchResult]:
        """
        Search documents using BM25 algorithm
        
        Args:
            query: Search query
            top_k: Number of results to return
            filters: Optional metadata filters
            min_score: Minimum BM25 score threshold
            
        Returns:
            List of BM25SearchResult objects
        """
        try:
            if not self.documents:
                logger.warning("BM25 index is empty")
                return []
            
            # Tokenize query
            query_terms = self._tokenize_and_preprocess(query)
            if not query_terms:
                logger.warning(f"Query tokenized to empty: {query}")
                return []
            
            logger.debug(f"Query terms: {query_terms}")
            
            # Calculate BM25 scores for all documents
            scores = []
            
            for chunk_id, document in self.documents.items():
                # Apply filters if provided
                if filters and not self._document_matches_filters(document, filters):
                    continue
                
                # Calculate BM25 score
                score, matched_terms, highlights = self._calculate_bm25_score(
                    query_terms, document
                )
                
                if score >= min_score and matched_terms:
                    scores.append((
                        score,
                        BM25SearchResult(
                            chunk_id=chunk_id,
                            doc_id=document.doc_id,
                            content=document.content,
                            metadata=document.metadata,
                            bm25_score=score,
                            matched_terms=matched_terms,
                            term_highlights=highlights
                        )
                    ))
            
            # Sort by score (descending) and return top_k
            scores.sort(key=lambda x: x[0], reverse=True)
            results = [result for _, result in scores[:top_k]]
            
            logger.info(f"BM25 search: '{query}' → {len(results)} results (from {len(scores)} candidates)")
            return results
            
        except Exception as e:
            logger.error(f"BM25 search failed: {str(e)}")
            return []
    
    def _calculate_bm25_score(
        self, 
        query_terms: List[str], 
        document: BM25Document
    ) -> tuple:
        """
        Calculate BM25 score for document given query terms
        
        Returns:
            (score, matched_terms, term_highlights)
        """
        score = 0.0
        matched_terms = []
        highlights = {}
        
        doc_length = len(document.terms)
        
        for term in query_terms:
            # Get term frequency in document
            tf = document.term_frequencies.get(term, 0)
            
            if tf > 0:
                matched_terms.append(term)
                
                # Find term positions for highlighting
                positions = [i for i, t in enumerate(document.terms) if t == term]
                highlights[term] = positions
                
                # Get document frequency
                df = self.document_frequencies.get(term, 0)
                
                if df > 0:
                    # Calculate IDF
                    idf = math.log((self.total_documents - df + 0.5) / (df + 0.5))
                    
                    # Calculate BM25 component
                    numerator = tf * (self.k1 + 1)
                    denominator = tf + self.k1 * (1 - self.b + self.b * (doc_length / self.average_doc_length))
                    
                    term_score = idf * (numerator / denominator)
                    score += term_score
        
        return score, matched_terms, highlights
    
    def _document_matches_filters(self, document: BM25Document, filters: Dict[str, Any]) -> bool:
        """Check if document matches metadata filters"""
        for key, value in filters.items():
            if key == 'doc_id':
                if document.doc_id != value:
                    return False
            elif key in document.metadata:
                if document.metadata[key] != value:
                    return False
        return True
    
    async def save_index(self) -> None:
        """Persist BM25 index to disk"""
        if not self._index_dirty:
            return
            
        try:
            index_data = {
                'documents': self.documents,
                'document_frequencies': dict(self.document_frequencies),
                'average_doc_length': self.average_doc_length,
                'total_documents': self.total_documents,
                'timestamp': datetime.utcnow().isoformat(),
                'parameters': {'k1': self.k1, 'b': self.b}
            }
            
            index_file = self.index_path / 'bm25_index.pkl'
            with open(index_file, 'wb') as f:
                pickle.dump(index_data, f)
            
            self._index_dirty = False
            logger.info(f"💾 BM25 index saved: {self.total_documents} documents")
            
        except Exception as e:
            logger.error(f"Failed to save BM25 index: {str(e)}")
    
    async def load_index(self) -> bool:
        """Load BM25 index from disk"""
        try:
            index_file = self.index_path / 'bm25_index.pkl'
            if not index_file.exists():
                logger.info("No existing BM25 index found")
                return False
            
            with open(index_file, 'rb') as f:
                index_data = pickle.load(f)
            
            self.documents = index_data['documents']
            self.document_frequencies = defaultdict(int, index_data['document_frequencies'])
            self.average_doc_length = index_data['average_doc_length']
            self.total_documents = index_data['total_documents']
            
            # Check if parameters match
            params = index_data.get('parameters', {})
            if params.get('k1') != self.k1 or params.get('b') != self.b:
                logger.warning(f"BM25 parameters changed - index may need rebuilding")
            
            self._index_dirty = False
            logger.info(f"📂 BM25 index loaded: {self.total_documents} documents, avg_len={self.average_doc_length:.1f}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load BM25 index: {str(e)}")
            return False
    
    async def get_index_stats(self) -> Dict[str, Any]:
        """Get BM25 index statistics"""
        vocab_size = len(self.document_frequencies)
        
        # Find most frequent terms
        top_terms = sorted(
            self.document_frequencies.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        return {
            'total_documents': self.total_documents,
            'vocabulary_size': vocab_size,
            'average_doc_length': round(self.average_doc_length, 2),
            'parameters': {'k1': self.k1, 'b': self.b},
            'most_frequent_terms': top_terms,
            'index_dirty': self._index_dirty
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance statistics for monitoring"""
        return {
            'total_searches': self.search_stats['total_searches'],
            'avg_search_time': self.search_stats['avg_search_time'],
            'cache_hits': self.search_stats['cache_hits'],
            'total_documents': self.total_documents,
            'vocabulary_size': len(self.document_frequencies)
        }
    
    async def remove_document(self, chunk_id: str) -> bool:
        """Remove document from index"""
        if chunk_id not in self.documents:
            return False
        
        document = self.documents[chunk_id]
        
        # Update document frequencies
        for term in set(document.term_frequencies.keys()):
            self.document_frequencies[term] -= 1
            if self.document_frequencies[term] <= 0:
                del self.document_frequencies[term]
        
        # Remove document
        del self.documents[chunk_id]
        self.total_documents -= 1
        
        # Recalculate average length
        if self.total_documents > 0:
            all_lengths = sum(len(doc.terms) for doc in self.documents.values())
            self.average_doc_length = all_lengths / self.total_documents
        else:
            self.average_doc_length = 0.0
        
        self._index_dirty = True
        logger.info(f"Removed document {chunk_id} from BM25 index")
        return True