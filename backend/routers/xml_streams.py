"""
XML Streams API Router
FastAPI endpoints for XML stream CRUD operations
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Path
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from services.xml_stream_service import XMLStreamService
from schemas.xml_streams import (
    XMLStreamCreate, XMLStreamUpdate, XMLStreamResponse,
    XMLStreamListResponse, StreamFilters, BulkStreamOperation,
    DuplicateStreamRequest, StreamOperationResponse,
    StreamExportRequest, StreamWorkflowUpdate,
    StreamSubmitForReview, StreamApproval, StreamPublish
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/xml-streams", tags=["XML Streams"])


@router.get("", response_model=XMLStreamListResponse)
async def list_streams(
    # Query parameters for filtering
    search: Optional[str] = Query(None, description="Search term for stream name or description"),
    job_types: Optional[List[str]] = Query(None, description="Filter by job types"),
    statuses: Optional[List[str]] = Query(None, description="Filter by statuses"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    is_favorite: Optional[bool] = Query(None, description="Filter by favorite status"),
    created_after: Optional[str] = Query(None, description="Filter by creation date (ISO format)"),
    created_before: Optional[str] = Query(None, description="Filter by creation date (ISO format)"),

    # Pagination and sorting
    sort_by: str = Query("updated_desc", description="Sort field and direction"),
    limit: int = Query(20, ge=1, le=100, description="Number of streams to return"),
    offset: int = Query(0, ge=0, description="Number of streams to skip"),

    # Dependencies
    db: AsyncSession = Depends(get_async_session)
):
    """
    List XML streams with filtering, sorting, and pagination
    """
    try:
        # Parse datetime strings if provided
        created_after_dt = None
        created_before_dt = None

        if created_after:
            from datetime import datetime
            created_after_dt = datetime.fromisoformat(created_after.replace('Z', '+00:00'))

        if created_before:
            from datetime import datetime
            created_before_dt = datetime.fromisoformat(created_before.replace('Z', '+00:00'))

        # Create filters
        filters = StreamFilters(
            search=search,
            job_types=job_types,
            statuses=statuses,
            tags=tags,
            is_favorite=is_favorite,
            created_after=created_after_dt,
            created_before=created_before_dt
        )

        # Get streams and total count
        streams, total_count = await XMLStreamService.list_streams(
            db=db,
            filters=filters,
            sort_by=sort_by,
            limit=limit,
            offset=offset
        )

        # Calculate if there are more results
        has_more = (offset + limit) < total_count

        # Convert to response models, ensuring tags is never None
        stream_responses = []
        for stream in streams:
            stream_dict = stream.__dict__.copy()
            if stream_dict.get('tags') is None:
                stream_dict['tags'] = []
            stream_responses.append(XMLStreamResponse.model_validate(stream_dict))

        return XMLStreamListResponse(
            streams=stream_responses,
            total_count=total_count,
            limit=limit,
            offset=offset,
            has_more=has_more
        )

    except Exception as e:
        logger.error(f"❌ Failed to list streams: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list streams: {str(e)}")


@router.post("", response_model=XMLStreamResponse, status_code=201)
async def create_stream(
    stream_data: XMLStreamCreate,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Create a new XML stream
    """
    try:
        # Create the stream
        db_stream = await XMLStreamService.create_stream(db=db, stream_data=stream_data)

        # Return response, ensuring tags is never None
        stream_dict = db_stream.__dict__.copy()
        if stream_dict.get('tags') is None:
            stream_dict['tags'] = []
        return XMLStreamResponse.model_validate(stream_dict)

    except Exception as e:
        logger.error(f"❌ Failed to create stream: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create stream: {str(e)}")


