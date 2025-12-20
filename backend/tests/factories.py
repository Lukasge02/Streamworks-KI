"""
Test Data Factories

Factory Boy patterns for generating consistent test data.
Use these factories instead of manually creating test data.

Usage:
    user = UserFactory()
    project = ProjectFactory(name="Custom Name")
    doc = DocumentFactory(category="ddd", rag_enabled=True)
"""

import factory
from factory import Factory, Faker, LazyAttribute, SubFactory
from datetime import datetime
import uuid
import json


class UserFactory(Factory):
    """Factory for creating test users."""
    
    class Meta:
        model = dict
    
    id = LazyAttribute(lambda _: str(uuid.uuid4()))
    email = Faker("email")
    name = Faker("name")
    role = "user"
    created_at = LazyAttribute(lambda _: datetime.utcnow().isoformat())
    
    class Params:
        admin = factory.Trait(
            role="admin",
            email=factory.LazyAttribute(lambda o: f"admin-{o.id[:8]}@example.com")
        )
        viewer = factory.Trait(
            role="viewer"
        )


class ProjectFactory(Factory):
    """Factory for creating test projects."""
    
    class Meta:
        model = dict
    
    id = LazyAttribute(lambda _: str(uuid.uuid4()))
    name = Faker("company")
    description = Faker("paragraph", nb_sentences=2)
    created_at = LazyAttribute(lambda _: datetime.utcnow().isoformat())
    updated_at = LazyAttribute(lambda _: datetime.utcnow().isoformat())
    
    class Params:
        empty = factory.Trait(
            description=""
        )


class DocumentFactory(Factory):
    """Factory for creating test documents."""
    
    class Meta:
        model = dict
    
    doc_id = LazyAttribute(lambda _: str(uuid.uuid4()))
    filename = Faker("file_name", extension="pdf")
    category = "context"
    rag_enabled = True
    processing_status = "completed"
    
    @factory.lazy_attribute
    def metadata(self):
        return {
            "filename": self.filename,
            "file_size": factory.Faker._get_faker().random_int(min=10000, max=5000000),
            "mime_type": "application/pdf",
            "uploaded_at": datetime.utcnow().isoformat(),
        }
    
    class Params:
        ddd = factory.Trait(
            category="ddd",
            filename=factory.LazyAttribute(lambda o: f"DDD-{o.doc_id[:8]}.pdf")
        )
        processing = factory.Trait(
            processing_status="processing"
        )
        disabled = factory.Trait(
            rag_enabled=False
        )


class ProjectDocumentLinkFactory(Factory):
    """Factory for project-document links."""
    
    class Meta:
        model = dict
    
    project_id = LazyAttribute(lambda _: str(uuid.uuid4()))
    doc_id = LazyAttribute(lambda _: str(uuid.uuid4()))
    category = "context"
    rag_enabled = True
    created_at = LazyAttribute(lambda _: datetime.utcnow().isoformat())
    
    class Params:
        ddd = factory.Trait(category="ddd")


class TestCaseFactory(Factory):
    """Factory for creating test cases."""
    
    class Meta:
        model = dict
    
    test_id = factory.Sequence(lambda n: f"TC-{n+1:03d}")
    title = Faker("sentence", nb_words=5)
    description = Faker("paragraph", nb_sentences=2)
    
    @factory.lazy_attribute
    def steps(self):
        fake = factory.Faker._get_faker()
        return [fake.sentence() for _ in range(3)]
    
    expected_result = Faker("sentence", nb_words=8)
    priority = "medium"
    category = "happy_path"
    
    @factory.lazy_attribute
    def related_requirements(self):
        return [f"REQ-{factory.Faker._get_faker().random_int(min=1, max=100):03d}"]
    
    class Params:
        critical = factory.Trait(priority="critical")
        high = factory.Trait(priority="high")
        low = factory.Trait(priority="low")
        edge_case = factory.Trait(category="edge_case")
        error_handling = factory.Trait(category="error_handling")


class TestPlanFactory(Factory):
    """Factory for creating test plans."""
    
    class Meta:
        model = dict
    
    id = LazyAttribute(lambda _: str(uuid.uuid4()))
    project_id = LazyAttribute(lambda _: str(uuid.uuid4()))
    created_at = LazyAttribute(lambda _: datetime.utcnow().isoformat())
    
    @factory.lazy_attribute
    def content(self):
        test_cases = [TestCaseFactory() for _ in range(3)]
        plan = {
            "project_name": "Test Project",
            "introduction": "Comprehensive test plan for the project",
            "test_cases": test_cases,
            "coverage_analysis": {
                "covered_use_cases": ["UC-001", "UC-002"],
                "covered_business_rules": ["BR-001"],
                "covered_error_codes": ["E-001"],
                "coverage_gaps": [],
            },
            "total_tests_count": len(test_cases),
            "critical_tests_count": sum(1 for tc in test_cases if tc.get("priority") == "critical"),
        }
        return json.dumps(plan)
    
    class Params:
        processing = factory.Trait(
            content=json.dumps({
                "status": "processing",
                "stage": "generating",
                "progress": 50,
                "message": "Generating test cases...",
            })
        )
        failed = factory.Trait(
            content=json.dumps({
                "status": "failed",
                "error": "Generation failed",
            })
        )


