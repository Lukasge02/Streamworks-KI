"""
Context Manager for Enhanced Conversational AI
Handles conversation context, memory, and intelligent follow-ups
"""

import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class ConversationTurn:
    """Represents a single turn in the conversation"""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    confidence_score: Optional[float] = None
    sources_used: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.sources_used is None:
            self.sources_used = []
        if self.metadata is None:
            self.metadata = {}

@dataclass
class ConversationContext:
    """Represents the full conversation context"""
    session_id: str
    user_id: str
    turns: List[ConversationTurn]
    topics: List[str]
    entities_mentioned: Dict[str, List[str]]
    last_updated: datetime
    context_summary: Optional[str] = None

class ContextManager:
    """
    Advanced Context Manager for Conversational AI

    Features:
    - Conversation memory and summarization
    - Topic tracking and drift detection
    - Entity recognition and tracking
    - Context window management
    - Intelligent follow-up suggestions
    """

    def __init__(self, max_context_turns: int = 10):
        self.max_context_turns = max_context_turns
        self._contexts: Dict[str, ConversationContext] = {}
        self._topic_keywords = {
            "streamworks": ["streamworks", "xml", "job", "scheduling", "stream", "agent"],
            "file_transfer": ["file", "transfer", "copy", "move", "ftp", "sftp"],
            "sap": ["sap", "report", "transaction", "variant", "system"],
            "database": ["database", "sql", "table", "query", "data"],
            "technical": ["error", "config", "setup", "installation", "problem"]
        }

    async def get_or_create_context(
        self,
        session_id: str,
        user_id: str
    ) -> ConversationContext:
        """Get existing context or create new one"""

        context_key = f"{session_id}_{user_id}"

        if context_key not in self._contexts:
            self._contexts[context_key] = ConversationContext(
                session_id=session_id,
                user_id=user_id,
                turns=[],
                topics=[],
                entities_mentioned={},
                last_updated=datetime.now()
            )
            logger.info(f"Created new conversation context for session {session_id}")

        return self._contexts[context_key]

    async def add_conversation_turn(
        self,
        session_id: str,
        user_id: str,
        role: str,
        content: str,
        confidence_score: Optional[float] = None,
        sources_used: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add a new turn to the conversation context"""

        context = await self.get_or_create_context(session_id, user_id)

        turn = ConversationTurn(
            role=role,
            content=content,
            timestamp=datetime.now(),
            confidence_score=confidence_score,
            sources_used=sources_used or [],
            metadata=metadata or {}
        )

        context.turns.append(turn)
        context.last_updated = datetime.now()

        # Maintain context window size
        if len(context.turns) > self.max_context_turns:
            context.turns = context.turns[-self.max_context_turns:]

        # Update topics and entities
        await self._update_topics(context, content)
        await self._extract_entities(context, content)

        # Generate context summary if needed
        if len(context.turns) % 5 == 0:  # Every 5 turns
            context.context_summary = await self._generate_context_summary(context)

        logger.debug(f"Added {role} turn to context for session {session_id}")

    async def get_relevant_context(
        self,
        session_id: str,
        user_id: str,
        current_query: str,
        max_turns: int = 5
    ) -> List[ConversationTurn]:
        """Get most relevant conversation turns for current query"""

        context = await self.get_or_create_context(session_id, user_id)

        if not context.turns:
            return []

        # Simple relevance: recent turns + keyword matching
        relevant_turns = []
        query_words = set(current_query.lower().split())

        for turn in reversed(context.turns[-10:]):  # Look at last 10 turns
            # Add recent turns
            if len(relevant_turns) < max_turns // 2:
                relevant_turns.append(turn)
                continue

            # Add turns with keyword overlap
            turn_words = set(turn.content.lower().split())
            overlap = len(query_words & turn_words)

            if overlap > 2 and len(relevant_turns) < max_turns:
                relevant_turns.append(turn)

        return list(reversed(relevant_turns))

    async def get_conversation_summary(
        self,
        session_id: str,
        user_id: str
    ) -> Optional[str]:
        """Get a summary of the conversation so far"""

        context = await self.get_or_create_context(session_id, user_id)

        if context.context_summary:
            return context.context_summary

        if len(context.turns) < 3:
            return None

        return await self._generate_context_summary(context)

    async def suggest_follow_up_questions(
        self,
        session_id: str,
        user_id: str,
        last_response: str
    ) -> List[str]:
        """Generate intelligent follow-up questions based on context"""

        context = await self.get_or_create_context(session_id, user_id)

        suggestions = []

        # Topic-based suggestions
        for topic in context.topics[-3:]:  # Last 3 topics
            if topic in self._get_topic_suggestions():
                suggestions.extend(self._get_topic_suggestions()[topic])

        # Entity-based suggestions
        for entity_type, entities in context.entities_mentioned.items():
            if entity_type == "streamworks_component" and entities:
                suggestions.append(f"Können Sie mehr über {entities[-1]} erklären?")

        # Generic helpful suggestions
        if not suggestions:
            suggestions = [
                "Haben Sie weitere Fragen zu diesem Thema?",
                "Möchten Sie ein konkretes Beispiel sehen?",
                "Soll ich eine detailliertere Erklärung geben?"
            ]

        return suggestions[:3]  # Return max 3 suggestions

    async def detect_topic_drift(
        self,
        session_id: str,
        user_id: str,
        current_query: str
    ) -> Tuple[bool, Optional[str]]:
        """Detect if conversation has drifted to a new topic"""

        context = await self.get_or_create_context(session_id, user_id)

        if not context.topics:
            return False, None

        current_topics = await self._identify_topics(current_query)
        recent_topics = set(context.topics[-3:])  # Last 3 topics

        # Check for topic drift
        if current_topics and not any(topic in recent_topics for topic in current_topics):
            new_topic = current_topics[0]
            return True, new_topic

        return False, None

    async def _update_topics(self, context: ConversationContext, content: str):
        """Update topics based on content"""

        topics = await self._identify_topics(content)

        for topic in topics:
            if topic not in context.topics:
                context.topics.append(topic)
            elif topic in context.topics:
                # Move to end to maintain recency
                context.topics.remove(topic)
                context.topics.append(topic)

        # Keep only recent topics
        context.topics = context.topics[-10:]

    async def _identify_topics(self, content: str) -> List[str]:
        """Identify topics in content using keyword matching"""

        content_lower = content.lower()
        identified_topics = []

        for topic, keywords in self._topic_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                identified_topics.append(topic)

        return identified_topics

    async def _extract_entities(self, context: ConversationContext, content: str):
        """Extract and track entities mentioned in content"""

        # Simple entity extraction (could be enhanced with NER)
        entities = {
            "files": [],
            "systems": [],
            "streamworks_components": []
        }

        words = content.split()
        for word in words:
            # File paths
            if ("/" in word or "\\" in word) and len(word) > 3:
                entities["files"].append(word)

            # System names (uppercase alphanumeric)
            elif word.isupper() and len(word) >= 3:
                entities["systems"].append(word)

            # StreamWorks components (XML, Job, Agent, etc.)
            elif any(comp in word.lower() for comp in ["job", "stream", "agent", "xml"]):
                entities["streamworks_components"].append(word)

        # Update context entities
        for entity_type, entity_list in entities.items():
            if entity_type not in context.entities_mentioned:
                context.entities_mentioned[entity_type] = []

            for entity in entity_list:
                if entity not in context.entities_mentioned[entity_type]:
                    context.entities_mentioned[entity_type].append(entity)

    async def _generate_context_summary(self, context: ConversationContext) -> str:
        """Generate a summary of the conversation context"""

        if not context.turns:
            return "Neue Unterhaltung gestartet."

        # Simple summarization based on topics and entities
        summary_parts = []

        if context.topics:
            topics_str = ", ".join(context.topics[-3:])
            summary_parts.append(f"Themen: {topics_str}")

        if context.entities_mentioned:
            for entity_type, entities in context.entities_mentioned.items():
                if entities:
                    entity_str = ", ".join(entities[-2:])  # Last 2 entities
                    summary_parts.append(f"{entity_type}: {entity_str}")

        turn_count = len(context.turns)
        summary_parts.append(f"{turn_count} Nachrichten ausgetauscht")

        return " | ".join(summary_parts)

    def _get_topic_suggestions(self) -> Dict[str, List[str]]:
        """Get follow-up suggestions for different topics"""

        return {
            "streamworks": [
                "Wie erstelle ich einen neuen Stream?",
                "Welche Job-Typen sind verfügbar?",
                "Wie konfiguriere ich Scheduling?"
            ],
            "sap": [
                "Welche SAP-Systeme werden unterstützt?",
                "Wie verwende ich Varianten?",
                "Was sind die häufigsten SAP-Probleme?"
            ],
            "file_transfer": [
                "Welche Protokolle werden unterstützt?",
                "Wie konfiguriere ich sichere Übertragungen?",
                "Was bei Fehlern beim Transfer?"
            ]
        }

    async def cleanup_old_contexts(self, max_age_hours: int = 24):
        """Clean up old conversation contexts"""

        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        contexts_to_remove = []

        for key, context in self._contexts.items():
            if context.last_updated < cutoff_time:
                contexts_to_remove.append(key)

        for key in contexts_to_remove:
            del self._contexts[key]

        if contexts_to_remove:
            logger.info(f"Cleaned up {len(contexts_to_remove)} old conversation contexts")

    async def export_context(self, session_id: str, user_id: str) -> Dict[str, Any]:
        """Export conversation context for analysis or backup"""

        context_key = f"{session_id}_{user_id}"
        if context_key not in self._contexts:
            return {}

        context = self._contexts[context_key]

        return {
            "session_id": context.session_id,
            "user_id": context.user_id,
            "turns": [asdict(turn) for turn in context.turns],
            "topics": context.topics,
            "entities_mentioned": context.entities_mentioned,
            "context_summary": context.context_summary,
            "last_updated": context.last_updated.isoformat()
        }


# Global context manager instance
_context_manager = None

async def get_context_manager() -> ContextManager:
    """Get global context manager instance"""
    global _context_manager
    if _context_manager is None:
        _context_manager = ContextManager()
    return _context_manager