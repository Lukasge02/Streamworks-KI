"""
XML Streams API Router
FastAPI endpoints for XML stream management
"""
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from fastapi.responses import Response

from services.xml_streams.xml_stream_service import XMLStreamService, get_xml_stream_service
from services.conversation_engine import ConversationEngine
from schemas.xml_streams import (
    XMLStreamCreate, XMLStreamUpdate, XMLStreamResponse, XMLStreamListResponse,
    StreamFilters, StreamSortBy, AutoSaveRequest, DuplicateStreamRequest,
    BulkActionRequest, StreamStatsResponse, StreamVersionResponse,
    ChatEntityExtractionRequest, ChatEntityExtractionResponse, JobType, ConversationState
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/xml-streams", tags=["XML Streams"])


def get_current_user() -> str:
    """Get current user ID - placeholder for actual auth implementation"""
    # TODO: Implement proper authentication
    return "anonymous"


@router.post("/", response_model=XMLStreamResponse)
async def create_stream(
    stream_data: XMLStreamCreate,
    service: XMLStreamService = Depends(get_xml_stream_service),
    current_user: str = Depends(get_current_user)
) -> XMLStreamResponse:
    """Create a new XML stream"""
    try:
        logger.info(f"Creating new stream: {stream_data.stream_name}")
        
        # Validate required fields
        if not stream_data.stream_name.strip():
            raise HTTPException(status_code=400, detail="Stream name is required")
        
        return await service.create_stream(stream_data, current_user)
        
    except ValueError as e:
        logger.error(f"Validation error creating stream: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating stream: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create stream")


@router.get("/", response_model=XMLStreamListResponse)
async def list_streams(
    search: Optional[str] = Query(None, description="Search term"),
    job_types: Optional[List[str]] = Query(None, description="Filter by job types"),
    statuses: Optional[List[str]] = Query(None, description="Filter by statuses"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    is_favorite: Optional[bool] = Query(None, description="Filter favorites"),
    sort_by: StreamSortBy = Query(StreamSortBy.UPDATED_DESC, description="Sort order"),
    limit: int = Query(50, ge=1, le=100, description="Number of streams per page"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    service: XMLStreamService = Depends(get_xml_stream_service),
    current_user: str = Depends(get_current_user)
) -> XMLStreamListResponse:
    """List XML streams with filtering and pagination"""
    try:
        # Build filters
        filters = StreamFilters(
            search=search,
            job_types=job_types,
            statuses=statuses,
            tags=tags,
            is_favorite=is_favorite
        )
        
        logger.info(f"Listing streams for user {current_user} with filters: {filters.dict()}")
        
        return await service.list_streams(
            user_id=current_user,
            filters=filters,
            sort_by=sort_by,
            limit=limit,
            offset=offset
        )
        
    except Exception as e:
        logger.error(f"Error listing streams: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list streams")


@router.get("/stats", response_model=StreamStatsResponse)
async def get_stream_stats(
    service: XMLStreamService = Depends(get_xml_stream_service),
    current_user: str = Depends(get_current_user)
) -> StreamStatsResponse:
    """Get stream statistics for the current user"""
    try:
        # Get all streams for stats calculation
        all_streams = await service.list_streams(
            user_id=current_user,
            limit=1000  # Get all streams for stats
        )
        
        streams = all_streams.streams
        total_streams = len(streams)
        
        # Calculate stats
        draft_streams = sum(1 for s in streams if s.status == "draft")
        complete_streams = sum(1 for s in streams if s.status == "complete")
        published_streams = sum(1 for s in streams if s.status == "published")
        favorite_streams = sum(1 for s in streams if s.is_favorite)
        
        # Recent streams (updated in last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_streams = sum(1 for s in streams if s.updated_at >= week_ago)
        
        # Job type distribution
        job_type_distribution = {}
        for stream in streams:
            job_type = stream.job_type or "unknown"
            job_type_distribution[job_type] = job_type_distribution.get(job_type, 0) + 1
        
        return StreamStatsResponse(
            total_streams=total_streams,
            draft_streams=draft_streams,
            complete_streams=complete_streams,
            published_streams=published_streams,
            favorite_streams=favorite_streams,
            recent_streams=recent_streams,
            job_type_distribution=job_type_distribution
        )
        
    except Exception as e:
        logger.error(f"Error getting stream stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get stream statistics")


@router.get("/{stream_id}", response_model=XMLStreamResponse)
async def get_stream(
    stream_id: UUID,
    service: XMLStreamService = Depends(get_xml_stream_service),
    current_user: str = Depends(get_current_user)
) -> XMLStreamResponse:
    """Get a specific XML stream by ID"""
    try:
        logger.info(f"Getting stream {stream_id} for user {current_user}")
        
        stream = await service.get_stream_by_id(stream_id, current_user)
        if not stream:
            raise HTTPException(status_code=404, detail="Stream not found")
        
        return stream
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting stream {stream_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get stream")


@router.put("/{stream_id}", response_model=XMLStreamResponse)
async def update_stream(
    stream_id: UUID,
    stream_update: XMLStreamUpdate,
    create_version: bool = Query(True, description="Create new version for significant changes"),
    service: XMLStreamService = Depends(get_xml_stream_service),
    current_user: str = Depends(get_current_user)
) -> XMLStreamResponse:
    """Update an XML stream"""
    try:
        logger.info(f"Updating stream {stream_id} for user {current_user}")
        
        updated_stream = await service.update_stream(
            stream_id, 
            stream_update, 
            current_user, 
            create_version
        )
        
        if not updated_stream:
            raise HTTPException(status_code=404, detail="Stream not found")
        
        return updated_stream
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error updating stream {stream_id}: {str(e)}")
        raise HTTPException(status_code=422, detail={
            "error": "Validation failed",
            "message": str(e),
            "stream_id": str(stream_id)
        })
    except Exception as e:
        logger.error(f"Error updating stream {stream_id}: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail={
            "error": "Internal server error",
            "message": "Failed to update stream",
            "stream_id": str(stream_id)
        })


@router.delete("/{stream_id}")
async def delete_stream(
    stream_id: UUID,
    service: XMLStreamService = Depends(get_xml_stream_service),
    current_user: str = Depends(get_current_user)
):
    """Delete an XML stream"""
    try:
        logger.info(f"Deleting stream {stream_id} for user {current_user}")
        
        success = await service.delete_stream(stream_id, current_user)
        if not success:
            raise HTTPException(status_code=404, detail="Stream not found")
        
        return {"message": "Stream deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting stream {stream_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete stream")


@router.post("/{stream_id}/duplicate", response_model=XMLStreamResponse)
async def duplicate_stream(
    stream_id: UUID,
    duplicate_request: DuplicateStreamRequest,
    service: XMLStreamService = Depends(get_xml_stream_service),
    current_user: str = Depends(get_current_user)
) -> XMLStreamResponse:
    """Duplicate an existing XML stream"""
    try:
        logger.info(f"Duplicating stream {stream_id} for user {current_user}")
        
        duplicated_stream = await service.duplicate_stream(
            stream_id, 
            current_user,
            duplicate_request.new_name
        )
        
        if not duplicated_stream:
            raise HTTPException(status_code=404, detail="Stream not found")
        
        return duplicated_stream
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error duplicating stream {stream_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to duplicate stream")


@router.post("/{stream_id}/favorite", response_model=XMLStreamResponse)
async def toggle_favorite(
    stream_id: UUID,
    service: XMLStreamService = Depends(get_xml_stream_service),
    current_user: str = Depends(get_current_user)
) -> XMLStreamResponse:
    """Toggle favorite status of a stream"""
    try:
        logger.info(f"Toggling favorite for stream {stream_id}")
        
        updated_stream = await service.toggle_favorite(stream_id, current_user)
        if not updated_stream:
            raise HTTPException(status_code=404, detail="Stream not found")
        
        return updated_stream
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling favorite for stream {stream_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to toggle favorite")


@router.post("/{stream_id}/auto-save", response_model=XMLStreamResponse)
async def auto_save_stream(
    stream_id: UUID,
    auto_save_data: AutoSaveRequest,
    service: XMLStreamService = Depends(get_xml_stream_service),
    current_user: str = Depends(get_current_user)
) -> XMLStreamResponse:
    """Auto-save stream data (lightweight updates)"""
    try:
        logger.debug(f"Auto-saving stream {stream_id} for user {current_user}")
        
        updated_stream = await service.auto_save_stream(
            stream_id,
            auto_save_data.wizard_data,
            auto_save_data.xml_content,
            current_user
        )
        
        if not updated_stream:
            raise HTTPException(status_code=404, detail="Stream not found")
        
        return updated_stream
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error auto-saving stream {stream_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to auto-save stream")


@router.post("/bulk-action")
async def bulk_action(
    bulk_request: BulkActionRequest,
    service: XMLStreamService = Depends(get_xml_stream_service),
    current_user: str = Depends(get_current_user)
):
    """Perform bulk actions on multiple streams"""
    try:
        logger.info(f"Performing bulk action '{bulk_request.action}' on {len(bulk_request.stream_ids)} streams")
        
        if bulk_request.action == "delete":
            deleted_count = 0
            for stream_id in bulk_request.stream_ids:
                success = await service.delete_stream(stream_id, current_user)
                if success:
                    deleted_count += 1
            
            return {
                "message": f"Deleted {deleted_count} streams",
                "processed": deleted_count,
                "total": len(bulk_request.stream_ids)
            }
        
        elif bulk_request.action == "toggle_favorite":
            updated_count = 0
            for stream_id in bulk_request.stream_ids:
                updated_stream = await service.toggle_favorite(stream_id, current_user)
                if updated_stream:
                    updated_count += 1
            
            return {
                "message": f"Updated {updated_count} streams",
                "processed": updated_count,
                "total": len(bulk_request.stream_ids)
            }
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown bulk action: {bulk_request.action}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error performing bulk action: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to perform bulk action")


@router.get("/{stream_id}/export")
async def export_stream(
    stream_id: UUID,
    format: str = Query("xml", description="Export format: xml, json"),
    service: XMLStreamService = Depends(get_xml_stream_service),
    current_user: str = Depends(get_current_user)
):
    """Export stream in various formats"""
    try:
        logger.info(f"Exporting stream {stream_id} in format {format}")
        
        stream = await service.get_stream_by_id(stream_id, current_user)
        if not stream:
            raise HTTPException(status_code=404, detail="Stream not found")
        
        if format == "xml":
            if not stream.xml_content:
                raise HTTPException(status_code=400, detail="No XML content available for export")
            
            return Response(
                content=stream.xml_content,
                media_type="application/xml",
                headers={
                    "Content-Disposition": f"attachment; filename={stream.stream_name}.xml"
                }
            )
        
        elif format == "json":
            import json
            export_data = {
                "stream_info": {
                    "id": str(stream.id),
                    "name": stream.stream_name,
                    "description": stream.description,
                    "job_type": stream.job_type,
                    "status": stream.status,
                    "created_at": stream.created_at.isoformat(),
                    "updated_at": stream.updated_at.isoformat()
                },
                "wizard_data": stream.wizard_data,
                "xml_content": stream.xml_content
            }
            
            return Response(
                content=json.dumps(export_data, indent=2),
                media_type="application/json",
                headers={
                    "Content-Disposition": f"attachment; filename={stream.stream_name}.json"
                }
            )
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported export format: {format}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting stream {stream_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to export stream")


@router.get("/{stream_id}/versions", response_model=List[StreamVersionResponse])
async def get_stream_versions(
    stream_id: UUID,
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    service: XMLStreamService = Depends(get_xml_stream_service),
    current_user: str = Depends(get_current_user)
) -> List[StreamVersionResponse]:
    """Get version history for a stream"""
    try:
        # Verify stream exists and user has access
        stream = await service.get_stream_by_id(stream_id, current_user)
        if not stream:
            raise HTTPException(status_code=404, detail="Stream not found")

        # TODO: Implement version retrieval in service
        # For now, return empty list
        return []

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting versions for stream {stream_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get stream versions")


@router.post("/{stream_id}/submit-for-review", response_model=XMLStreamResponse)
async def submit_for_review(
    stream_id: UUID,
    service: XMLStreamService = Depends(get_xml_stream_service),
    current_user: str = Depends(get_current_user)
) -> XMLStreamResponse:
    """Submit stream for expert review"""
    try:
        logger.info(f"Submitting stream {stream_id} for review by user {current_user}")

        # Get current stream
        stream = await service.get_stream_by_id(stream_id, current_user)
        if not stream:
            raise HTTPException(status_code=404, detail="Stream not found")

        # Check if stream is in draft status
        if stream.status != "draft":
            raise HTTPException(status_code=400, detail="Only draft streams can be submitted for review")

        # Update status to zur_freigabe
        from schemas.xml_streams import XMLStreamUpdate
        update_data = XMLStreamUpdate(status="zur_freigabe")

        updated_stream = await service.update_stream(
            stream_id,
            update_data,
            current_user,
            create_version=True  # Create version for status change
        )

        if not updated_stream:
            raise HTTPException(status_code=404, detail="Stream not found")

        logger.info(f"Stream {stream_id} submitted for review successfully")
        return updated_stream

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting stream {stream_id} for review: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to submit stream for review")


@router.post("/{stream_id}/approve", response_model=XMLStreamResponse)
async def approve_stream(
    stream_id: UUID,
    service: XMLStreamService = Depends(get_xml_stream_service),
    current_user: str = Depends(get_current_user)
) -> XMLStreamResponse:
    """Approve stream (expert action)"""
    try:
        logger.info(f"Approving stream {stream_id} by expert {current_user}")

        # Get current stream
        stream = await service.get_stream_by_id(stream_id, current_user)
        if not stream:
            raise HTTPException(status_code=404, detail="Stream not found")

        # Check if stream is awaiting review
        if stream.status != "zur_freigabe":
            raise HTTPException(status_code=400, detail="Only streams awaiting review can be approved")

        # Update status to freigegeben
        from schemas.xml_streams import XMLStreamUpdate
        update_data = XMLStreamUpdate(status="freigegeben")

        updated_stream = await service.update_stream(
            stream_id,
            update_data,
            current_user,
            create_version=True  # Create version for approval
        )

        if not updated_stream:
            raise HTTPException(status_code=404, detail="Stream not found")

        logger.info(f"Stream {stream_id} approved successfully by expert {current_user}")
        return updated_stream

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving stream {stream_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to approve stream")


@router.post("/{stream_id}/reject", response_model=XMLStreamResponse)
async def reject_stream(
    stream_id: UUID,
    reason: str = Body(..., embed=True, description="Reason for rejection"),
    service: XMLStreamService = Depends(get_xml_stream_service),
    current_user: str = Depends(get_current_user)
) -> XMLStreamResponse:
    """Reject stream and return to draft (expert action)"""
    try:
        logger.info(f"Rejecting stream {stream_id} by expert {current_user}, reason: {reason}")

        # Get current stream
        stream = await service.get_stream_by_id(stream_id, current_user)
        if not stream:
            raise HTTPException(status_code=404, detail="Stream not found")

        # Check if stream is awaiting review
        if stream.status != "zur_freigabe":
            raise HTTPException(status_code=400, detail="Only streams awaiting review can be rejected")

        # Update status to abgelehnt
        from schemas.xml_streams import XMLStreamUpdate
        update_data = XMLStreamUpdate(status="abgelehnt")

        updated_stream = await service.update_stream(
            stream_id,
            update_data,
            current_user,
            create_version=True  # Create version for rejection
        )

        if not updated_stream:
            raise HTTPException(status_code=404, detail="Stream not found")

        logger.info(f"Stream {stream_id} rejected by expert {current_user}")
        return updated_stream

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rejecting stream {stream_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to reject stream")


@router.post("/{stream_id}/publish", response_model=XMLStreamResponse)
async def publish_stream(
    stream_id: UUID,
    service: XMLStreamService = Depends(get_xml_stream_service),
    current_user: str = Depends(get_current_user)
) -> XMLStreamResponse:
    """Publish approved stream (expert action)"""
    try:
        logger.info(f"Publishing stream {stream_id} by expert {current_user}")

        # Get current stream
        stream = await service.get_stream_by_id(stream_id, current_user)
        if not stream:
            raise HTTPException(status_code=404, detail="Stream not found")

        # Check if stream is approved
        if stream.status != "freigegeben":
            raise HTTPException(status_code=400, detail="Only approved streams can be published")

        # Update status to published
        from schemas.xml_streams import XMLStreamUpdate
        update_data = XMLStreamUpdate(status="published")

        updated_stream = await service.update_stream(
            stream_id,
            update_data,
            current_user,
            create_version=True  # Create version for publishing
        )

        if not updated_stream:
            raise HTTPException(status_code=404, detail="Stream not found")

        logger.info(f"Stream {stream_id} published successfully by expert {current_user}")
        return updated_stream

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error publishing stream {stream_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to publish stream")


@router.post("/extract-entities", response_model=ChatEntityExtractionResponse)
async def extract_entities_from_chat(
    request: ChatEntityExtractionRequest,
    current_user: str = Depends(get_current_user)
) -> ChatEntityExtractionResponse:
    """Extract entities from user chat message using intelligent conversation engine"""
    try:
        logger.info(f"Extracting entities from message by user {current_user}")

        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        # Initialize conversation engine
        engine = ConversationEngine()

        # Current wizard data state
        current_data = request.current_wizard_data or {}

        # Extract entities from message
        extracted_entities = engine.extract_entities_from_message(request.message)

        # Detect or confirm job type
        detected_job_type, job_confidence = engine.detect_job_type(
            request.message,
            request.conversation_context
        )

        # If we already have a job type from wizard data, use that
        existing_job_type = current_data.get("jobType")
        if existing_job_type:
            # Map string to enum
            job_type_map = {
                "sap": JobType.SAP,
                "file_transfer": JobType.FILE_TRANSFER,
                "standard": JobType.STANDARD
            }
            final_job_type = job_type_map.get(existing_job_type, detected_job_type)
        else:
            final_job_type = detected_job_type

        # Analyze current conversation state
        conversation_state = engine.analyze_current_state(current_data, final_job_type)

        # Update wizard data with extracted entities
        updated_wizard_data = current_data.copy()

        # Apply extracted entities to wizard data structure
        for entity in extracted_entities:
            if entity.field_name == "sap_system" and final_job_type == JobType.SAP:
                if "jobForm" not in updated_wizard_data:
                    updated_wizard_data["jobForm"] = {}
                updated_wizard_data["jobForm"]["sapSystem"] = entity.value

            elif entity.field_name == "report_name" and final_job_type == JobType.SAP:
                if "jobForm" not in updated_wizard_data:
                    updated_wizard_data["jobForm"] = {}
                updated_wizard_data["jobForm"]["reportName"] = entity.value

            elif entity.field_name == "file_path" and final_job_type == JobType.FILE_TRANSFER:
                if "jobForm" not in updated_wizard_data:
                    updated_wizard_data["jobForm"] = {}
                # Determine if this is source or target based on context
                if not updated_wizard_data["jobForm"].get("sourcePath"):
                    updated_wizard_data["jobForm"]["sourcePath"] = entity.value
                elif not updated_wizard_data["jobForm"].get("targetPath"):
                    updated_wizard_data["jobForm"]["targetPath"] = entity.value

            elif entity.field_name == "script_name" and final_job_type == JobType.STANDARD:
                if "jobForm" not in updated_wizard_data:
                    updated_wizard_data["jobForm"] = {}
                updated_wizard_data["jobForm"]["scriptPath"] = entity.value

        # Set job type if newly detected
        if final_job_type and not updated_wizard_data.get("jobType"):
            updated_wizard_data["jobType"] = final_job_type.value

            # Initialize basic structure
            if "streamProperties" not in updated_wizard_data:
                updated_wizard_data["streamProperties"] = {
                    "streamName": f"{final_job_type.value.replace('_', ' ').title()} Job (via Chat)",
                    "description": "Via Chat erstellt"
                }
            if "jobForm" not in updated_wizard_data:
                updated_wizard_data["jobForm"] = {"jobType": final_job_type.value}

        # Generate contextual response
        bot_response, suggested_questions = engine.generate_contextual_response(
            extracted_entities, conversation_state, request.message
        )

        # Calculate confidence score
        confidence_score = max(job_confidence, max([e.confidence for e in extracted_entities] + [0.0]))

        # Re-analyze state after updates
        final_state = engine.analyze_current_state(updated_wizard_data, final_job_type)

        return ChatEntityExtractionResponse(
            extracted_entities=updated_wizard_data if updated_wizard_data != current_data else None,
            suggested_job_type=final_job_type,
            bot_response=bot_response,
            confidence_score=confidence_score,
            requires_clarification=final_state.completion_percentage < 1.0,
            conversation_state=final_state,
            next_suggested_questions=suggested_questions
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting entities: {str(e)}")
        logger.exception("Full stacktrace:")
        raise HTTPException(status_code=500, detail="Failed to extract entities")