"""
Enhanced chunks API with comprehensive logging and monitoring
"""
import time
import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, validator
from app.api.v1.chunks import (
    ChunksListResponse, ChunkDetailsResponse, ChunkStatsResponse,
    ChunkMetadata, ChunkContent, SortBy, SortOrder
)
from app.services.rag_service import rag_service
from app.middleware.enhanced_monitoring import search_metrics_logger, business_logger
from app.core.logging_config import get_logger, performance_logger

logger = get_logger(__name__)
router = APIRouter()


class ChunksRequest(BaseModel):
    """Request model for chunks listing with validation"""
    limit: int = Query(20, ge=1, le=100, description="Number of chunks to return")
    offset: int = Query(0, ge=0, description="Number of chunks to skip")
    search: Optional[str] = Query(None, min_length=2, max_length=500, description="Search query")
    source_file: Optional[str] = Query(None, max_length=255, description="Filter by source file")
    category: Optional[str] = Query(None, pattern="^(help_data|stream_templates)$", description="Filter by category")
    sort_by: SortBy = Query(SortBy.CREATION_DATE, description="Sort field")
    sort_order: SortOrder = Query(SortOrder.DESC, description="Sort order")
    
    @validator('search')
    def validate_search_query(cls, v):
        if v is not None:
            # Basic XSS prevention
            if any(char in v for char in ['<', '>', '"', "'"]):
                raise ValueError("Search query contains invalid characters")
            # Remove excessive whitespace
            v = ' '.join(v.split())
        return v


class ChunksSearchRequest(BaseModel):
    """Request model for chunk search with validation"""
    query: str = Query(..., min_length=2, max_length=500, description="Search query")
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results")
    
    @validator('query')
    def validate_query(cls, v):
        # Basic validation and sanitization
        if any(char in v for char in ['<', '>', '"', "'"]):
            raise ValueError("Query contains invalid characters")
        return ' '.join(v.split())


