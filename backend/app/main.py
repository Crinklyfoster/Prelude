from fastapi import FastAPI

from app.core.config import settings
from app.api.document_routes import router as document_router

app = FastAPI(
    title=settings.APP_NAME
)

app.include_router(document_router)


@app.get("/")
def root():
    return {
        "message": "Enterprise RAG Backend Running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }