from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from prometheus_client import generate_latest

from app.api.chat_routes import router as chat_router
from app.api.document_routes import router as document_router
from app.core.config import settings
from app.core.logger import get_logger
from app.services.health_service import HealthService
from app.api.auth_routes import router as auth_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Enterprise RAG backend starting")
    yield
    logger.info("Enterprise RAG backend shutting down")


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(document_router)
app.include_router(chat_router)
app.include_router(auth_router)


@app.get("/")
def root():
    return {"message": "Enterprise RAG Backend Running"}


@app.get("/health")
def health():
    return HealthService.get_health_status()


@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type="text/plain")
