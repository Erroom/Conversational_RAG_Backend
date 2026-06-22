from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # API Settings
    APP_NAME: str = Field("RAG Backend API", description="Application name")
    APP_VERSION: str = Field("1.0.0", description="Application version")
    DEBUG: bool = Field(True, description="Debug mode")
    
    # Google Gemini Settings
    GEMINI_API_KEY: str = Field(..., description="Google Gemini API key")
    GEMINI_MODEL: str = Field("gemini-2.0-flash", description="Gemini model name")
    EMBEDDING_MODEL: str = Field("text-embedding-004", description="Gemini embedding model")
    
    # Redis Settings
    REDIS_HOST: str = Field("localhost", description="Redis host")
    REDIS_PORT: int = Field(6379, description="Redis port")
    REDIS_PASSWORD: Optional[str] = Field(None, description="Redis password")
    REDIS_DB: int = Field(0, description="Redis database")
    
    # Vector Store Settings (Qdrant)
    VECTOR_STORE_TYPE: str = Field("qdrant", description="Vector store type")
    QDRANT_HOST: str = Field("localhost", description="Qdrant host")
    QDRANT_PORT: int = Field(6333, description="Qdrant port")
    QDRANT_API_KEY: Optional[str] = Field(None, description="Qdrant API key")
    VECTOR_COLLECTION_NAME: str = Field("documents", description="Vector collection name")
    
    # MySQL Database Settings
    MYSQL_HOST: str = Field("localhost", description="MySQL host")
    MYSQL_PORT: int = Field(3306, description="MySQL port")
    MYSQL_USER: str = Field(..., description="MySQL username")
    MYSQL_PASSWORD: str = Field(..., description="MySQL password")
    MYSQL_DATABASE: str = Field("rag_db", description="MySQL database name")
    
    # Chunking Settings
    DEFAULT_CHUNK_SIZE: int = Field(500, description="Default chunk size")
    CHUNK_OVERLAP: int = Field(50, description="Chunk overlap")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()