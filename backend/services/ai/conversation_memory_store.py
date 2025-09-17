"""
Conversation Memory Store for Enterprise AI Parameter Recognition
Manages conversation context and learns from successful interactions
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import deque
import hashlib
from sentence_transformers import SentenceTransformer

from .chroma_manager import get_chroma_manager

logger = logging.getLogger(__name__)

@dataclass
class ConversationTurn:
    """Single turn in a conversation"""
    turn_id: str
    session_id: str
    user_message: str
    ai_response: str
    extracted_parameters: Dict[str, Any]
    conversation_phase: str
    timestamp: str
    success_score: float  # How successful was this turn (0.0-1.0)

@dataclass
class ConversationSession:
    """Complete conversation session"""
    session_id: str
    user_id: str
    start_time: str
    end_time: Optional[str]
    total_turns: int
    final_parameters: Dict[str, Any]
    job_type: str
    success_rate: float
    completion_status: str  # 'completed', 'abandoned', 'error'
    stream_created: bool

@dataclass
class ConversationPattern:
    """Learned pattern from successful conversations"""
    pattern_id: str
    job_type: str
    common_flow: List[str]  # Sequence of conversation phases
    successful_phrases: List[Dict[str, Any]]  # Phrases that led to success
    parameter_sequence: List[str]  # Order parameters are typically collected
    average_turns: int
    success_rate: float
    learned_from_sessions: List[str]
    created_at: str
    updated_at: str

class ConversationMemoryStore:
    """
    Manages conversation memory and learns from interactions

    Features:
    - Turn-by-turn conversation storage
    - Success pattern learning
    - Context-aware response suggestions
    - Conversation flow optimization
    """

    def __init__(self, max_memory_days: int = 30):
        self.max_memory_days = max_memory_days
        self.chroma_manager = get_chroma_manager()
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        # Get ChromaDB collections
        self.conversations_collection = self.chroma_manager.get_collection(
            "conversation_memory", "conversations"
        )
        self.turns_collection = self.chroma_manager.get_collection(
            "conversation_memory", "conversation_turns"
        )
        self.patterns_collection = self.chroma_manager.get_collection(
            "conversation_memory", "success_patterns"
        )

        # In-memory session cache for active conversations
        self.active_sessions: Dict[str, ConversationSession] = {}
        self.session_turns: Dict[str, List[ConversationTurn]] = {}

    async def start_conversation(self, session_id: str, user_id: str = "default") -> ConversationSession:
        """
        Start a new conversation session

        Args:
            session_id: Unique session identifier
            user_id: User identifier

        Returns:
            ConversationSession object
        """
        session = ConversationSession(
            session_id=session_id,
            user_id=user_id,
            start_time=datetime.now().isoformat(),
            end_time=None,
            total_turns=0,
            final_parameters={},
            job_type="unknown",
            success_rate=0.0,
            completion_status="active",
            stream_created=False
        )

        self.active_sessions[session_id] = session
        self.session_turns[session_id] = []

        logger.info(f"🎯 Started conversation session: {session_id}")
        return session

    async def add_conversation_turn(
        self,
        session_id: str,
        user_message: str,
        ai_response: str,
        extracted_parameters: Dict[str, Any] = None,
        conversation_phase: str = "unknown",
        success_score: float = 0.5
    ) -> ConversationTurn:
        """
        Add a turn to an active conversation

        Args:
            session_id: Session identifier
            user_message: User's message
            ai_response: AI's response
            extracted_parameters: Parameters extracted this turn
            conversation_phase: Current phase of conversation
            success_score: How successful this turn was

        Returns:
            ConversationTurn object
        """
        try:
            turn_id = f"{session_id}_{len(self.session_turns.get(session_id, []))}"

            turn = ConversationTurn(
                turn_id=turn_id,
                session_id=session_id,
                user_message=user_message,
                ai_response=ai_response,
                extracted_parameters=extracted_parameters or {},
                conversation_phase=conversation_phase,
                timestamp=datetime.now().isoformat(),
                success_score=success_score
            )

            # Add to session turns
            if session_id not in self.session_turns:
                self.session_turns[session_id] = []
            self.session_turns[session_id].append(turn)

            # Update active session
            if session_id in self.active_sessions:
                self.active_sessions[session_id].total_turns += 1

            # Store in ChromaDB
            await self._store_conversation_turn(turn)

            logger.info(f"💬 Added conversation turn: {turn_id} (phase: {conversation_phase})")
            return turn

        except Exception as e:
            logger.error(f"❌ Error adding conversation turn: {str(e)}")
            raise

    async def end_conversation(
        self,
        session_id: str,
        final_parameters: Dict[str, Any],
        job_type: str,
        completion_status: str = "completed",
        stream_created: bool = False
    ) -> ConversationSession:
        """
        End a conversation session

        Args:
            session_id: Session identifier
            final_parameters: Final extracted parameters
            job_type: Determined job type
            completion_status: How the conversation ended
            stream_created: Whether a stream was successfully created

        Returns:
            Updated ConversationSession
        """
        try:
            if session_id not in self.active_sessions:
                raise ValueError(f"Session {session_id} not found")

            session = self.active_sessions[session_id]
            turns = self.session_turns.get(session_id, [])

            # Update session
            session.end_time = datetime.now().isoformat()
            session.final_parameters = final_parameters
            session.job_type = job_type
            session.completion_status = completion_status
            session.stream_created = stream_created

            # Calculate success rate
            if turns:
                session.success_rate = sum(turn.success_score for turn in turns) / len(turns)
            else:
                session.success_rate = 1.0 if stream_created else 0.0

            # Store completed session
            await self._store_conversation_session(session, turns)

            # Learn from successful conversation
            if completion_status == "completed" and stream_created:
                await self._learn_from_successful_conversation(session, turns)

            # Clean up active session
            del self.active_sessions[session_id]
            if session_id in self.session_turns:
                del self.session_turns[session_id]

            logger.info(f"🎯 Ended conversation: {session_id} (status: {completion_status}, success: {session.success_rate:.2f})")
            return session

        except Exception as e:
            logger.error(f"❌ Error ending conversation: {str(e)}")
            raise

    async def get_conversation_context(self, session_id: str, max_turns: int = 5) -> List[ConversationTurn]:
        """
        Get recent conversation context

        Args:
            session_id: Session identifier
            max_turns: Maximum number of turns to return

        Returns:
            List of recent conversation turns
        """
        if session_id in self.session_turns:
            turns = self.session_turns[session_id]
            return turns[-max_turns:] if turns else []

        # Try to get from storage
        return await self._get_stored_conversation_turns(session_id, max_turns)

    async def get_similar_conversations(
        self,
        query_text: str,
        job_type: str = None,
        limit: int = 5
    ) -> List[Tuple[ConversationSession, float]]:
        """
        Find similar successful conversations

        Args:
            query_text: Query text to find similar conversations
            job_type: Optional job type filter
            limit: Maximum number of results

        Returns:
            List of (session, similarity_score) tuples
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query_text).tolist()

            # Build where clause
            where_clause = {"completion_status": "completed"}
            if job_type:
                where_clause["job_type"] = job_type

            # Search in ChromaDB
            results = self.conversations_collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where_clause
            )

            similar_conversations = []

            if results['ids'] and results['ids'][0]:
                for i, session_id in enumerate(results['ids'][0]):
                    similarity_score = 1.0 - results['distances'][0][i]
                    session = await self._get_session_by_id(session_id)
                    if session:
                        similar_conversations.append((session, similarity_score))

            logger.info(f"🔍 Found {len(similar_conversations)} similar conversations")
            return similar_conversations

        except Exception as e:
            logger.error(f"❌ Error finding similar conversations: {str(e)}")
            return []

    async def get_success_patterns(self, job_type: str = None) -> List[ConversationPattern]:
        """
        Get learned success patterns for conversation flow

        Args:
            job_type: Optional job type filter

        Returns:
            List of conversation patterns
        """
        try:
            where_clause = {}
            if job_type:
                where_clause["job_type"] = job_type

            results = self.patterns_collection.query(
                query_texts=["successful conversation pattern"],
                n_results=10,
                where=where_clause if where_clause else None
            )

            patterns = []
            if results['ids'] and results['ids'][0]:
                for pattern_id in results['ids'][0]:
                    pattern = await self._get_pattern_by_id(pattern_id)
                    if pattern:
                        patterns.append(pattern)

            return patterns

        except Exception as e:
            logger.error(f"❌ Error getting success patterns: {str(e)}")
            return []

    async def suggest_next_response(
        self,
        session_id: str,
        current_phase: str,
        user_message: str
    ) -> Dict[str, Any]:
        """
        Suggest next AI response based on learned patterns

        Args:
            session_id: Current session
            current_phase: Current conversation phase
            user_message: User's latest message

        Returns:
            Dictionary with response suggestions
        """
        try:
            # Get conversation context
            context = await self.get_conversation_context(session_id)

            # Find similar conversations
            similar_conversations = await self.get_similar_conversations(user_message, limit=3)

            # Get success patterns
            patterns = await self.get_success_patterns()

            # Generate suggestions
            suggestions = {
                "recommended_responses": [],
                "next_phase": current_phase,
                "confidence": 0.0,
                "similar_contexts": len(similar_conversations)
            }

            if similar_conversations:
                best_session, confidence = similar_conversations[0]
                suggestions["confidence"] = confidence

                # Extract successful response patterns
                best_turns = await self._get_stored_conversation_turns(best_session.session_id)
                for turn in best_turns:
                    if turn.conversation_phase == current_phase:
                        suggestions["recommended_responses"].append({
                            "response": turn.ai_response,
                            "success_score": turn.success_score,
                            "extracted_params": turn.extracted_parameters
                        })

            return suggestions

        except Exception as e:
            logger.error(f"❌ Error suggesting next response: {str(e)}")
            return {"recommended_responses": [], "confidence": 0.0}

    async def _store_conversation_turn(self, turn: ConversationTurn):
        """Store a conversation turn in ChromaDB"""
        try:
            # Create text for embedding
            turn_text = f"User: {turn.user_message}\nAI: {turn.ai_response}"
            embedding = self.embedding_model.encode(turn_text).tolist()

            # Prepare metadata
            metadata = {
                "session_id": turn.session_id,
                "conversation_phase": turn.conversation_phase,
                "success_score": turn.success_score,
                "timestamp": turn.timestamp,
                "has_parameters": len(turn.extracted_parameters) > 0
            }

            # Store in ChromaDB
            self.turns_collection.add(
                ids=[turn.turn_id],
                embeddings=[embedding],
                documents=[turn_text],
                metadatas=[metadata]
            )

        except Exception as e:
            logger.error(f"❌ Error storing conversation turn: {str(e)}")

    async def _store_conversation_session(self, session: ConversationSession, turns: List[ConversationTurn]):
        """Store a complete conversation session"""
        try:
            # Create session summary for embedding
            user_messages = [turn.user_message for turn in turns]
            session_summary = " | ".join(user_messages)

            embedding = self.embedding_model.encode(session_summary).tolist()

            # Prepare metadata
            metadata = {
                "user_id": session.user_id,
                "job_type": session.job_type,
                "total_turns": session.total_turns,
                "success_rate": session.success_rate,
                "completion_status": session.completion_status,
                "stream_created": session.stream_created,
                "start_time": session.start_time,
                "end_time": session.end_time or ""
            }

            # Store in ChromaDB
            self.conversations_collection.add(
                ids=[session.session_id],
                embeddings=[embedding],
                documents=[session_summary],
                metadatas=[metadata]
            )

        except Exception as e:
            logger.error(f"❌ Error storing conversation session: {str(e)}")

    async def _learn_from_successful_conversation(self, session: ConversationSession, turns: List[ConversationTurn]):
        """Learn patterns from a successful conversation"""
        try:
            if not turns:
                return

            # Extract conversation flow
            flow = [turn.conversation_phase for turn in turns]

            # Extract successful phrases
            successful_phrases = []
            for turn in turns:
                if turn.success_score >= 0.7:  # High success turns
                    successful_phrases.append({
                        "user_phrase": turn.user_message[:100],
                        "ai_response": turn.ai_response[:100],
                        "phase": turn.conversation_phase,
                        "success_score": turn.success_score
                    })

            # Extract parameter collection order
            parameter_sequence = []
            for turn in turns:
                for param_name in turn.extracted_parameters.keys():
                    if param_name not in parameter_sequence:
                        parameter_sequence.append(param_name)

            # Create or update pattern
            pattern_id = f"{session.job_type}_pattern_{hashlib.md5(str(flow).encode()).hexdigest()[:8]}"

            pattern = ConversationPattern(
                pattern_id=pattern_id,
                job_type=session.job_type,
                common_flow=flow,
                successful_phrases=successful_phrases,
                parameter_sequence=parameter_sequence,
                average_turns=len(turns),
                success_rate=session.success_rate,
                learned_from_sessions=[session.session_id],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )

            await self._store_conversation_pattern(pattern)

            logger.info(f"🧠 Learned conversation pattern: {pattern_id} from session {session.session_id}")

        except Exception as e:
            logger.error(f"❌ Error learning from conversation: {str(e)}")

    async def _store_conversation_pattern(self, pattern: ConversationPattern):
        """Store a learned conversation pattern"""
        try:
            # Create description for embedding
            pattern_description = f"{pattern.job_type} conversation flow with {len(pattern.common_flow)} phases"

            embedding = self.embedding_model.encode(pattern_description).tolist()

            # Prepare metadata
            metadata = {
                "job_type": pattern.job_type,
                "average_turns": pattern.average_turns,
                "success_rate": pattern.success_rate,
                "flow_length": len(pattern.common_flow),
                "created_at": pattern.created_at,
                "updated_at": pattern.updated_at
            }

            # Store in ChromaDB
            self.patterns_collection.add(
                ids=[pattern.pattern_id],
                embeddings=[embedding],
                documents=[pattern_description],
                metadatas=[metadata]
            )

        except Exception as e:
            logger.error(f"❌ Error storing conversation pattern: {str(e)}")

    async def _get_stored_conversation_turns(self, session_id: str, max_turns: int = 5) -> List[ConversationTurn]:
        """Get conversation turns from storage"""
        try:
            results = self.turns_collection.query(
                query_texts=[session_id],
                n_results=max_turns,
                where={"session_id": session_id}
            )

            turns = []
            if results['ids'] and results['ids'][0]:
                # Note: This is a simplified reconstruction
                # In a full implementation, you'd store the complete turn data
                for i, turn_id in enumerate(results['ids'][0]):
                    metadata = results['metadatas'][0][i]
                    # Reconstruct turn (simplified)
                    turn = ConversationTurn(
                        turn_id=turn_id,
                        session_id=session_id,
                        user_message="",  # Would need separate storage
                        ai_response="",   # Would need separate storage
                        extracted_parameters={},
                        conversation_phase=metadata['conversation_phase'],
                        timestamp=metadata['timestamp'],
                        success_score=metadata['success_score']
                    )
                    turns.append(turn)

            return turns

        except Exception as e:
            logger.error(f"❌ Error getting stored turns: {str(e)}")
            return []

    async def _get_session_by_id(self, session_id: str) -> Optional[ConversationSession]:
        """Get session by ID from storage"""
        try:
            results = self.conversations_collection.get(
                ids=[session_id],
                include=['metadatas']
            )

            if results['ids'] and results['metadatas']:
                metadata = results['metadatas'][0]

                session = ConversationSession(
                    session_id=session_id,
                    user_id=metadata['user_id'],
                    start_time=metadata['start_time'],
                    end_time=metadata['end_time'],
                    total_turns=metadata['total_turns'],
                    final_parameters={},  # Would need separate storage
                    job_type=metadata['job_type'],
                    success_rate=metadata['success_rate'],
                    completion_status=metadata['completion_status'],
                    stream_created=metadata['stream_created']
                )

                return session

        except Exception as e:
            logger.error(f"❌ Error getting session {session_id}: {str(e)}")

        return None

    async def _get_pattern_by_id(self, pattern_id: str) -> Optional[ConversationPattern]:
        """Get pattern by ID from storage"""
        try:
            results = self.patterns_collection.get(
                ids=[pattern_id],
                include=['metadatas']
            )

            if results['ids'] and results['metadatas']:
                metadata = results['metadatas'][0]

                pattern = ConversationPattern(
                    pattern_id=pattern_id,
                    job_type=metadata['job_type'],
                    common_flow=[],  # Would need separate storage
                    successful_phrases=[],  # Would need separate storage
                    parameter_sequence=[],  # Would need separate storage
                    average_turns=metadata['average_turns'],
                    success_rate=metadata['success_rate'],
                    learned_from_sessions=[],
                    created_at=metadata['created_at'],
                    updated_at=metadata['updated_at']
                )

                return pattern

        except Exception as e:
            logger.error(f"❌ Error getting pattern {pattern_id}: {str(e)}")

        return None

    def get_stats(self) -> Dict[str, Any]:
        """Get conversation memory statistics"""
        try:
            conversations_count = self.conversations_collection.count()
            turns_count = self.turns_collection.count()
            patterns_count = self.patterns_collection.count()

            return {
                "total_conversations": conversations_count,
                "total_turns": turns_count,
                "total_patterns": patterns_count,
                "active_sessions": len(self.active_sessions),
                "embedding_model": "all-MiniLM-L6-v2",
                "max_memory_days": self.max_memory_days
            }
        except Exception as e:
            logger.error(f"❌ Error getting conversation memory stats: {str(e)}")
            return {"error": str(e)}

# Global instance
_conversation_memory_store = None

def get_conversation_memory_store() -> ConversationMemoryStore:
    """Get global conversation memory store instance"""
    global _conversation_memory_store
    if _conversation_memory_store is None:
        _conversation_memory_store = ConversationMemoryStore()
    return _conversation_memory_store