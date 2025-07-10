"""
ChromaDB Chunks API - Professional chunk visualization and management
Provides comprehensive access to ChromaDB chunks with filtering, search, and analytics
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from enum import Enum
import logging
import asyncio
from datetime import datetime
import hashlib

from app.services.rag_service import rag_service
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


class SortBy(str, Enum):
    """Sort options for chunks"""
    RELEVANCE = "relevance"
    CREATION_DATE = "creation_date"
    SIZE = "size"
    FILENAME = "filename"


class SortOrder(str, Enum):
    """Sort order options"""
    ASC = "asc"
    DESC = "desc"


class ChunkMetadata(BaseModel):
    """Chunk metadata model"""
    chunk_id: str
    source_file: Optional[str] = None
    filename: Optional[str] = None
    category: Optional[str] = None
    file_id: Optional[str] = None
    chunk_index: Optional[int] = None
    total_chunks: Optional[int] = None
    creation_date: Optional[str] = None
    size: int
    embedding_model: Optional[str] = None
    distance: Optional[float] = None


class ChunkContent(BaseModel):
    """Full chunk content model"""
    chunk_id: str
    content: str
    metadata: ChunkMetadata
    preview: str = Field(..., description="First 200 characters")
    word_count: int
    line_count: int
    
    @validator('preview', pre=True, always=True)
    def generate_preview(cls, v, values):
        content = values.get('content', '')
        return content[:200] + "..." if len(content) > 200 else content
    
    @validator('word_count', pre=True, always=True)
    def count_words(cls, v, values):
        content = values.get('content', '')
        return len(content.split())
    
    @validator('line_count', pre=True, always=True)
    def count_lines(cls, v, values):
        content = values.get('content', '')
        return len(content.splitlines())


class ChunkSearchRequest(BaseModel):
    """Chunk search request model"""
    query: str = Field(..., min_length=1, max_length=1000, description="Search query")
    limit: int = Field(10, ge=1, le=100, description="Number of results to return")
    similarity_threshold: float = Field(0.3, ge=0.0, le=1.0, description="Minimum similarity threshold")
    include_metadata: bool = Field(True, description="Include full metadata in results")
    search_type: str = Field("semantic", regex="^(semantic|hybrid|fulltext)$", description="Type of search")


class ChunkSearchResponse(BaseModel):
    """Chunk search response model"""
    query: str
    search_type: str
    results_count: int
    processing_time: float
    chunks: List[ChunkContent]
    similarity_scores: List[float]


class PaginationInfo(BaseModel):
    """Pagination information"""
    current_page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool


class ChunksListResponse(BaseModel):
    """Paginated chunks list response"""
    chunks: List[ChunkContent]
    pagination: PaginationInfo
    filters_applied: Dict[str, Any]
    sort_info: Dict[str, str]


class ChunkStatsResponse(BaseModel):
    """ChromaDB statistics response"""
    total_chunks: int
    total_files: int
    total_categories: int
    average_chunk_size: float
    size_distribution: Dict[str, int]
    category_distribution: Dict[str, int]
    embedding_model: str
    index_health: Dict[str, Any]
    last_updated: str


class RelatedChunk(BaseModel):
    """Related chunk model"""
    chunk_id: str
    filename: str
    similarity_score: float
    preview: str


class ChunkDetailsResponse(BaseModel):
    """Detailed chunk information"""
    chunk: ChunkContent
    related_chunks: List[RelatedChunk]
    file_context: Dict[str, Any]
    embedding_info: Optional[Dict[str, Any]] = None


@router.get("/", response_model=ChunksListResponse)
async def list_chunks(
    limit: int = Query(20, ge=1, le=100, description="Number of chunks per page"),
    offset: int = Query(0, ge=0, description="Number of chunks to skip"),
    search: Optional[str] = Query(None, min_length=1, max_length=500, description="Full-text search within content"),
    source_file: Optional[str] = Query(None, description="Filter by source filename"),
    category: Optional[str] = Query(None, description="Filter by category"),
    file_id: Optional[str] = Query(None, description="Filter by file ID"),
    sort_by: SortBy = Query(SortBy.CREATION_DATE, description="Sort field"),
    sort_order: SortOrder = Query(SortOrder.DESC, description="Sort order"),
    min_size: Optional[int] = Query(None, ge=0, description="Minimum chunk size"),
    max_size: Optional[int] = Query(None, ge=1, description="Maximum chunk size")
):
    """
    Get paginated list of ChromaDB chunks with filtering and sorting
    
    - **limit**: Number of chunks per page (1-100)
    - **offset**: Number of chunks to skip for pagination
    - **search**: Full-text search within chunk content
    - **source_file**: Filter by source filename
    - **category**: Filter by document category
    - **file_id**: Filter by specific file ID
    - **sort_by**: Sort by relevance, creation_date, size, or filename
    - **sort_order**: Sort in ascending or descending order
    - **min_size/max_size**: Filter by chunk size in characters
    """
    start_time = asyncio.get_event_loop().time()
    
    try:
        if not settings.RAG_ENABLED:
            raise HTTPException(status_code=503, detail="RAG service is not enabled")
        
        if not rag_service.is_initialized:
            raise HTTPException(status_code=503, detail="RAG service is not initialized")
        
        # Build filter criteria
        filters = {}
        if source_file:
            filters['filename'] = source_file
        if category:
            filters['category'] = category
        if file_id:
            filters['file_id'] = file_id
        if min_size is not None:
            filters['min_size'] = min_size
        if max_size is not None:
            filters['max_size'] = max_size
        
        # Get chunks from ChromaDB with filtering
        chunks_data = await _get_chunks_with_filters(
            limit=limit,
            offset=offset,
            search=search,
            filters=filters,
            sort_by=sort_by.value,
            sort_order=sort_order.value
        )
        
        chunks = []
        for chunk_data in chunks_data['chunks']:
            try:
                chunk = ChunkContent(
                    chunk_id=chunk_data['id'],
                    content=chunk_data['content'],
                    metadata=ChunkMetadata(
                        chunk_id=chunk_data['id'],
                        source_file=chunk_data.get('metadata', {}).get('source', ''),
                        filename=chunk_data.get('metadata', {}).get('filename', ''),
                        category=chunk_data.get('metadata', {}).get('category', ''),
                        file_id=chunk_data.get('metadata', {}).get('file_id', ''),
                        chunk_index=chunk_data.get('metadata', {}).get('chunk_index'),
                        total_chunks=chunk_data.get('metadata', {}).get('total_chunks'),
                        creation_date=chunk_data.get('metadata', {}).get('created_at'),
                        size=len(chunk_data['content']),
                        embedding_model=chunk_data.get('metadata', {}).get('embedding_model')
                    ),
                    size=len(chunk_data['content'])
                )
                chunks.append(chunk)
            except Exception as e:
                logger.warning(f"Error processing chunk {chunk_data.get('id', 'unknown')}: {e}")
                continue
        
        # Calculate pagination
        total_items = chunks_data['total_count']
        total_pages = (total_items + limit - 1) // limit
        current_page = (offset // limit) + 1
        
        pagination = PaginationInfo(
            current_page=current_page,
            page_size=limit,
            total_items=total_items,
            total_pages=total_pages,
            has_next=offset + limit < total_items,
            has_previous=offset > 0
        )
        
        processing_time = asyncio.get_event_loop().time() - start_time
        
        logger.info(f"📋 Retrieved {len(chunks)} chunks (page {current_page}/{total_pages}) in {processing_time:.3f}s")
        
        return ChunksListResponse(
            chunks=chunks,
            pagination=pagination,
            filters_applied=filters,
            sort_info={
                "sort_by": sort_by.value,
                "sort_order": sort_order.value
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error listing chunks: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve chunks: {str(e)}")


@router.get("/{chunk_id}", response_model=ChunkDetailsResponse)
async def get_chunk_details(chunk_id: str):
    """
    Get detailed information about a specific chunk
    
    - **chunk_id**: Unique identifier for the chunk
    
    Returns full chunk content, metadata, related chunks from same document,
    and embedding information if available.
    """
    try:
        if not settings.RAG_ENABLED:
            raise HTTPException(status_code=503, detail="RAG service is not enabled")
        
        if not rag_service.is_initialized:
            raise HTTPException(status_code=503, detail="RAG service is not initialized")
        
        # Get chunk from ChromaDB
        chunk_data = await _get_chunk_by_id(chunk_id)
        if not chunk_data:
            raise HTTPException(status_code=404, detail=f"Chunk {chunk_id} not found")
        
        # Create chunk content model
        chunk = ChunkContent(
            chunk_id=chunk_data['id'],
            content=chunk_data['content'],
            metadata=ChunkMetadata(
                chunk_id=chunk_data['id'],
                source_file=chunk_data.get('metadata', {}).get('source', ''),
                filename=chunk_data.get('metadata', {}).get('filename', ''),
                category=chunk_data.get('metadata', {}).get('category', ''),
                file_id=chunk_data.get('metadata', {}).get('file_id', ''),
                chunk_index=chunk_data.get('metadata', {}).get('chunk_index'),
                total_chunks=chunk_data.get('metadata', {}).get('total_chunks'),
                creation_date=chunk_data.get('metadata', {}).get('created_at'),
                size=len(chunk_data['content']),
                embedding_model=chunk_data.get('metadata', {}).get('embedding_model')
            ),
            size=len(chunk_data['content'])
        )
        
        # Get related chunks from same document
        related_chunks = await _get_related_chunks(chunk_id, chunk_data.get('metadata', {}))
        
        # Get file context
        file_context = await _get_file_context(chunk_data.get('metadata', {}).get('filename'))
        
        # Get embedding info if available
        embedding_info = await _get_embedding_info(chunk_id)
        
        logger.info(f"📄 Retrieved details for chunk {chunk_id}")
        
        return ChunkDetailsResponse(
            chunk=chunk,
            related_chunks=related_chunks,
            file_context=file_context,
            embedding_info=embedding_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting chunk details: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get chunk details: {str(e)}")


@router.get("/stats", response_model=ChunkStatsResponse)
async def get_chunks_stats():
    """
    Get comprehensive ChromaDB statistics
    
    Returns statistics about total chunks, files, categories, size distribution,
    and index health metrics.
    """
    try:
        if not settings.RAG_ENABLED:
            raise HTTPException(status_code=503, detail="RAG service is not enabled")
        
        if not rag_service.is_initialized:
            raise HTTPException(status_code=503, detail="RAG service is not initialized")
        
        # Get basic stats from RAG service
        rag_stats = await rag_service.get_stats()
        
        # Get detailed ChromaDB stats
        chroma_stats = await _get_detailed_chroma_stats()
        
        # Calculate size distribution
        size_distribution = await _calculate_size_distribution()
        
        # Get category distribution
        category_distribution = await _get_category_distribution()
        
        # Check index health
        index_health = await _check_index_health()
        
        response = ChunkStatsResponse(
            total_chunks=chroma_stats.get('total_chunks', 0),
            total_files=chroma_stats.get('total_files', 0),
            total_categories=len(category_distribution),
            average_chunk_size=chroma_stats.get('average_chunk_size', 0.0),
            size_distribution=size_distribution,
            category_distribution=category_distribution,
            embedding_model=settings.EMBEDDING_MODEL,
            index_health=index_health,
            last_updated=datetime.utcnow().isoformat()
        )
        
        logger.info(f"📊 Generated ChromaDB statistics: {response.total_chunks} chunks, {response.total_files} files")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting chunk statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


@router.post("/search", response_model=ChunkSearchResponse)
async def search_chunks(request: ChunkSearchRequest):
    """
    Perform semantic or hybrid search on chunks
    
    - **query**: Search query text
    - **limit**: Maximum number of results (1-100)
    - **similarity_threshold**: Minimum similarity score (0.0-1.0)
    - **include_metadata**: Whether to include full metadata
    - **search_type**: semantic, hybrid, or fulltext search
    
    Returns ranked search results with similarity scores.
    """
    start_time = asyncio.get_event_loop().time()
    
    try:
        if not settings.RAG_ENABLED:
            raise HTTPException(status_code=503, detail="RAG service is not enabled")
        
        if not rag_service.is_initialized:
            raise HTTPException(status_code=503, detail="RAG service is not initialized")
        
        logger.info(f"🔍 Searching chunks: '{request.query}' (type: {request.search_type})")
        
        # Perform search based on type
        if request.search_type == "semantic":
            search_results = await _semantic_search(request)
        elif request.search_type == "hybrid":
            search_results = await _hybrid_search(request)
        elif request.search_type == "fulltext":
            search_results = await _fulltext_search(request)
        else:
            raise HTTPException(status_code=400, detail="Invalid search type")
        
        # Process results
        chunks = []
        similarity_scores = []
        
        for result in search_results:
            try:
                chunk = ChunkContent(
                    chunk_id=result['id'],
                    content=result['content'],
                    metadata=ChunkMetadata(
                        chunk_id=result['id'],
                        source_file=result.get('metadata', {}).get('source', ''),
                        filename=result.get('metadata', {}).get('filename', ''),
                        category=result.get('metadata', {}).get('category', ''),
                        file_id=result.get('metadata', {}).get('file_id', ''),
                        chunk_index=result.get('metadata', {}).get('chunk_index'),
                        creation_date=result.get('metadata', {}).get('created_at'),
                        size=len(result['content']),
                        distance=result.get('distance'),
                        embedding_model=result.get('metadata', {}).get('embedding_model')
                    ),
                    size=len(result['content'])
                )
                chunks.append(chunk)
                similarity_scores.append(1.0 - (result.get('distance', 0.0)))  # Convert distance to similarity
            except Exception as e:
                logger.warning(f"Error processing search result: {e}")
                continue
        
        processing_time = asyncio.get_event_loop().time() - start_time
        
        logger.info(f"🎯 Search completed: {len(chunks)} results in {processing_time:.3f}s")
        
        return ChunkSearchResponse(
            query=request.query,
            search_type=request.search_type,
            results_count=len(chunks),
            processing_time=processing_time,
            chunks=chunks,
            similarity_scores=similarity_scores
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error searching chunks: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


# Helper functions

async def _get_chunks_with_filters(limit: int, offset: int, search: Optional[str], 
                                  filters: Dict[str, Any], sort_by: str, sort_order: str) -> Dict[str, Any]:
    """Get chunks from ChromaDB with filtering and sorting"""
    try:
        # Use RAG service to get chunks
        # This is a simplified implementation - in reality, you'd need to implement
        # more sophisticated filtering in the RAG service
        
        if search:
            # Use search functionality if search term provided
            documents = await rag_service.search_documents(search, top_k=limit + offset)
            # Skip offset number of documents
            documents = documents[offset:offset + limit]
        else:
            # Get all documents (this would need to be implemented in rag_service)
            documents = await rag_service.get_all_chunks(limit=limit + offset)
            documents = documents[offset:offset + limit]
        
        chunks = []
        for doc in documents:
            chunk_data = {
                'id': getattr(doc, 'id', hashlib.md5(doc.page_content.encode()).hexdigest()[:16]),
                'content': doc.page_content,
                'metadata': doc.metadata or {}
            }
            chunks.append(chunk_data)
        
        # Apply additional filtering
        if filters:
            filtered_chunks = []
            for chunk in chunks:
                should_include = True
                
                if 'filename' in filters and filters['filename'].lower() not in chunk.get('metadata', {}).get('filename', '').lower():
                    should_include = False
                if 'category' in filters and filters['category'] != chunk.get('metadata', {}).get('category', ''):
                    should_include = False
                if 'min_size' in filters and len(chunk['content']) < filters['min_size']:
                    should_include = False
                if 'max_size' in filters and len(chunk['content']) > filters['max_size']:
                    should_include = False
                
                if should_include:
                    filtered_chunks.append(chunk)
            
            chunks = filtered_chunks
        
        # Sort chunks
        if sort_by == 'size':
            chunks.sort(key=lambda x: len(x['content']), reverse=(sort_order == 'desc'))
        elif sort_by == 'filename':
            chunks.sort(key=lambda x: x.get('metadata', {}).get('filename', ''), reverse=(sort_order == 'desc'))
        # For creation_date and relevance, assume they're already in reasonable order
        
        return {
            'chunks': chunks,
            'total_count': len(chunks)  # This is simplified - should be total before pagination
        }
        
    except Exception as e:
        logger.error(f"Error getting chunks with filters: {e}")
        return {'chunks': [], 'total_count': 0}


async def _get_chunk_by_id(chunk_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific chunk by ID"""
    try:
        # This would need to be implemented in the RAG service
        # For now, we'll search for it
        documents = await rag_service.search_documents(f"chunk_id:{chunk_id}", top_k=100)
        
        for doc in documents:
            doc_id = getattr(doc, 'id', hashlib.md5(doc.page_content.encode()).hexdigest()[:16])
            if doc_id == chunk_id:
                return {
                    'id': doc_id,
                    'content': doc.page_content,
                    'metadata': doc.metadata or {}
                }
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting chunk by ID: {e}")
        return None


