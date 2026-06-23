import logging

from pinecone import Pinecone

from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    pinecone_index = pc.Index(settings.PINECONE_INDEX_NAME)
    logger.info(f"Sucessfully connected to Pinecone index: {settings.PINECONE_INDEX_NAME}")

except Exception as e:
    logger.error(f"Failed to connect to Pinecone: {str(e)}")
    pinecone_index = None

def get_vectore_store():
    if pinecone_index is None:
        raise ConnectionError("Pinecone index is not initialised.")
    return pinecone_index
