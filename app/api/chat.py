from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.relational import get_db
from app.models.schemas import ChatRequest, ChatResponse
from app.services.rag import converse_with_rag

router = APIRouter(prefix="/api/chat", tags=["Conversational AI"])

@router.post("", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """
    Main conversational interface. Handles contextual document lookup
    and automated event extraction transactions.
    """
    try:
        reply = await converse_with_rag(
            session_id=request.session_id,
            user_message=request.message,
            db=db
        )
        return ChatResponse(response=reply)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
