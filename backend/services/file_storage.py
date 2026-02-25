"""
MinIO file storage service.

Provides upload, download, and delete operations for document files.
Auto-creates the configured bucket on first use.
"""

import io
import logging
from functools import lru_cache
from minio import Minio
from minio.error import S3Error
from config import get_settings

logger = logging.getLogger(__name__)

_bucket_ensured = False


@lru_cache
def get_minio_client() -> Minio:
    """Return a cached MinIO client singleton."""
    settings = get_settings()
    return Minio(
        endpoint=settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_secure,
    )


def ensure_bucket() -> None:
    """Create the configured bucket if it does not exist."""
    global _bucket_ensured
    if _bucket_ensured:
        return

    settings = get_settings()
    client = get_minio_client()
    bucket = settings.minio_bucket

    try:
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)
            logger.info("Created MinIO bucket: %s", bucket)
        _bucket_ensured = True
    except S3Error as exc:
        logger.error("Failed to ensure MinIO bucket: %s", exc)
        raise


def upload_file(filename: str, data: bytes, content_type: str) -> str:
    """
    Upload a file to MinIO.

    Args:
        filename: The object name to store the file under.
        data: Raw file bytes.
        content_type: MIME type of the file (e.g. 'application/pdf').

    Returns:
        The object name that was stored (same as filename).
    """
    ensure_bucket()
    settings = get_settings()
    client = get_minio_client()

    client.put_object(
        bucket_name=settings.minio_bucket,
        object_name=filename,
        data=io.BytesIO(data),
        length=len(data),
        content_type=content_type,
    )
    logger.info("Uploaded file to MinIO: %s (%d bytes)", filename, len(data))
    return filename


def download_file(object_name: str) -> bytes:
    """
    Download a file from MinIO.

    Args:
        object_name: The object name in the bucket.

    Returns:
        Raw file bytes.

    Raises:
        S3Error: If the object does not exist or cannot be retrieved.
    """
    settings = get_settings()
    client = get_minio_client()

    response = None
    try:
        response = client.get_object(settings.minio_bucket, object_name)
        return response.read()
    finally:
        if response is not None:
            response.close()
            response.release_conn()


def delete_file(object_name: str) -> None:
    """
    Delete a file from MinIO.

    Args:
        object_name: The object name to delete.
    """
    settings = get_settings()
    client = get_minio_client()

    client.remove_object(settings.minio_bucket, object_name)
    logger.info("Deleted file from MinIO: %s", object_name)
