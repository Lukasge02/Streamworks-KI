"""
Parameter State Manager - MVP Implementation
JSON Storage und State Management für Chat-Parameter
"""

import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

from models.parameter_models import (
    JOB_TYPE_MODEL_MAPPING,
    ParameterValidationResult,
    JobParameterCollection,
    ParameterExtractionHistory,
    create_parameter_instance,
    HierarchicalStreamSession,
    JobConfiguration,
    CompletionStatus,
    ParameterScope,
    split_parameters_by_scope
)

logger = logging.getLogger(__name__)

# ================================
# SESSION STATE MODELS
# ================================

class SessionStatus(str, Enum):
    """Status einer Parameter-Collection Session"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    EXPIRED = "expired"
    ERROR = "error"

@dataclass
class ParameterSession:
    """Repräsentiert eine Parameter-Collection Session"""
    session_id: str
    user_id: Optional[str]
    job_type: Optional[str]
    status: SessionStatus
    created_at: datetime
    updated_at: datetime
    expires_at: datetime

    # Parameter State
    collected_parameters: Dict[str, Any]
    parameter_history: List[Dict[str, Any]]
    validation_results: List[Dict[str, Any]]

    # Dialog State
    dialog_state: str
    last_message: Optional[str]
    suggested_questions: List[str]
    completion_percentage: float

    # Metadata
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary für JSON Storage"""
        data = asdict(self)
        # Datetime zu ISO String
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        data['expires_at'] = self.expires_at.isoformat()
        data['status'] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ParameterSession':
        """Erstellt ParameterSession aus Dictionary"""
        # String zu Datetime
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        data['expires_at'] = datetime.fromisoformat(data['expires_at'])
        data['status'] = SessionStatus(data['status'])
        return cls(**data)

# ================================
# PARAMETER STATE MANAGER
# ================================

