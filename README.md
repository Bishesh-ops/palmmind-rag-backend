# PalmMind RAG Backend Assessment

A backend service built with FastAPI that provides document ingestion with chunking, vector-based retrieval, and a conversational RAG interface featuring multi-turn memory and appointment booking.

## Tech Stack

- **Framework:** FastAPI (Python)
- **LLM & Embeddings:** Gemini/Gemini-embedding
- **Vector Database:** Pinecone
- **Relational Database:** SQLite3
- **Memory:** Redis

## Features

1. **Document Ingestion API:** Upload `.pdf` or `.txt` files, apply configurable chunking strategies, generate embeddings, and store metadata.
2. **Conversational RAG API:** A custom Retrieval-Augmented Generation pipeline (built without LangChain's `RetrievalQAChain`) that leverages Redis for multi-turn chat memory.
3. **Interview Booking:** Agentic function calling to extract Name, Email, Date, and Time for automated booking scheduling.

## Local Setup Instructions

1. **Clone the repository:**

```bash
   git clone https://github.com/Bishesh-ops/palmmind-rag-backend.git
```

2. **Create a virtual environment and install dependencies:**

```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
```

W 3. **Set up Environment Variables:**
Create a `.env` file in the root directory and add the necessary keys:

```env
   # Add required API keys here (e.g., Gemini, Pinecone)
   REDIS_URL=redis://localhost:6379
```

4. **Run Redis:**
   Ensure you have a local Redis server running on port 6379.

5. **Start the API server:**

```bash
   uvicorn app.main:app --reload
```

6. **View API Documentation:**
   Open `http://localhost:8000/docs` in your browser to test the endpoints via the interactive Swagger UI.
