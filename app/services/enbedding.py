import uuid

from google import genai

from app.core.config import settings
from app.db.vector_store import get_vector_store

client = genai.Client(api_key=settings.GEMINI_API_KEY)

def embed_and_store(chunks: list[str], document_id: int, filename: str):
    if not chunks:
        return 0

    response = client.models.embed_content(
        model='text-embedding-004',
        contents=chunks
    )
    if not response.embeddings:
        return 0
    embeddings = [e.values for e in response.embeddings]

    vectors = []
    for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        chunk_id = f"doc_{document_id}_chunk_{i}_{uuid.uuid4().hex[:8]}"

        vectors.append({
            "id": chunk_id,
            "values": emb,
            "metadata": {
                "document_id": document_id,
                "filename": filename,
                "text": chunk
            }
        })

    index = get_vector_store()
    index.upsert(vectors=vectors)

    return len(vectors)
