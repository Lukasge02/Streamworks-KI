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
from services.rag.access_service import get_access_service
from services.auth_service import UserRole

from pydantic import BaseModel, Field

# --- structured output models ---

from typing import Literal


class TestCaseModel(BaseModel):
    """Enhanced test case model with priority and categorization."""
    test_id: str = Field(..., description="Unique Test ID, e.g. TC-001")
    title: str = Field(..., description="Short title of the test")
    description: str = Field(
        ..., description="Detailed description of what is being tested"
    )
    preconditions: str = Field(..., description="What must be true before the test")
    steps: str = Field(..., description="Step-by-step instructions")
    expected_result: str = Field(..., description="Expected outcome")
    # Enhanced fields for state-of-the-art test planning
    priority: Literal["critical", "high", "medium", "low"] = Field(
        default="medium", 
        description="Test priority: critical for security/data-loss scenarios, high for core functionality"
    )
    category: Literal["happy_path", "edge_case", "error_handling", "integration", "security", "performance"] = Field(
        default="happy_path",
        description="Test category for organization"
    )
    risk_level: Literal["high", "medium", "low"] = Field(
        default="medium",
        description="Business risk if this test fails"
    )
    related_requirements: List[str] = Field(
        default_factory=list,
        description="List of requirement IDs this test covers, e.g. ['BR-001', 'UC-002']"
    )


class CoverageAnalysis(BaseModel):
    """Analysis of test coverage."""
    covered_use_cases: List[str] = Field(
        default_factory=list,
        description="List of Use Cases covered by tests"
    )
    covered_business_rules: List[str] = Field(
        default_factory=list,
        description="List of Business Rules covered by tests"
    )
    covered_error_codes: List[str] = Field(
        default_factory=list,
        description="List of Error Codes tested"
    )
    coverage_gaps: List[str] = Field(
        default_factory=list,
        description="Identified gaps in test coverage"
    )


# --- Multi-Pass Generation Models ---

class UseCaseExtraction(BaseModel):
    """Extracted Use Case from DDD document."""
    id: str = Field(..., description="Use Case ID, e.g. UC-001")
    title: str = Field(..., description="Use Case title")
    actors: List[str] = Field(default_factory=list, description="Actors involved")
    preconditions: str = Field(default="", description="What must be true before")
    main_flow: str = Field(default="", description="Main success scenario steps")
    error_cases: List[str] = Field(default_factory=list, description="Error/exception flows")
    postconditions: str = Field(default="", description="What is true after")


class BusinessRuleExtraction(BaseModel):
    """Extracted Business Rule from DDD document."""
    id: str = Field(..., description="Business Rule ID, e.g. BR-001")
    description: str = Field(..., description="Rule description")
    priority: str = Field(default="medium", description="Priority: critical, high, medium, low")
    validation_type: str = Field(default="constraint", description="Type: constraint, calculation, authorization")


class ErrorCodeExtraction(BaseModel):
    """Extracted Error Code from DDD document."""
    code: str = Field(..., description="Error code, e.g. E-0001")
    description: str = Field(..., description="Error description")
    http_status: int = Field(default=400, description="HTTP status code")
    trigger_condition: str = Field(default="", description="When this error occurs")


class ExtractedRequirements(BaseModel):
    """First-pass extraction of all testable requirements from DDD."""
    use_cases: List[UseCaseExtraction] = Field(
        default_factory=list,
        description="All Use Cases (UC-xxx) found in document"
    )
    business_rules: List[BusinessRuleExtraction] = Field(
        default_factory=list,
        description="All Business Rules (BR-xxx) found in document"
    )
    error_codes: List[ErrorCodeExtraction] = Field(
        default_factory=list,
        description="All Error Codes (E-xxxx) found in document"
    )
    actors: List[str] = Field(
        default_factory=list,
        description="All actor/role names mentioned"
    )
    domain_entities: List[str] = Field(
        default_factory=list,
        description="Key domain entities (User, Project, Session, etc.)"
    )
    numeric_limits: List[str] = Field(
        default_factory=list,
        description="Numeric limits for boundary testing (max 2000 users, 5 attempts, etc.)"
    )


