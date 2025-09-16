from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Basic Configuration
    PROJECT_NAME: str = "ChatGPT Clone"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database Configuration
    DATABASE_URL: str = "postgresql://username:password@localhost:5432/chatgpt_clone"
    POSTGRES_DB: str = "chatgpt_clone"
    POSTGRES_USER: str = "username"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = ""
    
    # Security Configuration
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]
    
    # Chat Configuration
    MAX_TOKENS: int = 4000
    MODEL_NAME: str = "gpt-3.5-turbo"
    TEMPERATURE: float = 0.7
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()