@router.get("/", response_model=ChunksListResponse)
async def list_chunks(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None),
    source_file: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    sort_by: SortBy = Query(SortBy.CREATION_DATE),
    sort_order: SortOrder = Query(SortOrder.DESC)
) -> ChunksListResponse:
    """
    Get paginated list of chunks with filtering and sorting
    
    Enhanced with comprehensive logging and monitoring
    """
    start_time = time.time()
    operation_id = f"list_chunks_{int(start_time)}"
    
    logger.info(
        "Chunks list request started",
        operation_id=operation_id,
        limit=limit,
        offset=offset,
        search=bool(search),
        source_file=source_file,
        category=category,
        sort_by=sort_by.value,
        sort_order=sort_order.value
    )
    
    try:
        # Validate and sanitize search query
        if search:
            if any(char in search for char in ['<', '>', '"', "'"]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Search query contains invalid characters"
                )
            search = ' '.join(search.split())  # Normalize whitespace
        
        # Get chunks from service
        chunks = await rag_service.get_all_chunks(limit=limit, offset=offset)
        
        # Apply filters (this would be done in the service in a real implementation)
        filtered_chunks = chunks
        if search:
            filtered_chunks = [
                chunk for chunk in chunks 
                if search.lower() in chunk.page_content.lower()
            ]
        
        if source_file:
            filtered_chunks = [
                chunk for chunk in filtered_chunks
                if chunk.metadata.get('filename', '').lower() == source_file.lower()
            ]
        
        if category:
            filtered_chunks = [
                chunk for chunk in filtered_chunks
                if chunk.metadata.get('category') == category
            ]
        
        # Convert to response format
        chunk_responses = []
        for i, chunk in enumerate(filtered_chunks):
            chunk_metadata = ChunkMetadata(
                chunk_id=chunk.metadata.get('id', str(i)),
                chunk_index=i,
                filename=chunk.metadata.get('filename', 'unknown'),
                source_file=chunk.metadata.get('source', 'unknown'),
                category=chunk.metadata.get('category'),
                file_id=chunk.metadata.get('file_id'),
                total_chunks=chunk.metadata.get('total_chunks'),
                creation_date=chunk.metadata.get('timestamp'),
                size=len(chunk.page_content),
                embedding_model=chunk.metadata.get('embedding_model'),
                distance=chunk.metadata.get('distance')
            )
            
            content = chunk.page_content
            chunk_response = ChunkContent(
                chunk_id=chunk.metadata.get('id', str(i)),
                content=content,
                metadata=chunk_metadata,
                preview=content[:200] + "..." if len(content) > 200 else content,
                word_count=len(content.split()),
                line_count=len(content.split('\n'))
            )
            chunk_responses.append(chunk_response)
        
        # Calculate pagination
        total = len(chunk_responses)
        has_more = offset + limit < total
        
        # Apply pagination to results
        paginated_chunks = chunk_responses[offset:offset + limit]
        
        # Import PaginationInfo
        from app.api.v1.chunks import PaginationInfo
        
        total_pages = (total + limit - 1) // limit if total > 0 else 0
        current_page = (offset // limit) + 1
        
        pagination = PaginationInfo(
            current_page=current_page,
            page_size=limit,
            total_items=total,
            total_pages=total_pages,
            has_next=offset + limit < total,
            has_previous=offset > 0
        )
        
        response = ChunksListResponse(
            chunks=paginated_chunks,
            pagination=pagination,
            filters_applied={"category": category_filter, "source": source_filter} if category_filter or source_filter else {},
            sort_info={"sort_by": sort_by.value, "sort_order": sort_order.value}
        )
        
        # Calculate duration and log metrics
        duration = time.time() - start_time
        
        # Log business metrics
        business_logger.log_chunk_operation(
            operation="list",
            chunk_count=len(paginated_chunks),
            duration=duration
        )
        
        # Log performance
        performance_logger.log_request_performance(
            method="GET",
            path="/api/v1/chunks",
            status_code=200,
            duration=duration,
            extra_data={
                "chunks_returned": len(paginated_chunks),
                "total_chunks": total,
                "has_filters": bool(search or source_file or category)
            }
        )
        
        logger.info(
            "Chunks list request completed",
            operation_id=operation_id,
            duration_ms=round(duration * 1000, 2),
            chunks_returned=len(paginated_chunks),
            total_chunks=total
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        duration = time.time() - start_time
        logger.error(
            "Chunks list request failed",
            operation_id=operation_id,
            error=str(e),
            duration_ms=round(duration * 1000, 2),
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve chunks"
        )


@router.get("/{chunk_id}", response_model=ChunkDetailsResponse)
async def get_chunk_details(chunk_id: str) -> ChunkDetailsResponse:
    """
    Get detailed information about a specific chunk
    
    Enhanced with logging and monitoring
    """
    start_time = time.time()
    operation_id = f"get_chunk_{chunk_id}_{int(start_time)}"
    
    logger.info(
        "Chunk details request started",
        operation_id=operation_id,
        chunk_id=chunk_id
    )
    
    try:
        # Validate chunk ID format
        if not chunk_id or len(chunk_id) > 255:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid chunk ID format"
            )
        
        # Get chunk details (mock implementation)
        # In a real implementation, this would query the specific chunk
        chunks = await rag_service.get_all_chunks(limit=100)
        
        # Find the specific chunk
        target_chunk = None
        for i, chunk in enumerate(chunks):
            if chunk.metadata.get('id', str(i)) == chunk_id:
                target_chunk = chunk
                break
        
        if not target_chunk:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chunk with ID {chunk_id} not found"
            )
        
        # Get similar chunks (mock implementation)
        similar_chunks = chunks[:3] if chunks else []
        
        # Create response
        chunk_metadata = ChunkMetadata(
            chunk_id=target_chunk.metadata.get('id', chunk_id),
            chunk_index=0,
            filename=target_chunk.metadata.get('filename', 'unknown'),
            source_file=target_chunk.metadata.get('source', 'unknown'),
            category=target_chunk.metadata.get('category'),
            file_id=target_chunk.metadata.get('file_id'),
            total_chunks=target_chunk.metadata.get('total_chunks'),
            creation_date=target_chunk.metadata.get('timestamp'),
            size=len(target_chunk.page_content),
            embedding_model=target_chunk.metadata.get('embedding_model'),
            distance=target_chunk.metadata.get('distance')
        )
        
        content = target_chunk.page_content
        main_chunk = ChunkContent(
            chunk_id=chunk_id,
            content=content,
            metadata=chunk_metadata,
            preview=content[:200] + "..." if len(content) > 200 else content,
            word_count=len(content.split()),
            line_count=len(content.split('\n'))
        )
        
        similar_chunk_responses = []
        for i, chunk in enumerate(similar_chunks):
            similar_metadata = ChunkMetadata(
                chunk_id=chunk.metadata.get('id', str(i)),
                chunk_index=i,
                filename=chunk.metadata.get('filename', 'unknown'),
                source_file=chunk.metadata.get('source', 'unknown'),
                category=chunk.metadata.get('category'),
                file_id=chunk.metadata.get('file_id'),
                total_chunks=chunk.metadata.get('total_chunks'),
                creation_date=chunk.metadata.get('timestamp'),
                size=len(chunk.page_content),
                embedding_model=chunk.metadata.get('embedding_model'),
                distance=chunk.metadata.get('distance')
            )
            
            from app.api.v1.chunks import RelatedChunk
            
            similar_chunk = RelatedChunk(
                chunk_id=chunk.metadata.get('id', str(i)),
                filename=chunk.metadata.get('filename', 'unknown'),
                similarity_score=0.8,  # Mock similarity score
                preview=chunk.page_content[:200] + "..." if len(chunk.page_content) > 200 else chunk.page_content
            )
            similar_chunk_responses.append(similar_chunk)
        
        response = ChunkDetailsResponse(
            chunk=main_chunk,
            related_chunks=similar_chunk_responses,
            file_context={
                "content_length": len(main_chunk.content),
                "word_count": len(main_chunk.content.split()),
                "unique_words": len(set(main_chunk.content.lower().split())),
                "metadata_keys": list(main_chunk.metadata.dict().keys())
            },
            embedding_info={
                "model": main_chunk.metadata.embedding_model,
                "distance": main_chunk.metadata.distance
            }
        )
        
        # Log metrics
        duration = time.time() - start_time
        performance_logger.log_request_performance(
            method="GET",
            path=f"/api/v1/chunks/{chunk_id}",
            status_code=200,
            duration=duration
        )
        
        logger.info(
            "Chunk details request completed",
            operation_id=operation_id,
            duration_ms=round(duration * 1000, 2),
            similar_chunks_count=len(similar_chunk_responses)
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        duration = time.time() - start_time
        logger.error(
            "Chunk details request failed",
            operation_id=operation_id,
            chunk_id=chunk_id,
            error=str(e),
            duration_ms=round(duration * 1000, 2),
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve chunk details"
        )


@router.get("/search", response_model=ChunksListResponse)
async def search_chunks(
    query: str = Query(..., min_length=2, max_length=500),
    limit: int = Query(10, ge=1, le=50)
) -> ChunksListResponse:
    """
    Search chunks by content with enhanced logging
    """
    start_time = time.time()
    operation_id = f"search_chunks_{int(start_time)}"
    
    logger.info(
        "Chunk search request started",
        operation_id=operation_id,
        query_length=len(query),
        limit=limit
    )
    
    try:
        # Validate and sanitize query
        if any(char in query for char in ['<', '>', '"', "'"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Search query contains invalid characters"
            )
        
        query = ' '.join(query.split())  # Normalize whitespace
        
        # Perform search using RAG service
        search_results = await rag_service.search_documents(query, top_k=limit)
        
        # Convert to response format
        chunk_responses = []
        for i, result in enumerate(search_results):
            chunk_metadata = ChunkMetadata(
                chunk_id=result.metadata.get('id', str(i)),
                chunk_index=i,
                filename=result.metadata.get('filename', 'unknown'),
                source_file=result.metadata.get('source', 'unknown'),
                category=result.metadata.get('category'),
                file_id=result.metadata.get('file_id'),
                total_chunks=result.metadata.get('total_chunks'),
                creation_date=result.metadata.get('timestamp'),
                size=len(result.page_content),
                embedding_model=result.metadata.get('embedding_model'),
                distance=getattr(result, 'score', None)
            )
            
            content = result.page_content
            chunk_response = ChunkContent(
                chunk_id=result.metadata.get('id', str(i)),
                content=content,
                metadata=chunk_metadata,
                preview=content[:200] + "..." if len(content) > 200 else content,
                word_count=len(content.split()),
                line_count=len(content.split('\n'))
            )
            chunk_responses.append(chunk_response)
        
        total = len(chunk_responses)
        pagination = PaginationInfo(
            current_page=1,
            page_size=limit,
            total_items=total,
            total_pages=1,
            has_next=False,
            has_previous=False
        )
        
        response = ChunksListResponse(
            chunks=chunk_responses,
            pagination=pagination,
            filters_applied={"query": query},
            sort_info={"sort_by": "relevance", "sort_order": "desc"}
        )
        
        # Log metrics
        duration = time.time() - start_time
        
        search_metrics_logger.log_search_request(
            query=query,
            results_count=len(chunk_responses),
            duration=duration
        )
        
        performance_logger.log_request_performance(
            method="GET",
            path="/api/v1/chunks/search",
            status_code=200,
            duration=duration,
            extra_data={
                "query_length": len(query),
                "results_count": len(chunk_responses)
            }
        )
        
        logger.info(
            "Chunk search request completed",
            operation_id=operation_id,
            duration_ms=round(duration * 1000, 2),
            results_count=len(chunk_responses),
            query_length=len(query)
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        duration = time.time() - start_time
        logger.error(
            "Chunk search request failed",
            operation_id=operation_id,
            query=query[:100],  # Log first 100 chars only
            error=str(e),
            duration_ms=round(duration * 1000, 2),
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search operation failed"
        )


@router.get("/statistics", response_model=ChunksStatisticsResponse)
async def get_chunks_statistics() -> ChunksStatisticsResponse:
    """
    Get comprehensive statistics about chunks with enhanced logging
    """
    start_time = time.time()
    operation_id = f"get_statistics_{int(start_time)}"
    
    logger.info("Chunks statistics request started", operation_id=operation_id)
    
    try:
        # Get statistics from RAG service
        rag_stats = await rag_service.get_stats()
        
        # Get all chunks for detailed statistics
        chunks = await rag_service.get_all_chunks(limit=1000)
        
        # Calculate statistics
        total_chunks = len(chunks)
        total_documents = len(set(chunk.metadata.get('filename', 'unknown') for chunk in chunks))
        
        if chunks:
            chunk_sizes = [len(chunk.page_content) for chunk in chunks]
            chunk_size_avg = sum(chunk_sizes) / len(chunk_sizes)
            chunk_size_min = min(chunk_sizes)
            chunk_size_max = max(chunk_sizes)
        else:
            chunk_size_avg = chunk_size_min = chunk_size_max = 0
        
        # Get metadata keys
        metadata_keys = set()
        for chunk in chunks:
            metadata_keys.update(chunk.metadata.keys())
        
        # Source distribution
        source_distribution = {}
        for chunk in chunks:
            source = chunk.metadata.get('source', 'unknown')
            source_distribution[source] = source_distribution.get(source, 0) + 1
        
        # File type distribution
        file_type_distribution = {}
        for chunk in chunks:
            filename = chunk.metadata.get('filename', 'unknown')
            file_ext = filename.split('.')[-1] if '.' in filename else 'unknown'
            file_type_distribution[file_ext] = file_type_distribution.get(file_ext, 0) + 1
        
        response = ChunksStatisticsResponse(
            total_chunks=total_chunks,
            total_documents=total_documents,
            chunk_size_avg=chunk_size_avg,
            chunk_size_min=chunk_size_min,
            chunk_size_max=chunk_size_max,
            metadata_keys=list(metadata_keys),
            source_distribution=source_distribution,
            file_type_distribution=file_type_distribution,
            creation_timeline=[]  # Would be implemented with proper timestamp analysis
        )
        
        # Log metrics
        duration = time.time() - start_time
        performance_logger.log_request_performance(
            method="GET",
            path="/api/v1/chunks/statistics",
            status_code=200,
            duration=duration,
            extra_data={
                "total_chunks": total_chunks,
                "total_documents": total_documents
            }
        )
        
        logger.info(
            "Chunks statistics request completed",
            operation_id=operation_id,
            duration_ms=round(duration * 1000, 2),
            total_chunks=total_chunks,
            total_documents=total_documents
        )
        
        return response
        
    except Exception as e:
        duration = time.time() - start_time
        logger.error(
            "Chunks statistics request failed",
            operation_id=operation_id,
            error=str(e),
            duration_ms=round(duration * 1000, 2),
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve statistics"
        )