from pydantic import Field
from pydantic_settings import BaseSettings

from app.rag.retrieval_mode import RetrievalMode


class Settings(BaseSettings):
    APP_NAME: str = "Enterprise RAG Assistant"
    DATABASE_URL: str
    DEBUG: bool = False

    # ----------------------------
    # Retrieval
    # ----------------------------
    TOP_K: int = 3
    RETRIEVAL_MODE: RetrievalMode = RetrievalMode.HYBRID
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    ENABLE_CHUNK_DEDUP: bool = True
    MIN_CHUNK_LENGTH: int = 120
    MAX_CHUNK_LENGTH: int = 1600
    CHUNK_SEPARATORS: list[str] = [
        "\n# ",
        "\n## ",
        "\n### ",
        "\n\n",
        "\n",
        ". ",
        "! ",
        "? ",
        "; ",
        " ",
        "",
    ]

    # Retrieval Pipeline
    DENSE_TOP_K: int = 20
    SPARSE_TOP_K: int = 20
    FINAL_TOP_K: int = 5

    RRF_K: int = 60

    # Cache
    ENABLE_RETRIEVAL_CACHE: bool = True
    RETRIEVAL_CACHE_SIZE: int = 256

    ENABLE_MMR: bool = True
    MMR_LAMBDA: float = 0.5
    # ----------------------------
    # Ollama
    # ----------------------------
    OLLAMA_HOST: str = "http://host.docker.internal:11434"
    OLLAMA_KEEP_ALIVE: str = "5m"
    OLLAMA_NUM_PARALLEL: int = 4
    OLLAMA_MAX_QUEUE: int = 32

    # ----------------------------
    # Models
    # ----------------------------
    CHAT_MODEL: str = "qwen3:8b"
    EMBEDDING_MODEL: str = "nomic-embed-text"
    EMBEDDING_WORKERS: int = 4
    EMBEDDING_BATCH_SIZE: int = 32

    # ----------------------------
    # Generation
    # ----------------------------
    LLM_PROVIDER: str = "ollama"
    OLLAMA_MODEL: str = "qwen3:8b"
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""

    LLM_CONTEXT_WINDOW: int = 4096
    LLM_TEMPERATURE: float = 0.2
    LLM_MAX_TOKENS: int = 1024
    ENABLE_STREAMING: bool = True

    # ----------------------------
    # Features
    # ----------------------------
    ENABLE_QUERY_REWRITE: bool = True
    ENABLE_RERANKER: bool = False
    BENCHMARK_MODE: bool = False
    ENABLE_BENCHMARKS: bool = False

    # ----------------------------
    # Storage
    # ----------------------------
    CHROMA_DB_PATH: str = "./chroma_db"

    # ----------------------------
    # Auth
    # ----------------------------
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    BOOTSTRAP_ADMIN_EMAIL: str = ""

    BACKEND_CORS_ORIGINS: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
    )

    class Config:
        env_file = ".env"


settings = Settings()