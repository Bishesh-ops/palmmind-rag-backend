from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "PalmMind RAG Backend"

    GEMINI_API_KEY: str =""
    PINECONE_API_KEY: str = ""

    PINECONE_INDEX_NAME: str = "palmmind-rag"
    REDIS_URL: str = "redis://localhost:6379"
    DATABASE_URL: str = "sqlite+aiosqlite:///./palmmind.db"

    model_config= SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
