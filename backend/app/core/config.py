from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Environment
    ENV: str = "development"
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "StreamWorks-KI"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3001"
    ]
    
    # Database
    DATABASE_URL: str = "sqlite:///./streamworks_ki.db"
    
    # RAG Settings (Q&A System)
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"  # Fast & good
    VECTOR_DB_PATH: str = "./data/vector_db"
    RAG_CHUNK_SIZE: int = 500
    RAG_CHUNK_OVERLAP: int = 50
    RAG_TOP_K: int = 5
    
    # === MISTRAL 7B OPTIMIERUNG ===
    OLLAMA_MODEL: str = "mistral:7b-instruct"
    LLM_ENABLED: bool = True
    OLLAMA_HOST: str = "http://localhost:11434"
    
    # Mistral-spezifische Parameter
    MODEL_TEMPERATURE: float = 0.7    # Kreativ aber konsistent
    MODEL_TOP_P: float = 0.95        # Mistral arbeitet gut mit hohem top_p
    MODEL_TOP_K: int = 40            # Reduziert für Fokus
    MODEL_MAX_TOKENS: int = 2048     # Ausreichend für strukturierte Antworten
    MODEL_REPEAT_PENALTY: float = 1.1 # Verhindert Wiederholungen
    
    # Performance-Optimierung
    MODEL_THREADS: int = 8           # Für M4 MacBook optimal
    MODEL_BATCH_SIZE: int = 1        # Einzelne Requests
    MODEL_CONTEXT_WINDOW: int = 8192 # Mistral kann 8k Context
    
    # Deutsche Spezialisierung
    FORCE_GERMAN_RESPONSES: bool = True
    GERMAN_PROMPT_STYLE: str = "professional"
    USE_GERMAN_TECHNICAL_TERMS: bool = True
    
    # XML Generation Settings (LoRA Fine-Tuning)  
    LORA_ADAPTER_PATH: str = "./data/models/xml_lora"
    XML_GENERATION_ENABLED: bool = False  # Start disabled
    
    # LoRA Training Parameters
    LORA_R: int = 16
    LORA_ALPHA: int = 32
    LORA_DROPOUT: float = 0.1
    LORA_TARGET_MODULES: List[str] = ["c_attn", "c_proj"]  # For DialoGPT
    
    # Legacy Generation Parameters (für Kompatibilität)
    MAX_NEW_TOKENS: int = 512
    TEMPERATURE: float = 0.7
    TOP_P: float = 0.9
    DEVICE: str = "mps"  # auto, cuda, cpu, mps
    
    # Training Data Paths
    TRAINING_DATA_PATH: str = "./data/training_data"
    HELP_DATA_PATH: str = "./data/training_data/optimized/help_data"
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