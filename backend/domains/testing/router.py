from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks, Depends
from typing import List, Optional
from pydantic import BaseModel
import uuid
import traceback

from domains.testing.service import testing_service
from services.rag.document_service import document_service
from services.auth_service import get_current_user, require_role, UserRole

router = APIRouter(prefix="/api/testing", tags=["Testing"])

# --- Models ---


class ProjectCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    created_at: str


class TestPlanResponse(BaseModel):
    id: str
    project_id: str
    content: str
    created_at: str


class GenerateTestPlanRequest(BaseModel):
    context_categories: Optional[List[str]] = (
        None  # Filter RAG context by these categories
    )
    selected_doc_ids: Optional[List[str]] = (
        None  # Explicit document IDs to include (takes precedence)
    )
    exclude_doc_ids: Optional[List[str]] = None  # Document IDs to exclude from context


# --- Endpoints ---


@router.post(
    "/projects",
    response_model=ProjectResponse,
    dependencies=[Depends(require_role(["owner", "admin", "internal"]))],
)
async def create_project(request: ProjectCreateRequest):
    """Create a new testing project."""
    try:
        project = testing_service.create_project(request.name, request.description)
        if not project:
            raise HTTPException(status_code=500, detail="Failed to create project")
        return project
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects", response_model=List[ProjectResponse])
async def list_projects():
    """List all projects."""
    try:
        return testing_service.list_projects()
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str):
    """Get project details."""
    try:
        project = testing_service.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/projects/{project_id}", dependencies=[Depends(require_role(["owner", "admin"]))]
)
async def delete_project(project_id: str):
    """Delete a project."""
    try:
        success = testing_service.delete_project(project_id)
        if not success:
            raise HTTPException(
                status_code=404, detail="Project not found or failed to delete"
            )
        return {"success": True}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/projects/{project_id}/documents",
    dependencies=[Depends(require_role(["owner", "admin", "internal"]))],
)
async def upload_project_document(
    project_id: str,
    category: str = "context",
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
):
    """
    Upload a document to a project.
    - Uploads to DocumentService (background)
    - Links to Project with filename for immediate display
    """
    try:
        # Check project exists
        project = testing_service.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # 1. Prepare Document Upload
        # DDD documents - Accept PDF and Markdown
        if category == "ddd":
            allowed_exts = (".pdf", ".md", ".markdown")
            if not file.filename.lower().endswith(allowed_exts):
                raise HTTPException(
                    status_code=400,
                    detail="DDD muss als PDF oder Markdown hochgeladen werden.",
                )

        if not document_service.can_process(file.filename):
            raise HTTPException(status_code=400, detail="Unsupported file type")

        content = await file.read()
        doc_id = str(uuid.uuid4())

        # 2. Link to Project immediately with category AND filename
        testing_service.link_document(project_id, doc_id, category, file.filename)

        # 3. Start Background Processing
        document_service._update_status(doc_id, "queued", 0)

        if background_tasks:
            background_tasks.add_task(
                document_service.process_file_background,
                doc_id=doc_id,
                file_content=content,
                filename=file.filename,
                save_original=True,
                explicit_category=category,
            )

        return {
            "task_id": doc_id,
            "status": "queued",
            "filename": file.filename,
            "message": "Document uploading to project",
        }

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/documents")
async def list_project_documents(project_id: str):
    """List documents for a project."""
    try:
        return testing_service.get_project_documents(project_id)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/projects/{project_id}/documents/{doc_id}")
async def delete_project_document(project_id: str, doc_id: str):
    """
    Delete a document from a project.
    - Removes link from project_documents
    - Deletes chunks from Qdrant
    - Deletes original file from MinIO
    """
    try:
        result = testing_service.unlink_document(project_id, doc_id)
        if not result.get("success"):
            raise HTTPException(
                status_code=404, detail="Document not found or delete failed"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


class UpdateDocumentRAGRequest(BaseModel):
    rag_enabled: bool


@router.patch("/projects/{project_id}/documents/{doc_id}/rag")
async def update_document_rag(
    project_id: str, doc_id: str, request: UpdateDocumentRAGRequest
):
    """
    Toggle RAG enabled status for a document.
    When rag_enabled=False, document is excluded from RAG context in test plan generation and DDD chat.
    """
    try:
        from services.db import db

        success = db.update_project_document_rag(
            project_id, doc_id, request.rag_enabled
        )
        if not success:
            raise HTTPException(status_code=404, detail="Document link not found")
        return {"success": True, "rag_enabled": request.rag_enabled}
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/projects/{project_id}/generate")
async def generate_test_plan(
    project_id: str,
    request: GenerateTestPlanRequest = None,
    background_tasks: BackgroundTasks = None,
):
    """
    Trigger async test plan generation.
    Returns immediately with a task/plan ID.
    User should poll GET /projects/{project_id}/plans to check status.
    """
    try:
        categories = request.context_categories if request else None
        selected_docs = request.selected_doc_ids if request else None
        exclude_docs = request.exclude_doc_ids if request else None

        result = testing_service.start_test_plan_generation(
            project_id,
            context_categories=categories,
            selected_doc_ids=selected_docs,
            exclude_doc_ids=exclude_docs,
            background_tasks=background_tasks,
        )
        return result
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/plans")
async def list_test_plans(project_id: str):
    """List generated test plans."""
    try:
        return testing_service.get_test_plans(project_id)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


class UpdateTestPlanRequest(BaseModel):
    content: str  # Expecting the full JSON string of the plan structure


@router.put("/projects/{project_id}/plans/{plan_id}")
async def update_test_plan(
    project_id: str, plan_id: str, request: UpdateTestPlanRequest
):
    """Update a test plan (e.g. saving manual edits)."""
    try:
        success = testing_service.update_plan(plan_id, request.content)
        if not success:
            raise HTTPException(
                status_code=404, detail="Plan not found or update failed"
            )
        return {"success": True}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# --- DDD Enhancement Endpoints ---


@router.post("/projects/{project_id}/generate-description")
async def generate_project_description(project_id: str):
    """
    Generate a project description from the uploaded DDD using AI.
    Returns a short description summarizing the DDD content.
    """
    try:
        project = testing_service.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        description = testing_service.generate_project_description(project_id)
        return {"description": description, "success": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


class DDDChatRequest(BaseModel):
    query: str
    conversation_history: Optional[List[dict]] = None
    include_test_cases: bool = False


@router.post("/projects/{project_id}/chat")
async def chat_with_ddd(
    project_id: str, request: DDDChatRequest, user: dict = Depends(get_current_user)
):
    """
    RAG chat scoped to project's DDD documents.
    Answers questions based on the uploaded DDD.
    Optionally includes generated test cases as context.
    """
    try:
        project = testing_service.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        result = testing_service.chat_with_ddd(
            project_id=project_id,
            query=request.query,
            conversation_history=request.conversation_history,
            include_test_cases=request.include_test_cases,
            user=user,
        )
        return result
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


class UpdateProjectRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


@router.patch("/projects/{project_id}")
async def update_project(project_id: str, request: UpdateProjectRequest):
    """Update project name or description."""
    try:
        from services.db import db

        project = testing_service.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Build update dict
        updates = {}
        if request.name is not None:
            updates["name"] = request.name
        if request.description is not None:
            updates["description"] = request.description

        if not updates:
            return {"success": True, "message": "No changes"}

        # Update in database
        result = (
            db.supabase.table("projects").update(updates).eq("id", project_id).execute()
        )

        if result.data:
            return {"success": True, "project": result.data[0]}
        return {"success": False}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
