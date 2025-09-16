from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Basic Configuration
    PROJECT_NAME: str = "GPT.R1 - Advanced AI Assistant"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Additional fields from .env
    APP_NAME: str = "GPT.R1 - Advanced AI Assistant"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    JWT_ALGORITHM: str = "HS256"
    
    # Database Configuration - SQLite for immediate functionality
    DATABASE_URL: str = "sqlite:///./chatgpt_clone.db"
    POSTGRES_DB: str = "chatgpt_clone"
    POSTGRES_USER: str = "username"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = "test-key-will-be-replaced"
    
    # Security Configuration
    SECRET_KEY: str = "rajan-chatgpt-clone-super-secret-key-2025"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours for better UX
    
    # CORS Configuration
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000"
    
    # Chat Configuration
    MAX_TOKENS: int = 4000
    MODEL_NAME: str = "gpt-3.5-turbo"
    TEMPERATURE: float = 0.7
    
    # RAG Configuration
    ENABLE_WEB_SEARCH: bool = True
    MAX_SEARCH_RESULTS: int = 5
    
    def get_database_url(self) -> str:
        """Get the appropriate database URL with fallback to SQLite."""
        # Check if PostgreSQL URL is provided and we're in production
        if (self.ENVIRONMENT.lower() == "production" and 
            "postgresql://" in self.DATABASE_URL and 
            self.DATABASE_URL != "postgresql://username:password@localhost:5432/chatgpt_clone"):
            return self.DATABASE_URL
        else:
            # Use SQLite for development and testing
            return "sqlite:///./chatgpt_clone.db"
    
    def is_openai_configured(self) -> bool:
        """Check if OpenAI API key is properly configured."""
        return (self.OPENAI_API_KEY and 
                self.OPENAI_API_KEY != "test-key-will-be-replaced" and
                self.OPENAI_API_KEY.startswith("sk-"))
    
    def get_allowed_origins(self) -> List[str]:
        """Get CORS allowed origins as a list."""
        if isinstance(self.ALLOWED_ORIGINS, str):
            return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(',')]
        return self.ALLOWED_ORIGINS
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()