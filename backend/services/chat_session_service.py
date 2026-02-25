from services.db import get_db


def create_session(title: str = "Neuer Chat") -> dict:
    result = get_db().table("chat_sessions").insert({"title": title}).execute()
    return result.data[0]


def list_sessions() -> list[dict]:
    result = (
        get_db()
        .table("chat_sessions")
        .select("*")
        .order("updated_at", desc=True)
        .execute()
    )
    return result.data


def get_session(session_id: str) -> dict | None:
    result = (
        get_db()
        .table("chat_sessions")
        .select("*")
        .eq("id", session_id)
        .execute()
    )
    return result.data[0] if result.data else None


def update_session_title(session_id: str, title: str) -> dict:
    result = (
        get_db()
        .table("chat_sessions")
        .update({"title": title, "updated_at": "now()"})
        .eq("id", session_id)
        .execute()
    )
    return result.data[0] if result.data else None


def delete_session(session_id: str) -> None:
    get_db().table("chat_sessions").delete().eq("id", session_id).execute()


def add_message(session_id: str, role: str, content: str, sources: list = None) -> dict:
    row = {
        "session_id": session_id,
        "role": role,
        "content": content,
        "sources": sources or [],
    }
    result = get_db().table("chat_messages").insert(row).execute()
    # Touch session updated_at
    get_db().table("chat_sessions").update(
        {"updated_at": "now()"}
    ).eq("id", session_id).execute()
    return result.data[0]


def get_messages(session_id: str) -> list[dict]:
    result = (
        get_db()
        .table("chat_messages")
        .select("*")
        .eq("session_id", session_id)
        .order("created_at")
        .execute()
    )
    return result.data


def get_chat_history(session_id: str, limit: int = 10) -> list[dict]:
    """Get recent messages formatted for LLM chat history."""
    messages = get_messages(session_id)
    history = []
    for msg in messages[-limit:]:
        history.append({"role": msg["role"], "content": msg["content"]})
    return history
