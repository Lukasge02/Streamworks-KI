"""
DEPRECATED: Upload Job Manager - Redirects to refactored version
This file maintains compatibility while using the new dependency injection based implementation
"""

# Import everything from the refactored version
from .upload_job_manager_refactored import (
    UploadStage,
    UploadJobProgress,
    UploadJobManager
)

# Create global instance for backwards compatibility
upload_job_manager = UploadJobManager()

# Export all for backwards compatibility
__all__ = [
    "UploadStage",
    "UploadJobProgress",
    "UploadJobManager",
    "upload_job_manager"
]