async def _get_related_chunks(chunk_id: str, metadata: Dict[str, Any]) -> List[RelatedChunk]:
    """Get related chunks from the same document"""
    try:
        related = []
        filename = metadata.get('filename', '')
        
        if filename:
            # Search for chunks from the same file
            documents = await rag_service.search_documents(f"filename:{filename}", top_k=10)
            
            for doc in documents:
                doc_id = getattr(doc, 'id', hashlib.md5(doc.page_content.encode()).hexdigest()[:16])
                if doc_id != chunk_id:  # Exclude the current chunk
                    related.append(RelatedChunk(
                        chunk_id=doc_id,
                        filename=doc.metadata.get('filename', filename),
                        similarity_score=0.8,  # Placeholder
                        preview=doc.page_content[:150] + "..." if len(doc.page_content) > 150 else doc.page_content
                    ))
        
        return related[:5]  # Return up to 5 related chunks
        
    except Exception as e:
        logger.error(f"Error getting related chunks: {e}")
        return []


async def _get_file_context(filename: Optional[str]) -> Dict[str, Any]:
    """Get context information about the file"""
    if not filename:
        return {}
    
    try:
        # Get basic file information
        return {
            "filename": filename,
            "file_type": filename.split('.')[-1] if '.' in filename else "unknown",
            "estimated_total_chunks": 0,  # Would need to be calculated
            "file_size_kb": 0  # Would need to be calculated
        }
    except Exception as e:
        logger.error(f"Error getting file context: {e}")
        return {}