@router.get("/{stream_id}", response_model=XMLStreamResponse)
async def get_stream(
    stream_id: str = Path(..., description="Stream ID"),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get a single XML stream by ID
    """
    try:
        # Get the stream
        db_stream = await XMLStreamService.get_stream(db=db, stream_id=stream_id)

        if not db_stream:
            raise HTTPException(status_code=404, detail=f"Stream not found: {stream_id}")

        # Return response, ensuring tags is never None
        stream_dict = db_stream.__dict__.copy()
        if stream_dict.get('tags') is None:
            stream_dict['tags'] = []
        return XMLStreamResponse.model_validate(stream_dict)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get stream {stream_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get stream: {str(e)}")


@router.put("/{stream_id}", response_model=XMLStreamResponse)
async def update_stream(
    stream_id: str = Path(..., description="Stream ID"),
    stream_data: XMLStreamUpdate = ...,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Update an existing XML stream
    """
    try:
        # Update the stream
        db_stream = await XMLStreamService.update_stream(
            db=db,
            stream_id=stream_id,
            stream_data=stream_data
        )

        if not db_stream:
            raise HTTPException(status_code=404, detail=f"Stream not found: {stream_id}")

        # Return response, ensuring tags is never None
        stream_dict = db_stream.__dict__.copy()
        if stream_dict.get('tags') is None:
            stream_dict['tags'] = []
        return XMLStreamResponse.model_validate(stream_dict)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to update stream {stream_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update stream: {str(e)}")


@router.delete("/{stream_id}", response_model=StreamOperationResponse)
async def delete_stream(
    stream_id: str = Path(..., description="Stream ID"),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Delete an XML stream
    """
    try:
        # Delete the stream
        success = await XMLStreamService.delete_stream(db=db, stream_id=stream_id)

        if not success:
            raise HTTPException(status_code=404, detail=f"Stream not found: {stream_id}")

        return StreamOperationResponse(
            success=True,
            message=f"Stream deleted successfully: {stream_id}"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to delete stream {stream_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete stream: {str(e)}")


@router.post("/{stream_id}/favorite", response_model=XMLStreamResponse)
async def toggle_favorite(
    stream_id: str = Path(..., description="Stream ID"),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Toggle the favorite status of a stream
    """
    try:
        # Toggle favorite
        db_stream = await XMLStreamService.toggle_favorite(db=db, stream_id=stream_id)

        if not db_stream:
            raise HTTPException(status_code=404, detail=f"Stream not found: {stream_id}")

        # Return response, ensuring tags is never None
        stream_dict = db_stream.__dict__.copy()
        if stream_dict.get('tags') is None:
            stream_dict['tags'] = []
        return XMLStreamResponse.model_validate(stream_dict)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to toggle favorite for stream {stream_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to toggle favorite: {str(e)}")


@router.post("/duplicate", response_model=XMLStreamResponse)
async def duplicate_stream(
    request: DuplicateStreamRequest,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Create a duplicate of an existing stream
    """
    try:
        # Duplicate the stream
        db_stream = await XMLStreamService.duplicate_stream(
            db=db,
            stream_id=request.stream_id,
            new_name=request.new_name
        )

        if not db_stream:
            raise HTTPException(
                status_code=404,
                detail=f"Source stream not found: {request.stream_id}"
            )

        # Return response, ensuring tags is never None
        stream_dict = db_stream.__dict__.copy()
        if stream_dict.get('tags') is None:
            stream_dict['tags'] = []
        return XMLStreamResponse.model_validate(stream_dict)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to duplicate stream: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to duplicate stream: {str(e)}")


@router.post("/bulk/delete", response_model=StreamOperationResponse)
async def bulk_delete_streams(
    request: BulkStreamOperation,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Delete multiple streams in bulk
    """
    try:
        # Bulk delete
        deleted_count = await XMLStreamService.bulk_delete_streams(
            db=db,
            stream_ids=request.stream_ids
        )

        return StreamOperationResponse(
            success=True,
            message=f"Successfully deleted {deleted_count} streams",
            data={"deleted_count": deleted_count}
        )

    except Exception as e:
        logger.error(f"❌ Failed to bulk delete streams: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to bulk delete streams: {str(e)}")


@router.post("/bulk/favorite", response_model=StreamOperationResponse)
async def bulk_toggle_favorite(
    request: BulkStreamOperation,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Toggle favorite status for multiple streams
    """
    try:
        # Bulk toggle favorite
        updated_count = await XMLStreamService.bulk_toggle_favorite(
            db=db,
            stream_ids=request.stream_ids
        )

        return StreamOperationResponse(
            success=True,
            message=f"Successfully toggled favorites for {updated_count} streams",
            data={"updated_count": updated_count}
        )

    except Exception as e:
        logger.error(f"❌ Failed to bulk toggle favorites: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to bulk toggle favorites: {str(e)}")


@router.get("/{stream_id}/export")
async def export_stream(
    stream_id: str = Path(..., description="Stream ID"),
    format: str = Query("xml", pattern="^(xml|json)$", description="Export format"),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Export a stream in XML or JSON format
    """
    try:
        # Get the stream
        db_stream = await XMLStreamService.get_stream(db=db, stream_id=stream_id)

        if not db_stream:
            raise HTTPException(status_code=404, detail=f"Stream not found: {stream_id}")

        if format == "xml":
            # Return XML content
            if not db_stream.xml_content:
                raise HTTPException(status_code=400, detail="Stream has no XML content to export")

            return Response(
                content=db_stream.xml_content,
                media_type="application/xml",
                headers={
                    "Content-Disposition": f"attachment; filename={db_stream.stream_name}.xml"
                }
            )

        elif format == "json":
            # Return as JSON
            import json
            stream_dict = XMLStreamResponse.model_validate(db_stream).model_dump()
            json_content = json.dumps(stream_dict, indent=2, default=str)

            return Response(
                content=json_content,
                media_type="application/json",
                headers={
                    "Content-Disposition": f"attachment; filename={db_stream.stream_name}.json"
                }
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to export stream {stream_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to export stream: {str(e)}")


# Workflow endpoints
@router.post("/{stream_id}/submit-for-review", response_model=XMLStreamResponse)
async def submit_for_review(
    stream_id: str = Path(..., description="Stream ID"),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Submit a stream for review (changes status to 'zur_freigabe')
    """
    try:
        from schemas.xml_streams import XMLStreamUpdate

        # Update status to 'zur_freigabe'
        update_data = XMLStreamUpdate(status="zur_freigabe")
        db_stream = await XMLStreamService.update_stream(
            db=db,
            stream_id=stream_id,
            stream_data=update_data
        )

        if not db_stream:
            raise HTTPException(status_code=404, detail=f"Stream not found: {stream_id}")

        return XMLStreamResponse.model_validate(db_stream)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to submit stream for review {stream_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to submit for review: {str(e)}")


@router.post("/{stream_id}/approve", response_model=XMLStreamResponse)
async def approve_stream(
    stream_id: str = Path(..., description="Stream ID"),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Approve a stream (changes status to 'freigegeben')
    """
    try:
        from schemas.xml_streams import XMLStreamUpdate

        # Update status to 'freigegeben'
        update_data = XMLStreamUpdate(status="freigegeben")
        db_stream = await XMLStreamService.update_stream(
            db=db,
            stream_id=stream_id,
            stream_data=update_data
        )

        if not db_stream:
            raise HTTPException(status_code=404, detail=f"Stream not found: {stream_id}")

        return XMLStreamResponse.model_validate(db_stream)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to approve stream {stream_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to approve stream: {str(e)}")


@router.post("/{stream_id}/reject", response_model=XMLStreamResponse)
async def reject_stream(
    stream_id: str = Path(..., description="Stream ID"),
    reason: str = Query(..., description="Reason for rejection"),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Reject a stream (changes status to 'abgelehnt')
    """
    try:
        from schemas.xml_streams import XMLStreamUpdate

        # Update status to 'abgelehnt' and add rejection reason
        update_data = XMLStreamUpdate(
            status="abgelehnt",
            wizard_data={"rejection_reason": reason, "rejected_at": str(datetime.utcnow())}
        )
        db_stream = await XMLStreamService.update_stream(
            db=db,
            stream_id=stream_id,
            stream_data=update_data
        )

        if not db_stream:
            raise HTTPException(status_code=404, detail=f"Stream not found: {stream_id}")

        return XMLStreamResponse.model_validate(db_stream)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to reject stream {stream_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to reject stream: {str(e)}")


@router.post("/{stream_id}/publish", response_model=XMLStreamResponse)
async def publish_stream(
    stream_id: str = Path(..., description="Stream ID"),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Publish a stream (changes status to 'published')
    """
    try:
        from schemas.xml_streams import XMLStreamUpdate
        from datetime import datetime

        # Update status to 'published'
        update_data = XMLStreamUpdate(
            status="published",
            wizard_data={"published_at": str(datetime.utcnow())}
        )
        db_stream = await XMLStreamService.update_stream(
            db=db,
            stream_id=stream_id,
            stream_data=update_data
        )

        if not db_stream:
            raise HTTPException(status_code=404, detail=f"Stream not found: {stream_id}")

        return XMLStreamResponse.model_validate(db_stream)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to publish stream {stream_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to publish stream: {str(e)}")