from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Assesment API for document ingestion and conversational RAG",
    version="1.0.0"
)

@app.get("/health")
async def health_check():
    return{
        "status": "healthy",
        "project": settings.PROJECT_NAME,
    }
