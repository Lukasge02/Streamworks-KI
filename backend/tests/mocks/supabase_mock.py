"""
Supabase Mock

Provides mock implementations for Supabase database operations.
Simulates table operations without actual database connection.
"""

from unittest.mock import Mock, MagicMock
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime


class MockExecuteResult:
    """Mock result from execute() call."""
    
    def __init__(self, data: List[Dict] = None, count: int = None):
        self.data = data or []
        self.count = count if count is not None else len(self.data)


class MockTable:
    """
    Mock Supabase table with chainable query methods.
    
    Usage:
        table = MockTable("users")
        table.set_data([{"id": "1", "name": "Test"}])
        result = table.select("*").eq("id", "1").execute()
    """
    
    def __init__(self, name: str):
        self.name = name
        self._data: List[Dict[str, Any]] = []
        self._filters: List[tuple] = []
        self._order_by: Optional[tuple] = None
        self._limit_value: Optional[int] = None
        self._insert_data: Optional[Dict] = None
        self._update_data: Optional[Dict] = None
    
    def _reset_query(self):
        """Reset query state for next operation."""
        self._filters = []
        self._order_by = None
        self._limit_value = None
        self._insert_data = None
        self._update_data = None
    
    def set_data(self, data: List[Dict[str, Any]]):
        """Set the data this table should return."""
        self._data = data
    
    def select(self, columns: str = "*") -> "MockTable":
        """Select columns (chainable)."""
        return self
    
    def insert(self, data: Dict[str, Any]) -> "MockTable":
        """Insert data (chainable)."""
        self._insert_data = data
        return self
    
    def update(self, data: Dict[str, Any]) -> "MockTable":
        """Update data (chainable)."""
        self._update_data = data
        return self
    
    def delete(self) -> "MockTable":
        """Delete (chainable)."""
        return self
    
    def eq(self, column: str, value: Any) -> "MockTable":
        """Filter by equality (chainable)."""
        self._filters.append(("eq", column, value))
        return self
    
    def neq(self, column: str, value: Any) -> "MockTable":
        """Filter by inequality (chainable)."""
        self._filters.append(("neq", column, value))
        return self
    
    def in_(self, column: str, values: List[Any]) -> "MockTable":
        """Filter by in list (chainable)."""
        self._filters.append(("in", column, values))
        return self
    
    def is_(self, column: str, value: Any) -> "MockTable":
        """Filter by is (chainable)."""
        self._filters.append(("is", column, value))
        return self
    
    def order(self, column: str, desc: bool = False) -> "MockTable":
        """Order by column (chainable)."""
        self._order_by = (column, desc)
        return self
    
    def limit(self, count: int) -> "MockTable":
        """Limit results (chainable)."""
        self._limit_value = count
        return self
    
    def single(self) -> "MockTable":
        """Return single result (chainable)."""
        self._limit_value = 1
        return self
    
    def _apply_filters(self, data: List[Dict]) -> List[Dict]:
        """Apply stored filters to data."""
        result = data
        for filter_type, column, value in self._filters:
            if filter_type == "eq":
                result = [r for r in result if r.get(column) == value]
            elif filter_type == "neq":
                result = [r for r in result if r.get(column) != value]
            elif filter_type == "in":
                result = [r for r in result if r.get(column) in value]
            elif filter_type == "is":
                result = [r for r in result if r.get(column) is value]
        return result
    
    def execute(self) -> MockExecuteResult:
        """Execute the query and return results."""
        if self._insert_data:
            # Simulate insert
            new_record = {
                "id": str(uuid.uuid4()),
                "created_at": datetime.utcnow().isoformat(),
                **self._insert_data
            }
            result = MockExecuteResult([new_record])
            self._reset_query()
            return result
        
        if self._update_data:
            # Simulate update - return updated record
            result = MockExecuteResult([{
                "id": "updated-id",
                **self._update_data
            }])
            self._reset_query()
            return result
        
        # Regular select
        filtered = self._apply_filters(self._data)
        
        # Apply ordering
        if self._order_by:
            column, desc = self._order_by
            filtered.sort(key=lambda x: x.get(column, ""), reverse=desc)
        
        # Apply limit
        if self._limit_value:
            filtered = filtered[:self._limit_value]
        
        result = MockExecuteResult(filtered)
        self._reset_query()
        return result


class MockSupabaseClient:
    """
    Mock Supabase client for testing.
    
    Usage:
        client = MockSupabaseClient()
        client.setup_table("projects", [{"id": "1", "name": "Test"}])
        result = client.table("projects").select("*").execute()
    """
    
    def __init__(self):
        self._tables: Dict[str, MockTable] = {}
    
    def setup_table(self, name: str, data: List[Dict[str, Any]] = None):
        """
        Setup a table with initial data.
        
        Args:
            name: Table name
            data: Optional initial data
        """
        table = MockTable(name)
        if data:
            table.set_data(data)
        self._tables[name] = table
    
    def table(self, name: str) -> MockTable:
        """Get or create a table mock."""
        if name not in self._tables:
            self._tables[name] = MockTable(name)
        return self._tables[name]
    
    def rpc(self, function_name: str, params: Dict = None) -> MockExecuteResult:
        """Mock RPC call."""
        return MockExecuteResult([])
    
    @property
    def auth(self):
        """Mock auth module."""
        auth_mock = Mock()
        auth_mock.get_user.return_value = Mock(user=None)
        auth_mock.sign_in_with_password.return_value = Mock(
            user=Mock(id="test-user-id", email="test@example.com"),
            session=Mock(access_token="test-token")
        )
        return auth_mock


# Pre-configured mock setups for common scenarios
def create_project_mock_client() -> MockSupabaseClient:
    """Create a client with project-related tables configured."""
    client = MockSupabaseClient()
    
    # Projects table
    client.setup_table("projects", [
        {
            "id": "proj-001",
            "name": "Sample Project",
            "description": "A sample project",
            "created_at": datetime.utcnow().isoformat(),
        }
    ])
    
    # Project documents table
    client.setup_table("project_documents", [
        {
            "id": "link-001",
            "project_id": "proj-001",
            "doc_id": "doc-001",
            "category": "ddd",
            "rag_enabled": True,
        }
    ])
    
    # Test plans table
    client.setup_table("test_plans", [])
    
    return client
