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
    
    # LLM Settings
    MODEL_NAME: str = "codellama/CodeLlama-7b-Instruct-hf"
    MAX_TOKEN_LENGTH: int = 2048
    TEMPERATURE: float = 0.1
    MAX_NEW_TOKENS: int = 512
    DEVICE: str = "auto"  # auto, cuda, cpu
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()