"""
LangExtract Chat Router
🚀 Moderne, streamlined API für LangExtract-First Streamworks System
Ersetzt alle alten Chat-Router mit cleaner Architektur
"""

import logging
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

# New LangExtract System
from services.ai.langextract.unified_langextract_service import get_unified_langextract_service
from models.langextract_models import (
    LangExtractRequest,
    LangExtractResponse,
    XMLGenerationRequest,
    XMLGenerationResponse,
    ParameterCorrectionRequest,
    ParameterCorrectionResponse
)

# XML Stream Integration
from services.xml_stream_service import XMLStreamService

logger = logging.getLogger(__name__)

# Router Setup
router = APIRouter(prefix="/api/streamworks", tags=["Streamworks LangExtract"])

# Service Instance
langextract_service = get_unified_langextract_service()


# ================================
# SESSION MANAGEMENT
# ================================

@router.post("/sessions", response_model=dict)
async def create_session(job_type: Optional[str] = None):
    """
    🚀 Create new Streamworks session

    Args:
        job_type: Optional job type (SAP, FILE_TRANSFER, STANDARD)

    Returns:
        Session info with initial message
    """
    try:
        session = await langextract_service.create_session(job_type=job_type)

        # Generate welcome message
        if job_type:
            welcome_message = f"Hallo! 👋 Hier ist SKI - Ihr Streamworks KI-Assistent. Lassen Sie uns gemeinsam Ihren {job_type} Stream konfigurieren. Beschreiben Sie einfach, was Sie erreichen möchten!"
        else:
            welcome_message = "Hallo! 👋 Hier ist SKI - Ihr Streamworks KI-Assistent. Beschreiben Sie mir Ihren gewünschten Stream und ich extrahiere automatisch alle Parameter für Sie. Lassen Sie uns beginnen!"

        return {
            "session_id": session.session_id,
            "job_type": session.job_type,
            "state": session.state.value,
            "message": welcome_message,
            "created_at": session.created_at.isoformat(),
            "suggested_questions": [
                "💾 SAP Datenexport konfigurieren",
                "🔄 Server-zu-Server Datentransfer einrichten",
                "⚙️ Standard Verarbeitungsjob erstellen"
            ]
        }

    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail=f"Session creation failed: {str(e)}")


