"""
Testing Service
Handles projects, document linking, and AI-based test plan generation.
"""

from typing import List, Dict, Optional
import logging
from services.db import db
from services.rag.document_service import document_service
from services.rag.vector_store import vector_store

from openai import OpenAI
from config import config
import json
from services.rag.access_service import get_access_service, AccessLevel
from services.auth_service import UserRole

from pydantic import BaseModel, Field

# --- structured output models ---


class TestCaseModel(BaseModel):
    test_id: str = Field(..., description="Unique Test ID, e.g. TC-001")
    title: str = Field(..., description="Short title of the test")
    description: str = Field(
        ..., description="Detailed description of what is being tested"
    )
    preconditions: str = Field(..., description="What must be true before the test")
    steps: str = Field(..., description="Step-by-step instructions")
    expected_result: str = Field(..., description="Expected outcome")


class TestPlanModel(BaseModel):
    project_name: str
    introduction: str
    test_cases: List[TestCaseModel]
    summary: str


class TestingService:
    def __init__(self):
        self.db = db
        self.doc_service = document_service
        self.vector_store = vector_store

        self.openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.logger = logging.getLogger(__name__)
        self.access_service = get_access_service()

    # --- Projects ---

    def create_project(self, name: str, description: str = None) -> Dict:
        """Create a new project."""
        result = self.db.create_project(name, description)
        if result and result.data:
            return result.data[0]
        return None

    def list_projects(self) -> List[Dict]:
        """List all projects."""
        return self.db.list_projects()

    def get_project(self, project_id: str) -> Optional[Dict]:
        """Get project details."""
        return self.db.get_project(project_id)

    def delete_project(self, project_id: str) -> bool:
        """Delete a project."""
        return self.db.delete_project(project_id)

    def link_document(
        self,
        project_id: str,
        doc_id: str,
        category: str = "context",
        filename: str = None,
        user: Dict = None,
    ) -> Dict:
        """Link a project to a document with optional filename for immediate display."""
        # Enforce RBAC: Customers cannot upload
        if user and user.get("role") == UserRole.CUSTOMER:
            raise PermissionError("Customers are not allowed to link documents.")

        return self.db.link_project_document(project_id, doc_id, category, filename)

    def unlink_document(self, project_id: str, doc_id: str) -> Dict:
        """
        Unlink and delete a document from project.
        - Removes link from project_documents table
        - Deletes document chunks from Qdrant
        - Deletes original file from MinIO
        """
        # 1. Remove link from project
        unlinked = self.db.unlink_project_document(project_id, doc_id)

        # 2. Delete from document service (Qdrant + MinIO)
        delete_result = self.doc_service.delete_document(doc_id)

        return {
            "success": unlinked or delete_result.get("success", False),
            "unlinked": unlinked,
            "chunks_deleted": delete_result.get("chunks_deleted", 0),
            "file_deleted": delete_result.get("file_deleted", False),
        }

    def get_project_documents(self, project_id: str) -> List[Dict]:
        """Get documents linked to a project with full metadata and processing status."""
        links = self.db.get_project_documents(project_id)
        documents = []

        for link in links:
            doc_id = link.get("doc_id")
            link_category = link.get("category", "context")
            link_filename = link.get("filename")
            # Get rag_enabled from link, default to True for backward compat
            rag_enabled = link.get("rag_enabled", True)
            if rag_enabled is None:
                rag_enabled = True

            if not doc_id:
                continue

            # Try to find the document in Qdrant by parent_doc_id (how chunks are stored)
            try:
                # Search for any chunk with this parent_doc_id
                chunks = self.vector_store.search(
                    query="",  # Empty query to just match filter
                    limit=1,
                    score_threshold=0.0,
                    filters={"parent_doc_id": doc_id},
                )

                if chunks and len(chunks) > 0:
                    # Document found in Qdrant - use its metadata
                    chunk_meta = chunks[0].get("metadata", {})
                    filename = chunk_meta.get("filename", link_filename or "Dokument")
                    category = chunk_meta.get("category", link_category)

                    documents.append(
                        {
                            "doc_id": doc_id,
                            "content": chunks[0].get("content", ""),
                            "metadata": {
                                "filename": filename,
                                "category": category,
                                "doc_type": chunk_meta.get("doc_type", "unknown"),
                                "created_at": chunk_meta.get("created_at"),
                                "word_count": chunk_meta.get("word_count", 0),
                                "page_count": chunk_meta.get("page_count", 0),
                            },
                            "linked_at": link.get("created_at"),
                            "processing_status": "completed",
                            "rag_enabled": rag_enabled,
                        }
                    )
                else:
                    # Document not yet in Qdrant - check processing status
                    status_info = self.doc_service.get_upload_status(doc_id)
                    current_status = (
                        status_info.get("status", "processing")
                        if status_info
                        else "processing"
                    )
                    progress = status_info.get("progress", 0) if status_info else 0

                    # Get filename from status result if available
                    result_filename = None
                    if status_info and status_info.get("result"):
                        result_filename = status_info["result"].get("filename")

                    documents.append(
                        {
                            "doc_id": doc_id,
                            "metadata": {
                                "filename": result_filename
                                or link_filename
                                or "Wird verarbeitet...",
                                "category": link_category,
                            },
                            "linked_at": link.get("created_at"),
                            "processing_status": current_status,
                            "processing_progress": progress,
                            "rag_enabled": rag_enabled,
                        }
                    )
            except Exception as e:
                self.logger.warning(f"Error fetching document {doc_id}: {e}")
                # Fallback to processing state
                documents.append(
                    {
                        "doc_id": doc_id,
                        "metadata": {
                            "filename": link_filename or "Fehler beim Laden",
                            "category": link_category,
                        },
                        "linked_at": link.get("created_at"),
                        "processing_status": "error",
                        "rag_enabled": rag_enabled,
                    }
                )

        return documents

    # --- Test Plan Generation ---

    # --- Test Plan Generation (Async & Structured) ---

    def start_test_plan_generation(
        self,
        project_id: str,
        context_categories: List[str] = None,
        selected_doc_ids: List[str] = None,
        exclude_doc_ids: List[str] = None,
        background_tasks=None,
    ) -> Dict:
        """
        Start the async generation of a test plan.
        1. Create a placeholder record in DB with status "processing".
        2. Launch background task.
        """
        # Create placeholder
        placeholder_content = json.dumps(
            {
                "status": "processing",
                "stage": "initializing",
                "progress": 0,
                "message": "Starting generation...",
            }
        )

        result = self.db.save_test_plan(project_id, placeholder_content)

        if not result or not result.data:
            raise Exception("Failed to create test plan placeholder")

        plan_id = result.data[0]["id"]

        # Start background task
        if background_tasks:
            background_tasks.add_task(
                self._generate_test_plan_task,
                plan_id=plan_id,
                project_id=project_id,
                context_categories=context_categories,
                selected_doc_ids=selected_doc_ids,
                exclude_doc_ids=exclude_doc_ids,
            )

        return {
            "plan_id": plan_id,
            "status": "processing",
            "message": "Test plan generation started",
        }

    def _generate_test_plan_task(
        self,
        plan_id: str,
        project_id: str,
        context_categories: List[str] = None,
        selected_doc_ids: List[str] = None,
        exclude_doc_ids: List[str] = None,
    ):
        """Background task to generate test plan"""
        try:
            # Helper to update status
            def update_status(stage: str, progress: int, message: str):
                self.db.update_test_plan(
                    plan_id,
                    json.dumps(
                        {
                            "status": "processing",
                            "stage": stage,
                            "progress": progress,
                            "message": message,
                        }
                    ),
                )

            update_status("fetching_context", 10, "Retrieving project documents...")

            project = self.get_project(project_id)
            if not project:
                raise ValueError("Project not found")

            # 1. Get Project Context (DDDs) - only RAG-enabled documents
            project_docs = self.get_project_documents(project_id)
            # Filter to only include rag_enabled documents
            project_docs = [d for d in project_docs if d.get("rag_enabled", True)]
            if not project_docs:
                raise ValueError(
                    "No documents linked to this project. Please upload a DDD first."
                )

            project_context = ""
            project_doc_ids = []

            total_docs = len(project_docs)
            for idx, doc in enumerate(project_docs):
                update_status(
                    "analyzing_docs",
                    10 + int((idx / total_docs) * 20),
                    f"Analyzing document {doc.get('metadata', {}).get('filename')}...",
                )

                project_doc_ids.append(doc["doc_id"])

                # Fetch chunks
                chunks = self.vector_store.search(
                    query="", limit=100, filters={"parent_doc_id": doc["doc_id"]}
                )
                chunks.sort(key=lambda x: x.get("metadata", {}).get("chunk_index", 0))

                doc_content = f"\n--- Document: {doc.get('metadata', {}).get('filename', 'Unknown')} ---\n"
                doc_content += "\n".join([chunk["content"] for chunk in chunks])

                if not chunks:
                    doc_content += doc.get("content", "")

                project_context += doc_content + "\n"

            # 2. Get General Context (RAG)
            update_status("consulting_kb", 40, "Consulting knowledge base...")

            general_query = (
                "Streamworks test plan standards validation rules best practices"
            )

            search_filters = None
            access_filter = None

            if selected_doc_ids and len(selected_doc_ids) > 0:
                access_filter = {"doc_ids": selected_doc_ids}
            elif context_categories and len(context_categories) > 0:
                search_filters = {"category": context_categories}

            if exclude_doc_ids and len(exclude_doc_ids) > 0:
                if access_filter is None:
                    access_filter = {}
                access_filter["exclude_doc_ids"] = exclude_doc_ids

            general_results = self.vector_store.search(
                query=general_query,
                limit=5,
                filters=search_filters,
                access_filter=access_filter,
            )

            general_context = "\n".join(
                [
                    f"- {r['content']}"
                    for r in general_results
                    if r.get("metadata", {}).get("parent_doc_id") not in project_doc_ids
                ]
            )

            # 3. Construct Prompt with Structured Output
            update_status("generating_plan", 60, "Generating test plan with AI...")

            system_prompt = """
            You are an expert QA Lead at Streamworks specializing in Domain Driven Design (DDD) analysis.
            Your task is to create a high-precision User Acceptance Test (UAT) Plan based strictly on the provided DDD context.

            ### CRITICAL INSTRUCTIONS:
            1. **Role-Based Testing**: Identify specific actors mentioned (e.g., "System Admin", "Mandator Admin", "Planner"). Start test cases with "As [Role]...". If no roles are specified, use "As User".
            2. **Specific Error Codes**: If the DDD lists specific error codes (e.g., "11007", "98002"), you MUST create negative test cases that explicitly expect these codes in the "Expected Result".
            3. **Business Boundaries**: Search for limits (e.g., "max 2000 items", "50 retries"). Create tests that hit exactly these limits.
            4. **Ubiquitous Language**: Use the EXACT terminology from the document (e.g., use "Logically Deleted Agent" instead of just "Deleted Agent").

            ### OUTPUT FORMAT:
            - **Language**: The entire output (Scenario Titles, Steps, Results) MUST be in **GERMAN**.
            - **Structure**: Return strictly JSON matching the defined schema.
            - **Tone**: Professional, precise, and business-oriented.

            Create a comprehensive plan covering Happy Paths, Edge Cases, and Integration/Error Scenarios.
            """

            user_prompt = f"""
            # General Streamworks Context
            {general_context}

            # Project Context (DDD)
            {project_context}

            # Task
            Generate a Test Plan for the project: "{project["name"]}".
            Ensure at least 10-15 solid test cases.
            """

            # 4. Call LLM with Structured Output
            response = self.openai_client.beta.chat.completions.parse(
                model=config.LLM_MODEL or "gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format=TestPlanModel,
                temperature=0.3,
            )

            test_plan_data = response.choices[0].message.parsed

            # Serialize for DB storage
            final_content = test_plan_data.model_dump_json()

            # Final update: store the actual JSON plan inside a wrapper that indicates success/schema
            # We store the plan + status wrapper so frontend knows it's the structured version

            update_status("finalizing", 90, "Finalizing...")

            final_storage = json.dumps(
                {
                    "status": "completed",
                    "format": "structured_v1",
                    "data": json.loads(final_content),
                }
            )

            # 5. Save Final Plan
            self.db.update_test_plan(plan_id, final_storage)

        except Exception as e:
            self.logger.error(f"Test plan generation failed: {e}")
            import traceback

            traceback.print_exc()

            # Save error state
            error_content = json.dumps({"status": "failed", "error": str(e)})
            self.db.update_test_plan(plan_id, error_content)

    def get_test_plans(self, project_id: str) -> List[Dict]:
        """Get generated test plans."""
        return self.db.get_test_plans(project_id)

    def update_plan(self, plan_id: str, content: str) -> bool:
        """Update a test plan's content directly."""
        result = self.db.update_test_plan(plan_id, content)
        if result and hasattr(result, "data") and result.data:
            return True
        return False

    # --- DDD Enhancement Methods ---

    def generate_project_description(self, project_id: str) -> str:
        """
        Generate a project description from the uploaded DDD using AI.
        Extracts key information from DDD documents.
        """
        # Get project's DDD documents
        project_docs = self.get_project_documents(project_id)
        ddd_docs = [
            d for d in project_docs if d.get("metadata", {}).get("category") == "ddd"
        ]

        if not ddd_docs:
            raise ValueError(
                "Kein DDD-Dokument gefunden. Bitte lade zuerst ein DDD hoch."
            )

        # Gather DDD content
        ddd_content = ""
        for doc in ddd_docs:
            chunks = self.vector_store.search(
                query="",
                limit=50,  # Get enough chunks to understand the document
                filters={"parent_doc_id": doc["doc_id"]},
            )
            chunks.sort(key=lambda x: x.get("metadata", {}).get("chunk_index", 0))

            doc_text = "\n".join([c["content"] for c in chunks if c.get("content")])
            if doc_text:
                ddd_content += (
                    f"\n--- {doc.get('metadata', {}).get('filename', 'DDD')} ---\n"
                )
                ddd_content += doc_text[:15000]  # Limit to avoid token overflow

        if not ddd_content.strip():
            raise ValueError("DDD-Dokument hat keinen lesbaren Inhalt.")

        # Generate description using AI
        system_prompt = """Du bist ein technischer Analyst. Erstelle eine prägnante Projektbeschreibung 
basierend auf dem Domain Driven Design (DDD) Dokument. Die Beschreibung sollte:
- Max. 2-3 Sätze lang sein
- Die Hauptfunktionalität beschreiben
- Für Manager/Stakeholder verständlich sein
- Auf Deutsch sein

Gib NUR die Beschreibung zurück, keine Einleitung oder Erklärung."""

        try:
            response = self.openai_client.chat.completions.create(
                model=config.LLM_MODEL or "gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"DDD Dokument:\n\n{ddd_content[:8000]}",
                    },
                ],
                temperature=0.3,
                max_tokens=200,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            self.logger.error(f"Description generation failed: {e}")
            raise ValueError(f"Fehler bei der Beschreibungsgenerierung: {str(e)}")

    def chat_with_ddd(
        self,
        project_id: str,
        query: str,
        conversation_history: List[Dict] = None,
        include_test_cases: bool = False,
        user: Dict = None,
    ) -> Dict:
        """
        RAG chat scoped to project's DDD documents.
        Optionally includes generated test cases as context.

        Returns:
            {
                "answer": str,
                "sources": List[{filename, content_snippet, score}],
                "test_cases_used": bool
            }
        """
        # Get project's DDD doc_ids for scoped search
        project_docs = self.get_project_documents(project_id)
        ddd_doc_ids = [
            d["doc_id"]
            for d in project_docs
            if d.get("metadata", {}).get("category") == "ddd"
            and d.get("rag_enabled", True)  # Only include RAG-enabled documents
        ]

        # Enforce Access Control if User is present
        if user:
            # Check access for each DDD document
            # If Customer, ensure they can view this doc (though AccessService default is Internal)
            # We assume AccessService.check_document_access handles the logic.
            user_id = user.get("id")
            user_roles = [user.get("role")]

            allowed_ids = []
            for doc_id in ddd_doc_ids:
                if self.access_service.check_document_access(
                    doc_id, user_id, user_roles
                ):
                    allowed_ids.append(doc_id)
            ddd_doc_ids = allowed_ids

        if not ddd_doc_ids:
            return {
                "answer": "Kein DDD-Dokument in diesem Projekt gefunden. Bitte lade zuerst ein DDD hoch.",
                "sources": [],
                "test_cases_used": False,
            }

        # Scoped vector search - only search within project's DDDs
        search_results = self.vector_store.search(
            query=query,
            limit=6,
            score_threshold=0.3,
            access_filter={"doc_ids": ddd_doc_ids},
        )

        # Build context from search results
        context_parts = []
        sources = []

        for i, result in enumerate(search_results):
            content = result.get("content", "")
            filename = result.get("metadata", {}).get("filename", "Dokument")
            score = result.get("score", 0)

            context_parts.append(f"[Quelle {i + 1}: {filename}]\n{content}")
            sources.append(
                {
                    "filename": filename,
                    "content_snippet": content[:200] + "..."
                    if len(content) > 200
                    else content,
                    "score": round(score, 3),
                }
            )

        context = "\n\n---\n\n".join(context_parts) if context_parts else ""

        # Optionally add test cases as context
        test_case_context = ""
        if include_test_cases:
            test_plans = self.get_test_plans(project_id)
            if test_plans:
                try:
                    latest_plan = test_plans[0]
                    plan_data = json.loads(latest_plan.get("content", "{}"))
                    if plan_data.get("status") == "completed" and plan_data.get(
                        "data", {}
                    ).get("test_cases"):
                        cases = plan_data["data"]["test_cases"][:10]  # Limit to 10
                        test_case_context = "\n\n--- Existierende Testfälle ---\n"
                        for tc in cases:
                            test_case_context += (
                                f"- {tc.get('test_id', 'TC')}: {tc.get('title', '')}\n"
                            )
                except (json.JSONDecodeError, KeyError):
                    pass

        # Build messages for LLM
        system_prompt = """Du bist ein Experte für Domain Driven Design (DDD) Analyse bei Streamworks.
Beantworte Fragen basierend auf dem bereitgestellten DDD-Kontext.
- Antworte präzise und auf Deutsch
- Verweise auf spezifische Abschnitte wenn möglich
- Wenn die Antwort nicht im Kontext ist, sage das ehrlich"""

        messages = [{"role": "system", "content": system_prompt}]

        if context:
            messages.append(
                {
                    "role": "system",
                    "content": f"Relevanter DDD-Kontext:\n\n{context}{test_case_context}",
                }
            )

        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history[-6:])

        messages.append({"role": "user", "content": query})

        # Call LLM
        try:
            response = self.openai_client.chat.completions.create(
                model=config.LLM_MODEL or "gpt-4o-mini",
                messages=messages,
                temperature=0.5,
                max_tokens=1000,
            )
            answer = response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"DDD chat failed: {e}")
            answer = f"Fehler bei der Anfrage: {str(e)}"

        return {
            "answer": answer,
            "sources": sources,
            "test_cases_used": bool(test_case_context),
        }


testing_service = TestingService()