class ParameterStateManager:
    """
    Verwaltet Parameter-Sammlung State und JSON Storage

    Hauptfunktionen:
    - Session Management für Parameter-Collection
    - JSON Storage und Persistierung
    - Parameter History Tracking
    - Validation State Management
    - Auto-Cleanup abgelaufener Sessions
    """

    def __init__(
        self,
        storage_path: Optional[str] = None,
        session_timeout_minutes: int = 60,
        max_sessions_per_user: int = 10
    ):
        # Storage Setup
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            self.storage_path = Path(__file__).parent.parent.parent / "storage" / "parameter_sessions"

        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Configuration
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        self.max_sessions_per_user = max_sessions_per_user

        # In-Memory Cache für aktive Sessions
        self._active_sessions: Dict[str, ParameterSession] = {}

        # Load existing sessions
        self._load_existing_sessions()

        logger.info(f"ParameterStateManager initialisiert - Storage: {self.storage_path}")

    def create_session(
        self,
        user_id: Optional[str] = None,
        job_type: Optional[str] = None,
        initial_parameters: Optional[Dict[str, Any]] = None
    ) -> ParameterSession:
        """Erstellt neue Parameter-Collection Session"""

        import uuid
        session_id = str(uuid.uuid4())

        now = datetime.now()
        expires_at = now + self.session_timeout

        session = ParameterSession(
            session_id=session_id,
            user_id=user_id,
            job_type=job_type,
            status=SessionStatus.ACTIVE,
            created_at=now,
            updated_at=now,
            expires_at=expires_at,
            collected_parameters=initial_parameters or {},
            parameter_history=[],
            validation_results=[],
            dialog_state="initial",
            last_message=None,
            suggested_questions=[],
            completion_percentage=0.0,
            metadata={}
        )

        # Cleanup alte Sessions für User
        if user_id:
            self._cleanup_user_sessions(user_id)

        # Speichere Session
        self._active_sessions[session_id] = session
        self._persist_session(session)

        logger.info(f"Neue Session erstellt: {session_id} für User: {user_id}")
        return session

    def get_session(self, session_id: str) -> Optional[ParameterSession]:
        """Holt Session by ID"""

        # Prüfe Cache
        if session_id in self._active_sessions:
            session = self._active_sessions[session_id]

            # Prüfe Expiration
            if datetime.now() > session.expires_at:
                self._expire_session(session_id)
                return None

            return session

        # Versuche aus Storage zu laden
        session = self._load_session_from_storage(session_id)
        if session:
            if datetime.now() > session.expires_at:
                self._expire_session(session_id)
                return None

            # Zu Cache hinzufügen
            self._active_sessions[session_id] = session
            return session

        return None

    def update_session_parameters(
        self,
        session_id: str,
        new_parameters: Dict[str, Any],
        source_message: Optional[str] = None,
        extraction_confidence: Optional[float] = None
    ) -> bool:
        """Aktualisiert Parameter einer Session"""

        session = self.get_session(session_id)
        if not session:
            logger.warning(f"Session nicht gefunden: {session_id}")
            return False

        # Merge neue Parameter
        updated_params = session.collected_parameters.copy()
        updated_params.update(new_parameters)

        # History Entry
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "source_message": source_message,
            "updated_parameters": new_parameters,
            "confidence": extraction_confidence,
            "total_parameters": len(updated_params)
        }

        # Session aktualisieren
        session.collected_parameters = updated_params
        session.parameter_history.append(history_entry)
        session.updated_at = datetime.now()

        # Berechne Completion Percentage
        if session.job_type:
            session.completion_percentage = self._calculate_completion_percentage(
                session.job_type, updated_params
            )

        # Persistiere
        self._persist_session(session)

        logger.info(f"Session {session_id} aktualisiert - {len(new_parameters)} neue Parameter")
        return True

    def update_session_state(
        self,
        session_id: str,
        dialog_state: Optional[str] = None,
        job_type: Optional[str] = None,
        last_message: Optional[str] = None,
        suggested_questions: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Aktualisiert Dialog-State einer Session"""

        session = self.get_session(session_id)
        if not session:
            return False

        # Update Fields
        if dialog_state:
            session.dialog_state = dialog_state
        if job_type:
            session.job_type = job_type
        if last_message:
            session.last_message = last_message
        if suggested_questions is not None:
            session.suggested_questions = suggested_questions
        if metadata:
            session.metadata.update(metadata)

        session.updated_at = datetime.now()

        # Extend session if still active
        if session.status == SessionStatus.ACTIVE:
            session.expires_at = datetime.now() + self.session_timeout

        self._persist_session(session)
        return True

    def validate_session_parameters(
        self,
        session_id: str,
        job_type: Optional[str] = None
    ) -> Optional[ParameterValidationResult]:
        """Validiert Parameter einer Session"""

        session = self.get_session(session_id)
        if not session:
            return None

        target_job_type = job_type or session.job_type
        if not target_job_type:
            return ParameterValidationResult(
                is_valid=False,
                errors=["Job-Type nicht gesetzt"],
                completion_percentage=0.0,
                missing_required_parameters=[]
            )

        # Validiere mit Pydantic Model
        validation_result = self._validate_parameters_with_model(
            target_job_type, session.collected_parameters
        )

        # Speichere Validierungsergebnis
        validation_entry = {
            "timestamp": datetime.now().isoformat(),
            "job_type": target_job_type,
            "is_valid": validation_result.is_valid,
            "errors": validation_result.errors,
            "warnings": validation_result.warnings,
            "completion_percentage": validation_result.completion_percentage
        }

        session.validation_results.append(validation_entry)
        session.completion_percentage = validation_result.completion_percentage * 100
        self._persist_session(session)

        return validation_result

    def complete_session(self, session_id: str) -> bool:
        """Markiert Session als abgeschlossen"""

        session = self.get_session(session_id)
        if not session:
            return False

        session.status = SessionStatus.COMPLETED
        session.updated_at = datetime.now()
        session.completion_percentage = 100.0

        self._persist_session(session)
        logger.info(f"Session abgeschlossen: {session_id}")
        return True

    def get_session_json_export(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Exportiert Session-Parameter als strukturiertes JSON"""

        session = self.get_session(session_id)
        if not session:
            return None

        export_data = {
            "session_info": {
                "session_id": session_id,
                "job_type": session.job_type,
                "status": session.status.value,
                "completion_percentage": session.completion_percentage,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat()
            },
            "parameters": session.collected_parameters,
            "validation": session.validation_results[-1] if session.validation_results else None,
            "history": {
                "extraction_count": len(session.parameter_history),
                "dialog_state": session.dialog_state,
                "last_message": session.last_message
            },
            "metadata": session.metadata
        }

        return export_data

    def list_user_sessions(
        self,
        user_id: str,
        status_filter: Optional[SessionStatus] = None
    ) -> List[ParameterSession]:
        """Listet Sessions eines Users"""

        sessions = []

        # Durchsuche aktive Sessions
        for session in self._active_sessions.values():
            if session.user_id == user_id:
                if not status_filter or session.status == status_filter:
                    sessions.append(session)

        # Durchsuche Storage (falls nicht im Cache)
        for session_file in self.storage_path.glob("*.json"):
            session_id = session_file.stem
            if session_id not in self._active_sessions:
                session = self._load_session_from_storage(session_id)
                if session and session.user_id == user_id:
                    if not status_filter or session.status == status_filter:
                        sessions.append(session)

        # Sortiere nach Update-Zeit
        sessions.sort(key=lambda s: s.updated_at, reverse=True)
        return sessions

    def cleanup_expired_sessions(self) -> int:
        """Räumt abgelaufene Sessions auf"""

        now = datetime.now()
        cleaned_count = 0

        # Cleanup Cache
        expired_ids = []
        for session_id, session in self._active_sessions.items():
            if now > session.expires_at or session.status == SessionStatus.EXPIRED:
                expired_ids.append(session_id)

        for session_id in expired_ids:
            self._expire_session(session_id)
            cleaned_count += 1

        # Cleanup Storage Files
        for session_file in self.storage_path.glob("*.json"):
            session_id = session_file.stem
            if session_id not in self._active_sessions:
                session = self._load_session_from_storage(session_id)
                if session and now > session.expires_at:
                    session_file.unlink()
                    cleaned_count += 1

        if cleaned_count > 0:
            logger.info(f"Cleanup: {cleaned_count} abgelaufene Sessions entfernt")

        return cleaned_count

    def get_system_stats(self) -> Dict[str, Any]:
        """Gibt System-Statistiken zurück"""

        now = datetime.now()
        active_count = len([s for s in self._active_sessions.values() if s.status == SessionStatus.ACTIVE])
        completed_count = len([s for s in self._active_sessions.values() if s.status == SessionStatus.COMPLETED])

        # Job-Type Verteilung
        job_type_counts = {}
        for session in self._active_sessions.values():
            if session.job_type:
                job_type_counts[session.job_type] = job_type_counts.get(session.job_type, 0) + 1

        return {
            "timestamp": now.isoformat(),
            "session_counts": {
                "active": active_count,
                "completed": completed_count,
                "total_in_cache": len(self._active_sessions)
            },
            "job_type_distribution": job_type_counts,
            "storage_path": str(self.storage_path),
            "session_timeout_minutes": self.session_timeout.total_seconds() / 60
        }

    # ================================
    # PRIVATE METHODS
    # ================================

    def _load_existing_sessions(self):
        """Lädt bestehende Sessions beim Start"""

        if not self.storage_path.exists():
            return

        loaded_count = 0
        for session_file in self.storage_path.glob("*.json"):
            try:
                session = self._load_session_from_storage(session_file.stem)
                if session and datetime.now() <= session.expires_at:
                    self._active_sessions[session.session_id] = session
                    loaded_count += 1
            except Exception as e:
                logger.warning(f"Fehler beim Laden von Session {session_file}: {e}")

        logger.info(f"{loaded_count} Sessions aus Storage geladen")

    def _load_session_from_storage(self, session_id: str) -> Optional[ParameterSession]:
        """Lädt Session aus Storage File"""

        session_file = self.storage_path / f"{session_id}.json"
        if not session_file.exists():
            return None

        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return ParameterSession.from_dict(data)
        except Exception as e:
            logger.error(f"Fehler beim Laden von Session {session_id}: {e}")
            return None

    def _persist_session(self, session: ParameterSession):
        """Persistiert Session zu Storage"""

        session_file = self.storage_path / f"{session.session_id}.json"
        try:
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Fehler beim Speichern von Session {session.session_id}: {e}")

    def _expire_session(self, session_id: str):
        """Markiert Session als abgelaufen und entfernt aus Cache"""

        if session_id in self._active_sessions:
            session = self._active_sessions[session_id]
            session.status = SessionStatus.EXPIRED
            self._persist_session(session)
            del self._active_sessions[session_id]

    def _cleanup_user_sessions(self, user_id: str):
        """Räumt alte Sessions eines Users auf"""

        user_sessions = self.list_user_sessions(user_id)
        if len(user_sessions) >= self.max_sessions_per_user:
            # Entferne älteste Sessions
            sessions_to_remove = user_sessions[self.max_sessions_per_user-1:]
            for session in sessions_to_remove:
                self._expire_session(session.session_id)

    def _calculate_completion_percentage(
        self,
        job_type: str,
        parameters: Dict[str, Any]
    ) -> float:
        """Berechnet Completion-Percentage für Job-Type"""

        try:
            from services.ai.smart_parameter_extractor import get_smart_parameter_extractor
            extractor = get_smart_parameter_extractor()
            job_schema = extractor.get_job_type_info(job_type)

            if not job_schema:
                return 0.0

            total_params = len(job_schema["parameters"])
            filled_params = len([v for v in parameters.values() if v is not None])

            return filled_params / total_params if total_params > 0 else 0.0

        except Exception as e:
            logger.error(f"Fehler bei Completion-Berechnung: {e}")
            return 0.0

    def _validate_parameters_with_model(
        self,
        job_type: str,
        parameters: Dict[str, Any]
    ) -> ParameterValidationResult:
        """Validiert Parameter mit Pydantic Model"""

        try:
            model_class = JOB_TYPE_MODEL_MAPPING.get(job_type.upper())
            if not model_class:
                return ParameterValidationResult(
                    is_valid=False,
                    errors=[f"Unbekannter Job-Type: {job_type}"],
                    completion_percentage=0.0,
                    missing_required_parameters=[]
                )

            # Versuche Model zu erstellen
            try:
                model_instance = model_class(**parameters)

                # Erfolgreiche Validierung
                return ParameterValidationResult(
                    is_valid=True,
                    errors=[],
                    warnings=[],
                    completion_percentage=1.0,
                    missing_required_parameters=[]
                )

            except ValueError as ve:
                # Pydantic Validierungsfehler
                errors = []
                if hasattr(ve, 'errors'):
                    for error in ve.errors():
                        field = error.get('loc', ['unknown'])[0]
                        msg = error.get('msg', 'Validierungsfehler')
                        errors.append(f"{field}: {msg}")
                else:
                    errors.append(str(ve))

                # Berechne Completion trotz Fehlern
                completion = self._calculate_completion_percentage(job_type, parameters)

                return ParameterValidationResult(
                    is_valid=False,
                    errors=errors,
                    warnings=[],
                    completion_percentage=completion,
                    missing_required_parameters=[]
                )

        except Exception as e:
            logger.error(f"Fehler bei Model-Validierung: {e}")
            return ParameterValidationResult(
                is_valid=False,
                errors=[f"Validierungsfehler: {str(e)}"],
                completion_percentage=0.0,
                missing_required_parameters=[]
            )

# ================================
# FACTORY FUNCTION
# ================================

_state_manager_instance: Optional[ParameterStateManager] = None

def get_parameter_state_manager() -> ParameterStateManager:
    """Factory function für ParameterStateManager"""
    global _state_manager_instance

    if _state_manager_instance is None:
        _state_manager_instance = ParameterStateManager()

    return _state_manager_instance

# ================================
# HIERARCHICAL PARAMETER STATE MANAGER
# ================================

class HierarchicalParameterStateManager:
    """
    Erweiterte State Manager für hierarchische Stream-Sessions

    Unterstützt:
    - Stream-Level + Job-Level Parameter getrennt verwalten
    - Parameter-Akkumulation ohne Overwriting
    - Multi-Context Parameter-Extraktion
    - Intelligente Completion-Tracking
    """

    def __init__(
        self,
        storage_path: Optional[str] = None,
        session_timeout_minutes: int = 60,
        max_sessions_per_user: int = 10
    ):
        # Storage Setup
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            self.storage_path = Path(__file__).parent.parent.parent / "storage" / "hierarchical_sessions"

        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Configuration
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        self.max_sessions_per_user = max_sessions_per_user

        # In-Memory Cache für aktive Sessions
        self._active_sessions: Dict[str, HierarchicalStreamSession] = {}

        # Load existing sessions
        self._load_existing_sessions()

        logger.info(f"HierarchicalParameterStateManager initialisiert - Storage: {self.storage_path}")

    def create_hierarchical_session(
        self,
        user_id: Optional[str] = None,
        initial_stream_parameters: Optional[Dict[str, Any]] = None
    ) -> HierarchicalStreamSession:
        """Erstellt neue hierarchische Stream-Session"""

        import uuid
        session_id = str(uuid.uuid4())

        now = datetime.now()
        expires_at = now + self.session_timeout

        session = HierarchicalStreamSession(
            session_id=session_id,
            user_id=user_id,
            stream_parameters=initial_stream_parameters or {},
            jobs=[],
            completion_status=CompletionStatus(),
            dialog_state="initial",
            last_message=None,
            suggested_questions=[],
            created_at=now,
            updated_at=now,
            expires_at=expires_at,
            metadata={}
        )

        # Cleanup alte Sessions für User
        if user_id:
            self._cleanup_user_sessions(user_id)

        # Speichere Session
        self._active_sessions[session_id] = session
        self._persist_session(session)

        logger.info(f"Neue hierarchische Session erstellt: {session_id} für User: {user_id}")
        return session

    def get_hierarchical_session(self, session_id: str) -> Optional[HierarchicalStreamSession]:
        """Holt hierarchische Session by ID"""

        # Prüfe Cache
        if session_id in self._active_sessions:
            session = self._active_sessions[session_id]

            # Prüfe Expiration
            if datetime.now() > session.expires_at:
                self._expire_session(session_id)
                return None

            return session

        # Versuche aus Storage zu laden
        session = self._load_session_from_storage(session_id)
        if session:
            if datetime.now() > session.expires_at:
                self._expire_session(session_id)
                return None

            # Zu Cache hinzufügen
            self._active_sessions[session_id] = session
            return session

        return None

    def update_hierarchical_parameters(
        self,
        session_id: str,
        stream_parameters: Optional[Dict[str, Any]] = None,
        job_type: Optional[str] = None,
        job_parameters: Optional[Dict[str, Any]] = None,
        job_name: Optional[str] = None,
        source_message: Optional[str] = None,
        extraction_confidence: Optional[float] = None
    ) -> bool:
        """
        Aktualisiert Parameter einer hierarchischen Session

        WICHTIG: Akkumuliert Parameter statt sie zu überschreiben!
        """

        session = self.get_hierarchical_session(session_id)
        if not session:
            logger.warning(f"Hierarchische Session nicht gefunden: {session_id}")
            return False

        # Stream-Parameter aktualisieren (akkumulieren)
        if stream_parameters:
            session.update_stream_parameters(stream_parameters)
            logger.info(f"Stream-Parameter aktualisiert in Session {session_id}: {list(stream_parameters.keys())}")

        # Job-Parameter aktualisieren (akkumulieren)
        if job_type and job_parameters:
            job_id = session.add_or_update_job(job_type, job_parameters, job_name)
            logger.info(f"Job-Parameter aktualisiert in Session {session_id}: {job_type} -> {list(job_parameters.keys())}")

        # Dialog-State aktualisieren
        session.last_message = source_message
        session.updated_at = datetime.now()

        # Extend session if still active
        session.expires_at = datetime.now() + self.session_timeout

        # Completion-Status neu berechnen
        session.calculate_completion()

        # Persistiere
        self._persist_session(session)

        logger.info(f"Hierarchische Session {session_id} aktualisiert - Completion: {session.completion_status.overall_percentage:.2f}")
        return True

    def update_hierarchical_parameters_from_extraction(
        self,
        session_id: str,
        extraction_result: 'HierarchicalExtractionResult',  # Forward reference
        source_message: Optional[str] = None
    ) -> bool:
        """
        Aktualisiert Parameter basierend auf HierarchicalExtractionResult
        """

        session = self.get_hierarchical_session(session_id)
        if not session:
            return False

        # Stream-Parameter verarbeiten
        if extraction_result.stream_parameters:
            stream_params = {}
            for param in extraction_result.stream_parameters:
                stream_params[param.name] = param.value

            session.update_stream_parameters(stream_params)

        # Job-Parameter verarbeiten
        for job_type, job_param_list in extraction_result.job_parameters.items():
            if job_param_list:
                job_params = {}
                for param in job_param_list:
                    job_params[param.name] = param.value

                session.add_or_update_job(job_type, job_params)

        # Dialog-State aktualisieren
        session.dialog_state = extraction_result.context_detected
        session.last_message = source_message
        session.suggested_questions = extraction_result.suggested_questions
        session.updated_at = datetime.now()
        session.expires_at = datetime.now() + self.session_timeout

        # Completion-Status neu berechnen
        session.calculate_completion()

        # Persistiere
        self._persist_session(session)

        return True

    def get_session_export_for_xml(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Exportiert Session-Parameter für XML-Generierung"""

        session = self.get_hierarchical_session(session_id)
        if not session:
            return None

        # Kombiniere alle Parameter für XML Export
        all_parameters = session.stream_parameters.copy()

        # Füge Job-Parameter hinzu mit Prefixes
        for job in session.jobs:
            for param_name, param_value in job.parameters.items():
                # Verwende Job-Type als Prefix um Konflikte zu vermeiden
                prefixed_name = f"{job.job_type.lower()}_{param_name}"
                all_parameters[prefixed_name] = param_value

        export_data = {
            "session_info": {
                "session_id": session_id,
                "session_type": session.session_type,
                "completion_percentage": session.completion_status.overall_percentage,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat()
            },
            "stream_parameters": session.stream_parameters,
            "jobs": [
                {
                    "job_id": job.job_id,
                    "job_type": job.job_type,
                    "job_name": job.job_name,
                    "parameters": job.parameters,
                    "completion_percentage": job.completion_percentage
                }
                for job in session.jobs
            ],
            "all_parameters": all_parameters,  # Flache Struktur für XML
            "completion_status": {
                "stream_complete": session.completion_status.stream_complete,
                "jobs_complete": session.completion_status.jobs_complete,
                "overall_percentage": session.completion_status.overall_percentage,
                "validation_passed": session.completion_status.validation_passed
            },
            "metadata": session.metadata
        }

        return export_data

    def list_user_hierarchical_sessions(
        self,
        user_id: str,
        active_only: bool = True
    ) -> List[HierarchicalStreamSession]:
        """Listet hierarchische Sessions eines Users"""

        sessions = []

        # Durchsuche aktive Sessions
        for session in self._active_sessions.values():
            if session.user_id == user_id:
                if not active_only or datetime.now() <= session.expires_at:
                    sessions.append(session)

        # Durchsuche Storage (falls nicht im Cache)
        for session_file in self.storage_path.glob("*.json"):
            session_id = session_file.stem
            if session_id not in self._active_sessions:
                session = self._load_session_from_storage(session_id)
                if session and session.user_id == user_id:
                    if not active_only or datetime.now() <= session.expires_at:
                        sessions.append(session)

        # Sortiere nach Update-Zeit
        sessions.sort(key=lambda s: s.updated_at, reverse=True)
        return sessions

    def save_hierarchical_session(self, session: HierarchicalStreamSession) -> bool:
        """
        Speichert hierarchische Session (Public Interface)
        Delegates to _persist_session
        """
        try:
            self._persist_session(session)
            logger.info(f"Hierarchische Session gespeichert: {session.session_id}")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Speichern hierarchischer Session {session.session_id}: {e}")
            return False

    def get_hierarchical_session_statistics(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Gibt detaillierte Statistiken für eine Session zurück"""

        session = self.get_hierarchical_session(session_id)
        if not session:
            return None

        # Berechne Statistiken
        total_stream_params = len(session.stream_parameters)
        total_jobs = len(session.jobs)
        total_job_params = sum(len(job.parameters) for job in session.jobs)

        # Job-Type Verteilung
        job_type_counts = {}
        for job in session.jobs:
            job_type_counts[job.job_type] = job_type_counts.get(job.job_type, 0) + 1

        return {
            "session_id": session_id,
            "session_type": session.session_type,
            "parameter_counts": {
                "stream_parameters": total_stream_params,
                "total_jobs": total_jobs,
                "total_job_parameters": total_job_params,
                "total_parameters": total_stream_params + total_job_params
            },
            "job_type_distribution": job_type_counts,
            "completion_status": {
                "stream_complete": session.completion_status.stream_complete,
                "jobs_complete": session.completion_status.jobs_complete,
                "overall_percentage": session.completion_status.overall_percentage,
                "validation_passed": session.completion_status.validation_passed
            },
            "timeline": {
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
                "expires_at": session.expires_at.isoformat(),
                "age_minutes": (datetime.now() - session.created_at).total_seconds() / 60
            },
            "dialog_state": session.dialog_state,
            "last_message": session.last_message
        }

    # ================================
    # PRIVATE METHODS
    # ================================

    def _load_existing_sessions(self):
        """Lädt bestehende hierarchische Sessions beim Start"""

        if not self.storage_path.exists():
            return

        loaded_count = 0
        for session_file in self.storage_path.glob("*.json"):
            try:
                session = self._load_session_from_storage(session_file.stem)
                if session and datetime.now() <= session.expires_at:
                    self._active_sessions[session.session_id] = session
                    loaded_count += 1
            except Exception as e:
                logger.warning(f"Fehler beim Laden von hierarchischer Session {session_file}: {e}")

        logger.info(f"{loaded_count} hierarchische Sessions aus Storage geladen")

    def _load_session_from_storage(self, session_id: str) -> Optional[HierarchicalStreamSession]:
        """Lädt hierarchische Session aus Storage File"""

        session_file = self.storage_path / f"{session_id}.json"
        if not session_file.exists():
            return None

        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Konvertiere zu HierarchicalStreamSession
            return self._dict_to_hierarchical_session(data)
        except Exception as e:
            logger.error(f"Fehler beim Laden von hierarchischer Session {session_id}: {e}")
            return None

    def _persist_session(self, session: HierarchicalStreamSession):
        """Persistiert hierarchische Session zu Storage"""

        session_file = self.storage_path / f"{session.session_id}.json"
        try:
            # Konvertiere zu JSON-fähigem Dict
            data = self._hierarchical_session_to_dict(session)

            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Fehler beim Speichern von hierarchischer Session {session.session_id}: {e}")

    def _hierarchical_session_to_dict(self, session: HierarchicalStreamSession) -> Dict[str, Any]:
        """Konvertiert HierarchicalStreamSession zu JSON-fähigem Dict"""

        return {
            "session_id": session.session_id,
            "session_type": session.session_type,
            "user_id": session.user_id,
            "stream_parameters": session.stream_parameters,
            "jobs": [
                {
                    "job_id": job.job_id,
                    "job_type": job.job_type,
                    "job_name": job.job_name,
                    "parameters": job.parameters,
                    "completion_percentage": job.completion_percentage,
                    "validation_errors": job.validation_errors,
                    "created_at": job.created_at.isoformat(),
                    "updated_at": job.updated_at.isoformat()
                }
                for job in session.jobs
            ],
            "completion_status": {
                "stream_complete": session.completion_status.stream_complete,
                "jobs_complete": session.completion_status.jobs_complete,
                "overall_percentage": session.completion_status.overall_percentage,
                "missing_stream_parameters": session.completion_status.missing_stream_parameters,
                "incomplete_jobs": session.completion_status.incomplete_jobs,
                "validation_passed": session.completion_status.validation_passed
            },
            "dialog_state": session.dialog_state,
            "last_message": session.last_message,
            "suggested_questions": session.suggested_questions,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "expires_at": session.expires_at.isoformat(),
            "metadata": session.metadata
        }

    def _dict_to_hierarchical_session(self, data: Dict[str, Any]) -> HierarchicalStreamSession:
        """Konvertiert Dict zu HierarchicalStreamSession"""

        # Jobs rekonstruieren
        jobs = []
        for job_data in data.get("jobs", []):
            job = JobConfiguration(
                job_id=job_data["job_id"],
                job_type=job_data["job_type"],
                job_name=job_data.get("job_name"),
                parameters=job_data.get("parameters", {}),
                completion_percentage=job_data.get("completion_percentage", 0.0),
                validation_errors=job_data.get("validation_errors", []),
                created_at=datetime.fromisoformat(job_data["created_at"]),
                updated_at=datetime.fromisoformat(job_data["updated_at"])
            )
            jobs.append(job)

        # CompletionStatus rekonstruieren
        completion_data = data.get("completion_status", {})
        completion_status = CompletionStatus(
            stream_complete=completion_data.get("stream_complete", False),
            jobs_complete=completion_data.get("jobs_complete", False),
            overall_percentage=completion_data.get("overall_percentage", 0.0),
            missing_stream_parameters=completion_data.get("missing_stream_parameters", []),
            incomplete_jobs=completion_data.get("incomplete_jobs", []),
            validation_passed=completion_data.get("validation_passed", False)
        )

        # HierarchicalStreamSession erstellen
        session = HierarchicalStreamSession(
            session_id=data["session_id"],
            session_type=data.get("session_type", "STREAM_CONFIGURATION"),
            user_id=data.get("user_id"),
            stream_parameters=data.get("stream_parameters", {}),
            jobs=jobs,
            completion_status=completion_status,
            dialog_state=data.get("dialog_state", "initial"),
            last_message=data.get("last_message"),
            suggested_questions=data.get("suggested_questions", []),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]),
            metadata=data.get("metadata", {})
        )

        return session

    def _expire_session(self, session_id: str):
        """Markiert hierarchische Session als abgelaufen und entfernt aus Cache"""

        if session_id in self._active_sessions:
            session = self._active_sessions[session_id]
            # Session ist bereits abgelaufen - nur aus Cache entfernen
            del self._active_sessions[session_id]

    def _cleanup_user_sessions(self, user_id: str):
        """Räumt alte hierarchische Sessions eines Users auf"""

        user_sessions = self.list_user_hierarchical_sessions(user_id, active_only=False)
        if len(user_sessions) >= self.max_sessions_per_user:
            # Entferne älteste Sessions
            sessions_to_remove = user_sessions[self.max_sessions_per_user-1:]
            for session in sessions_to_remove:
                self._expire_session(session.session_id)

# ================================
# HIERARCHICAL FACTORY FUNCTION
# ================================

_hierarchical_state_manager_instance: Optional[HierarchicalParameterStateManager] = None

def get_hierarchical_parameter_state_manager() -> HierarchicalParameterStateManager:
    """Factory function für HierarchicalParameterStateManager"""
    global _hierarchical_state_manager_instance

    if _hierarchical_state_manager_instance is None:
        _hierarchical_state_manager_instance = HierarchicalParameterStateManager()

    return _hierarchical_state_manager_instance