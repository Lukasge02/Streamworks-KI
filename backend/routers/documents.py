from fastapi import APIRouter, UploadFile, File, HTTPException
from models.documents import UploadResponse, DocumentInfo
from services import document_processor, vector_store, file_storage
from services.db import get_db

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
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
    get_db().table("documents").insert({
        "id": result["document_id"],
        "filename": result["filename"],
        "object_name": f"{result['document_id']}/{result['filename']}",
        "file_size": len(file_bytes),
        "mime_type": file.content_type,
        "chunks": result["chunks_count"],
    }).execute()

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
