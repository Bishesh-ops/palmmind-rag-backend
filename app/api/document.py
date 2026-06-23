from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.relational import get_db
from app.models.schemas import Document
from app.services.enbedding import embed_and_store
from app.services.ingestion import extract_text_from_file, process_chunks

router = APIRouter(prefix="/api/documents", tags=["Documents"])

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    chunk_strategy: str = Form("paragraph"),
    db: AsyncSession = Depends(get_db)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="File name cannot be empty.")
    if not file.filename.endswith((".pdf", ".txt")):
        raise HTTPException(status_code=400, detail="Only .pdf and .txt files are allowed.")

    if chunk_strategy not in ["fixed", "paragraph"]:
        raise HTTPException(status_code=400, detail="Strategy must be 'fixed' or 'paragraph'.")

    # 2. Read file into memory
    content = await file.read()

    try:
        raw_text = await extract_text_from_file(content, file.filename)
        chunks = process_chunks(raw_text, chunk_strategy)

        new_doc = Document(
            filename=file.filename,
            file_type=file.filename.split('.')[-1],
            chunk_strategy=chunk_strategy
        )
        db.add(new_doc)
        await db.commit()
        await db.refresh(new_doc)
        num_chunks = embed_and_store(chunks, new_doc.id, file.filename)

        return {
            "message": "Document ingested successfully",
            "document_id": new_doc.id,
            "filename": file.filename,
            "chunks_processed": num_chunks,
            "strategy_used": chunk_strategy
        }

    except Exception as e:
        # If anything fails, return a 500 server error safely
        raise HTTPException(status_code=500, detail=str(e))
