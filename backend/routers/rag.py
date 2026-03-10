from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from models.rag import ChatRequest, ChatResponse, Source, ChatSession, ChatMessage
from services import rag_service, chat_session_service

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest):
    # Create or get session
    if body.session_id:
        session = chat_session_service.get_session(body.session_id)
        if not session:
            raise HTTPException(404, "Session not found")
        session_id = body.session_id
    else:
        session = chat_session_service.create_session()
        session_id = session["id"]

    # Save user message
    chat_session_service.add_message(session_id, "user", body.message)

    # Get chat history
    history = chat_session_service.get_chat_history(session_id)

    # Query RAG
    result = rag_service.query(body.message, chat_history=history[:-1])

    # Save assistant message -- normalize keys to match Source model
    sources_data = []
    for s in result["sources"]:
        d = s if isinstance(s, dict) else s.dict()
        sources_data.append({
            "document_name": d.get("document_name", ""),
            "chunk_text": d.get("chunk_text") or d.get("text_preview") or d.get("text", ""),
            "score": d.get("score", 0),
            "page": d.get("page"),
        })
    chat_session_service.add_message(
        session_id, "assistant", result["answer"], sources=sources_data
    )

    # Auto-title on first message
    if len(history) <= 1:
        title = body.message[:50] + ("..." if len(body.message) > 50 else "")
        chat_session_service.update_session_title(session_id, title)

    return ChatResponse(
        answer=result["answer"],
        sources=[
            Source(
                document_name=s.get("document_name", ""),
                chunk_text=s.get("text_preview") or s.get("text", ""),
                score=s.get("score", 0),
                page=s.get("page"),
            )
            for s in result["sources"]
        ],
        session_id=session_id,
        confidence=result.get("confidence", 0),
    )


@router.post("/chat/stream")
async def chat_stream(body: ChatRequest):
    # Create or get session
    if body.session_id:
        session = chat_session_service.get_session(body.session_id)
        if not session:
            raise HTTPException(404, "Session not found")
        session_id = body.session_id
    else:
        session = chat_session_service.create_session()
        session_id = session["id"]

    # Save user message
    chat_session_service.add_message(session_id, "user", body.message)

    # Get chat history
    history = chat_session_service.get_chat_history(session_id)

    async def event_generator():
        import json
        full_answer = ""
        sources = []

        for event in rag_service.query_stream(body.message, chat_history=history[:-1]):
            etype = event["type"]
            if etype == "sources":
                sources = event["data"]
                yield f"event: sources\ndata: {json.dumps({'sources': sources, 'session_id': session_id})}\n\n"
            elif etype == "chunk":
                full_answer += event["data"]
                yield f"event: chunk\ndata: {json.dumps({'text': event['data']})}\n\n"
            elif etype == "done":
                yield f"event: done\ndata: {json.dumps({'confidence': event['data']})}\n\n"

        # Save assistant message after streaming -- normalize keys to match Source model
        norm_sources = []
        for s in sources:
            d = s if isinstance(s, dict) else s.dict()
            norm_sources.append({
                "document_name": d.get("document_name", ""),
                "chunk_text": d.get("chunk_text") or d.get("text_preview") or d.get("text", ""),
                "score": d.get("score", 0),
                "page": d.get("page"),
            })
        chat_session_service.add_message(session_id, "assistant", full_answer, sources=norm_sources)

        # Auto-title on first message
        if len(history) <= 1:
            title = body.message[:50] + ("..." if len(body.message) > 50 else "")
            chat_session_service.update_session_title(session_id, title)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/sessions", response_model=list[ChatSession])
async def list_sessions():
    sessions = chat_session_service.list_sessions()
    return [
        ChatSession(
            id=s["id"],
            title=s["title"],
            created_at=s.get("created_at"),
            updated_at=s.get("updated_at"),
        )
        for s in sessions
    ]


@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessage])
async def get_messages(session_id: str):
    messages = chat_session_service.get_messages(session_id)
    return [
        ChatMessage(
            id=m["id"],
            session_id=m["session_id"],
            role=m["role"],
            content=m["content"],
            sources=[
                Source(**s) if isinstance(s, dict) else s
                for s in (m.get("sources") or [])
            ],
            created_at=m.get("created_at"),
        )
        for m in messages
    ]


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    chat_session_service.delete_session(session_id)
    return {"message": "Session deleted"}
