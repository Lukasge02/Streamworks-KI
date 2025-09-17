"""
Enterprise AI Parameter Recognition Module - Phase 3+
Provides intelligent parameter extraction and conversation management
"""

# Phase 3+ AI Services
from .parameter_extraction_ai import get_parameter_extraction_ai
from .chat_xml_database_service import get_chat_xml_database_service

# Legacy AI Services (if they exist)
try:
    from .chroma_manager import get_chroma_manager
except ImportError:
    get_chroma_manager = None

try:
    from .stream_schema_vector_store import get_stream_schema_vector_store
except ImportError:
    get_stream_schema_vector_store = None

try:
    from .parameter_pattern_store import get_parameter_pattern_store
except ImportError:
    get_parameter_pattern_store = None

try:
    from .conversation_memory_store import get_conversation_memory_store
except ImportError:
    get_conversation_memory_store = None

try:
    from .enterprise_parameter_engine import get_enterprise_parameter_engine
except ImportError:
    get_enterprise_parameter_engine = None

__all__ = [
    # Phase 3+ Services
    "get_parameter_extraction_ai",
    "get_chat_xml_database_service",

    # Legacy Services (conditional)
    "get_chroma_manager",
    "get_stream_schema_vector_store",
    "get_parameter_pattern_store",
    "get_conversation_memory_store",
    "get_enterprise_parameter_engine"
]

# Remove None values from __all__
__all__ = [name for name in __all__ if globals().get(name) is not None]