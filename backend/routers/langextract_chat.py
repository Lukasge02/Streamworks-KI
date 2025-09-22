"""
LangExtract Chat Router
🚀 Moderne, streamlined API für LangExtract-First StreamWorks System
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

logger = logging.getLogger(__name__)

# Router Setup
router = APIRouter(prefix="/api/streamworks", tags=["StreamWorks LangExtract"])

# Service Instance
langextract_service = get_unified_langextract_service()


# ================================
# SESSION MANAGEMENT
# ================================

@router.post("/sessions", response_model=dict)
async def create_session(job_type: Optional[str] = None):
    """
    🚀 Create new StreamWorks session

    Args:
        job_type: Optional job type (SAP, FILE_TRANSFER, STANDARD)

    Returns:
        Session info with initial message
    """
    try:
        session = await langextract_service.create_session(job_type=job_type)

        # Generate welcome message
        if job_type:
            welcome_message = f"Hallo! 👋 Hier ist SKI - Ihr StreamWorks KI-Assistent. Lassen Sie uns gemeinsam Ihren {job_type} Stream konfigurieren. Beschreiben Sie einfach, was Sie erreichen möchten!"
        else:
            welcome_message = "Hallo! 👋 Hier ist SKI - Ihr StreamWorks KI-Assistent. Beschreiben Sie mir Ihren gewünschten Stream und ich extrahiere automatisch alle Parameter für Sie. Lassen Sie uns beginnen!"

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
    🏗️ Generate StreamWorks XML from extracted parameters

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
            "service": "StreamWorks LangExtract",
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