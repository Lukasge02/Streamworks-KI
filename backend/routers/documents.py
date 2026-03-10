import uuid
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from typing import Optional
from models.documents import (
    UploadResponse,
    DocumentInfo,
    FolderCreate,
    FolderInfo,
    FolderUpdate,
    DocumentMove,
    DocumentPreview,
)
from services import document_processor, vector_store, file_storage
from services.db import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


# ── Folder Endpoints ───────────────────────────────────────────────


@router.post("/folders", response_model=FolderInfo)
async def create_folder(body: FolderCreate):
    folder_id = str(uuid.uuid4())
    get_db().table("folders").insert({
        "id": folder_id,
        "name": body.name,
        "color": body.color,
    }).execute()

    return FolderInfo(
        id=folder_id,
        name=body.name,
        color=body.color,
        document_count=0,
    )


@router.get("/folders", response_model=list[FolderInfo])
async def list_folders():
    result = (
        get_db()
        .table("folders")
        .select("*")
        .order("created_at", desc=False)
        .execute()
    )
    docs = (
        get_db()
        .table("documents")
        .select("*")
        .execute()
    )

    # Count documents per folder
    folder_counts: dict[str, int] = {}
    for doc in docs.data:
        fid = doc.get("folder_id")
        if fid:
            folder_counts[fid] = folder_counts.get(fid, 0) + 1

    return [
        FolderInfo(
            id=f["id"],
            name=f["name"],
            color=f.get("color", "#0066cc"),
            document_count=folder_counts.get(f["id"], 0),
            created_at=f.get("created_at"),
        )
        for f in result.data
    ]


