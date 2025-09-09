"""
Router Package for StreamWorks Backend
Exports all API routers for main.py imports
"""

from .folders import router as folders
from .documents import router as documents  
from .websockets import router as websockets
from .upload_progress_websocket import router as upload_progress_websocket
from .chat import router as chat
from .xml_generator import router as xml_generator
from .feature_flags import router as feature_flags
from .health import router as health

__all__ = [
    "folders",
    "documents", 
    "websockets",
    "upload_progress_websocket",
    "chat",
    "xml_generator", 
    "feature_flags",
    "health"
]