@router.post("/sessions/from-stream/{stream_id}", response_model=dict)
async def create_session_from_stream(stream_id: str):
    """
    🔄 Create LangExtract session from existing XML Stream

    Loads an existing XML Stream and creates a new LangExtract session
    with the stream's parameters pre-loaded for editing.

    Args:
        stream_id: UUID of the XML Stream to load

    Returns:
        Session info with stream parameters loaded
    """
    try:
        # Load XML Stream
        xml_service = XMLStreamService()
        stream = await xml_service.get_stream(stream_id)

        if not stream:
            raise HTTPException(status_code=404, detail=f"Stream {stream_id} not found")

        logger.info(f"🔄 Loading stream for editing: {stream.stream_name} (Job Type: {stream.job_type})")

        # Create new LangExtract session with stream's job type
        session = await langextract_service.create_session(job_type=stream.job_type)

        # Load stream parameters into session if available
        if stream.wizard_data and isinstance(stream.wizard_data, dict):
            stream_params = stream.wizard_data.get('stream_parameters', {})
            job_params = stream.wizard_data.get('job_parameters', {})

            if stream_params:
                # Update session with stream parameters
                for param_name, param_value in stream_params.items():
                    await langextract_service.update_stream_parameter(
                        session.session_id, param_name, param_value
                    )
                logger.info(f"✅ Loaded {len(stream_params)} stream parameters")

            if job_params:
                # Update session with job parameters
                for param_name, param_value in job_params.items():
                    await langextract_service.update_job_parameter(
                        session.session_id, param_name, param_value
                    )
                logger.info(f"✅ Loaded {len(job_params)} job parameters")

        # Generate welcome message for stream editing
        welcome_message = f"🔄 Stream '{stream.stream_name}' wurde geladen! Sie können jetzt die Parameter bearbeiten und anpassen. Alle vorhandenen Parameter wurden in diese Session übertragen."

        return {
            "session_id": session.session_id,
            "job_type": session.job_type,
            "state": session.state.value,
            "message": welcome_message,
            "created_at": session.created_at.isoformat(),
            "source_stream": {
                "id": stream.id,
                "name": stream.stream_name,
                "description": stream.description
            },
            "suggested_questions": [
                f"📝 Parameter für {stream.stream_name} anpassen",
                "🔧 Zusätzliche Parameter hinzufügen",
                "✅ XML für diesen Stream generieren"
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating session from stream {stream_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create session from stream: {str(e)}")


@router.get("/sessions/as-streams", response_model=dict)
async def get_sessions_as_streams(
    limit: int = 50,
    offset: int = 0,
    search: Optional[str] = None,
    job_types: Optional[str] = None,
    statuses: Optional[str] = None,
    sort_by: str = "updated_desc"
):
    """
    🔄 Get LangExtract Sessions formatted as XML Streams

    Returns LangExtract sessions in the same format as XML streams
    for seamless integration with the stream management UI.

    Args:
        limit: Number of sessions to return (default: 50)
        offset: Offset for pagination (default: 0)
        search: Search term for stream names/descriptions
        job_types: Comma-separated job types to filter
        statuses: Comma-separated statuses to filter
        sort_by: Sort order (updated_desc, created_desc, name_asc, etc.)

    Returns:
        Stream-formatted list of LangExtract sessions
    """
    try:
        logger.info(f"🔄 Fetching LangExtract sessions as streams: limit={limit}, offset={offset}")

        # Get all sessions from LangExtract service (persistent + in-memory)
        persistent_sessions = await langextract_service.list_sessions(limit=limit * 2)  # Get more to filter
        logger.info(f"📋 Found {len(persistent_sessions)} persistent sessions")

        # Also get active in-memory sessions if persistence is disabled
        in_memory_sessions = []
        if hasattr(langextract_service, 'sessions') and langextract_service.sessions:
            for session_id, session in langextract_service.sessions.items():
                in_memory_sessions.append({
                    "session_id": session_id,
                    "stream_name": session.stream_parameters.get("StreamName", "Unnamed Stream"),
                    "job_type": session.job_type,
                    "created_at": session.created_at.isoformat() if hasattr(session.created_at, 'isoformat') else str(session.created_at),
                    "last_activity": session.last_activity.isoformat() if hasattr(session.last_activity, 'isoformat') else str(session.last_activity)
                })

        # Combine both sources, prioritizing persistent sessions
        all_sessions = persistent_sessions + [s for s in in_memory_sessions if s['session_id'] not in [ps.get('session_id') for ps in persistent_sessions]]
        logger.info(f"🔍 Found {len(in_memory_sessions)} in-memory sessions")
        logger.info(f"📊 Total sessions to process: {len(all_sessions)}")

        # Convert sessions to stream format
        streams = []
        for session_data in all_sessions:
            try:
                session_id = session_data.get('session_id', '')
                logger.info(f"🔄 Processing session {session_id} for stream conversion")

                # Get detailed session info
                session_detail = await langextract_service.get_session_info(session_id)
                logger.info(f"📊 Session detail keys: {list(session_detail.keys()) if session_detail else 'None'}")

                # Extract parameters for stream metadata - different structure!
                session_params = session_detail.get('stream_parameters', {})
                job_params = session_detail.get('job_parameters', {})
                logger.info(f"📋 Stream params: {list(session_params.keys())}, Job params: {list(job_params.keys())}")

                # Determine stream name and description
                stream_name = session_params.get('StreamName') or session_params.get('streamName') or f"Session {session_data.get('session_id', '')[:8]}"

                # Count parameters for intelligent description
                total_params = len(session_params) + len(job_params)
                critical_missing = session_detail.get('critical_missing', [])
                missing_count = len(critical_missing)

                # Create intelligent description
                if total_params >= 5:
                    description = f"Vollständig konfiguriert • {total_params} Parameter extrahiert"
                elif total_params >= 2:
                    description = f"Grundkonfiguration vorhanden • {total_params} Parameter"
                elif total_params > 0:
                    description = f"Erste Parameter erkannt • {total_params} Parameter"
                else:
                    description = "Neue Session • Noch keine Parameter"

                # Determine and humanize job type
                raw_job_type = session_detail.get('job_type')
                if raw_job_type == 'FILE_TRANSFER':
                    job_type = 'FILE_TRANSFER'
                    job_type_display = '📁 Datentransfer'
                elif raw_job_type == 'SAP':
                    job_type = 'SAP'
                    job_type_display = '🏢 SAP Integration'
                elif raw_job_type == 'STANDARD':
                    job_type = 'STANDARD'
                    job_type_display = '⚙️ Standard Job'
                else:
                    job_type = 'UNKNOWN'
                    job_type_display = '❓ Typ nicht erkannt'

                # Determine status based on parameter completeness
                if total_params >= 5 and missing_count == 0:
                    status = "parameter_complete"
                elif total_params >= 2 and missing_count <= 2:
                    status = "parameter_partial"
                elif total_params > 0:
                    status = "parameter_minimal"
                else:
                    status = "parameter_empty"

                # Calculate completion percentage
                estimated_total = max(8, total_params + missing_count)  # Estimate based on job type
                completion_percentage = min(100, int((total_params / estimated_total) * 100))

                # Create informative tags
                tags = []

                # Add human-readable job type
                if raw_job_type:
                    tags.append(job_type_display)

                # Add parameter information
                if total_params > 0:
                    tags.append(f"{total_params} Parameter")

                # Add completion status (only if meaningful)
                if completion_percentage >= 50:
                    tags.append(f"{completion_percentage}% vollständig")

                # Add session age indicator (based on actual created_at from session_data)
                from datetime import datetime, timezone
                created_at = session_data.get('created_at', '')  # Use session_data, not session_detail
                if created_at:
                    try:
                        # Handle both timestamp formats
                        if '+' in created_at or 'Z' in created_at:
                            created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        else:
                            created_time = datetime.fromisoformat(created_at + '+00:00')

                        now = datetime.now(timezone.utc)
                        diff = now - created_time

                        if diff.days == 0:
                            if diff.seconds < 3600:  # Less than 1 hour
                                tags.append("Vor kurzer Zeit")
                            else:
                                tags.append("Heute erstellt")
                        elif diff.days == 1:
                            tags.append("Gestern erstellt")
                        elif diff.days <= 7:
                            tags.append("Diese Woche")
                        else:
                            tags.append("Älter")
                    except Exception as e:
                        logger.warning(f"Could not parse created_at: {created_at}, error: {e}")
                        pass

                # Create stream-like object with enhanced metadata
                stream = {
                    "id": session_data.get('session_id'),
                    "stream_name": stream_name,
                    "description": description,
                    "xml_content": None,  # Will be generated on-demand
                    "wizard_data": {
                        "stream_parameters": session_params,
                        "job_parameters": job_params,
                        "session_source": "langextract",
                        "total_parameters": total_params,
                        "completion_percentage": completion_percentage,
                        "missing_parameters": missing_count,
                        "job_type_display": job_type_display
                    },
                    "job_type": job_type,
                    "status": status,
                    "created_by": "AI Assistant",
                    "created_at": session_data.get('created_at', ''),
                    "updated_at": session_detail.get('last_activity', session_data.get('created_at', '')),
                    "last_generated_at": None,
                    "tags": tags,
                    "is_favorite": False,
                    "version": 1,
                    "template_id": None,
                    # Additional metadata for better display
                    "completion_percentage": completion_percentage,
                    "parameter_count": total_params,
                    "job_type_display": job_type_display
                }

                streams.append(stream)

            except Exception as e:
                logger.error(f"Error converting session {session_data.get('session_id')} to stream: {e}")
                continue

        # Apply filtering
        filtered_streams = streams

        # Search filter
        if search:
            search_lower = search.lower()
            filtered_streams = [
                s for s in filtered_streams
                if search_lower in s["stream_name"].lower()
                or search_lower in s["description"].lower()
            ]

        # Job type filter
        if job_types:
            job_type_list = [jt.strip() for jt in job_types.split(',')]
            filtered_streams = [s for s in filtered_streams if s["job_type"] in job_type_list]

        # Status filter
        if statuses:
            status_list = [st.strip() for st in statuses.split(',')]
            filtered_streams = [s for s in filtered_streams if s["status"] in status_list]

        # Apply sorting
        if sort_by == "updated_desc":
            filtered_streams.sort(key=lambda x: x["updated_at"], reverse=True)
        elif sort_by == "updated_asc":
            filtered_streams.sort(key=lambda x: x["updated_at"])
        elif sort_by == "created_desc":
            filtered_streams.sort(key=lambda x: x["created_at"], reverse=True)
        elif sort_by == "created_asc":
            filtered_streams.sort(key=lambda x: x["created_at"])
        elif sort_by == "name_asc":
            filtered_streams.sort(key=lambda x: x["stream_name"])
        elif sort_by == "name_desc":
            filtered_streams.sort(key=lambda x: x["stream_name"], reverse=True)

        # Apply pagination
        total_count = len(filtered_streams)
        paginated_streams = filtered_streams[offset:offset + limit]
        has_more = offset + limit < total_count

        logger.info(f"✅ Converted {len(paginated_streams)} LangExtract sessions to streams (total: {total_count})")

        return {
            "streams": paginated_streams,
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": has_more
        }

    except Exception as e:
        logger.error(f"Error fetching sessions as streams: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch sessions as streams: {str(e)}")


@router.get("/debug/sessions", response_model=dict)
async def debug_sessions():
    """
    🐛 Debug endpoint to see all sessions
    """
    try:
        # Check persistent sessions
        persistent = await langextract_service.list_sessions(limit=50)

        # Check in-memory sessions
        in_memory = []
        if hasattr(langextract_service, 'sessions'):
            in_memory = list(langextract_service.sessions.keys())

        # Test converting first session
        converted_stream = None
        if persistent:
            first_session = persistent[0]
            session_detail = await langextract_service.get_session_info(first_session['session_id'])
            converted_stream = {
                "session_detail_keys": list(session_detail.keys()) if session_detail else [],
                "session_detail": session_detail
            }

        return {
            "persistent_sessions": persistent,
            "in_memory_session_ids": in_memory,
            "service_type": type(langextract_service).__name__,
            "test_conversion": converted_stream
        }
    except Exception as e:
        return {"error": str(e)}


@router.get("/sessions/{session_id}", response_model=dict)
async def get_session(session_id: str):
    """
    📊 Get session status and current parameters

    Args:
        session_id: Session identifier

    Returns:
        Complete session state
    """
    try:
        session_info = await langextract_service.get_session_info(session_id)
        if not session_info:
            raise HTTPException(status_code=404, detail="Session not found")

        return session_info

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get session: {str(e)}")


# ================================
# MESSAGE PROCESSING
# ================================

@router.get("/sessions/{session_id}/messages", response_model=dict)
async def get_session_messages(session_id: str):
    """
    💬 Get all messages for a session

    Args:
        session_id: Session identifier

    Returns:
        List of session messages with metadata
    """
    try:
        session_info = await langextract_service.get_session_info(session_id)
        if not session_info:
            raise HTTPException(status_code=404, detail="Session not found")

        # Get session to access messages
        session = await langextract_service._get_session_async(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Convert messages to serializable format
        messages = []
        for msg in session.messages:
            messages.append({
                "type": msg.type,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat() if hasattr(msg.timestamp, 'isoformat') else str(msg.timestamp)
            })

        return {
            "session_id": session_id,
            "messages": messages,
            "total_messages": len(messages),
            "last_activity": session_info["last_activity"]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting messages for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get messages: {str(e)}")


@router.post("/sessions/{session_id}/messages", response_model=LangExtractResponse)
async def send_message(session_id: str, request: LangExtractRequest):
    """
    🎯 Process user message with LangExtract

    Args:
        session_id: Session identifier
        request: User message and context

    Returns:
        Complete LangExtract response with extracted parameters
    """
    try:
        logger.info(f"🔍 Processing message for session {session_id}: '{request.message[:50]}...'")

        # Process message with LangExtract
        response = await langextract_service.process_message(
            session_id=session_id,
            user_message=request.message
        )

        logger.info(f"✅ Message processed successfully: {len(response.extracted_stream_parameters) + len(response.extracted_job_parameters)} parameters")

        return response

    except ValueError as e:
        logger.warning(f"Invalid request for session {session_id}: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing message for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Message processing failed: {str(e)}")


# ================================
# PARAMETER MANAGEMENT
# ================================

@router.get("/sessions/{session_id}/parameters", response_model=dict)
async def get_parameters(session_id: str):
    """
    📋 Get all extracted parameters for session

    Args:
        session_id: Session identifier

    Returns:
        All stream and job parameters with metadata
    """
    try:
        session_info = await langextract_service.get_session_info(session_id)
        if not session_info:
            raise HTTPException(status_code=404, detail="Session not found")

        return {
            "session_id": session_id,
            "job_type": session_info["job_type"],
            "stream_parameters": session_info["stream_parameters"],
            "job_parameters": session_info["job_parameters"],
            "critical_missing": session_info["critical_missing"],
            "total_parameters": len(session_info["stream_parameters"]) + len(session_info["job_parameters"]),
            "last_updated": session_info["last_activity"]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting parameters for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get parameters: {str(e)}")


@router.post("/sessions/{session_id}/parameters/correct", response_model=ParameterCorrectionResponse)
async def correct_parameter(session_id: str, request: ParameterCorrectionRequest):
    """
    ✏️ Correct an extracted parameter

    Args:
        session_id: Session identifier
        request: Parameter correction details

    Returns:
        Correction result and impact
    """
    try:
        session = await langextract_service._get_session_async(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Apply correction
        if request.parameter_name in session.stream_parameters:
            session.stream_parameters[request.parameter_name] = request.new_value
            parameter_scope = "stream"
        elif request.parameter_name in session.job_parameters:
            session.job_parameters[request.parameter_name] = request.new_value
            parameter_scope = "job"
        else:
            raise HTTPException(status_code=404, detail=f"Parameter {request.parameter_name} not found")

        session.last_activity = datetime.now()

        # Save updated session
        await langextract_service._save_session_async(session)

        logger.info(f"✏️ Parameter corrected: {request.parameter_name} = {request.new_value}")

        return ParameterCorrectionResponse(
            session_id=session_id,
            parameter_name=request.parameter_name,
            correction_applied=True,
            updated_confidence=1.0,  # User corrections have full confidence
            impact_on_other_parameters=[]  # Could be enhanced later
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error correcting parameter in session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Parameter correction failed: {str(e)}")


# ================================
# XML GENERATION
# ================================

@router.post("/sessions/{session_id}/generate-xml", response_model=XMLGenerationResponse)
async def generate_xml(session_id: str, request: XMLGenerationRequest):
    """
    🏗️ Generate Streamworks XML from extracted parameters

    Args:
        session_id: Session identifier
        request: XML generation options

    Returns:
        Generated XML content or validation errors
    """
    try:
        session = await langextract_service._get_session_async(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Check if sufficient parameters are available
        total_params = len(session.stream_parameters) + len(session.job_parameters)
        if not request.force_generation and total_params < 3:
            return XMLGenerationResponse(
                session_id=session_id,
                xml_content="",
                generation_successful=False,
                validation_errors=[
                    f"Unzureichende Parameter für XML-Generierung (nur {total_params} Parameter vorhanden)",
                    "Verwenden Sie force_generation=true um trotzdem zu generieren"
                ],
                missing_parameters=session.critical_missing
            )

        # Generate XML
        xml_result = await langextract_service.generate_xml(session_id)

        if xml_result.get("success"):
            xml_content = xml_result.get("xml_content", "")
            logger.info(f"✅ XML generated successfully for session {session_id}")

            return XMLGenerationResponse(
                session_id=session_id,
                xml_content=xml_content,
                generation_successful=True,
                used_parameters={
                    **session.stream_parameters,
                    **session.job_parameters
                }
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"XML generation failed: {xml_result.get('error', 'Unknown error')}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating XML for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"XML generation failed: {str(e)}")


# ================================
# SESSION LISTING & MANAGEMENT
# ================================

@router.get("/sessions", response_model=dict)
async def list_sessions(limit: int = 50):
    """
    📋 List recent sessions

    Args:
        limit: Maximum number of sessions to return

    Returns:
        List of session summaries
    """
    try:
        sessions = await langextract_service.list_sessions(limit=limit)

        return {
            "sessions": sessions,
            "total_count": len(sessions),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list sessions: {str(e)}")


@router.delete("/sessions/{session_id}", response_model=dict)
async def delete_session(session_id: str):
    """
    🗑️ Delete a session

    Args:
        session_id: Session identifier

    Returns:
        Deletion status
    """
    try:
        success = await langextract_service.delete_session(session_id)

        if not success:
            raise HTTPException(status_code=404, detail="Session not found")

        return {
            "session_id": session_id,
            "deleted": True,
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")


@router.delete("/sessions", response_model=dict)
async def delete_all_sessions():
    """
    🗑️ Delete ALL sessions (bulk delete)

    Returns:
        Bulk deletion status with count
    """
    try:
        # Get all sessions first
        sessions = await langextract_service.list_sessions(limit=1000)
        session_count = len(sessions)

        if session_count == 0:
            return {
                "deleted_count": 0,
                "message": "No sessions to delete",
                "timestamp": datetime.now().isoformat()
            }

        # Delete all sessions
        deleted_count = 0
        failed_deletions = []

        for session in sessions:
            try:
                success = await langextract_service.delete_session(session["session_id"])
                if success:
                    deleted_count += 1
                else:
                    failed_deletions.append(session["session_id"])
            except Exception as e:
                logger.warning(f"Failed to delete session {session['session_id']}: {e}")
                failed_deletions.append(session["session_id"])

        logger.info(f"🗑️ Bulk delete completed: {deleted_count}/{session_count} sessions deleted")

        result = {
            "deleted_count": deleted_count,
            "total_sessions": session_count,
            "success_rate": round((deleted_count / session_count) * 100, 1) if session_count > 0 else 100,
            "timestamp": datetime.now().isoformat()
        }

        if failed_deletions:
            result["failed_deletions"] = failed_deletions
            result["warning"] = f"{len(failed_deletions)} sessions could not be deleted"

        return result

    except Exception as e:
        logger.error(f"Error during bulk session deletion: {e}")
        raise HTTPException(status_code=500, detail=f"Bulk deletion failed: {str(e)}")


# ================================
# ANALYTICS & MONITORING
# ================================

@router.get("/analytics/sessions", response_model=dict)
async def get_session_analytics():
    """
    📊 Get analytics for all sessions

    Returns:
        Session statistics and performance metrics
    """
    try:
        # Get session list for analytics
        sessions = await langextract_service.list_sessions(limit=1000)
        total_sessions = len(sessions)

        if total_sessions == 0:
            return {
                "total_sessions": 0,
                "active_sessions": 0,
                "completed_sessions": 0,
                "average_completion": 0.0,
                "job_type_distribution": {}
            }

        # Calculate statistics
        completed_sessions = sum(1 for s in sessions if len(s.get("stream_parameters", {})) >= 3)
        active_sessions = total_sessions - completed_sessions

        job_type_dist = {}
        for session in sessions:
            if session.get("job_type"):
                job_type = session["job_type"]
                job_type_dist[job_type] = job_type_dist.get(job_type, 0) + 1

        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "completed_sessions": completed_sessions,
            "job_type_distribution": job_type_dist,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Analytics failed: {str(e)}")


# ================================
# HEALTH & STATUS
# ================================

@router.get("/health", response_model=dict)
async def health_check():
    """
    🏥 Health check for LangExtract service

    Returns:
        Service status and capabilities
    """
    try:
        return {
            "status": "healthy",
            "service": "Streamworks LangExtract",
            "version": "2.0.0",
            "capabilities": [
                "LangExtract Parameter Extraction",
                "Source Grounding",
                "Multi-job-type Support",
                "Real-time Session Management",
                "XML Generation"
            ],
            "memory_sessions": len(langextract_service.sessions),
            "persistence_enabled": langextract_service.persistence_service.is_enabled(),
            "schemas_loaded": len(langextract_service.schemas),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


# ================================
# DEVELOPMENT & TESTING
# ================================

@router.post("/test/extract", response_model=dict)
async def test_extraction(message: str, job_type: Optional[str] = None):
    """
    🧪 Test LangExtract without creating a session

    For development and testing purposes only
    """
    try:
        # Create temporary session
        session = await langextract_service.create_session(job_type=job_type)

        # Process message
        response = await langextract_service.process_message(
            session_id=session.session_id,
            user_message=message
        )

        # Return results
        return {
            "test_message": message,
            "detected_job_type": session.job_type,
            "extracted_stream_parameters": response.extracted_stream_parameters,
            "extracted_job_parameters": response.extracted_job_parameters,
            "source_grounding": response.source_grounding_data,
            "processing_time": response.processing_time
        }

    except Exception as e:
        logger.error(f"Test extraction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")


# ================================
# ERROR HANDLERS
# ================================

# Note: Exception handlers are defined at the app level in main.py
# APIRouter doesn't support exception handlers directly