class CoverageValidation(BaseModel):
    """Third-pass validation of test coverage completeness."""
    missing_use_cases: List[str] = Field(
        default_factory=list,
        description="Use Case IDs without test coverage"
    )
    missing_business_rules: List[str] = Field(
        default_factory=list,
        description="Business Rule IDs without test coverage"
    )
    missing_error_codes: List[str] = Field(
        default_factory=list,
        description="Error Codes without negative tests"
    )
    coverage_percentage: float = Field(
        default=0.0,
        description="Percentage of requirements covered (0-100)"
    )
    is_complete: bool = Field(
        default=False,
        description="True if coverage >= 95%"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Suggestions for improving coverage"
    )


class TestPlanModel(BaseModel):
    """Enhanced test plan with coverage analysis."""
    project_name: str
    introduction: str = Field(..., description="Overview of what the test plan covers")
    test_cases: List[TestCaseModel]
    summary: str = Field(..., description="Executive summary with key findings")
    # Enhanced fields
    coverage: CoverageAnalysis = Field(
        default_factory=CoverageAnalysis,
        description="Analysis of test coverage"
    )
    total_test_count: int = Field(default=0, description="Total number of test cases")
    critical_tests_count: int = Field(default=0, description="Number of critical priority tests")
    recommended_test_order: List[str] = Field(
        default_factory=list,
        description="Recommended order of test execution (test_ids)"
    )



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

            # =====================================================
            # MULTI-PASS TEST GENERATION (State-of-the-Art 2024)
            # Pass 1: Extract requirements from DDD
            # Pass 2: Generate tests ensuring 100% coverage
            # Pass 3: Validate coverage (optional, for large DDDs)
            # =====================================================

            # PASS 1: REQUIREMENT EXTRACTION
            update_status("extracting_requirements", 45, "Extracting requirements from DDD...")

            extraction_prompt = """You are a Requirements Analyst. Extract ALL testable requirements from this DDD document.

## EXTRACTION RULES
1. Find EVERY Use Case (UC-xxx) - extract ID, title, actors, main flow, error cases
2. Find EVERY Business Rule (BR-xxx) - extract ID, description, priority
3. Find EVERY Error Code (E-xxxx) - extract code, description, HTTP status, trigger condition
4. List ALL actor/role names mentioned (exact names from document)
5. List key domain entities (User, Session, Role, etc.)
6. List ALL numeric limits for boundary testing (max X users, Y attempts, Z days, etc.)

BE EXHAUSTIVE - missing requirements here means missing tests later!"""

            extraction_user_prompt = f"""# DDD DOCUMENT TO ANALYZE
{project_context}

Extract every testable requirement. Do not miss any UC-xxx, BR-xxx, or E-xxxx codes."""

            extraction_response = self.openai_client.beta.chat.completions.parse(
                model=config.LLM_MODEL or "gpt-4o",
                messages=[
                    {"role": "system", "content": extraction_prompt},
                    {"role": "user", "content": extraction_user_prompt},
                ],
                response_format=ExtractedRequirements,
                temperature=0.1,  # Low temperature for accurate extraction
            )

            extracted = extraction_response.choices[0].message.parsed
            
            # Log extraction results
            self.logger.info(
                f"Extracted: {len(extracted.use_cases)} UCs, "
                f"{len(extracted.business_rules)} BRs, "
                f"{len(extracted.error_codes)} Error Codes"
            )

            # PASS 2: TEST GENERATION WITH EXPLICIT REQUIREMENTS
            update_status("generating_tests", 60, "Generating tests for each requirement...")

            # Format extracted requirements for the prompt
            uc_list = "\n".join([
                f"- {uc.id}: {uc.title} (Actors: {', '.join(uc.actors)})"
                for uc in extracted.use_cases
            ]) or "No Use Cases found"
            
            br_list = "\n".join([
                f"- {br.id}: {br.description} (Priority: {br.priority})"
                for br in extracted.business_rules
            ]) or "No Business Rules found"
            
            ec_list = "\n".join([
                f"- {ec.code}: {ec.description} (HTTP {ec.http_status})"
                for ec in extracted.error_codes
            ]) or "No Error Codes found"

            limits_list = "\n".join([f"- {limit}" for limit in extracted.numeric_limits]) or "No numeric limits found"

            generation_system_prompt = f"""You are an elite QA Architect creating a comprehensive UAT Test Plan.

## EXTRACTED REQUIREMENTS (You MUST cover ALL of these)

### Use Cases ({len(extracted.use_cases)} total) - EACH needs at least 1 happy path + 1 error test:
{uc_list}

### Business Rules ({len(extracted.business_rules)} total) - EACH needs at least 1 validation test:
{br_list}

### Error Codes ({len(extracted.error_codes)} total) - EACH needs exactly 1 negative test:
{ec_list}

### Numeric Limits (for boundary testing):
{limits_list}

### Actors (use exact names): {', '.join(extracted.actors)}
### Domain Entities: {', '.join(extracted.domain_entities)}

## TEST GENERATION RULES

### Mandatory Coverage (DO NOT SKIP ANY - THIS IS CRITICAL):

1. **Use Case Coverage**: For each UC-xxx in the extracted list, you MUST create:
   - 1 happy path test (successful scenario following main flow)
   - 1 error handling test for EACH error case mentioned in the Use Case
   - Link tests to UC-xxx in related_requirements field
   
2. **Business Rule Coverage**: For each BR-xxx in the extracted list, you MUST create:
   - At least 1 validation test proving the rule is enforced
   - Test both valid and invalid scenarios if applicable
   - Link test to BR-xxx in related_requirements field
   
3. **Error Code Coverage**: For each E-xxxx in the extracted list, you MUST create:
   - Exactly 1 negative test that triggers this specific error code
   - The test must clearly demonstrate the error condition
   - Link test to E-xxxx in related_requirements field
   
4. **Boundary Testing**: For each numeric limit, create:
   - Tests at limit-1, limit, limit+1 where applicable
   - Link to related Business Rule if applicable

### CRITICAL: Coverage Validation
- Every UC-xxx MUST appear in at least 2 test cases (1 happy + 1 error)
- Every BR-xxx MUST appear in at least 1 test case
- Every E-xxxx MUST appear in exactly 1 test case
- The coverage.covered_use_cases list MUST include ALL UC IDs from extraction
- The coverage.covered_business_rules list MUST include ALL BR IDs from extraction
- The coverage.covered_error_codes list MUST include ALL E-xxxx codes from extraction

### Priority Assignment:
- **critical**: Security, data loss, authentication (BR with "Kritisch" priority)
- **high**: Core business functionality (main UC flows)
- **medium**: Edge cases, boundary conditions  
- **low**: UI polish, minor validations

### Output Requirements:
- Use EXACT role names from actors list
- Use EXACT terms from DDD (Ubiquitous Language)
- All text in professional German
- Link EVERY test to related_requirements
- Fill coverage analysis accurately
- Minimum test count: {len(extracted.use_cases) * 2 + len(extracted.business_rules) + len(extracted.error_codes)}"""

            # Build validation checklist with extracted IDs
            uc_ids_str = ', '.join([uc.id for uc in extracted.use_cases])
            br_ids_str = ', '.join([br.id for br in extracted.business_rules])
            ec_codes_str = ', '.join([ec.code for ec in extracted.error_codes])
            min_test_count = len(extracted.use_cases) * 2 + len(extracted.business_rules) + len(extracted.error_codes)

            generation_user_prompt = f"""# PROJECT: "{project['name']}"

# ADDITIONAL CONTEXT
{general_context if general_context else "No additional context."}

# TASK
Generate a complete Test Plan covering 100% of the extracted requirements above.

### FINAL VALIDATION CHECKLIST (VERIFY BEFORE SUBMITTING):

Step 1: Count extracted requirements
- Use Cases extracted: {len(extracted.use_cases)}
- Business Rules extracted: {len(extracted.business_rules)}
- Error Codes extracted: {len(extracted.error_codes)}

Step 2: Verify test generation
☐ Every UC-xxx from extraction has at least 1 happy path test
☐ Every UC-xxx from extraction has at least 1 error test (for each error case)
☐ Every BR-xxx from extraction has at least 1 validation test
☐ Every E-xxxx from extraction has exactly 1 negative test
☐ All numeric limits have boundary tests

Step 3: Verify coverage lists
☐ coverage.covered_use_cases contains ALL {len(extracted.use_cases)} UC IDs: {uc_ids_str}
☐ coverage.covered_business_rules contains ALL {len(extracted.business_rules)} BR IDs: {br_ids_str}
☐ coverage.covered_error_codes contains ALL {len(extracted.error_codes)} E-xxxx codes: {ec_codes_str}

Step 4: Verify test case linking
☐ Every test case has related_requirements field populated
☐ Every test case links to at least one UC, BR, or E-code

Step 5: Final check
☐ Total test count >= {min_test_count}
☐ coverage_gaps is empty (or only contains items that truly cannot be tested)

IF ANY CHECKBOX IS UNCHECKED, GO BACK AND ADD THE MISSING TESTS!"""

            generation_response = self.openai_client.beta.chat.completions.parse(
                model=config.LLM_MODEL or "gpt-4o",
                messages=[
                    {"role": "system", "content": generation_system_prompt},
                    {"role": "user", "content": generation_user_prompt},
                ],
                response_format=TestPlanModel,
                temperature=0.3,
            )

            test_plan_data = generation_response.choices[0].message.parsed

            # Update counts
            test_plan_data.total_test_count = len(test_plan_data.test_cases)
            test_plan_data.critical_tests_count = sum(
                1 for tc in test_plan_data.test_cases if tc.priority == "critical"
            )

            # PASS 3: COVERAGE VALIDATION (Quick check)
            update_status("validating_coverage", 85, "Validating test coverage...")

            # Calculate coverage locally
            all_uc_ids = {uc.id for uc in extracted.use_cases}
            all_br_ids = {br.id for br in extracted.business_rules}
            all_ec_codes = {ec.code for ec in extracted.error_codes}

            covered_ucs = set(test_plan_data.coverage.covered_use_cases)
            covered_brs = set(test_plan_data.coverage.covered_business_rules)
            covered_ecs = set(test_plan_data.coverage.covered_error_codes)

            missing_ucs = all_uc_ids - covered_ucs
            missing_brs = all_br_ids - covered_brs
            missing_ecs = all_ec_codes - covered_ecs

            total_requirements = len(all_uc_ids) + len(all_br_ids) + len(all_ec_codes)
            covered_count = len(covered_ucs & all_uc_ids) + len(covered_brs & all_br_ids) + len(covered_ecs & all_ec_codes)
            coverage_pct = (covered_count / total_requirements * 100) if total_requirements > 0 else 100

            self.logger.info(
                f"Coverage: {coverage_pct:.1f}% - "
                f"Missing UCs: {missing_ucs}, Missing BRs: {missing_brs}, Missing ECs: {missing_ecs}"
            )

            # Add validation info to coverage gaps if any
            if missing_ucs or missing_brs or missing_ecs:
                gaps = []
                if missing_ucs:
                    gaps.append(f"Missing UC coverage: {', '.join(missing_ucs)}")
                if missing_brs:
                    gaps.append(f"Missing BR coverage: {', '.join(missing_brs)}")
                if missing_ecs:
                    gaps.append(f"Missing Error Code coverage: {', '.join(missing_ecs)}")
                test_plan_data.coverage.coverage_gaps = gaps

            # Serialize for DB storage
            final_content = test_plan_data.model_dump_json()

            update_status("finalizing", 95, "Finalizing test plan...")

            final_storage = json.dumps(
                {
                    "status": "completed",
                    "format": "structured_v2",  # v2 = multi-pass
                    "extraction_summary": {
                        "use_cases": len(extracted.use_cases),
                        "business_rules": len(extracted.business_rules),
                        "error_codes": len(extracted.error_codes),
                        "coverage_percentage": round(coverage_pct, 1),
                    },
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

    def delete_plan(self, plan_id: str) -> bool:
        """Delete a test plan and all associated executions."""
        return self.db.delete_test_plan(plan_id)

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
                temperature=0.4,
                max_tokens=1200,
            )
            answer = response.choices[0].message.content
            
            # Generate intelligent follow-up suggestions
            suggested_questions = self._generate_follow_up_suggestions(
                query, answer, context, conversation_history
            )
            
        except Exception as e:
            self.logger.error(f"DDD chat failed: {e}")
            answer = f"Fehler bei der Anfrage: {str(e)}"
            suggested_questions = []

        return {
            "answer": answer,
            "sources": sources,
            "test_cases_used": bool(test_case_context),
            "suggested_questions": suggested_questions,
        }

    def _generate_follow_up_suggestions(
        self,
        query: str,
        answer: str,
        context: str,
        conversation_history: List[Dict] = None,
    ) -> List[str]:
        """Generate intelligent follow-up question suggestions based on the conversation."""
        try:
            # Fast, lightweight suggestion generation
            suggestion_prompt = f"""Based on this DDD Q&A exchange, suggest 2-3 relevant follow-up questions.

Question: {query}
Answer: {answer[:500]}

Rules:
- Questions should help explore the DDD deeper
- Focus on: requirements, use cases, business rules, error handling, edge cases
- Keep questions short and specific (max 60 chars)
- Output as JSON array of strings

Example output: ["Welche Fehlercodes gibt es?", "Wer sind die Hauptakteure?"]"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": suggestion_prompt}],
                temperature=0.7,
                max_tokens=150,
            )
            
            # Parse suggestions
            content = response.choices[0].message.content.strip()
            # Handle JSON response
            if content.startswith("["):
                suggestions = json.loads(content)
                return suggestions[:3]  # Max 3 suggestions
            return []
        except Exception as e:
            self.logger.debug(f"Follow-up suggestion generation failed: {e}")
            # Fallback to static suggestions based on context
            return self._get_static_suggestions(query, context)

    def _get_static_suggestions(self, query: str, context: str) -> List[str]:
        """Provide static follow-up suggestions based on DDD keywords in context."""
        suggestions = []
        context_lower = context.lower()
        query_lower = query.lower()
        
        # Context-aware static suggestions
        if "use case" in context_lower or "uc-" in context_lower:
            if "use case" not in query_lower:
                suggestions.append("Welche Use Cases werden beschrieben?")
        
        if "business rule" in context_lower or "br-" in context_lower:
            if "business rule" not in query_lower and "geschäftsregel" not in query_lower:
                suggestions.append("Welche Business Rules gibt es?")
        
        if "fehler" in context_lower or "error" in context_lower or "e-" in context_lower:
            if "fehler" not in query_lower:
                suggestions.append("Welche Fehlercodes sind definiert?")
        
        if "rolle" in context_lower or "akteur" in context_lower or "admin" in context_lower:
            if "rolle" not in query_lower and "akteur" not in query_lower:
                suggestions.append("Welche Rollen/Akteure gibt es?")
        
        if "api" in context_lower or "endpoint" in context_lower:
            if "api" not in query_lower:
                suggestions.append("Welche API-Endpoints sind dokumentiert?")
        
        # Default suggestions if nothing matched
        if not suggestions:
            suggestions = [
                "Welche Entitäten werden beschrieben?",
                "Was sind die Hauptfunktionen?",
            ]
        
        return suggestions[:3]


testing_service = TestingService()
