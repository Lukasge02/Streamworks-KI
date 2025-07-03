from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Environment
    ENV: str = "development"
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "StreamWorks-KI"
    
    # CORS
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Database
    DATABASE_URL: str = "sqlite:///./streamworks_ki.db"
    
    # PRODUCTION LLM - Code-Llama-7B-Instruct
    MODEL_NAME: str = "codellama/CodeLlama-7b-Instruct-hf"  # 7B - Production ready
    DEVICE: str = "mps"  # MPS für M3/M4 Macs
    MAX_NEW_TOKENS: int = 256
    TEMPERATURE: float = 0.7
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()