class ChatMessageFactory(Factory):
    """Factory for chat messages."""
    
    class Meta:
        model = dict
    
    id = LazyAttribute(lambda _: str(uuid.uuid4()))
    session_id = LazyAttribute(lambda _: str(uuid.uuid4()))
    role = "user"
    content = Faker("paragraph", nb_sentences=1)
    created_at = LazyAttribute(lambda _: datetime.utcnow().isoformat())
    
    class Params:
        assistant = factory.Trait(role="assistant")
        system = factory.Trait(role="system")


class VectorSearchResultFactory(Factory):
    """Factory for vector search results."""
    
    class Meta:
        model = dict
    
    id = LazyAttribute(lambda _: f"chunk-{uuid.uuid4().hex[:8]}")
    doc_id = LazyAttribute(lambda _: str(uuid.uuid4()))
    text = Faker("paragraph", nb_sentences=3)
    score = LazyAttribute(lambda _: factory.Faker._get_faker().pyfloat(min_value=0.7, max_value=0.99))
    
    @factory.lazy_attribute
    def metadata(self):
        return {
            "filename": factory.Faker._get_faker().file_name(extension="pdf"),
            "page": factory.Faker._get_faker().random_int(min=1, max=50),
            "chunk_index": factory.Faker._get_faker().random_int(min=0, max=100),
        }


class RAGResponseFactory(Factory):
    """Factory for RAG responses."""
    
    class Meta:
        model = dict
    
    answer = Faker("paragraph", nb_sentences=3)
    confidence = LazyAttribute(lambda _: factory.Faker._get_faker().pyfloat(min_value=0.6, max_value=0.95))
    has_context = True
    
    @factory.lazy_attribute
    def confidence_level(self):
        if self.confidence >= 0.8:
            return "high"
        elif self.confidence >= 0.5:
            return "medium"
        return "low"
    
    @factory.lazy_attribute
    def sources(self):
        return [VectorSearchResultFactory() for _ in range(2)]
    
    class Params:
        no_context = factory.Trait(
            has_context=False,
            sources=[],
            confidence=0.3,
            answer="Leider konnte ich keine relevanten Informationen finden."
        )


# =============================================================================
# BATCH FACTORIES
# =============================================================================

def create_test_project_with_documents(
    num_context_docs: int = 2,
    num_ddd_docs: int = 1,
    include_disabled: bool = False
) -> dict:
    """
    Create a complete project setup with documents.
    
    Returns:
        dict with 'project', 'documents', 'links'
    """
    project = ProjectFactory()
    documents = []
    links = []
    
    # DDD documents
    for _ in range(num_ddd_docs):
        doc = DocumentFactory(ddd=True)
        documents.append(doc)
        links.append(ProjectDocumentLinkFactory(
            project_id=project["id"],
            doc_id=doc["doc_id"],
            category="ddd"
        ))
    
    # Context documents
    for i in range(num_context_docs):
        doc = DocumentFactory(disabled=include_disabled and i == 0)
        documents.append(doc)
        links.append(ProjectDocumentLinkFactory(
            project_id=project["id"],
            doc_id=doc["doc_id"],
            category="context",
            rag_enabled=doc["rag_enabled"]
        ))
    
    return {
        "project": project,
        "documents": documents,
        "links": links,
    }


def create_test_plan_with_cases(num_cases: int = 5, priorities: list = None) -> dict:
    """
    Create a test plan with specified number of test cases.
    
    Args:
        num_cases: Number of test cases to generate
        priorities: Optional list of priorities to cycle through
    
    Returns:
        TestPlan dict with embedded test cases
    """
    if priorities is None:
        priorities = ["high", "medium", "low"]
    
    test_cases = []
    for i in range(num_cases):
        priority = priorities[i % len(priorities)]
        test_cases.append(TestCaseFactory(priority=priority))
    
    plan = TestPlanFactory()
    plan_content = json.loads(plan["content"])
    plan_content["test_cases"] = test_cases
    plan_content["total_tests_count"] = len(test_cases)
    plan_content["critical_tests_count"] = sum(
        1 for tc in test_cases if tc.get("priority") == "critical"
    )
    plan["content"] = json.dumps(plan_content)
    
    return plan
