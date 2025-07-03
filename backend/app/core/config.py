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
    
    # LLM Settings - Microsoft Phi-2 for fast prototyping
    MODEL_NAME: str = "microsoft/phi-2"  # Phi-2 2.7B - Fast and efficient
    MAX_TOKEN_LENGTH: int = 1024  # Phi-2 supports up to 2048
    TEMPERATURE: float = 0.7
    MAX_NEW_TOKENS: int = 200  # Good balance for responses
    DEVICE: str = "mps"  # auto, cuda, cpu, mps - Using MPS for M3/M4 Macs
    
    # Fine-Tuning Settings (disabled for Phi-2 testing)
    USE_LORA: bool = False  # Disable LoRA for initial testing
    LORA_RANK: int = 16  # LoRA rank for parameter efficiency
    LORA_ALPHA: int = 32  # LoRA alpha scaling
    LORA_DROPOUT: float = 0.1  # LoRA dropout rate
    
    # Development Mode (skip heavy model loading)
    SKIP_MODEL_LOADING: bool = False
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()