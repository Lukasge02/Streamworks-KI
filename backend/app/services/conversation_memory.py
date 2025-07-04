"""
Conversation Memory Service für persistente Chat-Sessions
"""
import logging
import json
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class ConversationMessage:
    """Einzelne Konversations-Nachricht"""
    question: str
    answer: str
    timestamp: datetime
    metadata: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        """Konvertiert zu Dictionary für JSON-Serialisierung"""
        return {
            "question": self.question,
            "answer": self.answer,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ConversationMessage':
        """Erstellt aus Dictionary"""
        return cls(
            question=data["question"],
            answer=data["answer"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {})
        )

@dataclass
class ConversationSession:
    """Komplette Konversations-Session"""
    session_id: str
    messages: List[ConversationMessage]
    created_at: datetime
    last_activity: datetime
    metadata: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        """Konvertiert zu Dictionary für JSON-Serialisierung"""
        return {
            "session_id": self.session_id,
            "messages": [msg.to_dict() for msg in self.messages],
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "metadata": self.metadata or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ConversationSession':
        """Erstellt aus Dictionary"""
        return cls(
            session_id=data["session_id"],
            messages=[ConversationMessage.from_dict(msg) for msg in data["messages"]],
            created_at=datetime.fromisoformat(data["created_at"]),
            last_activity=datetime.fromisoformat(data["last_activity"]),
            metadata=data.get("metadata", {})
        )

class ConversationMemory:
    """Verwaltet persistente Konversations-Sessions"""
    
    def __init__(self, storage_path: str = "data/conversations"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # In-Memory Cache für aktive Sessions
        self.sessions: Dict[str, ConversationSession] = {}
        
        # Konfiguration
        self.max_messages_per_session = 50
        self.session_timeout_hours = 24
        self.context_window_size = 3  # Anzahl vorheriger Nachrichten für Kontext
        
        logger.info(f"💬 Conversation Memory initialisiert: {self.storage_path}")
    
    def add_message(self, session_id: str, question: str, answer: str, metadata: Optional[Dict] = None) -> bool:
        """
        Fügt Nachricht zu Session hinzu
        
        Args:
            session_id: Eindeutige Session-ID
            question: Benutzerfrage
            answer: KI-Antwort
            metadata: Zusätzliche Metadaten
            
        Returns:
            True wenn erfolgreich gespeichert
        """
        try:
            # Session laden oder erstellen
            session = self._get_or_create_session(session_id)
            
            # Neue Nachricht erstellen
            message = ConversationMessage(
                question=question,
                answer=answer,
                timestamp=datetime.utcnow(),
                metadata=metadata or {}
            )
            
            # Nachricht hinzufügen
            session.messages.append(message)
            session.last_activity = datetime.utcnow()
            
            # Session-Größe begrenzen
            if len(session.messages) > self.max_messages_per_session:
                session.messages = session.messages[-self.max_messages_per_session:]
            
            # Session speichern
            self._save_session(session)
            
            logger.info(f"💬 Nachricht zu Session {session_id} hinzugefügt")
            return True
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Hinzufügen der Nachricht: {e}")
            return False
    
    def get_context(self, session_id: str, include_current: bool = False) -> str:
        """
        Gibt Konversations-Kontext für bessere Antworten zurück
        
        Args:
            session_id: Session-ID
            include_current: Ob aktuelle Session einbezogen werden soll
            
        Returns:
            Formatierter Kontext-String
        """
        try:
            session = self._get_session(session_id)
            if not session or not session.messages:
                return ""
            
            # Hole letzte N Nachrichten
            recent_messages = session.messages[-self.context_window_size:]
            
            # Formatiere Kontext
            context_parts = []
            for i, msg in enumerate(recent_messages, 1):
                context_parts.append(f"Vorherige Frage {i}: {msg.question}")
                context_parts.append(f"Vorherige Antwort {i}: {msg.answer[:200]}...")  # Kürze Antworten
            
            context = "\n".join(context_parts)
            
            logger.debug(f"📚 Kontext für Session {session_id}: {len(context)} Zeichen")
            return context
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Abrufen des Kontexts: {e}")
            return ""
    
    def get_session_summary(self, session_id: str) -> Dict:
        """
        Erstellt Zusammenfassung einer Session
        
        Args:
            session_id: Session-ID
            
        Returns:
            Dictionary mit Session-Zusammenfassung
        """
        try:
            session = self._get_session(session_id)
            if not session:
                return {}
            
            # Häufige Themen analysieren
            topics = self._analyze_topics(session.messages)
            
            # Session-Statistiken
            duration = session.last_activity - session.created_at
            
            summary = {
                "session_id": session_id,
                "message_count": len(session.messages),
                "duration_minutes": int(duration.total_seconds() / 60),
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "main_topics": topics[:5],  # Top 5 Themen
                "first_question": session.messages[0].question if session.messages else "",
                "last_question": session.messages[-1].question if session.messages else ""
            }
            
            logger.info(f"📊 Session-Zusammenfassung für {session_id}: {summary['message_count']} Nachrichten")
            return summary
            
        except Exception as e:
            logger.error(f"❌ Fehler bei Session-Zusammenfassung: {e}")
            return {}
    
    def cleanup_old_sessions(self) -> int:
        """
        Bereinigt alte/inaktive Sessions
        
        Returns:
            Anzahl gelöschter Sessions
        """
        try:
            deleted_count = 0
            cutoff_time = datetime.utcnow() - timedelta(hours=self.session_timeout_hours)
            
            # Durchsuche alle Session-Dateien
            for session_file in self.storage_path.glob("session_*.json"):
                try:
                    session = self._load_session_from_file(session_file)
                    if session and session.last_activity < cutoff_time:
                        # Lösche alte Session
                        session_file.unlink()
                        # Entferne aus Cache
                        if session.session_id in self.sessions:
                            del self.sessions[session.session_id]
                        deleted_count += 1
                        logger.debug(f"🗑️ Alte Session gelöscht: {session.session_id}")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Fehler beim Löschen von {session_file}: {e}")
            
            logger.info(f"🧹 Cleanup abgeschlossen: {deleted_count} Sessions gelöscht")
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Session-Cleanup: {e}")
            return 0
    
    def get_all_sessions(self, limit: int = 50) -> List[Dict]:
        """
        Gibt Liste aller Sessions zurück (für Admin-Interface)
        
        Args:
            limit: Maximale Anzahl Sessions
            
        Returns:
            Liste von Session-Zusammenfassungen
        """
        try:
            sessions = []
            
            # Lade alle Session-Dateien
            session_files = sorted(
                self.storage_path.glob("session_*.json"),
                key=lambda f: f.stat().st_mtime,
                reverse=True
            )
            
            for session_file in session_files[:limit]:
                try:
                    session = self._load_session_from_file(session_file)
                    if session:
                        summary = self.get_session_summary(session.session_id)
                        sessions.append(summary)
                        
                except Exception as e:
                    logger.warning(f"⚠️ Fehler beim Laden von {session_file}: {e}")
            
            logger.info(f"📋 {len(sessions)} Sessions geladen")
            return sessions
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Laden aller Sessions: {e}")
            return []
    
    def _get_or_create_session(self, session_id: str) -> ConversationSession:
        """Holt oder erstellt neue Session"""
        session = self._get_session(session_id)
        if not session:
            session = ConversationSession(
                session_id=session_id,
                messages=[],
                created_at=datetime.utcnow(),
                last_activity=datetime.utcnow(),
                metadata={}
            )
            self.sessions[session_id] = session
        
        return session
    
    def _get_session(self, session_id: str) -> Optional[ConversationSession]:
        """Holt Session aus Cache oder Datei"""
        # Versuche aus Cache
        if session_id in self.sessions:
            return self.sessions[session_id]
        
        # Versuche aus Datei zu laden
        session_file = self.storage_path / f"session_{session_id}.json"
        if session_file.exists():
            session = self._load_session_from_file(session_file)
            if session:
                self.sessions[session_id] = session
                return session
        
        return None
    
    def _save_session(self, session: ConversationSession):
        """Speichert Session in Datei"""
        session_file = self.storage_path / f"session_{session.session_id}.json"
        
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session.to_dict(), f, ensure_ascii=False, indent=2)
        
        # Update Cache
        self.sessions[session.session_id] = session
    
    def _load_session_from_file(self, session_file: Path) -> Optional[ConversationSession]:
        """Lädt Session aus Datei"""
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return ConversationSession.from_dict(data)
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Laden von {session_file}: {e}")
            return None
    
    def _analyze_topics(self, messages: List[ConversationMessage]) -> List[str]:
        """Analysiert häufige Themen in Nachrichten"""
        try:
            # Einfache Keyword-Extraktion
            keywords = {}
            
            for msg in messages:
                words = msg.question.lower().split()
                for word in words:
                    if len(word) > 3:  # Ignoriere kurze Wörter
                        keywords[word] = keywords.get(word, 0) + 1
            
            # Sortiere nach Häufigkeit
            sorted_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)
            
            return [keyword for keyword, count in sorted_keywords if count > 1]
            
        except Exception as e:
            logger.error(f"❌ Topic-Analyse fehlgeschlagen: {e}")
            return []

# Global instance
conversation_memory = ConversationMemory()