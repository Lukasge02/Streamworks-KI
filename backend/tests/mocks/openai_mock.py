"""
OpenAI Mock

Provides mock implementations for OpenAI API calls.
Useful for testing LLM-dependent code without making actual API calls.
"""

from unittest.mock import Mock, MagicMock
from typing import List, Dict, Any, Optional
import json


class MockChoice:
    """Mock OpenAI choice object."""
    
    def __init__(self, content: str, finish_reason: str = "stop"):
        self.message = Mock(content=content, role="assistant")
        self.finish_reason = finish_reason
        self.index = 0


class MockUsage:
    """Mock OpenAI usage object."""
    
    def __init__(
        self,
        prompt_tokens: int = 100,
        completion_tokens: int = 50,
        total_tokens: int = 150
    ):
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = total_tokens


class MockChatCompletion:
    """Mock OpenAI chat completion response."""
    
    def __init__(
        self,
        content: str,
        finish_reason: str = "stop",
        prompt_tokens: int = 100,
        completion_tokens: int = 50
    ):
        self.id = "chatcmpl-mock-12345"
        self.object = "chat.completion"
        self.created = 1234567890
        self.model = "gpt-4o"
        self.choices = [MockChoice(content, finish_reason)]
        self.usage = MockUsage(prompt_tokens, completion_tokens)


class MockOpenAI:
    """
    Mock OpenAI client for testing.
    
    Usage:
        mock_client = MockOpenAI()
        mock_client.set_response("Test response")
        
        # Or with structured output
        mock_client.set_structured_response({
            "test_cases": [...]
        })
    """
    
    def __init__(self):
        self.chat = Mock()
        self.chat.completions = Mock()
        self._default_response = "This is a mock response."
        self._setup_create()
    
    def _setup_create(self):
        """Setup the create method with default behavior."""
        def create_completion(**kwargs):
            return MockChatCompletion(self._default_response)
        
        self.chat.completions.create = Mock(side_effect=create_completion)
    
    def set_response(self, content: str):
        """Set the response content for the next call."""
        self._default_response = content
        self._setup_create()
    
    def set_structured_response(self, data: Dict[str, Any]):
        """Set a JSON structured response."""
        self._default_response = json.dumps(data)
        self._setup_create()
    
    def set_error(self, error_class, message: str = "Mock error"):
        """Configure to raise an error on next call."""
        self.chat.completions.create.side_effect = error_class(message)
    
    def get_call_count(self) -> int:
        """Get number of times create was called."""
        return self.chat.completions.create.call_count
    
    def get_last_call_args(self) -> Dict[str, Any]:
        """Get arguments from the last call."""
        if self.chat.completions.create.call_args:
            return self.chat.completions.create.call_args.kwargs
        return {}


def create_chat_completion_mock(
    content: str,
    finish_reason: str = "stop"
) -> MockChatCompletion:
    """
    Create a mock chat completion response.
    
    Args:
        content: Response content
        finish_reason: Completion finish reason
    
    Returns:
        MockChatCompletion object
    """
    return MockChatCompletion(content, finish_reason)


def create_structured_output_mock(
    test_plan: Dict[str, Any] = None
) -> MockChatCompletion:
    """
    Create mock for structured output (test plan generation).
    
    Args:
        test_plan: Optional test plan dict, uses default if not provided
    
    Returns:
        MockChatCompletion with JSON content
    """
    if test_plan is None:
        test_plan = {
            "project_name": "Test Project",
            "introduction": "Test plan introduction",
            "test_cases": [
                {
                    "test_id": "TC-001",
                    "title": "Test Case 1",
                    "description": "Description",
                    "steps": ["Step 1", "Step 2"],
                    "expected_result": "Expected result",
                    "priority": "high",
                    "category": "happy_path",
                }
            ],
            "coverage_analysis": {
                "covered_use_cases": ["UC-001"],
                "covered_business_rules": ["BR-001"],
                "covered_error_codes": [],
                "coverage_gaps": [],
            },
        }
    
    return MockChatCompletion(json.dumps(test_plan))


# Predefined responses for common scenarios
MOCK_RESPONSES = {
    "test_plan": create_structured_output_mock(),
    "ddd_chat": MockChatCompletion(
        "Based on the DDD document, the system should handle user authentication "
        "using JWT tokens with a 24-hour expiration period."
    ),
    "project_description": MockChatCompletion(
        "This project implements a document management system with RAG capabilities."
    ),
    "error": MockChatCompletion("I'm sorry, I couldn't process that request."),
}
