from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    openai_embed_model: str = "text-embedding-3-large"

    # Supabase
    supabase_url: str = ""
    supabase_key: str = ""

    # Qdrant
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "streamworks"

    # MinIO
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "streamworks"
    minio_secret_key: str = "streamworks123"
    minio_bucket: str = "documents"
    minio_secure: bool = False

    # Server
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    # CORS
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    # Environment
    environment: str = "development"

    model_config = {
        "env_file": (".env", "../.env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


@lru_cache
def get_settings() -> Settings:
    return Settings()
