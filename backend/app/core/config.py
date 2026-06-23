from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    PROJECT_NAME: str = "University Search System"
    VERSION: str = "1.0.0"
    
    # Elasticsearch
    ELASTICSEARCH_URL: str = Field(default="http://localhost:9200")
    ELASTICSEARCH_INDEX: str = Field(default="documents")
    
    # PostgreSQL
    POSTGRES_URL: str = Field(default="postgresql://user:password@localhost:5432/app_db")
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379")
    
    # Application limits
    MAX_FILE_SIZE_MB: int = Field(default=20)
    CHUNK_SIZE: int = Field(default=1000)
    CHUNK_OVERLAP: int = Field(default=100)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()