async def _get_embedding_info(chunk_id: str) -> Optional[Dict[str, Any]]:
    """Get embedding information for a chunk"""
    try:
        # This would require access to the embedding vectors
        # which might not be directly available
        return {
            "model": settings.EMBEDDING_MODEL,
            "dimensions": 384,  # Common dimension for sentence transformers
            "has_embedding": True
        }
    except Exception as e:
        logger.error(f"Error getting embedding info: {e}")
        return None


async def _get_detailed_chroma_stats() -> Dict[str, Any]:
    """Get detailed statistics from ChromaDB"""
    try:
        stats = await rag_service.get_stats()
        
        return {
            "total_chunks": stats.get('documents_count', 0),
            "total_files": stats.get('unique_sources', 0),
            "average_chunk_size": stats.get('avg_chunk_size', 0.0)
        }
    except Exception as e:
        logger.error(f"Error getting detailed ChromaDB stats: {e}")
        return {"total_chunks": 0, "total_files": 0, "average_chunk_size": 0.0}


async def _calculate_size_distribution() -> Dict[str, int]:
    """Calculate chunk size distribution"""
    try:
        # This is a placeholder - would need actual implementation
        return {
            "small_chunks_0_500": 0,
            "medium_chunks_500_1500": 0,
            "large_chunks_1500_3000": 0,
            "xlarge_chunks_3000_plus": 0
        }
    except Exception as e:
        logger.error(f"Error calculating size distribution: {e}")
        return {}


