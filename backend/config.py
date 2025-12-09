"""
Configuration module for Streamworks-KI Backend
Loads environment variables from .env file
"""
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class Config:
    """Application configuration"""
    
    # OpenAI Settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    
    # Validation
    @classmethod
    def validate(cls) -> bool:
        """Check if required configuration is present"""
        if not cls.OPENAI_API_KEY:
            print("⚠️ OPENAI_API_KEY not set in .env file!")
            return False
        return True


# Singleton instance
config = Config()
