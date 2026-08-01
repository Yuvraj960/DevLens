from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "DevLens API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://devlens:devlens@localhost:5432/devlens",
        description="Async PostgreSQL connection URL",
    )

    # Redis & Celery
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL",
    )

    # Qdrant
    QDRANT_URL: str = Field(
        default="http://localhost:6333",
        description="Qdrant vector database URL",
    )

    # Security
    JWT_SECRET: str = Field(
        default="devlens-local-secret-change-in-production-256bit",
        description="Secret key for JWT signing",
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 600

    # LiteLLM & Ollama
    LITELLM_MODEL: str = "ollama/phi3"
    LITELLM_EMBEDDING_MODEL: str = "ollama/nomic-embed-text"
    LITELLM_API_BASE: str = "http://localhost:11434/v1"
    LITELLM_API_KEY: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env.local",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
