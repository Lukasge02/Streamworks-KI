"""
Chat XML Database Service - Phase 3+ Enterprise Integration
Persistente Speicherung und Verwaltung von Chat-XML Sessions und Parameter-History
"""

import logging
import uuid
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from sqlalchemy import select, update, delete, and_, or_, desc, asc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from models.core import ChatXMLSession, ChatXMLMessage
from database import get_async_session

logger = logging.getLogger(__name__)

@dataclass
class SessionSearchFilters:
    """Filter-Optionen für Session-Suche"""
    user_id: Optional[str] = None
    job_type: Optional[str] = None
    status: Optional[str] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    is_active: Optional[bool] = None
    completion_percentage_min: Optional[float] = None
    completion_percentage_max: Optional[float] = None

@dataclass
class ParameterHistoryEntry:
    """Entry für Parameter-History Tracking"""
    timestamp: datetime
    parameter_name: str
    old_value: Any
    new_value: Any
    extraction_method: str
    confidence_score: float
    user_action: bool = False  # True wenn User manuell geändert, False wenn AI extrahiert

@dataclass
class SessionMetrics:
    """Session-Metriken für Analytics"""
    total_sessions: int
    active_sessions: int
    completed_sessions: int
    average_completion_time: Optional[float]
    average_parameter_accuracy: Optional[float]
    most_common_job_types: List[Tuple[str, int]]
    error_rate: float