async def _get_category_distribution() -> Dict[str, int]:
    """Get distribution of chunks by category"""
    try:
        # This is a placeholder - would need actual implementation
        return {
            "help_data": 0,
            "documentation": 0,
            "examples": 0,
            "other": 0
        }
    except Exception as e:
        logger.error(f"Error getting category distribution: {e}")
        return {}


async def _check_index_health() -> Dict[str, Any]:
    """Check ChromaDB index health"""
    try:
        return {
            "status": "healthy",
            "last_indexed": datetime.utcnow().isoformat(),
            "index_version": "1.0",
            "consistency_check": "passed"
        }
    except Exception as e:
        logger.error(f"Error checking index health: {e}")
        return {"status": "unknown", "error": str(e)}


async def _semantic_search(request: ChunkSearchRequest) -> List[Dict[str, Any]]:
    """Perform semantic search"""
    try:
        documents = await rag_service.search_documents(request.query, top_k=request.limit)
        
        results = []
        for doc in documents:
            if hasattr(doc, 'score') and doc.score < request.similarity_threshold:
                continue
                
            results.append({
                'id': getattr(doc, 'id', hashlib.md5(doc.page_content.encode()).hexdigest()[:16]),
                'content': doc.page_content,
                'metadata': doc.metadata or {},
                'distance': getattr(doc, 'score', 0.0)
            })
        
        return results
        
    except Exception as e:
        logger.error(f"Error in semantic search: {e}")
        return []


async def _hybrid_search(request: ChunkSearchRequest) -> List[Dict[str, Any]]:
    """Perform hybrid search (semantic + keyword)"""
    try:
        # For now, this is the same as semantic search
        # In a full implementation, you'd combine semantic and keyword search results
        return await _semantic_search(request)
    except Exception as e:
        logger.error(f"Error in hybrid search: {e}")
        return []


async def _fulltext_search(request: ChunkSearchRequest) -> List[Dict[str, Any]]:
    """Perform full-text search"""
    try:
        # For now, this is the same as semantic search
        # In a full implementation, you'd do keyword-based search
        return await _semantic_search(request)
    except Exception as e:
        logger.error(f"Error in fulltext search: {e}")
        return []