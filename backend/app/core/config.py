from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Environment
    ENV: str = "development"
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "StreamWorks-KI"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Database
    DATABASE_URL: str = "sqlite:///./streamworks_ki.db"
    
    # RAG Settings (Q&A System)
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"  # Fast & good
    VECTOR_DB_PATH: str = "./data/vector_db"
    RAG_CHUNK_SIZE: int = 500
    RAG_CHUNK_OVERLAP: int = 50
    RAG_TOP_K: int = 5
    
    # XML Generation Settings (LoRA Fine-Tuning)
    BASE_MODEL: str = "microsoft/DialoGPT-small"  # Lightweight base
    LORA_ADAPTER_PATH: str = "./data/models/xml_lora"
    XML_GENERATION_ENABLED: bool = False  # Start disabled
    
    # LoRA Training Parameters
    LORA_R: int = 16
    LORA_ALPHA: int = 32
    LORA_DROPOUT: float = 0.1
    LORA_TARGET_MODULES: List[str] = ["c_attn", "c_proj"]  # For DialoGPT
    
    # Generation Parameters
    MAX_NEW_TOKENS: int = 512
    TEMPERATURE: float = 0.7
    TOP_P: float = 0.9
    DEVICE: str = "mps"  # auto, cuda, cpu, mps
    
    # Training Data Paths
    TRAINING_DATA_PATH: str = "./data/training_data"
    HELP_DATA_PATH: str = "./data/training_data/help_data"
    XML_TEMPLATE_PATH: str = "./data/training_data/stream_templates"
    
    # Services Toggle
    RAG_ENABLED: bool = True
    TRAINING_ENABLED: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()