import chromadb
import requests  # type: ignore
from sqlalchemy import text

from app.core.config import settings
from app.core.logger import get_logger
from app.database.db import engine

logger = get_logger(__name__)


class HealthService:
    @staticmethod
    def check_postgres():
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            return "healthy"

        except Exception as e:
            logger.error(f"Postgres health check failed: {e}")
            return "unhealthy"

    @staticmethod
    def check_ollama():
        try:
            response = requests.get(
                f"{settings.OLLAMA_HOST}/api/tags", timeout=5
            )

            if response.status_code == 200:
                return "healthy"

            return "unhealthy"

        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return "unhealthy"

    @staticmethod
    def check_chromadb():
        try:
            client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)

            client.heartbeat()

            return "healthy"

        except Exception as e:
            logger.error(f"ChromaDB health check failed: {e}")
            return "unhealthy"

    @classmethod
    def get_health_status(cls):

        postgres = cls.check_postgres()
        ollama = cls.check_ollama()
        chromadb_status = cls.check_chromadb()

        overall = "healthy"

        if (
            postgres == "unhealthy"
            or ollama == "unhealthy"
            or chromadb_status == "unhealthy"
        ):
            overall = "degraded"

        return {
            "status": overall,
            "postgres": postgres,
            "ollama": ollama,
            "chromadb": chromadb_status,
        }