@router.put("/folders/{folder_id}", response_model=FolderInfo)
async def update_folder(folder_id: str, body: FolderUpdate):
    update_data = {}
    if body.name is not None:
        update_data["name"] = body.name
    if body.color is not None:
        update_data["color"] = body.color

    if not update_data:
        raise HTTPException(400, "Keine Aenderungen angegeben")

    update_data["updated_at"] = "now()"

    result = (
        get_db()
        .table("folders")
        .update(update_data)
        .eq("id", folder_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(404, "Ordner nicht gefunden")

    folder = result.data[0]

    # Count documents
    docs = get_db().table("documents").select("*").eq("folder_id", folder_id).execute()
    doc_count = len(docs.data) if docs.data else 0

    return FolderInfo(
        id=folder["id"],
        name=folder["name"],
        color=folder.get("color", "#0066cc"),
        document_count=doc_count,
        created_at=folder.get("created_at"),
    )


@router.delete("/folders/{folder_id}")
async def delete_folder(folder_id: str):
    # Move documents in this folder back to root (folder_id = None)
    docs = get_db().table("documents").select("*").eq("folder_id", folder_id).execute()
    if docs.data:
        for doc in docs.data:
            get_db().table("documents").update({"folder_id": None}).eq("id", doc["id"]).execute()

    get_db().table("folders").delete().eq("id", folder_id).execute()
    return {"message": "Ordner geloescht"}


# ── Document Move & Preview ────────────────────────────────────────


@router.put("/{document_id}/move")
async def move_document(document_id: str, body: DocumentMove):
    # Verify folder exists if folder_id is given
    if body.folder_id:
        folder = get_db().table("folders").select("*").eq("id", body.folder_id).execute()
        if not folder.data:
            raise HTTPException(404, "Ordner nicht gefunden")

    result = (
        get_db()
        .table("documents")
        .update({"folder_id": body.folder_id, "updated_at": "now()"})
        .eq("id", document_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(404, "Dokument nicht gefunden")

    return {"message": "Dokument verschoben"}


@router.get("/{document_id}/preview", response_model=DocumentPreview)
async def preview_document(document_id: str):
    doc = get_db().table("documents").select("*").eq("id", document_id).execute()
    if not doc.data:
        raise HTTPException(404, "Dokument nicht gefunden")

    doc_info = doc.data[0]
    object_name = doc_info.get("object_name")
    mime_type = doc_info.get("mime_type", "")

    if not object_name:
        raise HTTPException(404, "Datei nicht im Speicher gefunden")

    try:
        file_bytes = file_storage.download_file(object_name)
        text = document_processor._parse_file(
            doc_info["filename"], file_bytes, mime_type
        )
    except Exception as e:
        logger.warning("Vorschau fehlgeschlagen fuer %s: %s", document_id, e)
        text = f"(Vorschau nicht verfuegbar: {e})"

    # Limit preview to first 10000 chars
    if len(text) > 10000:
        text = text[:10000] + "\n\n... (gekuerzt)"

    return DocumentPreview(
        id=document_id,
        filename=doc_info["filename"],
        content=text,
        mime_type=mime_type,
    )


# ── Existing Endpoints (modified) ─────────────────────────────────


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    folder_id: Optional[str] = Query(None),
):
    allowed = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "text/plain",
        "text/csv",
    }
    if file.content_type not in allowed:
        raise HTTPException(400, f"Unsupported file type: {file.content_type}")

    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(400, "Leere Datei kann nicht verarbeitet werden")
    if len(file_bytes) > 40 * 1024 * 1024:
        raise HTTPException(400, "File too large (max 40MB)")

    # Check for duplicate filename
    existing = (
        get_db()
        .table("documents")
        .select("id")
        .eq("filename", file.filename)
        .execute()
    )
    if existing.data:
        raise HTTPException(
            409,
            f"Dokument '{file.filename}' existiert bereits. Bitte zuerst loeschen oder umbenennen.",
        )

    # Verify folder exists if folder_id is given
    if folder_id:
        folder = get_db().table("folders").select("*").eq("id", folder_id).execute()
        if not folder.data:
            raise HTTPException(404, "Ordner nicht gefunden")

    try:
        result = document_processor.process_document(
            file.filename, file_bytes, file.content_type
        )
    except Exception as e:
        raise HTTPException(
            500,
            f"Dokument konnte nicht verarbeitet werden: {e}"
        )

    # Persist document metadata in DB so GET /api/documents/ returns it
    insert_data = {
        "id": result["document_id"],
        "filename": result["filename"],
        "object_name": f"{result['document_id']}/{result['filename']}",
        "file_size": len(file_bytes),
        "mime_type": file.content_type,
        "chunks": result["chunks_count"],
    }
    if folder_id:
        insert_data["folder_id"] = folder_id

    get_db().table("documents").insert(insert_data).execute()

    # Mark hybrid search index dirty so new chunks are found
    from services.rag_service import mark_index_dirty
    mark_index_dirty()

    return UploadResponse(
        document_id=result["document_id"],
        filename=result["filename"],
        chunks=result["chunks_count"],
        message=f"Document '{file.filename}' processed successfully",
    )


@router.get("/", response_model=list[DocumentInfo])
async def list_documents():
    result = (
        get_db()
        .table("documents")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )
    return [
        DocumentInfo(
            id=doc["id"],
            filename=doc["filename"],
            file_size=doc.get("file_size", 0),
            mime_type=doc.get("mime_type", ""),
            chunks=doc.get("chunks", 0),
            folder_id=doc.get("folder_id"),
            created_at=doc.get("created_at"),
        )
        for doc in result.data
    ]


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    # Delete from vector store
    vector_store.delete_document(document_id)

    # Delete from file storage
    doc = (
        get_db()
        .table("documents")
        .select("*")
        .eq("id", document_id)
        .execute()
    )
    if doc.data:
        object_name = doc.data[0].get("object_name")
        if object_name:
            try:
                file_storage.delete_file(object_name)
            except Exception:
                pass

    # Delete from database
    get_db().table("documents").delete().eq("id", document_id).execute()

    # Mark hybrid search index dirty
    from services.rag_service import mark_index_dirty
    mark_index_dirty()

    return {"message": "Document deleted"}
