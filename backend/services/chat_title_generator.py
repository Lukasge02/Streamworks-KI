"""
Chat Title Generation Service using Ollama
Provides intelligent chat title generation using local AI models
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from services.ollama_service import ollama_service
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from database import AsyncSessionLocal

logger = logging.getLogger(__name__)

class ChatTitleGenerator:
    """Service for generating intelligent chat titles using local AI"""
    
    def __init__(self):
        self.ollama = ollama_service
        self.default_model = "qwen2.5:7b"  # Fast and good quality model
        
    async def generate_title_from_user_message(
        self, 
        user_message: str,
        max_length: int = 30
    ) -> str:
        """
        Generate a short, descriptive title from a single user message
        
        Args:
            user_message: The first user message content
            max_length: Maximum title length in characters
            
        Returns:
            Generated title string
        """
        try:
            if not user_message or len(user_message.strip()) < 3:
                return "Neue Unterhaltung"
            
            primary_content = user_message.strip()
            
            # Truncate content for faster processing
            if len(primary_content) > 200:
                primary_content = primary_content[:200] + "..."
            
            # Create prompt for title generation
            prompt = f"""Generiere einen sehr kurzen, prägnanten deutschen Titel für diesen Chat (max. {max_length} Zeichen).

Nur das Wichtigste, keine Artikel oder Füllwörter:

Nachricht: {primary_content}

Beispiele guter Titel:
- "PDF Upload"
- "Preisfrage" 
- "Python Hilfe"
- "Dokument Analyse"
- "API Problem"

Titel:"""

            response = await self.ollama.generate_completion(
                prompt=prompt,
                model=self.default_model,
                temperature=0.2,
                max_tokens=20  # Very short response
            )
            
            # Clean and validate title
            title = response.get("response", "").strip()
            title = title.replace('"', '').replace("'", "")
            title = title.strip('.-:!')
            
            # Ensure it's not too long
            if len(title) > max_length:
                title = title[:max_length].strip()
            
            # Fallback if empty or too short
            if not title or len(title) < 3:
                # Simple fallback based on keywords
                content_lower = primary_content.lower()
                if any(word in content_lower for word in ['pdf', 'dokument', 'datei']):
                    return "Dokument Frage"
                elif any(word in content_lower for word in ['preis', 'kosten', 'euro', '€']):
                    return "Preisfrage"
                elif any(word in content_lower for word in ['python', 'code', 'programm']):
                    return "Code Hilfe"
                elif any(word in content_lower for word in ['api', 'endpoint', 'server']):
                    return "API Problem"
                else:
                    return "Chat Frage"
            
            return title
            
        except Exception as e:
            logger.error(f"Error generating chat title: {str(e)}")
            return "Neue Unterhaltung"
    
    async def generate_title_from_messages(
        self, 
        messages: List[Dict[str, Any]],
        max_length: int = 30
    ) -> str:
        """
        Legacy method - Generate title from message list (for backward compatibility)
        """
        try:
            if not messages:
                return "Neue Unterhaltung"
            
            # Take first user message
            user_messages = [msg for msg in messages[:3] if msg.get('role') == 'user']
            if not user_messages:
                return "Neue Unterhaltung"
            
            # Use new direct method
            return await self.generate_title_from_user_message(
                user_messages[0].get('content', ''),
                max_length
            )
            
        except Exception as e:
            logger.error(f"Error generating chat title from messages: {str(e)}")
            return "Neue Unterhaltung"
    
    async def generate_title_for_session(
        self, 
        session_id: str,
        force_refresh: bool = False
    ) -> str:
        """
        Generate title for a chat session based on its messages
        
        Args:
            session_id: Chat session ID
            force_refresh: Force regeneration even if title exists
            
        Returns:
            Generated title
        """
        try:
            async with AsyncSessionLocal() as db:
                # Check if session already has a custom title
                if not force_refresh:
                    result = await db.execute(text("""
                        SELECT title FROM chat_sessions 
                        WHERE id = :session_id AND title != 'Neue Unterhaltung'
                    """), {"session_id": session_id})
                    
                    existing = result.fetchone()
                    if existing:
                        return existing[0]
                
                # Get first few messages from session
                result = await db.execute(text("""
                    SELECT role, content FROM chat_messages
                    WHERE session_id = :session_id
                    ORDER BY sequence_number, created_at
                    LIMIT 3
                """), {"session_id": session_id})
                
                messages = []
                for row in result.fetchall():
                    messages.append({
                        "role": row[0],
                        "content": row[1]
                    })
                
                # Generate title from first user message if available
                user_messages = [msg for msg in messages if msg.get('role') == 'user']
                if user_messages:
                    title = await self.generate_title_from_user_message(user_messages[0]['content'])
                else:
                    title = "Neue Unterhaltung"
                
                # Save title to database
                await db.execute(text("""
                    UPDATE chat_sessions 
                    SET title = :title, updated_at = now()
                    WHERE id = :session_id
                """), {
                    "session_id": session_id,
                    "title": title
                })
                
                await db.commit()
                logger.info(f"Generated title '{title}' for session {session_id}")
                
                return title
                
        except Exception as e:
            logger.error(f"Error generating title for session {session_id}: {str(e)}")
            return "Neue Unterhaltung"
    
    async def update_session_title(
        self,
        session_id: str,
        user_id: str,
        custom_title: Optional[str] = None
    ) -> str:
        """
        Update session title - either with custom title or auto-generated
        
        Args:
            session_id: Chat session ID
            user_id: User ID for security check
            custom_title: Optional custom title, if None will auto-generate
            
        Returns:
            Final title
        """
        try:
            async with AsyncSessionLocal() as db:
                # Verify user owns session
                result = await db.execute(text("""
                    SELECT id FROM chat_sessions 
                    WHERE id = :session_id AND user_id = :user_id
                """), {"session_id": session_id, "user_id": user_id})
                
                if not result.fetchone():
                    raise Exception("Session not found or access denied")
                
                if custom_title:
                    # Use custom title
                    title = custom_title[:30]  # Limit length
                else:
                    # Generate title from messages
                    title = await self.generate_title_for_session(session_id, force_refresh=True)
                    return title  # Already saved in generate_title_for_session
                
                # Save custom title
                await db.execute(text("""
                    UPDATE chat_sessions 
                    SET title = :title, updated_at = now()
                    WHERE id = :session_id
                """), {
                    "session_id": session_id,
                    "title": title
                })
                
                await db.commit()
                return title
                
        except Exception as e:
            logger.error(f"Error updating session title: {str(e)}")
            raise Exception(f"Title update failed: {str(e)}")

# Singleton instance
chat_title_generator = ChatTitleGenerator()