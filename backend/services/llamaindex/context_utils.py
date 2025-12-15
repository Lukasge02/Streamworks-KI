"""
Context Utilities for RAG
"""

from typing import List, Dict, Optional
from .settings import LlamaIndexSettings

def enhance_query_with_history(
    query: str,
    history: Optional[List[Dict[str, str]]],
) -> str:
    """
    Enhance query with conversation context using LLM rewriting.
    
    Uses the LLM to rewrite the user's latest question into a standalone
    question that includes necessary context from the conversation history.
    """
    if not history or len(history) == 0:
        return query
        
    # Get LLM
    from llama_index.core.llms import ChatMessage
    llm = LlamaIndexSettings.get_llm()
    
    # Format history for the prompt
    history_str = ""
    # Take last 3 exchanges (6 messages) to avoid overflowing context window
    recent_history = history[-6:]
    
    for msg in recent_history:
        role = "Human" if msg.get("role") == "user" else "Assistant"
        content = msg.get("content", "").replace("\n", " ").strip()
        # Truncate very long messages
        if len(content) > 500:
            content = content[:500] + "..."
        history_str += f"{role}: {content}\n"
        
    # Create prompt messages
    messages = [
        ChatMessage(
            role="system",
            content="""Du bist ein Experte für Query-Rewriting. Deine Aufgabe ist es, die letzte Frage eines Nutzers so umzuformulieren, dass sie eigenständig verständlich ist (Standalone Query).
            
Nutze den direkten Gesprächsverlauf (Chat History), um Kontext (z.B. "er", "sie", "es", "das Projekt") aufzulösen.
Verändere die ursprüngliche Intention der Frage NICHT.
Füge keine neuen Informationen hinzu, die nicht im Verlauf stehen.
Antworte NUR mit der umformulierten Frage, ohne Erklärungen.

Beispiel:
History:
Human: Was kostet Projekt X?
Assistant: Projekt X kostet 5000€.
Human: Und wie lange dauert es?

Rewritten Query: Wie lange dauert Projekt X?"""
        ),
        ChatMessage(
            role="user",
            content=f"""Chat History:
{history_str}

Human: {query}

Rewritten Query:"""
        )
    ]
    
    try:
        # Generate rewritten query
        response = llm.chat(messages)
        rewritten = response.message.content.strip()
        
        # Basic sanity check - if empty or too short, use original
        if not rewritten or len(rewritten) < 3:
            return query
            
        print(f"🔄 Contextual Memory: '{query}' -> '{rewritten}'")
        return rewritten
        
    except Exception as e:
        print(f"⚠️ Query rewriting failed: {e}")
        return query
