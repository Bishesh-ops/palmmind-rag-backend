from contextlib import asynccontextmanager
from pydoc import doc

from fastapi import FastAPI

from app.api import document
from app.core.config import settings
from app.db.relational import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Assessment API for document ingestion and conversational RAG.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "project": settings.PROJECT_NAME}

app.include_router(document.router)
