"""
Router Package for StreamWorks Backend
Exports all API routers for main.py imports
"""

from .folders import router as folders
from .documents import router as documents
from .websockets import router as websockets
from .upload_progress_websocket import router as upload_progress_websocket
# from .chat import router as chat  # Disabled due to service dependencies
# from .chat_v2 import router as chat_v2  # File doesn't exist
# from .xml_generator import router as xml_generator  # Disabled due to service dependencies
from .xml_streams import router as xml_streams
from .feature_flags import router as feature_flags
from .health import router as health

__all__ = [
    "folders",
    "documents",
    "websockets",
    "upload_progress_websocket",
    # "chat",
    # "chat_v2",
    # "xml_generator",
    "xml_streams",
    "feature_flags",
    "health"
]