class ChatXMLDatabaseService:
    """
    Enterprise Database Service für Chat-XML System

    Features:
    - Session Lifecycle Management
    - Parameter History Tracking
    - Performance Analytics
    - Data Retention Policies
    - Search und Filtering
    """

    def __init__(self):
        """Initialize Chat XML Database Service"""
        self.initialized = False

        # Configuration
        self.session_timeout_hours = 24
        self.max_parameter_history_entries = 1000
        self.data_retention_days = 365

        logger.info("Chat XML Database Service initialized")

    async def initialize(self) -> None:
        """Initialisiert den Database Service"""
        try:
            # Test database connection
            async with get_async_session() as session:
                await session.execute(select(ChatXMLSession).limit(1))

            self.initialized = True
            logger.info("Chat XML Database Service fully initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Chat XML Database Service: {str(e)}")
            raise

    # ================================
    # SESSION MANAGEMENT
    # ================================

    async def create_session(
        self,
        user_id: str,
        job_type: str,
        session_name: Optional[str] = None,
        initial_parameters: Optional[Dict[str, Any]] = None
    ) -> ChatXMLSession:
        """Erstellt eine neue Chat-XML Session"""

        session_name = session_name or f"{job_type} Session {datetime.now().strftime('%Y-%m-%d %H:%M')}"

        session = ChatXMLSession(
            id=uuid.uuid4(),
            session_name=session_name,
            user_id=user_id,
            job_type=job_type,
            status="PARAMETER_COLLECTION",
            completion_percentage=0.0,
            collected_parameters=initial_parameters or {},
            parameter_history=[],
            validation_errors=[],
            ai_extraction_metadata={},
            xml_generation_metadata={},
            is_active=True,
            retry_count=0
        )

        async with get_async_session() as db_session:
            db_session.add(session)
            await db_session.commit()
            await db_session.refresh(session)

        logger.info(f"Created Chat-XML session: {session.id} for user: {user_id}")
        return session

    async def get_session(
        self,
        session_id: uuid.UUID,
        include_messages: bool = False
    ) -> Optional[ChatXMLSession]:
        """Lädt eine Session mit optionalen Messages"""

        async with get_async_session() as db_session:
            query = select(ChatXMLSession).where(ChatXMLSession.id == session_id)

            if include_messages:
                query = query.options(selectinload(ChatXMLSession.xml_messages))

            result = await db_session.execute(query)
            return result.scalar_one_or_none()

    async def update_session_parameters(
        self,
        session_id: uuid.UUID,
        parameters: Dict[str, Any],
        extraction_metadata: Optional[Dict[str, Any]] = None,
        completion_percentage: Optional[float] = None
    ) -> bool:
        """Aktualisiert Session-Parameter mit History-Tracking"""

        async with get_async_session() as db_session:
            # Load current session
            session = await db_session.get(ChatXMLSession, session_id)
            if not session:
                return False

            # Track parameter changes in history
            current_parameters = session.collected_parameters or {}
            parameter_history = list(session.parameter_history or [])

            for param_name, new_value in parameters.items():
                old_value = current_parameters.get(param_name)
                if old_value != new_value:
                    # Add to parameter history
                    history_entry = {
                        "timestamp": datetime.utcnow().isoformat(),
                        "parameter_name": param_name,
                        "old_value": old_value,
                        "new_value": new_value,
                        "extraction_method": extraction_metadata.get("extraction_method", "unknown") if extraction_metadata else "manual",
                        "confidence_score": extraction_metadata.get("confidence_scores", {}).get(param_name, 0.0) if extraction_metadata else 1.0,
                        "user_action": extraction_metadata is None
                    }
                    parameter_history.append(history_entry)

            # Limit history size
            if len(parameter_history) > self.max_parameter_history_entries:
                parameter_history = parameter_history[-self.max_parameter_history_entries:]

            # Update session
            update_data = {
                "collected_parameters": {**current_parameters, **parameters},
                "parameter_history": parameter_history,
                "last_activity_at": datetime.utcnow()
            }

            if extraction_metadata:
                current_ai_metadata = session.ai_extraction_metadata or {}
                current_ai_metadata.update(extraction_metadata)
                update_data["ai_extraction_metadata"] = current_ai_metadata

            if completion_percentage is not None:
                update_data["completion_percentage"] = completion_percentage

            await db_session.execute(
                update(ChatXMLSession)
                .where(ChatXMLSession.id == session_id)
                .values(**update_data)
            )
            await db_session.commit()

        logger.info(f"Updated parameters for session {session_id}: {list(parameters.keys())}")
        return True

    async def update_session_status(
        self,
        session_id: uuid.UUID,
        status: str,
        xml_content: Optional[str] = None,
        xml_metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Aktualisiert Session-Status und XML-Content"""

        async with get_async_session() as db_session:
            update_data = {
                "status": status,
                "last_activity_at": datetime.utcnow()
            }

            if status == "COMPLETED":
                update_data["completed_at"] = datetime.utcnow()
                update_data["completion_percentage"] = 100.0

            if xml_content is not None:
                update_data["generated_xml"] = xml_content

            if xml_metadata is not None:
                update_data["xml_generation_metadata"] = xml_metadata

            result = await db_session.execute(
                update(ChatXMLSession)
                .where(ChatXMLSession.id == session_id)
                .values(**update_data)
            )
            await db_session.commit()

            return result.rowcount > 0

    async def deactivate_session(self, session_id: uuid.UUID) -> bool:
        """Deaktiviert eine Session"""

        async with get_async_session() as db_session:
            result = await db_session.execute(
                update(ChatXMLSession)
                .where(ChatXMLSession.id == session_id)
                .values(is_active=False, last_activity_at=datetime.utcnow())
            )
            await db_session.commit()
            return result.rowcount > 0

    # ================================
    # MESSAGE MANAGEMENT
    # ================================

    async def add_message(
        self,
        session_id: uuid.UUID,
        message_type: str,
        content: str,
        role: str,
        extracted_parameters: Optional[Dict[str, Any]] = None,
        ai_metadata: Optional[Dict[str, Any]] = None
    ) -> ChatXMLMessage:
        """Fügt eine neue Message zur Session hinzu"""

        message = ChatXMLMessage(
            id=uuid.uuid4(),
            session_id=session_id,
            message_type=message_type,
            content=content,
            role=role,
            extracted_parameters=extracted_parameters or {},
            parameter_confidence_scores=ai_metadata.get("confidence_scores", {}) if ai_metadata else {},
            extraction_method=ai_metadata.get("extraction_method") if ai_metadata else None,
            ai_processing_metadata=ai_metadata or {},
            suggestions=ai_metadata.get("suggestions", []) if ai_metadata else [],
            validation_errors=ai_metadata.get("validation_errors", []) if ai_metadata else [],
            precision_score=ai_metadata.get("precision_score") if ai_metadata else None,
            completeness_score=ai_metadata.get("completeness_score") if ai_metadata else None,
            consistency_score=ai_metadata.get("consistency_score") if ai_metadata else None,
            parameter_name=ai_metadata.get("parameter_name") if ai_metadata else None,
            processing_time_ms=ai_metadata.get("processing_time_ms") if ai_metadata else None
        )

        async with get_async_session() as db_session:
            db_session.add(message)
            await db_session.commit()
            await db_session.refresh(message)

        return message

    async def get_session_messages(
        self,
        session_id: uuid.UUID,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[ChatXMLMessage]:
        """Lädt Messages einer Session"""

        async with get_async_session() as db_session:
            query = (
                select(ChatXMLMessage)
                .where(ChatXMLMessage.session_id == session_id)
                .order_by(ChatXMLMessage.created_at.asc())
            )

            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)

            result = await db_session.execute(query)
            return result.scalars().all()

    # ================================
    # SEARCH AND FILTERING
    # ================================

    async def search_sessions(
        self,
        filters: SessionSearchFilters,
        limit: Optional[int] = 50,
        offset: Optional[int] = 0
    ) -> List[ChatXMLSession]:
        """Sucht Sessions basierend auf Filtern"""

        async with get_async_session() as db_session:
            query = select(ChatXMLSession)

            # Apply filters
            conditions = []

            if filters.user_id:
                conditions.append(ChatXMLSession.user_id == filters.user_id)

            if filters.job_type:
                conditions.append(ChatXMLSession.job_type == filters.job_type)

            if filters.status:
                conditions.append(ChatXMLSession.status == filters.status)

            if filters.is_active is not None:
                conditions.append(ChatXMLSession.is_active == filters.is_active)

            if filters.created_after:
                conditions.append(ChatXMLSession.created_at >= filters.created_after)

            if filters.created_before:
                conditions.append(ChatXMLSession.created_at <= filters.created_before)

            if filters.completion_percentage_min is not None:
                conditions.append(ChatXMLSession.completion_percentage >= filters.completion_percentage_min)

            if filters.completion_percentage_max is not None:
                conditions.append(ChatXMLSession.completion_percentage <= filters.completion_percentage_max)

            if conditions:
                query = query.where(and_(*conditions))

            query = query.order_by(desc(ChatXMLSession.last_activity_at))

            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)

            result = await db_session.execute(query)
            return result.scalars().all()

    async def get_user_sessions(
        self,
        user_id: str,
        active_only: bool = False,
        limit: Optional[int] = 20
    ) -> List[ChatXMLSession]:
        """Lädt Sessions eines Users"""

        filters = SessionSearchFilters(
            user_id=user_id,
            is_active=active_only if active_only else None
        )

        return await self.search_sessions(filters, limit=limit)

    # ================================
    # ANALYTICS AND METRICS
    # ================================

    async def get_session_metrics(
        self,
        user_id: Optional[str] = None,
        days_back: int = 30
    ) -> SessionMetrics:
        """Berechnet Session-Metriken für Analytics"""

        since_date = datetime.utcnow() - timedelta(days=days_back)

        async with get_async_session() as db_session:
            # Base query
            base_query = select(ChatXMLSession).where(ChatXMLSession.created_at >= since_date)

            if user_id:
                base_query = base_query.where(ChatXMLSession.user_id == user_id)

            # Total sessions
            result = await db_session.execute(base_query)
            all_sessions = result.scalars().all()

            total_sessions = len(all_sessions)
            active_sessions = len([s for s in all_sessions if s.is_active])
            completed_sessions = len([s for s in all_sessions if s.status == "COMPLETED"])

            # Average completion time
            completed_with_times = [
                s for s in all_sessions
                if s.status == "COMPLETED" and s.completed_at and s.created_at
            ]

            average_completion_time = None
            if completed_with_times:
                completion_times = [
                    (s.completed_at - s.created_at).total_seconds() / 60  # minutes
                    for s in completed_with_times
                ]
                average_completion_time = sum(completion_times) / len(completion_times)

            # Job type distribution
            from collections import Counter
            job_type_counts = Counter(s.job_type for s in all_sessions)
            most_common_job_types = job_type_counts.most_common()

            # Error rate
            error_sessions = len([s for s in all_sessions if s.status == "ERROR"])
            error_rate = error_sessions / total_sessions if total_sessions > 0 else 0.0

            # Average parameter accuracy (from AI metadata)
            accuracy_scores = []
            for session in all_sessions:
                ai_metadata = session.ai_extraction_metadata or {}
                if "average_confidence" in ai_metadata:
                    accuracy_scores.append(ai_metadata["average_confidence"])

            average_parameter_accuracy = None
            if accuracy_scores:
                average_parameter_accuracy = sum(accuracy_scores) / len(accuracy_scores)

        return SessionMetrics(
            total_sessions=total_sessions,
            active_sessions=active_sessions,
            completed_sessions=completed_sessions,
            average_completion_time=average_completion_time,
            average_parameter_accuracy=average_parameter_accuracy,
            most_common_job_types=most_common_job_types,
            error_rate=error_rate
        )

    # ================================
    # MAINTENANCE AND CLEANUP
    # ================================

    async def cleanup_expired_sessions(self) -> int:
        """Räumt abgelaufene Sessions auf"""

        timeout_threshold = datetime.utcnow() - timedelta(hours=self.session_timeout_hours)

        async with get_async_session() as db_session:
            # Mark inactive sessions as inactive
            result = await db_session.execute(
                update(ChatXMLSession)
                .where(
                    and_(
                        ChatXMLSession.last_activity_at < timeout_threshold,
                        ChatXMLSession.is_active == True,
                        ChatXMLSession.status.in_(["PARAMETER_COLLECTION", "VALIDATION"])
                    )
                )
                .values(is_active=False)
            )
            await db_session.commit()

            cleaned_count = result.rowcount

        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} expired Chat-XML sessions")

        return cleaned_count

    async def archive_old_sessions(self) -> int:
        """Archiviert alte Sessions basierend auf Retention Policy"""

        retention_threshold = datetime.utcnow() - timedelta(days=self.data_retention_days)

        async with get_async_session() as db_session:
            # For now, just mark very old sessions as inactive
            # In production, you might want to move to archive storage
            result = await db_session.execute(
                update(ChatXMLSession)
                .where(
                    and_(
                        ChatXMLSession.created_at < retention_threshold,
                        ChatXMLSession.is_active == True
                    )
                )
                .values(is_active=False)
            )
            await db_session.commit()

            archived_count = result.rowcount

        if archived_count > 0:
            logger.info(f"Archived {archived_count} old Chat-XML sessions")

        return archived_count

    async def get_parameter_learning_data(
        self,
        job_type: str,
        parameter_name: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Lädt Parameter-Learning Daten für AI-Verbesserung"""

        async with get_async_session() as db_session:
            # Get sessions with successful parameter extraction
            query = (
                select(ChatXMLSession)
                .where(
                    and_(
                        ChatXMLSession.job_type == job_type,
                        ChatXMLSession.collected_parameters.has_key(parameter_name),
                        ChatXMLSession.completion_percentage > 80
                    )
                )
                .order_by(desc(ChatXMLSession.created_at))
                .limit(limit)
            )

            result = await db_session.execute(query)
            sessions = result.scalars().all()

            learning_data = []
            for session in sessions:
                parameter_history = session.parameter_history or []
                relevant_entries = [
                    entry for entry in parameter_history
                    if entry.get("parameter_name") == parameter_name
                ]

                if relevant_entries:
                    learning_data.append({
                        "session_id": str(session.id),
                        "job_type": session.job_type,
                        "parameter_name": parameter_name,
                        "final_value": session.collected_parameters.get(parameter_name),
                        "extraction_history": relevant_entries,
                        "ai_metadata": session.ai_extraction_metadata
                    })

            return learning_data


# Singleton instance
_chat_xml_db_service = None

def get_chat_xml_database_service() -> ChatXMLDatabaseService:
    """Get Chat XML Database Service singleton"""
    global _chat_xml_db_service
    if _chat_xml_db_service is None:
        _chat_xml_db_service = ChatXMLDatabaseService()
    return _chat_xml_db_service