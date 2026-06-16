from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Enterprise RAG Assistant"
    DATABASE_URL: str
    DEBUG: bool = False
    TOP_K: int = 3
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    OLLAMA_HOST: str = "http://host.docker.internal:11434"
    EMBEDDING_MODEL: str = "nomic-embed-text"
    CHAT_MODEL: str = "qwen3:8b"
    BACKEND_CORS_ORIGINS: list[str] = Field(default_factory=lambda: [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ])

    class Config:
        env_file = ".env"


settings = Settings()
